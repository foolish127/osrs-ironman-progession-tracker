#!/usr/bin/env python3
"""
Build data/league_tasks.yaml from the OSRS Wiki Trailblazer Reloaded task list,
auto-completing tasks that the account's own data already proves.

LOCAL / MANUAL tool (like update_wiki_refs.py) — NOT wired into CI. It needs
internet (the wiki) and reads the generated data/*.json. Re-run it any time to
refresh the task list or re-derive completions:

    python scripts/build_league_tasks.py

Auto-completion is conservative (precision over recall): it only marks a task
done on strong evidence (clue/skill/quest/KC/owned-item matches). Everything
else is left unchecked for you to review in the dashboard's Leagues tab
("Remaining Only" filter). A summary is printed at the end.
"""

import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from osrs_utils import DATA_DIR

WIKI_API = "https://oldschool.runescape.wiki/api.php"
TASKS_PAGE = "Demonic_Pacts_League/Tasks"

# Demonic Pacts (Leagues VI) tier point values.
TIER_BY_POINTS = {10: "easy", 30: "medium", 80: "hard", 200: "elite", 400: "master"}
TIER_ORDER = ["easy", "medium", "hard", "elite", "master"]


# ── wiki scraping ────────────────────────────────────────────────────────

def fetch_tasks_html():
    params = {"action": "parse", "page": TASKS_PAGE, "prop": "text",
              "format": "json", "formatversion": "2"}
    url = f"{WIKI_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "OSRS-Ironman-Tracker/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["parse"]["text"]


class TableParser(HTMLParser):
    """Collect tables; each cell keeps text + <a> titles + <img> alts."""
    def __init__(self):
        super().__init__()
        self.tables = []
        self._t = self._r = self._c = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self._t = []
        elif tag == "tr" and self._t is not None:
            self._r = []
        elif tag in ("td", "th") and self._r is not None:
            self._c = {"text": [], "titles": []}
        elif tag == "a" and self._c is not None and a.get("title"):
            self._c["titles"].append(a["title"])

    def handle_data(self, d):
        if self._c is not None:
            self._c["text"].append(d)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._c is not None:
            self._c["value"] = re.sub(r"\s+", " ", "".join(self._c["text"]).strip())
            self._r.append(self._c)
            self._c = None
        elif tag == "tr" and self._r is not None:
            if self._r:
                self._t.append(self._r)
            self._r = None
        elif tag == "table" and self._t is not None:
            if self._t:
                self.tables.append(self._t)
            self._t = None


def scrape_tasks():
    parser = TableParser()
    parser.feed(fetch_tasks_html())
    table = max(parser.tables, key=len)  # the 1480-row task table
    tasks = []
    for row in table[1:]:
        if len(row) < 6:
            continue
        area_cell = row[0]
        area = area_cell["titles"][0].split("/")[-1] if area_cell["titles"] else "General"
        name = row[1]["value"]
        desc = row[2]["value"]
        reqs = row[3]["value"]
        m = re.search(r"\d+", row[4]["value"])
        pts = int(m.group()) if m else 10
        tier = TIER_BY_POINTS.get(pts, "easy")
        if name:
            tasks.append({"area": area, "name": name, "desc": desc, "reqs": reqs, "tier": tier})
    return tasks


# ── account data ─────────────────────────────────────────────────────────

def _load(name):
    path = DATA_DIR / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_account():
    acc = {"skills": {}, "total_level": 0, "combat_level": 0, "clues": {},
           "boss_kc": {}, "items": set(), "ca": set(), "quests_all_done": False}

    skills = _load("skills.json") or {}
    for n, s in (skills.get("skills") or {}).items():
        acc["skills"][n.lower()] = s.get("level", 1)
    ms = skills.get("milestones") or {}
    acc["total_level"] = ms.get("total_level", 0)
    acc["combat_level"] = ms.get("combat_level", 0)

    for tier_key, d in (_load("clues.json") or {}).get("clues", {}).items():
        m = re.search(r"\((\w+)\)", tier_key)
        if m:
            acc["clues"][m.group(1).lower()] = d.get("count", 0)

    for name, d in (_load("bosses.json") or {}).get("bosses", {}).items():
        acc["boss_kc"][name.lower()] = d.get("kc", 0)

    clog = (_load("collection_log.json") or {}).get("collection_log", {})
    for cat in clog.get("collections", {}).values():
        for it in cat.get("obtained", []):
            nm = it.get("name") if isinstance(it, dict) else it
            if nm:
                acc["items"].add(nm.lower())
    for p in (_load("pets.json") or {}).get("pets", {}).get("obtained", []):
        nm = p.get("name") if isinstance(p, dict) else p
        if nm:
            acc["items"].add(nm.lower())
    drops_path = DATA_DIR / "drops.yaml"
    if drops_path.exists():
        for line in drops_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*item:\s*(.+?)\s*$", line)
            if m:
                acc["items"].add(m.group(1).strip().strip("\"'").lower())

    ca = (_load("combat_achievements.json") or {}).get("combat_achievements", {})
    for tier in ca.get("tiers", {}).values():
        for t in tier.get("completed", []):
            nm = t.get("name") if isinstance(t, dict) else t
            if nm:
                acc["ca"].add(nm.lower())

    quests = (_load("quests.json") or {}).get("quests", {})
    acc["quests_all_done"] = quests.get("total_completed", 0) >= quests.get("total_quests", 1) > 0

    # Achievement diaries: region -> set of completed tiers.
    acc["diaries"] = {}
    dpath = DATA_DIR / "diaries.yaml"
    if dpath.exists():
        region = None
        for line in dpath.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            if not line.startswith(" ") and line.rstrip().endswith(":"):
                region = line.strip()[:-1].lower()
                acc["diaries"][region] = set()
            elif region and ":" in line:
                k, _, v = line.strip().partition(":")
                if k.strip().lower() in ("easy", "medium", "hard", "elite") and v.strip():
                    acc["diaries"][region].add(k.strip().lower())

    return acc


# ── conservative auto-completion matchers ────────────────────────────────

ACQUIRE = (r"(?:obtain|receive|equip|wield|wear|unlock|create|build|craft|make|"
           r"loot|collect|purchase|buy|fill|assemble|fletch|smith|brew|mix)")


# Phrases that mean a task has a special restriction KC/ownership can't prove
# (challenge/speed/no-supply variants), so we must NOT auto-complete them.
RESTRICTED = re.compile(
    r"\b(under|without|no food|no prayer|no supplies|only|solo|sub-?\d|"
    r"\d+ ?(?:minute|second)|challenge mode|hard mode|\bcm\b|flawless|perfect|"
    r"untouchable|unattuned|trio|duo|hardcore|pet)\b"
)

# Item qualifiers that can appear between an acquisition verb and the item name.
QUAL = (r"(?:a |an |the |some |your |full |a full |a set of |any |a piece of |"
        r"the superior |complete |your first |\d+ )*")


def is_done(task, acc):
    """Return (done, reason) — only True on strong, specific evidence."""
    t = f"{task['name']} {task['desc']}".lower()
    restricted = bool(RESTRICTED.search(t))

    # Clues — numeric.
    m = re.search(r"(\d+)\s*(beginner|easy|medium|hard|elite|master)\s+clue", t)
    if m and acc["clues"].get(m.group(2), 0) >= int(m.group(1)):
        return True, "clue"
    m = re.search(r"\b(?:a|an|one|your first)\b[^.]*?(beginner|easy|medium|hard|elite|master)\s+clue", t)
    if m and acc["clues"].get(m.group(1), 0) >= 1:
        return True, "clue"

    # Levels / combat — numeric.
    m = re.search(r"total level (?:of )?(\d[\d,]{2,})", t)
    if m:
        return (acc["total_level"] >= int(m.group(1).replace(",", "")), "level")
    if "maximum total level" in t:
        return (acc["total_level"] >= 2277, "level")
    m = re.search(r"combat level (?:of )?(\d+)", t)
    if m:
        return (acc["combat_level"] >= int(m.group(1)), "level")
    m = re.search(r"first level (\d+)", t)
    if m and acc["skills"]:
        return (max(acc["skills"].values()) >= int(m.group(1)), "level")
    for pat in (r"reach (?:a )?level (\d+)(?: in)? ([a-z]+)",
                r"reach (?:a |an )?([a-z]+) level of (\d+)",
                r"reach (\d+) ([a-z]+)\b",
                r"(\d+) ([a-z]+) level\b"):
        m = re.search(pat, t)
        if m:
            a, b = m.group(1), m.group(2)
            (n, sk) = (int(a), b) if a.isdigit() else (int(b), a)
            if sk in acc["skills"]:
                return (acc["skills"][sk] >= n, "level")

    # Quests — all regular quests done, so quest-completion tasks are done.
    if acc["quests_all_done"] and re.search(r"complete (?:the )?[\w '\-&]+ quest", t):
        return True, "quest"

    # Diaries — region + tier completed.
    if "diary" in t:
        for region, tiers in acc["diaries"].items():
            if region and region in t:
                for tier in ("easy", "medium", "hard", "elite"):
                    if tier in t and tier in tiers:
                        return True, "diary"

    # Boss kills — plain KC tasks only (skip restricted/challenge variants).
    if not restricted and re.search(r"\b(kill|defeat|slay|raid|finish|complete)\b", t):
        for bname, kc in acc["boss_kc"].items():
            if len(bname) >= 4 and re.search(r"\b" + re.escape(bname) + r"\b", t):
                mn = re.search(r"(?:kill|defeat|slay)\s+(\d+)|(\d+)\s*(?:kills|kill count|times|kc)", t)
                need = int(next(g for g in mn.groups() if g)) if mn else 1
                if kc >= need:
                    return True, "kc"

    # Owned items — acquisition verb then (qualifiers) an item you own.
    for item in acc["items"]:
        if len(item) >= 5 and re.search(ACQUIRE + r"\s+" + QUAL + re.escape(item) + r"\b", t):
            return True, "item"

    # Exact combat-achievement name match (skip restricted phrasing).
    if not restricted and task["name"].lower() in acc["ca"]:
        return True, "ca"

    return False, None


# ── output ───────────────────────────────────────────────────────────────

def clean(text):
    return re.sub(r"\s+", " ", text).replace("|", "/").strip().rstrip(".")


def main():
    print("Fetching Demonic Pacts (Leagues VI) task list from the wiki...")
    tasks = scrape_tasks()
    print(f"  scraped {len(tasks)} tasks")

    acc = load_account()
    print(f"  loaded account data: {len(acc['items'])} owned items, "
          f"{len(acc['boss_kc'])} bosses, {len(acc['ca'])} CAs, "
          f"quests_all_done={acc['quests_all_done']}")

    reasons = {}
    for task in tasks:
        done, reason = is_done(task, acc)
        task["done"] = done
        if done:
            reasons[reason] = reasons.get(reason, 0) + 1

    # Group: General first, then regions alphabetically; tasks under tier.
    regions = sorted({t["area"] for t in tasks}, key=lambda a: (a != "General", a))
    lines = [
        "# Leagues Task Tracker — Demonic Pacts (Leagues VI) task list, ALL regions.",
        "# Auto-generated by scripts/build_league_tasks.py (re-run to refresh).",
        "# Auto-completions are best-effort; mark/clear by adding or removing",
        "# ' | done' (optionally a date) after a task. Points: Easy 10, Medium 30,",
        "# Hard 80, Elite 200, Master 400.",
        "",
    ]
    for region in regions:
        lines.append(f"{region}:")
        for tier in TIER_ORDER:
            tt = [t for t in tasks if t["area"] == region and t["tier"] == tier]
            if not tt:
                continue
            lines.append(f"  {tier}:")
            for t in tt:
                suffix = " | done" if t["done"] else ""
                lines.append(f"    - {clean(t['desc'] or t['name'])}{suffix}")
        lines.append("")

    out = DATA_DIR / "league_tasks.yaml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    done_total = sum(1 for t in tasks if t["done"])
    print(f"\nWrote {out}")
    print(f"Auto-completed {done_total}/{len(tasks)} tasks. By evidence: {reasons}")
    print("By tier (done / total):")
    for tier in TIER_ORDER:
        tt = [t for t in tasks if t["tier"] == tier]
        print(f"  {tier:7s} {sum(1 for t in tt if t['done']):4d} / {len(tt)}")
    print("Remaining by region:")
    for region in regions:
        rr = [t for t in tasks if t["area"] == region]
        rem = sum(1 for t in rr if not t["done"])
        print(f"  {region:12s} {rem:4d} remaining / {len(rr)}")
    print("\nReview the rest in the dashboard's Leagues tab -> 'Remaining Only'.")


if __name__ == "__main__":
    main()
