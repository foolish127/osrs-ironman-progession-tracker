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
TEMPLE_COLLECTION_URL = "https://templeosrs.com/api/collection-log/player_collection_log.php"
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


def fetch_temple_collection_log(rsn: str) -> dict | None:
    """Fetch collection log data from TempleOSRS API."""
    # Use the correct endpoint with categories=all to get summary
    data = fetch_json(TEMPLE_COLLECTION_URL, {"player": rsn})
    return data


def fetch_temple_gains(rsn: str, days: int = 30) -> dict | None:
    """Fetch recent gains from TempleOSRS API."""
    # time parameter is in seconds
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
    
    # Prefer official hiscores for accuracy, fall back to Temple
    if official_data and "skills" in official_data:
        for skill_data in official_data["skills"]:
            name = skill_data.get("name", "Unknown")
            skills[name] = {
                "level": skill_data.get("level", 1),
                "xp": skill_data.get("xp", 0),
                "rank": skill_data.get("rank", -1)
            }
    
    # Add EHP data from Temple if available
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
    
    # Get from official hiscores
    if official_data and "activities" in official_data:
        for activity in official_data["activities"]:
            name = activity.get("name", "Unknown")
            score = activity.get("score", -1)
            if score > 0:
                bosses[name] = {
                    "kc": score,
                    "rank": activity.get("rank", -1)
                }
    
    # Add EHB data from Temple
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


def update_collection_log(temple_clog: dict) -> dict:
    """Format collection log data from TempleOSRS API response."""
    if not temple_clog:
        return {}
    
    # The API returns data in different formats, handle both
    if "data" in temple_clog:
        clog_data = temple_clog["data"]
    else:
        clog_data = temple_clog
    
    # Try to extract the summary info
    result = {
        "unique_obtained": clog_data.get("Unique Obtained") or clog_data.get("unique_obtained") or clog_data.get("obtained", 0),
        "unique_items": clog_data.get("Unique") or clog_data.get("unique_items") or clog_data.get("total", 0),
        "rank": clog_data.get("Rank") or clog_data.get("rank", -1),
    }
    
    # If we got item-level data, count them
    if "items" in clog_data:
        result["unique_obtained"] = len(clog_data["items"])
    
    return result


def calculate_milestones(skills: dict) -> dict:
    """Calculate various account milestones."""
    # Use Overall skill's level directly instead of summing
    overall_skill = skills.get("Overall", {})
    total_level = overall_skill.get("level", 0)
    total_xp = overall_skill.get("xp", 0)
    
    # If Overall isn't available, calculate from individual skills
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
    
    # Count skills at various thresholds (excluding Overall)
    individual_skills = {k: v for k, v in skills.items() if k != "Overall"}
    skills_99 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 99)
    skills_90 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 90)
    skills_80 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 80)
    skills_70 = sum(1 for s in individual_skills.values() if s.get("level", 0) >= 70)
    
    # Combat level calculation
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
    temple_clog = fetch_temple_collection_log(RSN)
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
    
    # Save collection log
    clog = update_collection_log(temple_clog)
    if clog:
        save_json(DATA_DIR / "collection_log.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "collection_log": clog
        })
    else:
        print("Note: Collection log data not available. Make sure you've synced via the TempleOSRS RuneLite plugin.")
    
    # Save recent gains for tracking progress
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
