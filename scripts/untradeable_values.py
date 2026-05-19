"""
Manual value overrides for untradeable items.
Applied in update_stats.py when ge_price == 0.

Values are best-effort proxies:
- Crystal/bowfa: tradeable inactive equivalent GE price
- Barrows degraded: tradeable full version (4847+ id space)
- Cosmetic/quest items: 0 (intentionally)
"""

UNTRADEABLE_VALUES = {
    # --- Crystal / Bowfa ---
    33021: 132_260_955,  # Bow of faerdhinen (c)  — inactive bowfa GE
    33023: 35_000_000,   # Crystal body (corrupted)
    33027: 35_000_000,   # Crystal legs (corrupted)
    33031: 18_000_000,   # Crystal helm (corrupted)
    23983: 1_000_000,    # Crystal bow
    23987: 1_000_000,    # Crystal halberd
    23991: 1_000_000,    # Crystal shield

    # --- Capes (skill capes + fire cape) ---
    6570:  152_900,      # Fire cape (HA)
    21795: 50_000,       # Imbued zamorak cape
    9769:  99_000,       # Hitpoints cape(t)
    9763:  99_000,       # Magic cape(t)
    9751:  99_000,       # Strength cape(t)
    9752:  1_000,        # Strength hood
    9811:  99_000,       # Farming cape(t)
    22114: 50_000,       # Mythical cape
    1052:  50_000,       # Cape of legends
    9813:  99_000,       # Quest point cape
    31290: 99_000,       # Sailing cape(t)
    31292: 1_000,        # Sailing hood

    # --- Slayer / combat ---
    26674: 5_000_000,    # Slayer helmet (i)
    26770: 2_000_000,    # Berserker ring (i)
    26762: 35_000_000,   # Ring of suffering (ri)
    28327: 30_000_000,   # Ring of shadows
    12018: 25_000_000,   # Salve amulet(ei)
    7462:  130_000,      # Barrows gloves (HA)
    12954: 100_000,      # Dragon defender (HA)
    31094: 80_000_000,   # Avernic treads (pr)(pe) — base avernic + 2 mokhaiotl upgrades
    25930: 50_000,       # Ghommal's hilt 3

    # --- Void ---
    13072: 1_000_000,    # Elite void top
    13073: 1_000_000,    # Elite void robe
    11664: 100_000,      # Void ranger helm
    8842:  100_000,      # Void knight gloves

    # --- Moon armor (CA reward, untradeable) ---
    29047: 500_000, 29043: 1_000_000, 29045: 1_000_000,  # Blood moon h/c/t
    29041: 500_000, 29037: 1_000_000, 29039: 1_000_000,  # Blue moon h/c/t
    29035: 500_000, 29031: 1_000_000, 29033: 1_000_000,  # Eclipse moon h/c/t
    29000: 5_000_000,    # Eclipse atlatl
    28997: 5_000_000,    # Dual macuahuitl
    28988: 1_000_000,    # Blue moon spear
    30955: 5_000_000,    # Arkan blade
    28792: 100_000,      # Bone mace
    28810: 50_000,       # Zombie axe
    28869: 200_000,      # Hunters' sunlight crossbow

    # --- Other key weapons/equipment ---
    20714: 350_000,      # Tome of fire (HA)
    22109: 75_000,       # Ava's assembler
    10499: 50_000,       # Ava's accumulator
    11907: 250_000,      # Trident of the seas (HA-ish)
    29589: 5_000_000,    # Emberlight
    29594: 5_000_000,    # Purging staff
    29591: 3_000_000,    # Scorching bow
    29577: 5_000_000,    # Burning claws
    25979: 1_000_000,    # Keris partisan
    24699: 500_000,      # Blisterwood flail
    6746:  60_000,       # Darklight
    13576: 150_000,      # Already tradeable? skip if so
    24266: 5_000_000,    # V's shield

    # --- Resources (untradeable but valuable) ---
    23962: 1_000,        # Crystal shard
    23964: 500,          # Crystal dust
    23956: 8_047_160,    # Crystal armour seed (matches seed GE)
    29381: 50,           # Blessed bone shards
    29378: 200,          # Sun-kissed bones
    25527: 50,           # Stardust
    12012: 800,          # Golden nugget
    11849: 100_000,      # Mark of grace (rough convenience value)
    13204: 1_000,        # Platinum token (1k coins each)
    19677: 1_000,        # Ancient shard
    21726: 100,          # Granite dust
    13446: 5_000,        # Dark essence block

    # --- Mokhaiotl ---
    31109: 50_000_000,   # Mokhaiotl cloth

    # --- Pets (symbolic) ---
    20663: 1, 20693: 1, 28670: 1, 13321: 1, 6560: 1, 7581: 1,

    # --- Diary rewards (no good value) ---
    # Keep at 0: Ardougne cloak, Falador shield, Karamja gloves, etc.
}
