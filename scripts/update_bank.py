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

# Categories checked in priority order - more specific categories first
# Each tuple is (category, subcategory, keywords)
CATEGORY_RULES = [
    # Barrows - check first since they contain equipment keywords
    ("Barrows", "Ahrim's", ["ahrim"]),
    ("Barrows", "Dharok's", ["dharok"]),
    ("Barrows", "Guthan's", ["guthan"]),
    ("Barrows", "Karil's", ["karil"]),
    ("Barrows", "Torag's", ["torag"]),
    ("Barrows", "Verac's", ["verac"]),
    
    # Moon armor sets - check before general equipment
    ("Moon Armor", "Blood Moon", ["blood moon"]),
    ("Moon Armor", "Blue Moon", ["blue moon"]),
    ("Moon Armor", "Eclipse Moon", ["eclipse moon"]),
    
    # Currency - check early for coins
    ("Currency", "Coins & Tokens", ["coins", "platinum token", "tokkul", "trading sticks", "numulite", "golden nugget", "mark of grace", "stardust", "crystal shard", "amylase", "warrior guild token", "ecto-token"]),
    
    # Runes - check before other categories
    ("Runes", "Elemental", ["air rune", "water rune", "earth rune", "fire rune"]),
    ("Runes", "Catalytic", ["mind rune", "body rune", "cosmic rune", "chaos rune", "nature rune", "law rune", "death rune", "blood rune", "soul rune", "astral rune", "wrath rune"]),
    ("Runes", "Combination", ["mist rune", "dust rune", "mud rune", "smoke rune", "steam rune", "lava rune"]),
    ("Runes", "Talismans", ["talisman"]),
    
    # Food - raw fish before cooked to avoid overlap
    ("Food", "Raw Fish", ["raw shark", "raw monkfish", "raw lobster", "raw swordfish", "raw tuna", "raw salmon", "raw trout", "raw bass", "raw cod", "raw pike", "raw anglerfish", "raw manta ray", "raw karambwan", "raw sardine"]),
    ("Food", "Cooked Fish", ["shark", "monkfish", "lobster", "swordfish", "tuna", "salmon", "trout", "bass", "cod", "pike", "anglerfish", "manta ray", "sea turtle", "dark crab", "karambwan"]),
    ("Food", "Cooked Meals", ["stew", "pie", "potato", "pizza"]),
    ("Food", "Fruit", ["fruit", "berries", "papaya", "coconut", "dragonfruit", "grapes", "watermelon", "calquat"]),
    ("Food", "Other Food", ["sweets", "cake", "bread", "moth"]),
    
    # Potions
    ("Potions", "Unfinished", ["potion (unf)"]),
    ("Potions", "Combat Potions", ["super combat", "divine", "ranging potion", "magic potion", "super strength", "super attack", "super defence"]),
    ("Potions", "Restoration", ["saradomin brew", "prayer potion", "super restore", "sanfew", "guthix rest"]),
    ("Potions", "Skilling Potions", ["stamina", "energy potion", "agility potion", "hunter potion"]),
    ("Potions", "Other Potions", ["antifire", "antidote", "antipoison", "antivenom", "relicym", "balm"]),
    
    # Slayer - before equipment
    ("Slayer", "Ensouled Heads", ["ensouled"]),
    ("Slayer", "Slayer Equipment", ["slayer helmet", "nose peg", "earmuffs", "face mask", "mirror shield", "rock hammer", "bag of salt", "ice cooler", "witchwood icon", "slayer bell", "fungicide", "slayer's staff", "leaf-bladed"]),
    ("Slayer", "Slayer Drops", ["dark totem", "ancient shard", "brimstone key", "larran's key"]),
    
    # Ammunition - before equipment to catch darts/knives
    ("Ammunition", "Arrows", ["arrow", "arrowtips"]),
    ("Ammunition", "Bolts", ["bolt"]),
    ("Ammunition", "Cannonballs", ["cannonball"]),
    ("Ammunition", "Other Ammo", ["javelin", "dart", "thrownaxe", "chinchompa", "atlatl dart"]),
    
    # Teleportation
    ("Teleportation", "Jewelry", ["games necklace", "ring of dueling", "amulet of glory", "ring of wealth", "necklace of passage", "digsite pendant", "burning amulet", "skills necklace", "combat bracelet"]),
    ("Teleportation", "Tablets", ["teleport to house", "varrock teleport", "lumbridge teleport", "falador teleport", "camelot teleport"]),
    ("Teleportation", "Other Teleports", ["ectophial", "royal seed pod", "xeric's talisman", "drakan's medallion", "teleport crystal", "pharaoh's sceptre", "skull sceptre"]),
    
    # Clue Items
    ("Clue Items", "Clue Scrolls", ["clue scroll", "scroll box"]),
    ("Clue Items", "Clue Rewards", ["firelighter", "blessing", "ornament kit"]),
    
    # Skilling materials
    ("Skilling", "Herbs", ["grimy", "guam leaf", "marrentill", "tarromin", "harralander", "ranarr", "irit leaf", "avantoe", "kwuarm", "cadantine", "lantadyme", "dwarf weed", "torstol", "snapdragon", "toadflax"]),
    ("Skilling", "Seeds", ["seed"]),
    ("Skilling", "Ores", [" ore", "coal"]),
    ("Skilling", "Bars", [" bar"]),
    ("Skilling", "Logs", ["logs"]),
    ("Skilling", "Planks", ["plank"]),
    ("Skilling", "Gems", ["sapphire", "emerald", "ruby", "diamond", "dragonstone", "onyx", "opal", "jade", "topaz", "uncut"]),
    ("Skilling", "Hides & Leather", ["dragonhide", "leather", "cowhide"]),
    ("Skilling", "Bones", ["bones"]),
    ("Skilling", "Ashes", ["ashes"]),
    ("Skilling", "Essence", ["essence"]),
    ("Skilling", "Farming", ["compost", "bottomless", "secateurs", "seaweed", "spore"]),
    ("Skilling", "Fishing", ["bait", "feather", "harpoon", "fishing net", "fishing rod", "sandworms"]),
    ("Skilling", "Hunter", ["trap", "snare", "box trap", "noose", "fur", "kebbit", "salamander", "chinchompa"]),
    ("Skilling", "Construction", ["nail", "bolt of cloth", "limestone", "marble"]),
    ("Skilling", "Crafting", ["molten glass", "glassblowing", "lantern lens", "orb"]),
    
    # Equipment - checked last since many items contain these keywords
    ("Equipment", "Melee Weapons", ["scimitar", "longsword", "sword", "dagger", "mace", "warhammer", "battleaxe", "2h sword", "halberd", "spear", "whip", "rapier", "hasta", "claws", "maul", "axe"]),
    ("Equipment", "Ranged Weapons", ["shortbow", "longbow", "crossbow", "blowpipe"]),
    ("Equipment", "Magic Weapons", ["staff", "wand", "trident"]),
    ("Equipment", "Helmets", ["helm", "hat", "hood", "coif", "mask", "faceguard"]),
    ("Equipment", "Body Armor", ["platebody", "chainbody", "body", "top", "torso", "chestplate", "hauberk", "robetop"]),
    ("Equipment", "Leg Armor", ["platelegs", "plateskirt", "chaps", "tassets", "cuisse", "greaves", "robeskirt", "robe bottom"]),
    ("Equipment", "Shields", ["shield", "defender", "kiteshield", "sq shield", "book of"]),
    ("Equipment", "Gloves", ["gloves", "vambraces", "gauntlets"]),
    ("Equipment", "Boots", ["boots", "sandals", "shoes"]),
    ("Equipment", "Capes", ["cape", "cloak", "ava's"]),
    ("Equipment", "Amulets & Necklaces", ["amulet", "necklace", "fury", "torture", "anguish", "tormented"]),
    ("Equipment", "Rings", ["ring of", "berserker ring", "archers ring", "seers ring", "warrior ring", "ring (i)"]),
    ("Equipment", "Bracelets", ["bracelet"]),
    
    # Quest Items - very generic, keep near end
    ("Quest Items", "Quest Items", ["greegree", "sigil", "seal of passage"]),
    
    # Miscellaneous - catchall at the end
    ("Miscellaneous", "Tools", ["hammer", "chisel", "knife", "saw", "needle", "tinderbox", "spade", "rake", "trowel", "pickaxe"]),
    ("Miscellaneous", "Containers", ["bucket", "jug", "vial", "pot", "bowl", "basket", "sack", "pouch"]),
]


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
    print("Update complete!")


def fetch_item_mapping():
    """Fetch item name to ID mapping from OSRS Wiki API."""
    print("Fetching item mapping...")
    data = fetch_json(ITEM_MAPPING_URL)
    if data:
        # Create name -> id mapping
        mapping = {}
        for item in data:
            mapping[item.get("name", "")] = item.get("id", 0)
        return mapping
    return {}


def load_potion_storage_as_items():
    """Load potion storage from YAML and convert doses to 4-dose potions."""
    yaml_path = DATA_DIR / "potion_storage.yaml"
    if not yaml_path.exists():
        print(f"Potion storage YAML not found: {yaml_path}")
        return None
    
    with open(yaml_path, 'r') as f:
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
                    # Convert doses to 4-dose potions (round up)
                    quantity = (doses + 3) // 4
                    
                    # Normalize name to (4) version
                    # Handle various formats like (4), (3), (2), (1), (unf)
                    import re
                    normalized_name = re.sub(r'\(\d\)$', '(4)', name)
                    # Keep (unf) as-is
                    if '(unf)' in name.lower():
                        normalized_name = name
                    
                    items.append({
                        "id": 0,  # Will be looked up
                        "name": normalized_name,
                        "quantity": quantity,
                        "source": "potion_storage"
                    })
                except ValueError:
                    pass
    
    return items if items else None


if __name__ == "__main__":
    main()
