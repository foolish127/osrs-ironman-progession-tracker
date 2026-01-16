#!/usr/bin/env python3
"""
OSRS Ironman Progression Tracker
Fetches data from TempleOSRS API and official hiscores, updates local JSON files.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# Configuration
RSN = os.environ.get("RSN", "FoolinSlays")
DATA_DIR = Path(__file__).parent.parent / "data"

# API URLs
TEMPLE_STATS_URL = "https://templeosrs.com/api/player_stats.php"
TEMPLE_PLAYER_CLOG_URL = "https://templeosrs.com/api/collection-log/player_collection_log.php"
TEMPLE_CLOG_CATEGORIES_URL = "https://templeosrs.com/api/collection-log/categories.php"
TEMPLE_CLOG_ITEMS_URL = "https://templeosrs.com/api/collection-log/items.php"
TEMPLE_GAINS_URL = "https://templeosrs.com/api/player_gains.php"
HISCORES_URL = "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json"

# All 24 skills (including Sailing)
SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecraft", "Hunter", "Construction",
    "Sailing"
]

# Number of actual trainable skills (excluding Overall)
NUM_SKILLS = 24

# Boss list (subset - full list in actual API response)
BOSSES = [
    "Abyssal Sire", "Alchemical Hydra", "Araxxor", "Barrows Chests", 
    "Bryophyta", "Callisto", "Cerberus", "Chambers of Xeric",
    "Chambers of Xeric: Challenge Mode", "Chaos Elemental", "Chaos Fanatic",
    "Commander Zilyana", "Corporeal Beast", "Dagannoth Prime",
    "Dagannoth Rex", "Dagannoth Supreme", "Duke Sucellus", "General Graardor",
    "Giant Mole", "Grotesque Guardians", "Hespori", "Kalphite Queen",
    "King Black Dragon", "Kraken", "Kree'Arra", "K'ril Tsutsaroth",
    "Mimic", "Nex", "Nightmare", "Obor", "Phantom Muspah", "Sarachnis",
    "Scorpia", "Skotizo", "Sol Heredit", "Tempoross", "The Gauntlet",
    "The Corrupted Gauntlet", "The Hueycoatl", "The Leviathan",
    "Theatre of Blood", "Theatre of Blood: Hard Mode", "Thermonuclear Smoke Devil",
    "Tombs of Amascut", "Tombs of Amascut: Expert Mode", "TzKal-Zuk",
    "TzTok-Jad", "Vardorvis", "Venenatis", "Vet'ion", "Vorkath",
    "Wintertodt", "Zalcano", "Zulrah"
]


def fetch_json(url: str, params: dict = None) -> dict | None:
    """Fetch JSON from a URL with optional query parameters."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OSRS-Ironman-Tracker/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def fetch_temple_stats(rsn: str) -> dict | None:
    """Fetch player stats from TempleOSRS API."""
    data = fetch_json(TEMPLE_STATS_URL, {"player": rsn, "bosses": 1})
    if data and "data" in data:
        return data["data"]
    return None


def fetch_temple_collection_log(rsn: str) -> tuple[dict | None, dict | None, dict | None]:
    """
    Fetch collection log data from TempleOSRS API.
    Returns: (player_items, all_categories, item_names)
    """
    # Fetch player's obtained items with all categories
    player_data = fetch_json(TEMPLE_PLAYER_CLOG_URL, {"player": rsn, "categories": "all"})
    
    # Fetch the master list of all categories and their items
    categories_data = fetch_json(TEMPLE_CLOG_CATEGORIES_URL)
    
    # Fetch item ID to name mapping
    items_data = fetch_json(TEMPLE_CLOG_ITEMS_URL)
    
    return player_data, categories_data, items_data


def fetch_temple_gains(rsn: str, days: int = 30) -> dict | None:
    """Fetch recent gains from TempleOSRS API."""
    data = fetch_json(TEMPLE_GAINS_URL, {"player": rsn, "time": days * 86400, "bosses": 1})
    if data and "data" in data:
        return data["data"]
    return None


def fetch_official_hiscores(rsn: str) -> dict | None:
    """Fetch from official OSRS hiscores JSON endpoint."""
    data = fetch_json(HISCORES_URL, {"player": rsn})
    return data


def load_json(filepath: Path) -> dict:
    """Load JSON file or return empty dict."""
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def save_json(filepath: Path, data: dict):
    """Save data to JSON file with pretty formatting."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filepath}")


def update_skills_data(temple_data: dict, official_data: dict) -> dict:
    """Merge and format skills data from both sources."""
    skills = {}
    
    if official_data and "skills" in official_data:
        for skill_data in official_data["skills"]:
            name = skill_data.get("name", "Unknown")
            skills[name] = {
                "level": skill_data.get("level", 1),
                "xp": skill_data.get("xp", 0),
                "rank": skill_data.get("rank", -1)
            }
    
    if temple_data:
        for skill in SKILLS:
            skill_key = skill.lower().replace(" ", "_")
            if skill_key in temple_data:
                if skill not in skills:
                    skills[skill] = {}
                temple_skill = temple_data[skill_key]
                if isinstance(temple_skill, dict):
                    skills[skill]["ehp"] = temple_skill.get("ehp", 0)
    
    return skills


def update_bosses_data(temple_data: dict, official_data: dict) -> dict:
    """Merge and format boss KC data from both sources."""
    bosses = {}
    
    if official_data and "activities" in official_data:
        for activity in official_data["activities"]:
            name = activity.get("name", "Unknown")
            score = activity.get("score", -1)
            if score > 0:
                bosses[name] = {
                    "kc": score,
                    "rank": activity.get("rank", -1)
                }
    
    if temple_data:
        for boss in BOSSES:
            boss_key = boss.lower().replace(" ", "_").replace("'", "").replace(":", "")
            if boss_key in temple_data:
                if boss not in bosses:
                    bosses[boss] = {"kc": 0, "rank": -1}
                temple_boss = temple_data[boss_key]
                if isinstance(temple_boss, dict):
                    bosses[boss]["ehb"] = temple_boss.get("ehb", 0)
    
    return bosses


def process_collection_log(player_data: dict, categories_data: dict, items_data: dict) -> dict:
    """
    Process collection log data into a structured format.
    """
    result = {
        "obtained_items": [],  # List of item IDs the player has
        "categories": {},      # Category -> list of items with obtained status
        "item_names": {},      # Item ID -> name mapping
        "summary": {
            "unique_obtained": 0,
            "unique_total": 0,
            "rank": -1
        }
    }
    
    # Store item names mapping
    if items_data and "data" in items_data:
        result["item_names"] = {str(k): v for k, v in items_data["data"].items()}
    elif items_data:
        result["item_names"] = {str(k): v for k, v in items_data.items()}
    
    # Get player's obtained items
    obtained_set = set()
    if player_data and "data" in player_data:
        pdata = player_data["data"]
        # The API returns items as a dict with item_id: count or as a list
        if isinstance(pdata, dict):
            for key, value in pdata.items():
                if key.isdigit():
                    obtained_set.add(str(key))
                elif key == "items" and isinstance(value, (list, dict)):
                    if isinstance(value, list):
                        obtained_set.update(str(i) for i in value)
                    else:
                        obtained_set.update(str(k) for k in value.keys())
        elif isinstance(pdata, list):
            obtained_set.update(str(i) for i in pdata)
    elif player_data:
        # Try direct access if no "data" wrapper
        if isinstance(player_data, dict):
            for key, value in player_data.items():
                if key.isdigit():
                    obtained_set.add(str(key))
    
    result["obtained_items"] = list(obtained_set)
    
    # Process categories
    total_items = 0
    if categories_data and "data" in categories_data:
        cats = categories_data["data"]
    elif categories_data:
        cats = categories_data
    else:
        cats = {}
    
    for cat_name, cat_items in cats.items():
        if not isinstance(cat_items, list):
            continue
        
        cat_item_list = []
        for item_id in cat_items:
            item_id_str = str(item_id)
            item_name = result["item_names"].get(item_id_str, f"Item {item_id}")
            cat_item_list.append({
                "id": item_id_str,
                "name": item_name,
                "obtained": item_id_str in obtained_set
            })
            total_items += 1
        
        result["categories"][cat_name] = cat_item_list
    
    result["summary"]["unique_obtained"] = len(obtained_set)
    result["summary"]["unique_total"] = total_items if total_items > 0 else len(result["item_names"])
    
    return result


def calculate_milestones(skills: dict) -> dict:
    """Calculate various account milestones."""
    overall_skill = skills.get("Overall", {})
    total_level = overall_skill.get("level", 0)
    total_xp = overall_skill.get("xp", 0)
    
    if total_level == 0:
        total_level = sum(
            s.get("level", 1) 
            for name, s in skills.items() 
            if name != "Overall" and s.get("level")
        )
        total_xp = sum(
            s.get("xp", 0) 
            for name, s in skills.items() 
            if name != "Overall" and s.get("xp")
        )
    
    individual_skills = {k: v for k, v in skills.items() if k != "Overall"}
    skills_99 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 99)
    skills_90 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 90)
    skills_80 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 80)
    skills_70 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 70)
    
    attack = skills.get("Attack", {}).get("level", 1)
    strength = skills.get("Strength", {}).get("level", 1)
    defence = skills.get("Defence", {}).get("level", 1)
    hitpoints = skills.get("Hitpoints", {}).get("level", 10)
    prayer = skills.get("Prayer", {}).get("level", 1)
    ranged = skills.get("Ranged", {}).get("level", 1)
    magic = skills.get("Magic", {}).get("level", 1)
    
    base = 0.25 * (defence + hitpoints + (prayer // 2))
    melee = 0.325 * (attack + strength)
    range_cb = 0.325 * (ranged * 1.5)
    mage_cb = 0.325 * (magic * 1.5)
    combat_level = base + max(melee, range_cb, mage_cb)
    
    return {
        "total_level": total_level,
        "total_xp": total_xp,
        "combat_level": round(combat_level, 2),
        "skills_99": skills_99,
        "skills_90": skills_90,
        "skills_80": skills_80,
        "skills_70": skills_70,
        "num_skills": NUM_SKILLS,
        "maxed": skills_99 == NUM_SKILLS
    }


def main():
    now = datetime.now(timezone.utc)
    print(f"Updating stats for: {RSN}")
    print(f"Timestamp: {now.isoformat()}")
    print("-" * 50)
    
    # Fetch from all sources
    print("Fetching from TempleOSRS...")
    temple_stats = fetch_temple_stats(RSN)
    player_clog, clog_categories, clog_items = fetch_temple_collection_log(RSN)
    temple_gains = fetch_temple_gains(RSN)
    
    print("Fetching from official hiscores...")
    official_data = fetch_official_hiscores(RSN)
    
    # Process and save skills
    skills = update_skills_data(temple_stats, official_data)
    if skills:
        save_json(DATA_DIR / "skills.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "skills": skills,
            "milestones": calculate_milestones(skills)
        })
    
    # Process and save bosses
    bosses = update_bosses_data(temple_stats, official_data)
    if bosses:
        save_json(DATA_DIR / "bosses.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "bosses": bosses
        })
    
    # Process and save collection log
    clog = process_collection_log(player_clog, clog_categories, clog_items)
    if clog["summary"]["unique_obtained"] > 0 or clog["categories"]:
        save_json(DATA_DIR / "collection_log.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "collection_log": clog["summary"],
            "obtained_items": clog["obtained_items"],
            "categories": clog["categories"],
            "item_names": clog["item_names"]
        })
        print(f"Collection log: {clog['summary']['unique_obtained']} / {clog['summary']['unique_total']} items")
    else:
        print("Note: Collection log data not available. Make sure you've synced via the TempleOSRS RuneLite plugin.")
    
    # Save recent gains
    if temple_gains:
        save_json(DATA_DIR / "recent_gains.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "period_days": 30,
            "gains": temple_gains
        })
    
    print("-" * 50)
    print("Update complete!")


if __name__ == "__main__":
    main()
