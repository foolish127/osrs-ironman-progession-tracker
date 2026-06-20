#!/usr/bin/env python3
"""
Suggest draft drops.yaml entries for recently obtained collection-log items
that aren't already logged.

Runs in CI (prints suggestions to the Actions log) and can be run locally:
    python scripts/suggest_drops.py

Review the output, fill in `kc` and `droprate`, and paste the ones you care
about into data/drops.yaml. Nothing is written automatically — notable drops
stay a deliberate, manual choice.
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_logged_items():
    """Item names already present in drops.yaml (loose line-based parse)."""
    path = DATA_DIR / "drops.yaml"
    names = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*item:\s*(.+?)\s*$", line)
            if m:
                names.add(m.group(1).strip().strip('"\'').lower())
    return names


def main():
    clog_path = DATA_DIR / "collection_log.json"
    if not clog_path.exists():
        print("suggest_drops: collection_log.json not found — run update_stats.py first.")
        return

    clog = json.loads(clog_path.read_text(encoding="utf-8")).get("collection_log", {})
    recent = clog.get("recent_items", [])
    logged = load_logged_items()

    suggestions = [it for it in recent if it.get("name", "").lower() not in logged]

    print("-" * 50)
    if not suggestions:
        print("suggest_drops: no new collection-log items — drops.yaml looks current.")
        return

    print(f"suggest_drops: {len(suggestions)} recently obtained item(s) not yet in "
          f"drops.yaml.\nReview, add kc + droprate, and paste into data/drops.yaml:\n")
    for it in suggestions:
        source = (it.get("collection") or "").replace("_", " ").title()
        print(f"  - boss: {source}")
        print("    kc:")
        print(f"    item: {it.get('name', '')}")
        print(f"    date: {it.get('date') or ''}")
        print("    droprate:")
        print()


if __name__ == "__main__":
    main()
