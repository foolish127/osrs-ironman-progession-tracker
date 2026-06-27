#!/usr/bin/env python3
"""
Scrape OSRS Wiki achievement-diary tasks into <data dir>/diary_tasks.yaml.

Re-run to refresh. Writes to OSRS_DATA_DIR (so `OSRS_DATA_DIR=data/gim
python scripts/build_diary_tasks.py` targets the GIM account). The dashboard's
Diaries tab reads this list; delete a task once it's done and it drops off.
"""

import re
import urllib.parse

from osrs_utils import DATA_DIR, fetch_json

API = "https://oldschool.runescape.wiki/api.php"
TIERS = ["Easy", "Medium", "Hard", "Elite"]
REGIONS = [
    "Ardougne Diary", "Desert Diary", "Falador Diary", "Fremennik Diary",
    "Kandarin Diary", "Karamja Diary", "Kourend & Kebos Diary",
    "Lumbridge & Draynor Diary", "Morytania Diary", "Varrock Diary",
    "Western Provinces Diary", "Wilderness Diary",
]


def clean(s):
    """Strip wiki markup from a task line down to plain text."""
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*/>", "", s)
    for _ in range(5):  # remove templates ({{...}}), allowing simple nesting
        s2 = re.sub(r"\{\{[^{}]*\}\}", "", s)
        if s2 == s:
            break
        s = s2
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)  # [[link|text]] -> text
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)            # [[text]] -> text
    s = s.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", s).strip()


def fetch_wikitext(page):
    url = f"{API}?" + urllib.parse.urlencode(
        {"action": "parse", "page": page, "prop": "wikitext", "format": "json", "formatversion": "2"})
    data = fetch_json(url)
    return (data or {}).get("parse", {}).get("wikitext", "")


def parse_tasks(wt):
    """Return {tier: [tasks]} from a diary page's wikitext."""
    out = {t: [] for t in TIERS}
    tier = None
    for line in wt.split("\n"):
        m = re.search(r'data-diary-tier="(\w+)"', line)
        if m:
            tier = m.group(1) if m.group(1) in TIERS else None
            continue
        m = re.match(r"\|\s*\d+\.\s*(.+)$", line)
        if m and tier:
            task = clean(m.group(1))
            if task:
                out[tier].append(task)
    return out


def main():
    lines = ["# Achievement diary tasks (scraped from the OSRS Wiki).",
             "# Delete a task once it's completed; the Diaries tab shows what's left.",
             ""]
    total = 0
    for page in REGIONS:
        print(f"Fetching {page}...")
        tasks = parse_tasks(fetch_wikitext(page))
        n = sum(len(v) for v in tasks.values())
        total += n
        print(f"  {n} tasks ({'/'.join(str(len(tasks[t])) for t in TIERS)})")
        lines.append(f"{page[:-len(' Diary')]}:")
        for tier in TIERS:
            lines.append(f"  {tier}:")
            lines.extend(f"    - {t}" for t in tasks[tier])
        lines.append("")

    out = DATA_DIR / "diary_tasks.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {out} ({total} tasks)")


if __name__ == "__main__":
    main()
