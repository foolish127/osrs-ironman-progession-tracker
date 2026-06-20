#!/usr/bin/env python3
"""
Refresh the Targets-tab reference data scraped from the OSRS Wiki:
  - data/wiki_comp_rates.json  (Collection_log/Table)
  - data/wiki_ca_table.json    (Combat_Achievements/All_tasks)

⚠️ EXPERIMENTAL / best-effort and UNTESTED in this environment. Wiki tables are
brittle to parse and the column layout can change. To avoid ever corrupting the
live reference files, this writes to *.new.json and NEVER overwrites them. Run
it, then DIFF the .new.json against the live file and only replace it manually
if the data looks right:

    python scripts/update_wiki_refs.py
    # review data/wiki_comp_rates.new.json vs data/wiki_comp_rates.json
    # if good:  move/rename it over the live file

It is intentionally NOT wired into the GitHub Actions workflow.
"""

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
API = "https://oldschool.runescape.wiki/api.php"


def fetch_rendered_html(page):
    params = {"action": "parse", "page": page, "prop": "text",
              "format": "json", "formatversion": "2"}
    url = f"{API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "OSRS-Ironman-Tracker/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())["parse"]["text"]


class TableExtractor(HTMLParser):
    """Collect every <table> as a list of rows; each cell keeps text + links."""

    def __init__(self):
        super().__init__()
        self.tables = []
        self._depth = 0
        self._table = None
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._depth += 1
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = {"text": [], "links": [], "header": tag == "th"}
        elif tag == "a" and self._cell is not None:
            self._cell["links"].append(dict(attrs).get("href", ""))

    def handle_data(self, data):
        if self._cell is not None:
            self._cell["text"].append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._cell["value"] = " ".join("".join(self._cell["text"]).split())
            self._row.append(self._cell)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None
            self._depth = max(0, self._depth - 1)


def biggest_table(html):
    parser = TableExtractor()
    parser.feed(html)
    return max(parser.tables, key=len) if parser.tables else []


def header_map(table):
    """lowercase header text -> column index, from the first row that has <th>."""
    for row in table[:3]:
        if any(c["header"] for c in row):
            return {c["value"].lower(): i for i, c in enumerate(row)}, table[table.index(row) + 1:]
    return {}, table


def col(headers, *names):
    for n in names:
        for h, i in headers.items():
            if n in h:
                return i
    return None


def pct(value):
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", value or "")
    return float(m.group(1)) if m else None


def scrape_collection_log():
    table = biggest_table(fetch_rendered_html("Collection_log/Table"))
    headers, rows = header_map(table)
    c_name = col(headers, "item", "name")
    c_src = col(headers, "source")
    c_pct = col(headers, "%", "rate", "completion")
    items = []
    for r in rows:
        if c_name is None or c_name >= len(r):
            continue
        name = r[c_name]["value"]
        if not name:
            continue
        sources = []
        if c_src is not None and c_src < len(r):
            sources = [s.strip() for s in re.split(r",|/", r[c_src]["value"]) if s.strip()]
        items.append({
            "name": name,
            "sources": sources,
            "source_display": ", ".join(sources),
            "comp_pct": pct(r[c_pct]["value"]) if c_pct is not None and c_pct < len(r) else None,
        })
    return {"item_count": len(items), "items": items,
            "source_url": "https://oldschool.runescape.wiki/w/Collection_log/Table"}


def scrape_ca_tasks():
    table = biggest_table(fetch_rendered_html("Combat_Achievements/All_tasks"))
    headers, rows = header_map(table)
    c_name = col(headers, "name", "task")
    c_mon = col(headers, "monster", "boss")
    c_desc = col(headers, "description", "task description")
    c_type = col(headers, "type")
    c_tier = col(headers, "tier")
    c_pts = col(headers, "point")
    c_pct = col(headers, "%", "rate", "completion")
    tasks = []
    for r in rows:
        if c_name is None or c_name >= len(r):
            continue
        name = r[c_name]["value"]
        if not name:
            continue
        pts = None
        if c_pts is not None and c_pts < len(r):
            m = re.search(r"\d+", r[c_pts]["value"])
            pts = int(m.group()) if m else None
        link = r[c_name]["links"][0] if r[c_name]["links"] else ""
        tasks.append({
            "name": name,
            "monster": r[c_mon]["value"] if c_mon is not None and c_mon < len(r) else "",
            "description": r[c_desc]["value"] if c_desc is not None and c_desc < len(r) else "",
            "type": r[c_type]["value"] if c_type is not None and c_type < len(r) else "",
            "tier": r[c_tier]["value"] if c_tier is not None and c_tier < len(r) else "",
            "points": pts,
            "comp_pct": pct(r[c_pct]["value"]) if c_pct is not None and c_pct < len(r) else None,
            "wiki_url": ("https://oldschool.runescape.wiki" + link) if link.startswith("/") else link,
        })
    return {"task_count": len(tasks), "tasks": tasks,
            "source_url": "https://oldschool.runescape.wiki/w/Combat_Achievements/All_tasks"}


def write_review(name, payload, expected_min):
    payload["updated"] = datetime.now(timezone.utc).isoformat()
    rows = payload.get("items") or payload.get("tasks") or []
    count = len(rows)
    out = DATA_DIR / f"{name}.new.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    msg = f"  wrote {out.name}: {count} rows"
    if count < expected_min:
        msg += f"  ⚠️  LOW (expected >= {expected_min}) — parsing likely failed, do not use."
    elif rows and all(r.get("comp_pct") is None for r in rows[:10]):
        msg += "  ⚠️  completion % not detected — review before replacing."
    else:
        msg += f"  — diff vs {name}.json, then rename over it if correct."
    print(msg)


def main():
    print("Scraping OSRS Wiki reference tables (writing *.new.json for review)...")
    try:
        write_review("wiki_comp_rates", scrape_collection_log(), expected_min=1000)
    except Exception as e:
        print(f"  collection log scrape failed: {e}")
    try:
        write_review("wiki_ca_table", scrape_ca_tasks(), expected_min=500)
    except Exception as e:
        print(f"  CA tasks scrape failed: {e}")
    print("Done. Nothing live was overwritten.")


if __name__ == "__main__":
    main()
