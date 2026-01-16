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

SKILLS = [
    "Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged",
    "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
    "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
    "Thieving", "Slayer", "Farming", "Runecraft", "Hunter", "Construction",
    "Sailing"
]

NUM_SKILLS = 24

# XP table for levels 1-99
XP_TABLE = [
    0, 83, 174, 276, 388, 512, 650, 801, 969, 1154, 1358, 1584, 1833, 2107,
    2411, 2746, 3115, 3523, 3973, 4470, 5018, 5624, 6291, 7028, 7842, 8740,
    9730, 10824, 12031, 13363, 14833, 16456, 18247, 20224, 22406, 24815,
    27473, 30408, 33648, 37224, 41171, 45529, 50339, 55649, 61512, 67983,
    75127, 83014, 91721, 101333, 111945, 123660, 136594, 150872, 166636,
    184040, 203254, 224466, 247886, 273742, 302288, 333804, 368599, 407015,
    449428, 496254, 547953, 605032, 668051, 737627, 814445, 899257, 992895,
    1096278, 1210421, 1336443, 1475581, 1629200, 1798808, 1986068, 2192818,
    2421087, 2673114, 2951373, 3258594, 3597792, 3972294, 4385776, 4842295,
    5346332, 5902831, 6517253, 7195629, 7944614, 8771558, 9684577, 10692629,
    11805606, 13034431
]

def xp_for_level(level: int) -> int:
    if level < 1: return 0
    if level > 99: return XP_TABLE[98]
    return XP_TABLE[level - 1]

def get_level_progress(xp: int, current_level: int) -> dict:
    if current_level >= 99:
        return {"progress": 100, "xp_to_level": 0}
    current_level_xp = xp_for_level(current_level)
    next_level_xp = xp_for_level(current_level + 1)
    xp_in_level = xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    progress = (xp_in_level / xp_needed * 100) if xp_needed > 0 else 100
    return {
        "progress": round(progress, 1),
        "xp_to_level": next_level_xp - xp
    }

def fetch_json(url: str, params: dict = None) -> dict | None:
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
    data = fetch_json(TEMPLE_STATS_URL, {"player": rsn, "bosses": 1})
    return data.get("data") if data else None

def fetch_temple_collection_log(rsn: str) -> tuple:
    player_data = fetch_json(TEMPLE_PLAYER_CLOG_URL, {"player": rsn, "categories": "all"})
    categories_data = fetch_json(TEMPLE_CLOG_CATEGORIES_URL)
    items_data = fetch_json(TEMPLE_CLOG_ITEMS_URL)
    return player_data, categories_data, items_data

def fetch_temple_gains(rsn: str, days: int = 30) -> dict | None:
    data = fetch_json(TEMPLE_GAINS_URL, {"player": rsn, "time": days * 86400, "bosses": 1})
    return data.get("data") if data else None

def fetch_official_hiscores(rsn: str) -> dict | None:
    return fetch_json(HISCORES_URL, {"player": rsn})

def save_json(filepath: Path, data: dict):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filepath}")

def update_skills_data(temple_data: dict, official_data: dict) -> dict:
    skills = {}
    if official_data and "skills" in official_data:
        for skill_data in official_data["skills"]:
            name = skill_data.get("name", "Unknown")
            level = skill_data.get("level", 1)
            xp = skill_data.get("xp", 0)
            skills[name] = {
                "level": level,
                "xp": xp,
                "rank": skill_data.get("rank", -1),
                "progress": get_level_progress(xp, level) if name != "Overall" else None
            }
    return skills

def update_bosses_data(official_data: dict) -> dict:
    bosses = {}
    if official_data and "activities" in official_data:
        for activity in official_data["activities"]:
            name = activity.get("name", "Unknown")
            score = activity.get("score", -1)
            if score > 0:
                bosses[name] = {"kc": score, "rank": activity.get("rank", -1)}
    return bosses

def get_collection_log_count(official_data: dict) -> int:
    if not official_data or "activities" not in official_data:
        return 0
    for activity in official_data["activities"]:
        if activity.get("name") == "Collections Logged":
            return max(0, activity.get("score", 0))
    return 0

def process_collection_log(player_data, categories_data, items_data, official_count: int) -> dict:
    result = {
        "obtained_items": [],
        "categories": {},
        "item_names": {},
        "summary": {"unique_obtained": official_count, "unique_total": 1615, "rank": -1}
    }
    
    if items_data:
        data = items_data.get("data", items_data)
        if isinstance(data, dict):
            result["item_names"] = {str(k): v for k, v in data.items()}
    
    obtained_set = set()
    if player_data:
        pdata = player_data.get("data", player_data)
        if isinstance(pdata, dict):
            for key, value in pdata.items():
                if key.isdigit():
                    obtained_set.add(str(key))
                elif isinstance(value, dict):
                    for item_id in value.keys():
                        if str(item_id).isdigit():
                            obtained_set.add(str(item_id))
        elif isinstance(pdata, list):
            obtained_set.update(str(i) for i in pdata)
    
    result["obtained_items"] = list(obtained_set)
    
    if categories_data:
        cats = categories_data.get("data", categories_data)
        total_items = 0
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
        if total_items > 0:
            result["summary"]["unique_total"] = total_items
    
    if obtained_set and official_count == 0:
        result["summary"]["unique_obtained"] = len(obtained_set)
    
    return result

def calculate_milestones(skills: dict) -> dict:
    overall = skills.get("Overall", {})
    total_level = overall.get("level", 0)
    total_xp = overall.get("xp", 0)
    
    individual = {k: v for k, v in skills.items() if k != "Overall"}
    skills_99 = sum(1 for s in individual.values() if s.get("level", 0) >= 99)
    skills_90 = sum(1 for s in individual.values() if s.get("level", 0) >= 90)
    
    att = skills.get("Attack", {}).get("level", 1)
    str_ = skills.get("Strength", {}).get("level", 1)
    def_ = skills.get("Defence", {}).get("level", 1)
    hp = skills.get("Hitpoints", {}).get("level", 10)
    pray = skills.get("Prayer", {}).get("level", 1)
    rng = skills.get("Ranged", {}).get("level", 1)
    mag = skills.get("Magic", {}).get("level", 1)
    
    base = 0.25 * (def_ + hp + (pray // 2))
    melee = 0.325 * (att + str_)
    combat = base + max(melee, 0.325 * rng * 1.5, 0.325 * mag * 1.5)
    
    return {
        "total_level": total_level,
        "total_xp": total_xp,
        "combat_level": round(combat, 2),
        "skills_99": skills_99,
        "skills_90": skills_90,
        "num_skills": NUM_SKILLS,
        "maxed": skills_99 == NUM_SKILLS
    }

def main():
    now = datetime.now(timezone.utc)
    print(f"Updating stats for: {RSN}")
    print(f"Timestamp: {now.isoformat()}")
    print("-" * 50)
    
    print("Fetching from TempleOSRS...")
    temple_stats = fetch_temple_stats(RSN)
    player_clog, clog_categories, clog_items = fetch_temple_collection_log(RSN)
    temple_gains = fetch_temple_gains(RSN)
    
    print("Fetching from official hiscores...")
    official_data = fetch_official_hiscores(RSN)
    
    clog_count = get_collection_log_count(official_data)
    print(f"Official collection log count: {clog_count}")
    
    skills = update_skills_data(temple_stats, official_data)
    if skills:
        save_json(DATA_DIR / "skills.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "skills": skills,
            "milestones": calculate_milestones(skills)
        })
    
    bosses = update_bosses_data(official_data)
    if bosses:
        save_json(DATA_DIR / "bosses.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "bosses": bosses
        })
    
    clog = process_collection_log(player_clog, clog_categories, clog_items, clog_count)
    save_json(DATA_DIR / "collection_log.json", {
        "rsn": RSN,
        "updated": now.isoformat(),
        "collection_log": clog["summary"],
        "obtained_items": clog["obtained_items"],
        "categories": clog["categories"],
        "item_names": clog["item_names"]
    })
    print(f"Collection log: {clog['summary']['unique_obtained']} / {clog['summary']['unique_total']} items")
    
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
