#!/usr/bin/env python3
"""
OSRS Ironman Progression Tracker
Fetches data from official hiscores and reads manual YAML tracking files.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

RSN = os.environ.get("RSN", "FoolinSlays")
DATA_DIR = Path(__file__).parent.parent / "data"

HISCORES_URL = "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.json"

NUM_SKILLS = 24

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

def xp_for_level(level):
    if level < 1: return 0
    if level > 99: return XP_TABLE[98]
    return XP_TABLE[level - 1]

def get_level_progress(xp, level):
    if level >= 99:
        return {"progress": 100, "xp_to_level": 0}
    curr = xp_for_level(level)
    nxt = xp_for_level(level + 1)
    prog = ((xp - curr) / (nxt - curr) * 100) if (nxt - curr) > 0 else 100
    return {"progress": round(prog, 1), "xp_to_level": nxt - xp}

def fetch_json(url, params=None):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OSRS-Ironman-Tracker/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {path}")

def parse_yaml_simple(content):
    """Simple YAML parser for our specific format"""
    result = {}
    current_key = None
    current_subkey = None
    
    for line in content.split('\n'):
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Count leading spaces
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        if indent == 0 and stripped.endswith(':'):
            # Top-level key (collection/tier name)
            current_key = stripped[:-1]
            result[current_key] = {}
            current_subkey = None
        elif indent == 2 and stripped.endswith(':'):
            # Sub-key (obtained/missing or completed/not_completed)
            current_subkey = stripped[:-1]
            result[current_key][current_subkey] = []
        elif stripped.startswith('- ') and current_key and current_subkey:
            # List item
            item = stripped[2:]
            result[current_key][current_subkey].append(item)
        elif stripped == '[]' and current_key and current_subkey:
            # Empty list
            result[current_key][current_subkey] = []
    
    return result

def load_collection_log():
    """Load collection log from YAML file"""
    yaml_path = DATA_DIR / "collection_log.yaml"
    if not yaml_path.exists():
        print(f"Collection log YAML not found: {yaml_path}")
        return None
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    data = parse_yaml_simple(content)
    
    # Convert to structured format
    collections = {}
    total_obtained = 0
    total_items = 0
    
    for collection_name, items in data.items():
        obtained = items.get('obtained', [])
        missing = items.get('missing', [])
        
        collections[collection_name] = {
            'obtained': obtained,
            'missing': missing,
            'obtained_count': len(obtained),
            'total_count': len(obtained) + len(missing)
        }
        
        total_obtained += len(obtained)
        total_items += len(obtained) + len(missing)
    
    return {
        'collections': collections,
        'total_obtained': total_obtained,
        'total_items': total_items
    }

def load_combat_achievements():
    """Load combat achievements from YAML file"""
    yaml_path = DATA_DIR / "combat_achievements.yaml"
    if not yaml_path.exists():
        print(f"Combat achievements YAML not found: {yaml_path}")
        return None
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    data = parse_yaml_simple(content)
    
    # Tier point values
    tier_points = {
        'Easy': 1, 'Medium': 2, 'Hard': 3,
        'Elite': 4, 'Master': 5, 'Grandmaster': 6
    }
    
    tiers = {}
    total_completed = 0
    total_tasks = 0
    total_points = 0
    
    for tier_name in ['Easy', 'Medium', 'Hard', 'Elite', 'Master', 'Grandmaster']:
        if tier_name not in data:
            continue
            
        completed = data[tier_name].get('completed', [])
        not_completed = data[tier_name].get('not_completed', [])
        points = tier_points.get(tier_name, 1)
        
        tiers[tier_name] = {
            'completed': completed,
            'not_completed': not_completed,
            'completed_count': len(completed),
            'total_count': len(completed) + len(not_completed),
            'points_per_task': points,
            'points_earned': len(completed) * points
        }
        
        total_completed += len(completed)
        total_tasks += len(completed) + len(not_completed)
        total_points += len(completed) * points
    
    return {
        'tiers': tiers,
        'total_completed': total_completed,
        'total_tasks': total_tasks,
        'total_points': total_points,
        'max_points': sum(t['total_count'] * t['points_per_task'] for t in tiers.values())
    }

def main():
    now = datetime.now(timezone.utc)
    print(f"Updating stats for: {RSN}")
    print(f"Timestamp: {now.isoformat()}")
    print("-" * 50)

    # Fetch official hiscores
    print("Fetching from official hiscores...")
    official = fetch_json(HISCORES_URL, {"player": RSN})

    # Process skills
    skills = {}
    if official and "skills" in official:
        for s in official["skills"]:
            name, lvl, xp = s.get("name"), s.get("level", 1), s.get("xp", 0)
            skills[name] = {
                "level": lvl, "xp": xp, "rank": s.get("rank", -1),
                "progress": get_level_progress(xp, lvl) if name != "Overall" else None
            }

    # Calculate milestones
    overall = skills.get("Overall", {})
    indiv = {k: v for k, v in skills.items() if k != "Overall"}
    n99 = sum(1 for s in indiv.values() if s.get("level", 0) >= 99)
    
    att = skills.get("Attack", {}).get("level", 1)
    str_ = skills.get("Strength", {}).get("level", 1)
    def_ = skills.get("Defence", {}).get("level", 1)
    hp = skills.get("Hitpoints", {}).get("level", 10)
    pray = skills.get("Prayer", {}).get("level", 1)
    rng = skills.get("Ranged", {}).get("level", 1)
    mag = skills.get("Magic", {}).get("level", 1)
    combat = 0.25 * (def_ + hp + (pray // 2)) + max(0.325 * (att + str_), 0.325 * rng * 1.5, 0.325 * mag * 1.5)

    if skills:
        save_json(DATA_DIR / "skills.json", {
            "rsn": RSN, "updated": now.isoformat(), "skills": skills,
            "milestones": {
                "total_level": overall.get("level", 0),
                "total_xp": overall.get("xp", 0),
                "combat_level": round(combat, 2),
                "skills_99": n99, "num_skills": NUM_SKILLS
            }
        })

    # Process bosses
    bosses = {}
    if official and "activities" in official:
        for a in official["activities"]:
            name, score = a.get("name"), a.get("score", -1)
            if score > 0 and name not in ["Collections Logged", "Combat Achievements"]:
                bosses[name] = {"kc": score, "rank": a.get("rank", -1)}

    if bosses:
        save_json(DATA_DIR / "bosses.json", {"rsn": RSN, "updated": now.isoformat(), "bosses": bosses})

    # Load and save collection log from YAML
    print("Loading collection log from YAML...")
    clog = load_collection_log()
    if clog:
        save_json(DATA_DIR / "collection_log.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "collection_log": clog
        })
        print(f"Collection log: {clog['total_obtained']}/{clog['total_items']} items")
    else:
        print("No collection log data found")

    # Load and save combat achievements from YAML
    print("Loading combat achievements from YAML...")
    ca = load_combat_achievements()
    if ca:
        save_json(DATA_DIR / "combat_achievements.json", {
            "rsn": RSN,
            "updated": now.isoformat(),
            "combat_achievements": ca
        })
        print(f"Combat achievements: {ca['total_completed']}/{ca['total_tasks']} tasks ({ca['total_points']}/{ca['max_points']} points)")
    else:
        print("No combat achievements data found")

    print("-" * 50)
    print("Update complete!")

if __name__ == "__main__":
    main()
