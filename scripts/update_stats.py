#!/usr/bin/env python3
"""
OSRS Ironman Progression Tracker
Fetches data from official hiscores and TempleOSRS API.
Preserves manually-entered dates from YAML files.
"""

import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from osrs_config import BOSS_EXCLUSIONS, PET_NAMES
from osrs_utils import (
    DATA_DIR,
    check_no_dropped_items,
    count_items,
    date_sort_key,
    fetch_json,
    names_lower,
    normalize_date,
    parse_yaml_with_dates,
    read_data_file,
    save_json,
)

RSN = os.environ.get("RSN", "FoolinSlays")

# Hiscores leaderboard variant. Default is the ironman board; group-ironman
# accounts (e.g. GIM Foolin) aren't on it, so set HISCORES_VARIANT=hiscore_oldschool.
HISCORES_VARIANT = os.environ.get("HISCORES_VARIANT", "hiscore_oldschool_ironman")
HISCORES_URL = f"https://secure.runescape.com/m={HISCORES_VARIANT}/index_lite.json"
TEMPLE_CLOG_URL = "https://templeosrs.com/api/collection-log/player_collection_log.php"
TEMPLE_ITEMS_URL = "https://templeosrs.com/api/collection-log/items.php"

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

def load_yaml_collection_log():
    """Load the full collection log from YAML including missing items"""
    content = read_data_file("collection_log.yaml")
    if content is None:
        return {}

    data = parse_yaml_with_dates(content)
    # Warn (don't hard-fail) here: collection_log.yaml is large and mostly machine
    # -maintained, so a non-blocking notice is safer than failing the whole run.
    check_no_dropped_items(content, count_items(data), "collection_log.yaml", strict=False)
    return data

def fetch_temple_collection_log(rsn):
    """Fetch collection log from TempleOSRS API"""
    print(f"Fetching collection log from TempleOSRS for {rsn}...")

    # Request ALL categories
    data = fetch_json(TEMPLE_CLOG_URL, {"player": rsn, "categories": "all"})

    if not data:
        print("Failed to fetch from TempleOSRS")
        return None

    if "error" in data:
        print(f"TempleOSRS error: {data['error']}")
        return None

    return data

def load_item_names():
    """Load item ID to name mapping from Temple API"""
    data = fetch_json(TEMPLE_ITEMS_URL)
    # Structure is {'items': {'id': 'name', ...}}
    items = (data or {}).get('items', {})
    if isinstance(items, dict):
        print(f"  Loaded {len(items)} item names")
        return items
    return {}

def load_collection_log(temple_data, item_names):
    """
    Build the collection log from pre-fetched TempleOSRS data, preserving manual
    dates AND missing items from YAML. Falls back to YAML if the API data is absent.
    """
    # Load full YAML data (for manual dates AND missing items)
    yaml_data = load_yaml_collection_log()
    print(f"Loaded {len(yaml_data)} categories from YAML")

    # Build manual dates lookup
    manual_dates = {}
    for items in yaml_data.values():
        for item in items.get('obtained', []):
            if item.get('date'):
                manual_dates[item['name'].lower()] = item['date']
    print(f"Loaded {len(manual_dates)} manual dates")

    if temple_data and 'data' in temple_data:
        print("Using TempleOSRS API data (merged with YAML missing items)")
        return process_temple_clog(temple_data, manual_dates, yaml_data, item_names)
    else:
        print("Falling back to YAML collection log")
        return load_collection_log_from_yaml()

def load_drops_sources():
    """Map lowercased item name -> source boss from drops.yaml.

    Used to attribute collection-log items that fill several Temple category
    logs at once (e.g. Uncut onyx) to the source the player actually recorded.
    """
    content = read_data_file("drops.yaml")
    if content is None:
        return {}
    sources = {}
    current_boss = None
    for line in content.split('\n'):
        s = line.strip()
        if s.startswith('- '):
            s = s[2:].strip()
        if s.startswith('boss:'):
            current_boss = s.split(':', 1)[1].strip()
        elif s.startswith('item:') and current_boss:
            item = s.split(':', 1)[1].strip().strip('"\'')
            if item:
                sources.setdefault(item.lower(), current_boss)
    return sources


def dedup_recent_items(items, drops_sources=None):
    """Sort newest-first and keep a single entry per item name.

    One obtained item can fill the collection-log slot under every boss that
    drops it (all at the same timestamp), which would list it many times. When
    such a multi-source item is in drops.yaml, attribute it to that real source.
    """
    items = sorted(items, key=lambda x: date_sort_key(x.get('date')), reverse=True)
    name_counts = Counter(it['name'].lower() for it in items)
    seen, out = set(), []
    for it in items:
        key = it['name'].lower()
        if key in seen:
            continue
        seen.add(key)
        if drops_sources and name_counts[key] > 1 and key in drops_sources:
            it = {**it, 'collection': drops_sources[key].lower().replace(' ', '_')}
        out.append(it)
    return out


def process_temple_clog(temple_data, manual_dates, yaml_data, item_names):
    """Process TempleOSRS collection log data, merging with manual dates AND missing items from YAML"""
    collections = {}
    total_obtained = 0
    recent_items = []

    # Temple structure: data.items = { category_name: [ {id, count, date}, ... ] }
    temple_info = temple_data.get('data', {})
    items_data = temple_info.get('items', {})

    # Get totals from Temple response
    total_from_temple = temple_info.get('total_collections_finished', 0)
    total_available = temple_info.get('total_collections_available', 0)

    print(f"  Temple reports: {total_from_temple}/{total_available} items")

    # Build a set of obtained item names from Temple (lowercase for matching)
    temple_obtained_names = set()

    for category_name, category_items in items_data.items():
        obtained = []

        # category_items is a list of obtained items
        if isinstance(category_items, list):
            for item in category_items:
                item_id = item.get('id')
                item_name = item_names.get(str(item_id), f"Item {item_id}")
                temple_date = item.get('date')
                count = item.get('count', 1)

                # Manual date wins over Temple's; normalize both to ISO so they
                # sort and display consistently regardless of source format.
                manual_date = manual_dates.get(item_name.lower())
                final_date = normalize_date(manual_date or temple_date)

                obtained.append({
                    'name': item_name,
                    'date': final_date,
                    'quantity': count
                })

                temple_obtained_names.add(item_name.lower())

                if final_date:
                    recent_items.append({
                        'name': item_name,
                        'date': final_date,
                        'collection': category_name
                    })

        if obtained:
            # Format category name nicely
            display_name = category_name.replace('_', ' ').title()
            collections[display_name] = {
                'obtained': obtained,
                'missing': [],  # Will be filled from YAML below
                'obtained_count': len(obtained),
                'total_count': len(obtained)  # Will be updated after merging missing
            }
            total_obtained += len(obtained)

    # Now merge missing items from YAML
    # We need to match YAML category names to Temple category names
    yaml_to_temple_map = {}
    for yaml_cat in yaml_data.keys():
        # Try exact match first
        yaml_lower = yaml_cat.lower().replace(' ', '_').replace(',', '')
        for temple_cat in collections.keys():
            temple_lower = temple_cat.lower().replace(' ', '_')
            if yaml_lower == temple_lower or yaml_cat == temple_cat:
                yaml_to_temple_map[yaml_cat] = temple_cat
                break

    # Add missing items from YAML to matching categories
    missing_added = 0
    for yaml_cat, yaml_items in yaml_data.items():
        yaml_missing = yaml_items.get('missing', [])
        if not yaml_missing:
            continue

        # Find matching Temple category or create new one
        temple_cat = yaml_to_temple_map.get(yaml_cat, yaml_cat)

        if temple_cat not in collections:
            collections[temple_cat] = {
                'obtained': [],
                'missing': [],
                'obtained_count': 0,
                'total_count': 0
            }

        # Add missing items that aren't already obtained
        for item in yaml_missing:
            item_name = item.get('name', item) if isinstance(item, dict) else item
            if item_name.lower() not in temple_obtained_names:
                collections[temple_cat]['missing'].append(item_name)
                missing_added += 1

        # Update total_count
        collections[temple_cat]['total_count'] = (
            collections[temple_cat]['obtained_count'] +
            len(collections[temple_cat]['missing'])
        )

    print(f"  Added {missing_added} missing items from YAML")

    # Recalculate total_items
    total_items = sum(c['total_count'] for c in collections.values())

    # Newest first, then collapse items that filled several category logs at
    # once into a single entry attributed to their real source (via drops.yaml).
    recent_items = dedup_recent_items(recent_items, load_drops_sources())

    return {
        'collections': collections,
        'total_obtained': total_from_temple if total_from_temple else total_obtained,
        'total_items': total_items,
        'recent_items': recent_items[:20],
        'source': 'templeosrs'
    }

def load_collection_log_from_yaml():
    """Load collection log from YAML file (fallback)"""
    content = read_data_file("collection_log.yaml")
    if content is None:
        return None

    data = parse_yaml_with_dates(content)

    collections = {}
    total_obtained = 0
    total_items = 0
    recent_items = []

    for collection_name, items in data.items():
        obtained = items.get('obtained', [])
        missing = items.get('missing', [])

        for item in obtained:
            item['date'] = normalize_date(item.get('date'))

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

    recent_items = dedup_recent_items(recent_items, load_drops_sources())

    return {
        'collections': collections,
        'total_obtained': total_obtained,
        'total_items': total_items,
        'recent_items': recent_items[:20],
        'source': 'yaml'
    }

def load_combat_achievements():
    """Load combat achievements from YAML file with date support"""
    content = read_data_file("combat_achievements.yaml")
    if content is None:
        return None

    data = parse_yaml_with_dates(content)
    check_no_dropped_items(content, count_items(data), "combat_achievements.yaml")

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

        for task in completed:
            task['date'] = normalize_date(task.get('date'))

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

    recent_tasks.sort(key=lambda x: date_sort_key(x.get('date')), reverse=True)

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
                parts = item_text.split(' | ', 2)
                name = parts[0].strip()
                date = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
                notes = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
            elif item_text.endswith(' |'):
                name = item_text[:-2].strip()
                date = None
                notes = None
            else:
                name = item_text.strip()
                date = None
                notes = None

            result[current_section].append({'name': name, 'date': date, 'notes': notes})

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
    content = read_data_file("quests.yaml")
    if content is None:
        return None

    data = parse_quests_yaml(content)
    parsed_count = sum(len(items) for cat in data.values() for items in cat.values())
    check_no_dropped_items(content, parsed_count, "quests.yaml")

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

    # NOTE: quest points are intentionally NOT computed here. QP is not exposed by
    # any API, the max changes with every new quest (335 as of Oct 2025), and a
    # hardcoded per-quest table would be error-prone and quickly go stale. The
    # dashboard shows accurate quest + miniquest completion counts instead.
    return {
        'categories': categories,
        'total_completed': total_completed,
        'total_quests': total_quests,
        'miniquests_completed': miniquest_completed,
        'total_miniquests': miniquest_total
    }

def load_pets():
    """Load pets from YAML file with date support"""
    content = read_data_file("pets.yaml")
    if content is None:
        return None

    data = parse_pets_yaml(content)
    check_no_dropped_items(
        content, len(data.get('obtained', [])) + len(data.get('missing', [])), "pets.yaml")

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

def extract_pets_from_clog(clog):
    """Extract pets from collection log data"""
    if not clog or 'collections' not in clog:
        return None

    collections = clog['collections']
    obtained = []
    missing = []

    # Load manual dates and notes from pets.yaml for merging
    manual_pet_dates = {}
    manual_pet_notes = {}
    content = read_data_file("pets.yaml")
    data = parse_pets_yaml(content) if content is not None else {'obtained': [], 'missing': []}
    for pet in data.get('obtained', []):
        if pet.get('date'):
            manual_pet_dates[pet['name'].lower()] = pet['date']
        if pet.get('notes'):
            manual_pet_notes[pet['name'].lower()] = pet['notes']
    # Also get missing pets from YAML for the full list
    missing_names = names_lower(missing)
    for pet in data.get('missing', []):
        pet_name = pet.get('name', pet) if isinstance(pet, dict) else pet
        if pet_name.lower() not in missing_names:
            # Parse source from "name (source)" format
            source = None
            if '(' in pet_name and pet_name.endswith(')'):
                parts = pet_name.rsplit('(', 1)
                pet_name = parts[0].strip()
                source = parts[1][:-1].strip()
            missing.append({'name': pet_name, 'source': source})
            missing_names.add(pet_name.lower())

    # Scan all collections for pet items
    obtained_names = set()
    for category_name, category_data in collections.items():
        source = category_name.replace('_', ' ').title()

        for item in category_data.get('obtained', []):
            item_name = item.get('name', '') if isinstance(item, dict) else item

            # Check if this is a pet (avoid duplicates)
            if item_name.lower() in PET_NAMES and item_name.lower() not in obtained_names:
                manual_date = manual_pet_dates.get(item_name.lower())
                clog_date = item.get('date') if isinstance(item, dict) else None

                obtained.append({
                    'name': item_name,
                    'date': normalize_date(manual_date or clog_date),
                    'source': source,
                    'notes': manual_pet_notes.get(item_name.lower())
                })
                obtained_names.add(item_name.lower())

    # Pets recorded in pets.yaml's obtained list but not yet synced into the
    # collection log (e.g. a freshly obtained pet) — count them as obtained too.
    for pet in data.get('obtained', []):
        name = pet['name']
        if name.lower() not in obtained_names:
            obtained.append({
                'name': name,
                'date': normalize_date(pet.get('date')),
                'source': None,
                'notes': pet.get('notes'),
            })
            obtained_names.add(name.lower())

    if not obtained and not missing:
        # Fallback to YAML only
        return None

    return {
        'obtained': obtained,
        'missing': missing,
        'total_obtained': len(obtained),
        'total_pets': len(obtained) + len(missing),
        'source': 'collection_log'
    }

def main():
    now = datetime.now(timezone.utc)
    print(f"Updating stats for: {RSN}")
    print(f"Timestamp: {now.isoformat()}")
    print("-" * 50)

    # Fetch the three independent network sources concurrently — they don't
    # depend on each other, so there's no reason to wait for them in series.
    print("Fetching hiscores, collection log and item names...")
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_official = pool.submit(fetch_json, HISCORES_URL, {"player": RSN})
        f_temple = pool.submit(fetch_temple_collection_log, RSN)
        f_items = pool.submit(load_item_names)
        official = f_official.result()
        temple_data = f_temple.result()
        item_names = f_items.result()

    # Pull Combat Achievement points and collection-log count straight from the
    # hiscores so the headline numbers stay current without any manual edits.
    ca_points = ca_rank = collections_logged = collections_rank = None
    for a in (official.get("activities", []) if official else []):
        name, score = a.get("name"), a.get("score", -1)
        if name == "Combat Achievements" and score > 0:
            ca_points, ca_rank = score, a.get("rank", -1)
        elif name == "Collections Logged" and score > 0:
            collections_logged, collections_rank = score, a.get("rank", -1)

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
                "skills_99": n99, "num_skills": NUM_SKILLS,
                "ca_points": ca_points, "ca_rank": ca_rank,
                "collections_logged": collections_logged, "collections_rank": collections_rank
            }
        })

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

    # Build collection log from pre-fetched Temple data (falls back to YAML)
    print("Loading collection log...")
    clog = load_collection_log(temple_data, item_names)
    if clog:
        save_json(DATA_DIR / "collection_log.json", {
            "rsn": RSN, "updated": now.isoformat(), "collection_log": clog
        })
        print(f"Collection log: {clog['total_obtained']}/{clog['total_items']} items (source: {clog.get('source', 'unknown')})")

        # Extract pets from collection log
        print("Extracting pets from collection log...")
        pets = extract_pets_from_clog(clog)
        if pets:
            save_json(DATA_DIR / "pets.json", {
                "rsn": RSN, "updated": now.isoformat(), "pets": pets
            })
            print(f"Pets: {pets['total_obtained']}/{pets['total_pets']} pets (from clog)")
    else:
        # Fallback to YAML for pets if clog fails
        print("Loading pets from YAML (fallback)...")
        pets = load_pets()
        if pets:
            save_json(DATA_DIR / "pets.json", {
                "rsn": RSN, "updated": now.isoformat(), "pets": pets
            })
            print(f"Pets: {pets['total_obtained']}/{pets['total_pets']} pets")

    # Load and save combat achievements (YAML only - no API)
    print("Loading combat achievements from YAML...")
    ca = load_combat_achievements()
    if ca:
        save_json(DATA_DIR / "combat_achievements.json", {
            "rsn": RSN, "updated": now.isoformat(), "combat_achievements": ca
        })
        print(f"Combat achievements: {ca['total_completed']}/{ca['total_tasks']} tasks")

    # Load and save quests (YAML only)
    print("Loading quests from YAML...")
    quests = load_quests()
    if quests:
        save_json(DATA_DIR / "quests.json", {
            "rsn": RSN, "updated": now.isoformat(), "quests": quests
        })
        print(f"Quests: {quests['total_completed']}/{quests['total_quests']} "
              f"(+{quests['miniquests_completed']}/{quests['total_miniquests']} miniquests)")

    print("-" * 50)
    print("Update complete!")

if __name__ == "__main__":
    main()
