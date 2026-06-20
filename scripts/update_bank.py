#!/usr/bin/env python3
"""
OSRS Bank Parser and GE Price Fetcher
Parses bank export from Bank Memory plugin and fetches GE prices from OSRS Wiki API.
"""

import re
from datetime import datetime, timezone

from osrs_config import CATEGORY_RULES
from osrs_utils import DATA_DIR, fetch_json, save_json
from untradeable_values import UNTRADEABLE_VALUES

GE_PRICES_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
ITEM_MAPPING_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"


def load_bank_data():
    """Load bank data from YAML-like text file."""
    bank_path = DATA_DIR / "bank.txt"
    if not bank_path.exists():
        print(f"Bank data not found: {bank_path}")
        return None

    items = []
    with open(bank_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    # Skip header line
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        parts = line.split('\t')
        if len(parts) >= 3:
            try:
                item_id = int(parts[0])
                item_name = parts[1]
                quantity = int(parts[2])
                items.append({
                    "id": item_id,
                    "name": item_name,
                    "quantity": quantity
                })
            except ValueError:
                continue

    return items


def categorize_item(item_name):
    """Categorize an item based on its name using priority-ordered rules."""
    name_lower = item_name.lower()

    for category, subcategory, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword.lower() in name_lower:
                return category, subcategory

    return "Miscellaneous", "Other"


def fetch_ge_prices():
    """Fetch current GE prices from OSRS Wiki API."""
    print("Fetching GE prices from OSRS Wiki...")
    data = fetch_json(GE_PRICES_URL)
    if data and "data" in data:
        return data["data"]
    return {}


def fetch_item_mapping():
    """Fetch item name to ID mapping from OSRS Wiki API."""
    print("Fetching item mapping...")
    data = fetch_json(ITEM_MAPPING_URL)
    if data:
        # Create name -> id mapping
        return {item.get("name", ""): item.get("id", 0) for item in data}
    return {}


def load_potion_storage_as_items():
    """Load potion storage from YAML and convert doses to 4-dose potions."""
    yaml_path = DATA_DIR / "potion_storage.yaml"
    if not yaml_path.exists():
        print(f"Potion storage YAML not found: {yaml_path}")
        return None

    with open(yaml_path, 'r', encoding="utf-8") as f:
        content = f.read()

    # Simple YAML parsing
    items = []
    current_section = None

    for line in content.split('\n'):
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue

        # Section header
        if not line.startswith(' ') and line.endswith(':'):
            current_section = line[:-1]
        # Item line
        elif current_section and ':' in line:
            line = line.strip()
            parts = line.rsplit(':', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                try:
                    doses = int(parts[1].strip())
                except ValueError:
                    continue
                # Convert doses to 4-dose potions (round up)
                quantity = (doses + 3) // 4

                # Normalize name to (4) version, handling (4)/(3)/(2)/(1).
                # Keep (unf) as-is.
                if '(unf)' in name.lower():
                    normalized_name = name
                else:
                    normalized_name = re.sub(r'\(\d\)$', '(4)', name)

                items.append({
                    "id": 0,  # Will be looked up
                    "name": normalized_name,
                    "quantity": quantity,
                    "source": "potion_storage"
                })

    return items if items else None


def main():
    now = datetime.now(timezone.utc)
    print("Updating bank data...")
    print(f"Timestamp: {now.isoformat()}")
    print("-" * 50)

    # Load bank data
    items = load_bank_data()
    if not items:
        items = []
        print("No bank data found.")
    else:
        print(f"Loaded {len(items)} items from bank")

    # Load potion storage and convert to bank items
    potion_items = load_potion_storage_as_items()
    if potion_items:
        print(f"Loaded {len(potion_items)} potion types from storage")
        items.extend(potion_items)

    if not items:
        print("No data to process.")
        return

    # Fetch GE prices
    ge_prices = fetch_ge_prices()
    print(f"Fetched prices for {len(ge_prices)} items")

    # Fetch item mapping to get IDs for potions
    item_mapping = fetch_item_mapping()
    print(f"Fetched mapping for {len(item_mapping)} items")

    # Process items
    processed_items = []
    total_value = 0
    categories_summary = {}

    for item in items:
        item_id = str(item.get("id", 0))

        # If no ID, try to look it up by name
        if item_id == "0" and item_mapping:
            item_id = str(item_mapping.get(item["name"], 0))

        category, subcategory = categorize_item(item["name"])

        # Get GE price
        price_data = ge_prices.get(item_id, {})
        high_price = price_data.get("high", 0) or 0
        low_price = price_data.get("low", 0) or 0
        avg_price = (high_price + low_price) // 2 if high_price and low_price else high_price or low_price

        # Fall back to manual override for untradeables (ge_price == 0)
        if avg_price == 0:
            avg_price = UNTRADEABLE_VALUES.get(int(item_id) if item_id.isdigit() else 0, 0)

        item_value = avg_price * item["quantity"]
        total_value += item_value

        processed_item = {
            "id": int(item_id) if item_id.isdigit() else 0,
            "name": item["name"],
            "quantity": item["quantity"],
            "ge_price": avg_price,
            "total_value": item_value,
            "category": category,
            "subcategory": subcategory,
            "source": item.get("source", "bank")
        }
        processed_items.append(processed_item)

        # Track category totals
        if category not in categories_summary:
            categories_summary[category] = {"count": 0, "value": 0, "subcategories": {}}
        categories_summary[category]["count"] += item["quantity"]
        categories_summary[category]["value"] += item_value

        if subcategory not in categories_summary[category]["subcategories"]:
            categories_summary[category]["subcategories"][subcategory] = {"count": 0, "value": 0}
        categories_summary[category]["subcategories"][subcategory]["count"] += item["quantity"]
        categories_summary[category]["subcategories"][subcategory]["value"] += item_value

    # Sort by value for top items
    sorted_by_value = sorted(processed_items, key=lambda x: x["total_value"], reverse=True)
    top_items = sorted_by_value[:10]

    # Build output
    output = {
        "updated": now.isoformat(),
        "total_items": len(processed_items),
        "total_quantity": sum(i["quantity"] for i in processed_items),
        "total_value": total_value,
        "top_items": top_items,
        "categories": categories_summary,
        "items": processed_items
    }

    save_json(DATA_DIR / "bank.json", output)

    print("-" * 50)
    print(f"Total items: {len(processed_items)}")
    print(f"Total value: {total_value:,} gp")

    # Surface items that fell through to the catch-all so you can add keyword
    # rules for them (these are the ones whose categorization is just a guess).
    uncategorized = sorted(
        {i["name"] for i in processed_items
         if i["category"] == "Miscellaneous" and i["subcategory"] == "Other"}
    )
    if uncategorized:
        print("-" * 50)
        print(f"{len(uncategorized)} uncategorized item(s) -> Miscellaneous/Other:")
        for name in uncategorized:
            print(f"  - {name}")
        print("Add keywords to CATEGORY_RULES in osrs_config.py to classify these.")

    print("Update complete!")


if __name__ == "__main__":
    main()
