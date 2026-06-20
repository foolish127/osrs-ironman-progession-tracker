"""Tests for bank categorization and potion-storage parsing (no network)."""

import update_bank as B


def test_categorize_barrows_beats_equipment():
    # "platebody" is an Equipment keyword, but Barrows rules run first.
    assert B.categorize_item("Dharok's platebody") == ("Barrows", "Dharok's")


def test_categorize_pickaxe_is_a_tool_not_a_weapon():
    # Deliberately: Equipment has no bare "axe" keyword, so pickaxes fall to Tools.
    assert B.categorize_item("Rune pickaxe") == ("Miscellaneous", "Tools")


def test_categorize_claws_are_melee():
    assert B.categorize_item("Dragon claws") == ("Equipment", "Melee Weapons")


def test_categorize_cannonball():
    assert B.categorize_item("Cannonball") == ("Ammunition", "Cannonballs")


def test_categorize_coins():
    assert B.categorize_item("Coins") == ("Currency", "Coins & Tokens")


def test_categorize_unknown_falls_through():
    assert B.categorize_item("Mysterious widget") == ("Miscellaneous", "Other")


def test_load_potion_storage_doses_to_4dose(monkeypatch, tmp_path):
    monkeypatch.setattr(B, "DATA_DIR", tmp_path)
    (tmp_path / "potion_storage.yaml").write_text(
        "Combat:\n"
        "  Super combat potion(4): 10\n"   # 10 doses -> ceil(10/4) = 3
        "  Prayer potion(2): 4\n",         # normalized to (4); 4 doses -> 1
        encoding="utf-8",
    )
    items = B.load_potion_storage_as_items()
    by_name = {i["name"]: i for i in items}
    assert by_name["Super combat potion(4)"]["quantity"] == 3
    assert by_name["Prayer potion(4)"]["quantity"] == 1
    assert all(i["source"] == "potion_storage" for i in items)
