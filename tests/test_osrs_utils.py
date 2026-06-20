"""Tests for the shared helpers in osrs_utils."""

import json
from datetime import date

import osrs_utils as U

# --- date handling -------------------------------------------------------

def test_parse_date_iso():
    assert U.parse_date("2024-01-15") == date(2024, 1, 15)


def test_parse_date_iso_timestamp():
    # TempleOSRS returns dates with a time component.
    assert U.parse_date("2024-01-15 12:30:45") == date(2024, 1, 15)


def test_parse_date_us_slashes():
    assert U.parse_date("1/15/2024") == date(2024, 1, 15)


def test_parse_date_garbage_is_none():
    assert U.parse_date("not a date") is None
    assert U.parse_date("") is None
    assert U.parse_date(None) is None


def test_normalize_date_to_iso():
    assert U.normalize_date("1/15/2024") == "2024-01-15"
    assert U.normalize_date("2024-01-15 09:00:00") == "2024-01-15"


def test_normalize_date_passthrough_unparseable():
    # An unrecognized-but-present value is preserved, never silently dropped.
    assert U.normalize_date("sometime") == "sometime"
    assert U.normalize_date(None) is None


def test_date_sort_key_orders_chronologically_across_formats():
    # The bug this fixes: lexicographic sorting put "9/01/2024" after
    # "2024-10-01". Chronologically September precedes October.
    values = ["2024-10-01", "9/01/2024", "2024-01-05"]
    ordered = sorted(values, key=U.date_sort_key)
    assert ordered == ["2024-01-05", "9/01/2024", "2024-10-01"]


def test_date_sort_key_undated_sorts_oldest():
    assert U.date_sort_key(None) == date.min


# --- YAML-ish parsing ----------------------------------------------------

def test_parse_item_with_date_variants():
    assert U.parse_item_with_date("Twisted bow | 2024-01-15") == {
        "name": "Twisted bow", "date": "2024-01-15"}
    assert U.parse_item_with_date("Twisted bow |") == {"name": "Twisted bow", "date": None}
    assert U.parse_item_with_date("Twisted bow") == {"name": "Twisted bow", "date": None}


def test_parse_yaml_with_dates_two_levels():
    content = (
        "Chambers of Xeric:\n"
        "  obtained:\n"
        "    - Twisted bow | 2024-01-15\n"
        "    - Kodai insignia |\n"
        "  missing:\n"
        "    - Elder maul\n"
    )
    data = U.parse_yaml_with_dates(content)
    assert data["Chambers of Xeric"]["obtained"][0] == {
        "name": "Twisted bow", "date": "2024-01-15"}
    assert data["Chambers of Xeric"]["missing"][0] == {"name": "Elder maul", "date": None}
    assert U.count_items(data) == 3


def test_check_no_dropped_items_raises_on_mismatch():
    # A "- " line with no section heading above it can't be placed -> dropped.
    content = "- Orphan item\nChambers of Xeric:\n  obtained:\n    - Twisted bow\n"
    data = U.parse_yaml_with_dates(content)
    try:
        U.check_no_dropped_items(content, U.count_items(data), "x.yaml", strict=True)
    except ValueError:
        return
    raise AssertionError("expected ValueError for dropped item")


def test_names_lower_handles_dicts_and_strings():
    assert U.names_lower([{"name": "Beaver"}, "Heron"]) == {"beaver", "heron"}


# --- JSON output ---------------------------------------------------------

def test_save_json_skips_timestamp_only_change(tmp_path, capsys):
    path = tmp_path / "out.json"
    U.save_json(path, {"updated": "t1", "value": 1})
    U.save_json(path, {"updated": "t2", "value": 1})  # only timestamp differs
    captured = capsys.readouterr().out
    assert "Unchanged" in captured
    # File still holds the original timestamp because the rewrite was skipped.
    assert json.loads(path.read_text())["updated"] == "t1"


def test_save_json_writes_real_change(tmp_path):
    path = tmp_path / "out.json"
    U.save_json(path, {"updated": "t1", "value": 1})
    U.save_json(path, {"updated": "t2", "value": 2})
    assert json.loads(path.read_text())["value"] == 2
