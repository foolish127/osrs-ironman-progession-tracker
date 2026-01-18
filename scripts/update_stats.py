#!/usr/bin/env python3
"""
OSRS Ironman Progression Tracker
Fetches data from official hiscores and TempleOSRS API.
Preserves manually-entered dates from YAML files.
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
TEMPLE_CLOG_URL = "https://templeosrs.com/api/collection-log/player_collection_log.php"

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

def parse_item_with_date(line):
    """Parse 'item name | 2024-01-15' or 'item name |' or 'item name'"""
    line = line.strip()
    if ' | ' in line:
        parts = line.split(' | ', 1)
        name = parts[0].strip()
        date = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        return {'name': name, 'date': date}
    elif line.endswith(' |'):
        return {'name': line[:-2].strip(), 'date': None}
    else:
        return {'name': line, 'date': None}

def parse_yaml_with_dates(content):
    """Parse YAML with optional date support (item | date format)"""
    result = {}
    current_key = None
    current_subkey = None
    
    for line in content.split('\n'):
        if not line or line.startswith('#'):
            continue
        
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        if indent == 0 and stripped.endswith(':'):
            current_key = stripped[:-1]
            result[current_key] = {}
            current_subkey = None
        elif indent == 2 and stripped.endswith(':'):
            current_subkey = stripped[:-1]
            result[current_key][current_subkey] = []
        elif stripped.startswith('- ') and current_key and current_subkey:
            item_text = stripped[2:]
            item = parse_item_with_date(item_text)
            result[current_key][current_subkey].append(item)
    
    return result

def load_manual_dates():
    """Load manually-entered dates from collection_log.yaml"""
    yaml_path = DATA_DIR / "collection_log.yaml"
    if not yaml_path.exists():
        return {}
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    data = parse_yaml_with_dates(content)
    
    # Build a lookup: item_name -> date
    dates = {}
    for collection_name, items in data.items():
        for item in items.get('obtained', []):
            if item.get('date'):
                # Store by item name (lowercase for matching)
                dates[item['name'].lower()] = item['date']
    
    return dates

def fetch_temple_collection_log(rsn):
    """Fetch collection log from TempleOSRS API"""
    print(f"Fetching collection log from TempleOSRS for {rsn}...")
    
    # Fetch all categories
    data = fetch_json(TEMPLE_CLOG_URL, {"player": rsn})
    
    if not data:
        print("Failed to fetch from TempleOSRS")
        return None
    
    if "error" in data:
        print(f"TempleOSRS error: {data['error']}")
        return None
    
    return data

def load_collection_log():
    """
    Load collection log from TempleOSRS API, preserving manual dates.
    Falls back to YAML if API fails.
    """
    # Load manual dates first
    manual_dates = load_manual_dates()
    print(f"Loaded {len(manual_dates)} manual dates from YAML")
    
    # Try TempleOSRS API
    temple_data = fetch_temple_collection_log(RSN)
    
    if temple_data and 'data' in temple_data:
        print("Using TempleOSRS API data")
        return process_temple_clog(temple_data, manual_dates)
    else:
        print("Falling back to YAML collection log")
        return load_collection_log_from_yaml()

def process_temple_clog(temple_data, manual_dates):
    """Process TempleOSRS collection log data, merging with manual dates"""
    collections = {}
    total_obtained = 0
    total_items = 0
    recent_items = []
    
    # Temple returns data in 'data' key with categories
    clog_data = temple_data.get('data', {})
    
    for category_name, category_data in clog_data.items():
        items = category_data.get('items', {})
        
        obtained = []
        missing = []
        
        for item_name, item_info in items.items():
            if item_info.get('obtained', False):
                # Check for manual date first, then Temple date
                manual_date = manual_dates.get(item_name.lower())
                temple_date = item_info.get('date')
                
                # Prefer manual date if it exists
                final_date = manual_date or temple_date
                
                obtained.append({
                    'name': item_name,
                    'date': final_date,
                    'quantity': item_info.get('quantity', 1)
                })
                
                if final_date:
                    recent_items.append({
                        'name': item_name,
                        'date': final_date,
                        'collection': category_name
                    })
            else:
                missing.append(item_name)
        
        collections[category_name] = {
            'obtained': obtained,
            'missing': missing,
            'obtained_count': len(obtained),
            'total_count': len(obtained) + len(missing)
        }
        
        total_obtained += len(obtained)
        total_items += len(obtained) + len(missing)
    
    # Sort recent items by date
    recent_items.sort(key=lambda x: x['date'] or '', reverse=True)
    
    return {
        'collections': collections,
        'total_obtained': total_obtained,
        'total_items': total_items,
        'recent_items': recent_items[:20],
        'source': 'templeosrs'
    }

def load_collection_log_from_yaml():
    """Load collection log from YAML file (fallback)"""
    yaml_path = DATA_DIR / "collection_log.yaml"
    if not yaml_path.exists():
        print(f"Collection log YAML not found: {yaml_path}")
        return None
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    data = parse_yaml_with_dates(content)
    
    collections = {}
    total_obtained = 0
    total_items = 0
    recent_items = []
    
    for collection_name, items in data.items():
        obtained = items.get('obtained', [])
        missing = items.get('missing', [])
        
        collections[collection_name] = {
            'obtained': obtained,
            'missing': [m['name'] if isinstance(m, dict) else m for m in missing],
            'obtained_count': len(obtained),
            'total_count': len(obtained) + len(missing)
        }
        
        total_obtained += len(obtained)
        total_items += len(obtained) + len(missing)
        
        for item in obtained:
            if item.get('date'):
                recent_items.append({
                    'name': item['name'],
                    'date': item['date'],
                    'collection': collection_name
                })
    
    recent_items.sort(key=lambda x: x['date'] or '', reverse=True)
    
    return {
        'collections': collections,
        'total_obtained': total_obtained,
        'total_items': total_items,
        'recent_items': recent_items[:20],
        'source': 'yaml'
    }

def load_combat_achievements():
    """Load combat achievements from YAML file with date support"""
    yaml_path = DATA_DIR / "combat_achievements.yaml"
    if not yaml_path.exists():
        print(f"Combat achievements YAML not found: {yaml_path}")
        return None
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    data = parse_yaml_with_dates(content)
    
    tier_points = {'Easy': 1, 'Medium': 2, 'Hard': 3, 'Elite': 4, 'Master': 5, 'Grandmaster': 6}
    
    tiers = {}
    total_completed = 0
    total_tasks = 0
    total_points = 0
    recent_tasks = []
    
    for tier_name in ['Easy', 'Medium', 'Hard', 'Elite', 'Master', 'Grandmaster']:
        if tier_name not in data:
            continue
        
        completed = data[tier_name].get('completed', [])
        not_completed = data[tier_name].get('not_completed', [])
        points = tier_points.get(tier_name, 1)
        
        tiers[tier_name] = {
            'completed': completed,
            'not_completed': [m['name'] if isinstance(m, dict) else m for m in not_completed],
            'completed_count': len(completed),
            'total_count': len(completed) + len(not_completed),
            'points_per_task': points,
            'points_earned': len(completed) * points
        }
        
        total_completed += len(completed)
        total_tasks += len(completed) + len(not_completed)
        total_points += len(completed) * points
        
        for task in completed:
            if task.get('date'):
                recent_tasks.append({
                    'name': task['name'],
                    'date': task['date'],
                    'tier': tier_name
                })
    
    recent_tasks.sort(key=lambda x: x['date'] or '', reverse=True)
    
    return {
        'tiers': tiers,
        'total_completed': total_completed,
        'total_tasks': total_tasks,
        'total_points': total_points,
        'max_points': sum(t['total_count'] * t['points_per_task'] for t in tiers.values()),
        'recent_tasks': recent_tasks[:20]
    }

def parse_pets_yaml(content):
    """Parse the flat pets.yaml structure"""
    result = {'obtained': [], 'missing': []}
    current_section = None
    
    for line in content.split('\n'):
        if not line or line.startswith('#'):
            continue
        
        stripped = line.strip()
        
        if stripped == 'obtained:':
            current_section = 'obtained'
        elif stripped == 'missing:':
            current_section = 'missing'
        elif stripped.startswith('- ') and current_section:
            item_text = stripped[2:]
            if ' | ' in item_text:
                parts = item_text.split(' | ', 1)
                name = parts[0].strip()
                date = parts[1].strip() if parts[1].strip() else None
            elif item_text.endswith(' |'):
                name = item_text[:-2].strip()
                date = None
            else:
                name = item_text.strip()
                date = None
            
            result[current_section].append({'name': name, 'date': date})
    
    return result

def parse_quests_yaml(content):
    """Parse the quests.yaml structure"""
    result = {}
    current_category = None
    current_section = None
    
    for line in content.split('\n'):
        if not line or line.startswith('#'):
            continue
        
        stripped = line.strip()
        indent = len(line) - len(stripped)
        
        if indent == 0 and stripped.endswith(':'):
            current_category = stripped[:-1]
            result[current_category] = {'completed': [], 'not_completed': []}
            current_section = None
        elif indent == 2 and stripped.endswith(':'):
            current_section = stripped[:-1]
        elif stripped.startswith('- ') and current_category and current_section:
            item_text = stripped[2:]
            if ' | ' in item_text:
                parts = item_text.split(' | ', 1)
                name = parts[0].strip()
                date = parts[1].strip() if parts[1].strip() else None
            elif item_text.endswith(' |'):
                name = item_text[:-2].strip()
                date = None
            else:
                name = item_text.strip()
                date = None
            
            result[current_category][current_section].append({'name': name, 'date': date})
    
    return result

def load_quests():
    """Load quests from YAML file with date support"""
    yaml_path = DATA_DIR / "quests.yaml"
    if not yaml_path.exists():
        print(f"Quests YAML not found: {yaml_path}")
        return None
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    data = parse_quests_yaml(content)
    
    categories = {}
    total_completed = 0
    total_quests = 0
    miniquest_completed = 0
    miniquest_total = 0
    
    for cat_name in ['Free-to-play', 'Members', 'Miniquests']:
        if cat_name not in data:
            continue
        
        completed = data[cat_name].get('completed', [])
        not_completed = data[cat_name].get('not_completed', [])
        
        categories[cat_name] = {
            'completed': completed,
            'not_completed': not_completed
        }
        
        cat_total = len(completed) + len(not_completed)
        
        if cat_name == 'Miniquests':
            miniquest_completed = len(completed)
            miniquest_total = cat_total
        else:
            total_completed += len(completed)
            total_quests += cat_total
    
    quest_points = 314 if total_completed == total_quests else 0
    
    return {
        'categories': categories,
        'total_completed': total_completed,
        'total_quests': total_quests,
        'quest_points': quest_points,
        'max_quest_points': 314,
        'miniquests_completed': miniquest_completed,
        'total_miniquests': miniquest_total
    }

def load_pets():
    """Load pets from YAML file with date support"""
    yaml_path = DATA_DIR / "pets.yaml"
    if not yaml_path.exists():
        print(f"Pets YAML not found: {yaml_path}")
        return None
    
    with open(yaml_path, 'r') as f:
        content = f.read()
    
    data = parse_pets_yaml(content)
    
    obtained = data.get('obtained', [])
    missing_raw = data.get('missing', [])
    
    missing_parsed = []
    for item in missing_raw:
        name = item['name'] if isinstance(item, dict) else item
        source = None
        if '(' in name and name.endswith(')'):
            parts = name.rsplit('(', 1)
            name = parts[0].strip()
            source = parts[1][:-1].strip()
        missing_parsed.append({'name': name, 'source': source})
    
    return {
        'obtained': obtained,
        'missing': missing_parsed,
        'total_obtained': len(obtained),
        'total_pets': len(obtained) + len(missing_raw)
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

    # Items to exclude from boss list
    BOSS_EXCLUSIONS = {
        "Collections Logged", "Combat Achievements", 
        "PvP Arena", "PvP Arena - Rank", "Colosseum Glory"
    }
    
    # Process bosses and clue scrolls separately
    bosses = {}
    clues = {}
    if official and "activities" in official:
        for a in official["activities"]:
            name, score = a.get("name"), a.get("score", -1)
            if score > 0:
                if name in BOSS_EXCLUSIONS or name.startswith("PvP Arena"):
                    continue
                elif "Clue Scrolls" in name:
                    clues[name] = {"count": score, "rank": a.get("rank", -1)}
                else:
                    bosses[name] = {"kc": score, "rank": a.get("rank", -1)}

    if bosses:
        save_json(DATA_DIR / "bosses.json", {"rsn": RSN, "updated": now.isoformat(), "bosses": bosses})

    if clues:
        save_json(DATA_DIR / "clues.json", {"rsn": RSN, "updated": now.isoformat(), "clues": clues})

    # Load and save collection log (tries Temple API first, falls back to YAML)
    print("Loading collection log...")
    clog = load_collection_log()
    if clog:
        save_json(DATA_DIR / "collection_log.json", {
            "rsn": RSN, "updated": now.isoformat(), "collection_log": clog
        })
        print(f"Collection log: {clog['total_obtained']}/{clog['total_items']} items (source: {clog.get('source', 'unknown')})")

    # Load and save combat achievements (YAML only - no API)
    print("Loading combat achievements from YAML...")
    ca = load_combat_achievements()
    if ca:
        save_json(DATA_DIR / "combat_achievements.json", {
            "rsn": RSN, "updated": now.isoformat(), "combat_achievements": ca
        })
        print(f"Combat achievements: {ca['total_completed']}/{ca['total_tasks']} tasks")

    # Load and save pets (YAML only)
    print("Loading pets from YAML...")
    pets = load_pets()
    if pets:
        save_json(DATA_DIR / "pets.json", {
            "rsn": RSN, "updated": now.isoformat(), "pets": pets
        })
        print(f"Pets: {pets['total_obtained']}/{pets['total_pets']} pets")

    # Load and save quests (YAML only)
    print("Loading quests from YAML...")
    quests = load_quests()
    if quests:
        save_json(DATA_DIR / "quests.json", {
            "rsn": RSN, "updated": now.isoformat(), "quests": quests
        })
        print(f"Quests: {quests['total_completed']}/{quests['total_quests']} ({quests['quest_points']} QP)")

    print("-" * 50)
    print("Update complete!")

if __name__ == "__main__":
    main()
