#!/usr/bin/env python3
"""
OSRS Bank Parser and GE Price Fetcher
Parses bank export from Bank Memory plugin and fetches GE prices from OSRS Wiki API.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
GE_PRICES_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
ITEM_MAPPING_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"

# Item categories based on OSRS Wiki categories and common groupings
CATEGORIES = {
    "Food": {
        "Cooked Fish": ["shark", "monkfish", "lobster", "swordfish", "tuna", "salmon", "trout", "bass", "cod", "pike", "anglerfish", "manta ray", "sea turtle", "dark crab", "karambwan"],
        "Raw Fish": ["raw shark", "raw monkfish", "raw lobster", "raw swordfish", "raw tuna", "raw salmon", "raw trout", "raw bass", "raw cod", "raw pike", "raw anglerfish", "raw manta ray"],
        "Cooked Meat": ["cooked", "stew", "pie", "potato"],
        "Fruit": ["fruit", "berries", "papaya", "coconut", "dragonfruit", "grapes", "watermelon"],
        "Other Food": ["sweets", "cake", "bread"]
    },
    "Potions": {
        "Combat Potions": ["super combat", "divine", "ranging potion", "magic potion", "super strength", "super attack", "super defence"],
        "Restoration": ["saradomin brew", "prayer potion", "super restore", "sanfew"],
        "Skilling Potions": ["stamina", "energy", "agility", "hunter"],
        "Unfinished": ["potion (unf)"],
        "Other Potions": ["antifire", "antidote", "antipoison", "antivenom", "relicym"]
    },
    "Runes": {
        "Elemental": ["air rune", "water rune", "earth rune", "fire rune"],
        "Catalytic": ["mind rune", "body rune", "cosmic rune", "chaos rune", "nature rune", "law rune", "death rune", "blood rune", "soul rune", "astral rune", "wrath rune"],
        "Combination": ["mist rune", "dust rune", "mud rune", "smoke rune", "steam rune", "lava rune"],
        "Talismans": ["talisman"]
    },
    "Equipment": {
        "Melee Weapons": ["scimitar", "longsword", "sword", "dagger", "mace", "warhammer", "battleaxe", "2h sword", "halberd", "spear", "whip", "rapier", "hasta", "claws"],
        "Ranged Weapons": ["shortbow", "longbow", "crossbow", "javelin", "dart", "knife", "thrownaxe", "chinchompa", "blowpipe"],
        "Magic Weapons": ["staff", "wand", "trident"],
        "Helmets": ["helm", "hat", "hood", "coif", "mask", "faceguard"],
        "Body Armor": ["platebody", "chainbody", "body", "top", "torso", "chestplate", "hauberk"],
        "Leg Armor": ["platelegs", "plateskirt", "chaps", "legs", "tassets", "cuisse", "skirt", "bottoms", "greaves"],
        "Shields": ["shield", "defender", "kiteshield", "sq shield", "book of"],
        "Gloves": ["gloves", "vambraces", "bracelet", "gauntlets"],
        "Boots": ["boots", "sandals", "shoes"],
        "Capes": ["cape", "cloak", "ava's"],
        "Amulets & Necklaces": ["amulet", "necklace", "fury", "torture", "anguish", "tormented"],
        "Rings": ["ring of", "berserker ring", "archers ring", "seers ring", "warrior ring"]
    },
    "Ammunition": {
        "Arrows": ["arrow", "arrowtips"],
        "Bolts": ["bolt"],
        "Other Ammo": ["cannonball", "javelin", "dart", "knife", "thrownaxe"]
    },
    "Skilling": {
        "Herbs": ["grimy", "guam", "marrentill", "tarromin", "harralander", "ranarr", "irit", "avantoe", "kwuarm", "cadantine", "lantadyme", "dwarf weed", "torstol", "snapdragon", "toadflax"],
        "Seeds": ["seed"],
        "Ores": ["ore", "coal"],
        "Bars": ["bar"],
        "Logs": ["logs"],
        "Planks": ["plank"],
        "Gems": ["sapphire", "emerald", "ruby", "diamond", "dragonstone", "onyx", "opal", "jade", "topaz", "uncut"],
        "Hides & Leather": ["dragonhide", "leather", "hide"],
        "Bones": ["bones", "ashes"],
        "Essence": ["essence"],
        "Farming": ["compost", "ultracompost", "supercompost", "bottomless"],
        "Fishing": ["bait", "feather", "harpoon", "net", "rod"],
        "Hunter": ["trap", "snare", "box trap", "noose", "fur", "kebbit"],
        "Construction": ["nail", "bolt of cloth", "limestone", "marble"]
    },
    "Teleportation": {
        "Jewelry": ["games necklace", "ring of dueling", "amulet of glory", "ring of wealth", "necklace of passage", "digsite pendant", "burning amulet", "skills necklace", "combat bracelet"],
        "Tablets": ["teleport to house", "varrock teleport", "lumbridge teleport", "falador teleport", "camelot teleport"],
        "Other Teleports": ["ectophial", "royal seed pod", "xeric's talisman", "scroll", "drakan's medallion", "teleport crystal"]
    },
    "Clue Items": {
        "Clue Scrolls": ["clue scroll", "scroll box"],
        "Clue Rewards": ["firelighter", "blessing", "ornament kit", "page"]
    },
    "Barrows": {
        "Ahrim's": ["ahrim"],
        "Dharok's": ["dharok"],
        "Guthan's": ["guthan"],
        "Karil's": ["karil"],
        "Torag's": ["torag"],
        "Verac's": ["verac"]
    },
    "Slayer": {
        "Slayer Equipment": ["slayer helmet", "nose peg", "earmuffs", "face mask", "mirror shield", "rock hammer", "bag of salt", "ice cooler", "witchwood icon", "slayer bell", "fungicide"],
        "Ensouled Heads": ["ensouled"],
        "Slayer Drops": ["dark totem", "ancient shard", "brimstone key", "larran's key"]
    },
    "Currency": {
        "Coins & Tokens": ["coins", "platinum token", "tokkul", "trading sticks", "numulite", "golden nugget", "mark of grace", "stardust", "crystal shard", "amylase"]
    },
    "Quest Items": {
        "Quest Items": ["quest", "diary", "scroll"]
    },
    "Miscellaneous": {
        "Tools": ["hammer", "chisel", "knife", "saw", "needle", "tinderbox", "spade", "rake", "trowel", "secateurs", "axe", "pickaxe"],
        "Containers": ["bucket", "jug", "vial", "pot", "bowl", "basket", "sack"],
        "Other": []
    }
}


def fetch_json(url):
    """Fetch JSON from URL with appropriate headers."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "OSRS-Ironman-Tracker/1.0 (GitHub: foolish127)",
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def load_bank_data():
    """Load bank data from YAML-like text file."""
    bank_path = DATA_DIR / "bank.txt"
    if not bank_path.exists():
        print(f"Bank data not found: {bank_path}")
        return None
    
    items = []
    with open(bank_path, 'r') as f:
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
    """Categorize an item based on its name."""
    name_lower = item_name.lower()
    
    for category, subcategories in CATEGORIES.items():
        for subcategory, keywords in subcategories.items():
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


def save_json(path, data):
    """Save data to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {path}")


def main():
    now = datetime.now(timezone.utc)
    print(f"Updating bank data...")
    print(f"Timestamp: {now.isoformat()}")
    print("-" * 50)
    
    # Load bank data
    items = load_bank_data()
    if not items:
        print("No bank data to process.")
        return
    
    print(f"Loaded {len(items)} items from bank")
    
    # Fetch GE prices
    ge_prices = fetch_ge_prices()
    print(f"Fetched prices for {len(ge_prices)} items")
    
    # Process items
    processed_items = []
    total_value = 0
    categories_summary = {}
    
    for item in items:
        item_id = str(item["id"])
        category, subcategory = categorize_item(item["name"])
        
        # Get GE price
        price_data = ge_prices.get(item_id, {})
        high_price = price_data.get("high", 0) or 0
        low_price = price_data.get("low", 0) or 0
        avg_price = (high_price + low_price) // 2 if high_price and low_price else high_price or low_price
        
        item_value = avg_price * item["quantity"]
        total_value += item_value
        
        processed_item = {
            "id": item["id"],
            "name": item["name"],
            "quantity": item["quantity"],
            "ge_price": avg_price,
            "total_value": item_value,
            "category": category,
            "subcategory": subcategory
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
    print("Update complete!")


if __name__ == "__main__":
    main()
