#!/usr/bin/env python3
"""
Shared helpers for the OSRS Ironman tracker scripts.

Consolidates what used to be duplicated across update_stats.py and
update_bank.py: HTTP fetching, JSON saving, date handling and the
hand-rolled YAML-ish parsing used for the manually-edited data files.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path
from typing import Any

# Data directory. Override with OSRS_DATA_DIR to point at a specific account
# (e.g. "data/gim") so the same scripts can build multiple accounts.
DATA_DIR = Path(os.environ["OSRS_DATA_DIR"]) if os.environ.get("OSRS_DATA_DIR") else (Path(__file__).parent.parent / "data")

USER_AGENT = "OSRS-Ironman-Tracker/1.0 (github.com/foolish127)"


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def fetch_json(
    url: str,
    params: dict | None = None,
    *,
    headers: dict | None = None,
    timeout: int = 30,
    retries: int = 3,
    backoff: float = 2.0,
) -> Any | None:
    """Fetch and parse JSON, retrying transient failures with linear backoff.

    Returns the parsed JSON on success, or None if every attempt failed (the
    caller is responsible for falling back gracefully). Distinguishes itself
    from the old version by retrying instead of giving up on the first error.
    """
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)

    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:  # noqa: BLE001 - network/JSON errors are all non-fatal here
            last_err = e
            print(f"  fetch attempt {attempt}/{retries} failed for {url}: {e}")
            if attempt < retries:
                time.sleep(backoff * attempt)

    print(f"Error fetching {url} (gave up after {retries} attempts): {last_err}")
    return None


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def _strip_updated(obj: Any) -> Any:
    """A dict without its top-level 'updated' timestamp, for change detection."""
    if isinstance(obj, dict):
        return {k: v for k, v in obj.items() if k != "updated"}
    return obj


def save_json(path: Path, data: Any, *, skip_if_only_timestamp_changed: bool = True) -> None:
    """Write JSON, optionally skipping rewrites that only bump 'updated'.

    Skipping timestamp-only changes keeps CI commits (and git history) limited
    to real data changes instead of churning on every scheduled run.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if skip_if_only_timestamp_changed and path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
            if _strip_updated(old) == _strip_updated(data):
                print(f"Unchanged: {path}")
                return
        except Exception:  # noqa: BLE001 - unreadable old file just means "rewrite it"
            pass
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------

# Formats accepted from manually-edited YAML and from the TempleOSRS API.
_DATE_FORMATS = ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y")


def parse_date(value: Any) -> date | None:
    """Parse a date string into a date, or None if it isn't a recognized date.

    Handles ISO dates/timestamps ('2024-01-15', '2024-01-15 12:30:00') plus a
    few common manual formats ('1/15/2024'). Used so dates sort chronologically
    instead of lexicographically.
    """
    if not value:
        return None
    s = str(value).strip()
    if not s:
        return None
    # ISO date or timestamp (with a space or 'T' separating the time).
    try:
        return datetime.fromisoformat(s.replace(" ", "T")).date()
    except ValueError:
        pass
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def normalize_date(value: Any) -> str | None:
    """Return a date as an ISO 'YYYY-MM-DD' string, or None.

    Unrecognized-but-present values are passed through unchanged so we never
    silently drop a date we simply failed to parse.
    """
    if not value:
        return None
    d = parse_date(value)
    if d is not None:
        return d.isoformat()
    return str(value).strip() or None


def date_sort_key(value: Any) -> date:
    """Sort key that orders by real date; undated/garbage sorts oldest."""
    return parse_date(value) or date.min


# ---------------------------------------------------------------------------
# YAML-ish parsing for the manually-edited data files
# ---------------------------------------------------------------------------

def parse_item_with_date(line: str) -> dict:
    """Parse 'item name | 2024-01-15' or 'item name |' or 'item name'."""
    line = line.strip()
    if ' | ' in line:
        name, _, rest = line.partition(' | ')
        rest = rest.strip()
        return {'name': name.strip(), 'date': rest or None}
    if line.endswith(' |'):
        return {'name': line[:-2].strip(), 'date': None}
    return {'name': line, 'date': None}


def parse_yaml_with_dates(content: str) -> dict:
    """Parse the two-level 'category: / subsection: / - item | date' structure."""
    result: dict = {}
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
            result[current_key][current_subkey].append(
                parse_item_with_date(stripped[2:])
            )

    return result


def check_no_dropped_items(
    content: str, parsed_count: int, source: str, *, strict: bool = True
) -> None:
    """Fail loudly if a hand-edited YAML file has list items that didn't parse.

    Counts raw '- ' list lines and compares against how many items were parsed.
    A mismatch means a line was silently dropped (usually a bad indent or a
    missing 'section:'/'subsection:' heading), which would otherwise vanish
    from the dashboard with no warning at all.
    """
    raw_count = sum(1 for ln in content.split('\n') if ln.lstrip().startswith('- '))
    if raw_count != parsed_count:
        msg = (f"{source}: found {raw_count} '- ' list lines but only parsed "
               f"{parsed_count} of them — {raw_count - parsed_count} item(s) were "
               f"dropped. Check indentation and the section/subsection headings.")
        if strict:
            raise ValueError(msg)
        print(f"  WARNING: {msg}")


def read_data_file(name: str) -> str | None:
    """Read a file from the data dir, or return None if it doesn't exist."""
    path = DATA_DIR / name
    if not path.exists():
        print(f"Data file not found: {path}")
        return None
    return path.read_text(encoding="utf-8")


def count_items(nested: dict) -> int:
    """Total leaf items in a {key: {subkey: [items]}} structure."""
    return sum(len(items) for sub in nested.values() for items in sub.values())


def names_lower(items: Iterable) -> set:
    """Lowercased names from a list of {'name': ...} dicts or bare strings."""
    out = set()
    for it in items:
        name = it.get('name') if isinstance(it, dict) else it
        if name:
            out.add(name.lower())
    return out
