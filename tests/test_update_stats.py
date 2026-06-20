"""Tests for the data-shaping logic in update_stats (no network involved)."""

import update_stats as S

# --- xp / level math -----------------------------------------------------

def test_xp_for_level_bounds():
    assert S.xp_for_level(1) == 0
    assert S.xp_for_level(99) == 13034431
    assert S.xp_for_level(120) == S.xp_for_level(99)  # clamps at 99


def test_get_level_progress_at_99_is_complete():
    assert S.get_level_progress(13034431, 99) == {"progress": 100, "xp_to_level": 0}


def test_get_level_progress_midway():
    prog = S.get_level_progress(0, 1)  # level 1, no xp into level 2
    assert prog["progress"] == 0.0
    assert prog["xp_to_level"] == 83


# --- collection log processing ------------------------------------------

def _temple(items, finished=2, available=100):
    return {"data": {
        "items": items,
        "total_collections_finished": finished,
        "total_collections_available": available,
    }}


def test_process_temple_clog_normalizes_and_sorts_dates():
    temple = _temple({
        "some_boss": [
            {"id": 1, "count": 1, "date": "2024-01-05 08:00:00"},
            {"id": 2, "count": 1, "date": "2024-10-01 08:00:00"},
        ]
    })
    item_names = {"1": "Item A", "2": "Item B"}
    result = S.process_temple_clog(temple, manual_dates={}, yaml_data={}, item_names=item_names)

    # Dates normalized to plain ISO (time stripped).
    recent = result["recent_items"]
    assert recent[0] == {"name": "Item B", "date": "2024-10-01", "collection": "some_boss"}
    # Newest first.
    assert [r["date"] for r in recent] == ["2024-10-01", "2024-01-05"]
    assert result["source"] == "templeosrs"
    assert result["total_obtained"] == 2  # taken from total_collections_finished


def test_process_temple_clog_manual_date_wins_and_sorts_across_formats():
    # Item B has a manual date in US format that is chronologically newer than
    # Item A's ISO date. The fix must order by real date, not string compare.
    temple = _temple({
        "some_boss": [
            {"id": 1, "count": 1, "date": "2024-08-01"},
            {"id": 2, "count": 1, "date": "2024-01-01"},
        ]
    })
    item_names = {"1": "Item A", "2": "Item B"}
    manual = {"item b": "9/15/2024"}  # newer than Item A
    result = S.process_temple_clog(temple, manual_dates=manual, yaml_data={}, item_names=item_names)
    assert result["recent_items"][0]["name"] == "Item B"
    assert result["recent_items"][0]["date"] == "2024-09-15"


def test_process_temple_clog_merges_yaml_missing():
    temple = _temple({"some_boss": [{"id": 1, "count": 1, "date": "2024-01-01"}]})
    item_names = {"1": "Item A"}
    yaml_data = {"Some Boss": {"obtained": [], "missing": [{"name": "Item Z", "date": None}]}}
    result = S.process_temple_clog(temple, manual_dates={}, yaml_data=yaml_data, item_names=item_names)
    cat = result["collections"]["Some Boss"]
    assert "Item Z" in cat["missing"]
    assert cat["obtained_count"] == 1
    assert cat["total_count"] == 2


# --- pet extraction ------------------------------------------------------

def test_extract_pets_from_clog_finds_pets(monkeypatch):
    # No pets.yaml in the test data dir -> read_data_file returns None, fine.
    monkeypatch.setattr(S, "read_data_file", lambda name: None)
    clog = {"collections": {
        "vorkath": {"obtained": [
            {"name": "Vorki", "date": "2024-02-02"},
            {"name": "Dragon bones", "date": "2024-02-02"},  # not a pet
        ]},
    }}
    pets = S.extract_pets_from_clog(clog)
    names = {p["name"] for p in pets["obtained"]}
    assert names == {"Vorki"}
    assert pets["source"] == "collection_log"
