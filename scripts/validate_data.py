#!/usr/bin/env python3
"""
Validate the generated data/*.json files have the shape the dashboard expects.

Run in CI after update_stats.py so a malformed/empty payload fails the build
instead of being silently committed and breaking the live dashboard. Only
files that exist are checked, so optional/local-only data is fine to omit.

Exit code 0 = all present files valid, 1 = at least one problem.
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# filename -> list of (key_path, expected_type). A key_path like
# "collection_log.collections" means data["collection_log"]["collections"].
SCHEMA = {
    "skills.json": [("rsn", str), ("updated", str), ("skills", dict), ("milestones", dict)],
    "bosses.json": [("rsn", str), ("updated", str), ("bosses", dict)],
    "clues.json": [("rsn", str), ("updated", str), ("clues", dict)],
    "collection_log.json": [
        ("updated", str),
        ("collection_log.collections", dict),
        ("collection_log.total_obtained", int),
        ("collection_log.total_items", int),
        ("collection_log.recent_items", list),
    ],
    "combat_achievements.json": [
        ("updated", str),
        ("combat_achievements.tiers", dict),
        ("combat_achievements.total_completed", int),
    ],
    "quests.json": [("updated", str), ("quests.categories", dict)],
    "pets.json": [("updated", str), ("pets.obtained", list), ("pets.missing", list)],
}


def _get(data, dotted):
    for part in dotted.split("."):
        if not isinstance(data, dict) or part not in data:
            return None, False
        data = data[part]
    return data, True


def validate_file(path: Path, rules) -> list:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"{path.name}: not valid JSON ({e})"]

    for key_path, expected_type in rules:
        value, found = _get(data, key_path)
        if not found:
            errors.append(f"{path.name}: missing '{key_path}'")
        elif not isinstance(value, expected_type):
            errors.append(
                f"{path.name}: '{key_path}' should be {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
    return errors


def main() -> int:
    all_errors = []
    checked = 0
    for filename, rules in SCHEMA.items():
        path = DATA_DIR / filename
        if not path.exists():
            print(f"skip (absent): {filename}")
            continue
        checked += 1
        errors = validate_file(path, rules)
        if errors:
            all_errors.extend(errors)
        else:
            print(f"ok: {filename}")

    print("-" * 50)
    if all_errors:
        print(f"VALIDATION FAILED ({len(all_errors)} problem(s)):")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"All {checked} present data file(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
