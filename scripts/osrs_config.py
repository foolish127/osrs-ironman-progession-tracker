#!/usr/bin/env python3
"""
Shared configuration tables for the OSRS Ironman tracker.

These are pure data, kept out of the logic modules so they're easy to find and
edit in one place. Comments next to individual rules carry maintenance notes
(priority ordering, deliberate keyword choices) — keep them when editing.
"""

# ---------------------------------------------------------------------------
# update_stats.py
# ---------------------------------------------------------------------------

# Hiscores "activities" that are not actual bosses (points/counters/PvP).
BOSS_EXCLUSIONS = {
    "Collections Logged", "Combat Achievements",
    "PvP Arena", "PvP Arena - Rank", "Colosseum Glory",
}

# Collection-log item names that are pets. Used to pull a pet list out of the
# full collection log. Stored lowercase for case-insensitive matching.
PET_NAMES = {
    'abyssal orphan', 'baby chinchompa', 'baby mole', 'beaver', 'bloodhound',
    'callisto cub', 'chompy chick', 'giant squirrel', 'hellpuppy', 'herbi',
    'heron', 'ikkle hydra', 'jal-nib-rek', 'kalphite princess', 'little nightmare',
    'noon', 'midnight', 'olmlet', 'pet chaos elemental', 'pet dagannoth prime',
    'pet dagannoth rex', 'pet dagannoth supreme', 'pet dark core', 'pet general graardor',
    "pet k'ril tsutsaroth", 'pet kraken', 'pet penance queen', 'pet smoke devil',
    'pet snakeling', 'pet zilyana', 'phoenix', 'prince black dragon', 'rift guardian',
    'rock golem', 'rocky', "scorpia's offspring", 'skotos', 'smolcano', 'sraracha',
    'tangleroot', 'tiny tempor', "tumeken's guardian", 'tzrek-jad', 'venenatis spiderling',
    "vet'ion jr", 'vorki', 'youngllef', 'lil creator', 'muphin', 'smol heredit',
    'baron', 'butch', 'sol heredit', 'scurry', 'wisp', "lil'viathan",
    "lil' maiden", 'quetzin', 'nexling', 'puppadile', 'tektiny', 'vanguard',
    'vasa minirio', 'metamorphic dust', 'dom', 'bran',
    'beef', 'maggot marquess',
}

# ---------------------------------------------------------------------------
# update_bank.py
# ---------------------------------------------------------------------------

# Categories checked in priority order - more specific categories first.
# Each tuple is (category, subcategory, keywords).
CATEGORY_RULES = [
    # Barrows - check first since they contain equipment keywords
    ("Barrows", "Ahrim's", ["ahrim"]),
    ("Barrows", "Dharok's", ["dharok"]),
    ("Barrows", "Guthan's", ["guthan"]),
    ("Barrows", "Karil's", ["karil"]),
    ("Barrows", "Torag's", ["torag"]),
    ("Barrows", "Verac's", ["verac"]),

    # Moon armor sets - check before general equipment
    ("Moon Armor", "Blood Moon", ["blood moon"]),
    ("Moon Armor", "Blue Moon", ["blue moon"]),
    ("Moon Armor", "Eclipse Moon", ["eclipse moon"]),

    # Currency - check early for coins
    ("Currency", "Coins & Tokens", ["coins", "platinum token", "tokkul", "trading sticks", "numulite", "golden nugget", "mark of grace", "stardust", "crystal shard", "amylase", "warrior guild token", "ecto-token"]),

    # Runes - check before other categories
    ("Runes", "Elemental", ["air rune", "water rune", "earth rune", "fire rune"]),
    ("Runes", "Catalytic", ["mind rune", "body rune", "cosmic rune", "chaos rune", "nature rune", "law rune", "death rune", "blood rune", "soul rune", "astral rune", "wrath rune"]),
    ("Runes", "Combination", ["mist rune", "dust rune", "mud rune", "smoke rune", "steam rune", "lava rune"]),
    ("Runes", "Talismans", ["talisman"]),

    # Food - raw fish before cooked to avoid overlap
    ("Food", "Raw Fish", ["raw shark", "raw monkfish", "raw lobster", "raw swordfish", "raw tuna", "raw salmon", "raw trout", "raw bass", "raw cod", "raw pike", "raw anglerfish", "raw manta ray", "raw karambwan", "raw sardine"]),
    ("Food", "Cooked Fish", ["shark", "monkfish", "lobster", "swordfish", "tuna", "salmon", "trout", "bass", "cod", "pike", "anglerfish", "manta ray", "sea turtle", "dark crab", "karambwan"]),
    ("Food", "Cooked Meals", ["stew", "pie", "potato", "pizza"]),
    ("Food", "Fruit", ["fruit", "berries", "papaya", "coconut", "dragonfruit", "grapes", "watermelon", "calquat"]),
    ("Food", "Other Food", ["sweets", "cake", "bread", "moth"]),

    # Potions
    ("Potions", "Unfinished", ["potion (unf)"]),
    ("Potions", "Combat Potions", ["super combat", "divine", "ranging potion", "magic potion", "super strength", "super attack", "super defence"]),
    ("Potions", "Restoration", ["saradomin brew", "prayer potion", "super restore", "sanfew", "guthix rest"]),
    ("Potions", "Skilling Potions", ["stamina", "energy potion", "agility potion", "hunter potion"]),
    ("Potions", "Other Potions", ["antifire", "antidote", "antipoison", "antivenom", "relicym", "balm"]),

    # Slayer - before equipment
    ("Slayer", "Ensouled Heads", ["ensouled"]),
    ("Slayer", "Slayer Equipment", ["slayer helmet", "nose peg", "earmuffs", "face mask", "mirror shield", "rock hammer", "bag of salt", "ice cooler", "witchwood icon", "slayer bell", "fungicide", "slayer's staff", "leaf-bladed"]),
    ("Slayer", "Slayer Drops", ["dark totem", "ancient shard", "brimstone key", "larran's key"]),

    # Ammunition - before equipment to catch darts/knives
    ("Ammunition", "Arrows", ["arrow", "arrowtips"]),
    ("Ammunition", "Bolts", ["bolt"]),
    ("Ammunition", "Cannonballs", ["cannonball"]),
    ("Ammunition", "Other Ammo", ["javelin", "dart", "thrownaxe", "chinchompa", "atlatl dart"]),

    # Teleportation
    ("Teleportation", "Jewelry", ["games necklace", "ring of dueling", "amulet of glory", "ring of wealth", "necklace of passage", "digsite pendant", "burning amulet", "skills necklace", "combat bracelet"]),
    ("Teleportation", "Tablets", ["teleport to house", "varrock teleport", "lumbridge teleport", "falador teleport", "camelot teleport"]),
    ("Teleportation", "Other Teleports", ["ectophial", "royal seed pod", "xeric's talisman", "drakan's medallion", "teleport crystal", "pharaoh's sceptre", "skull sceptre"]),

    # Clue Items
    ("Clue Items", "Clue Scrolls", ["clue scroll", "scroll box"]),
    ("Clue Items", "Clue Rewards", ["firelighter", "blessing", "ornament kit"]),

    # Skilling materials
    ("Skilling", "Herbs", ["grimy", "guam leaf", "marrentill", "tarromin", "harralander", "ranarr", "irit leaf", "avantoe", "kwuarm", "cadantine", "lantadyme", "dwarf weed", "torstol", "snapdragon", "toadflax"]),
    ("Skilling", "Seeds", ["seed"]),
    ("Skilling", "Ores", [" ore", "coal"]),
    ("Skilling", "Bars", [" bar"]),
    ("Skilling", "Logs", ["logs"]),
    ("Skilling", "Planks", ["plank"]),
    ("Skilling", "Gems", ["sapphire", "emerald", "ruby", "diamond", "dragonstone", "onyx", "opal", "jade", "topaz", "uncut"]),
    ("Skilling", "Hides & Leather", ["dragonhide", "leather", "cowhide"]),
    ("Skilling", "Bones", ["bones"]),
    ("Skilling", "Ashes", ["ashes"]),
    ("Skilling", "Essence", ["essence"]),
    ("Skilling", "Farming", ["compost", "bottomless", "secateurs", "seaweed", "spore"]),
    ("Skilling", "Fishing", ["bait", "feather", "harpoon", "fishing net", "fishing rod", "sandworms"]),
    ("Skilling", "Hunter", ["trap", "snare", "box trap", "noose", "fur", "kebbit", "salamander", "chinchompa"]),
    ("Skilling", "Construction", ["nail", "bolt of cloth", "limestone", "marble"]),
    ("Skilling", "Crafting", ["molten glass", "glassblowing", "lantern lens", "orb"]),

    # Equipment - checked last since many items contain these keywords
    # NOTE: no bare "axe" keyword here — it would swallow pickaxes and woodcutting
    # axes (tools). "battleaxe" covers the actual melee weapon; throwing axes are
    # caught earlier under Ammunition ("thrownaxe").
    ("Equipment", "Melee Weapons", ["scimitar", "longsword", "sword", "dagger", "mace", "warhammer", "battleaxe", "2h sword", "halberd", "spear", "whip", "rapier", "hasta", "claws", "maul"]),
    ("Equipment", "Ranged Weapons", ["shortbow", "longbow", "crossbow", "blowpipe"]),
    ("Equipment", "Magic Weapons", ["staff", "wand", "trident"]),
    ("Equipment", "Helmets", ["helm", "hat", "hood", "coif", "mask", "faceguard"]),
    ("Equipment", "Body Armor", ["platebody", "chainbody", "body", "top", "torso", "chestplate", "hauberk", "robetop"]),
    ("Equipment", "Leg Armor", ["platelegs", "plateskirt", "chaps", "tassets", "cuisse", "greaves", "robeskirt", "robe bottom"]),
    ("Equipment", "Shields", ["shield", "defender", "kiteshield", "sq shield", "book of"]),
    ("Equipment", "Gloves", ["gloves", "vambraces", "gauntlets"]),
    ("Equipment", "Boots", ["boots", "sandals", "shoes"]),
    ("Equipment", "Capes", ["cape", "cloak", "ava's"]),
    ("Equipment", "Amulets & Necklaces", ["amulet", "necklace", "fury", "torture", "anguish", "tormented"]),
    ("Equipment", "Rings", ["ring of", "berserker ring", "archers ring", "seers ring", "warrior ring", "ring (i)"]),
    ("Equipment", "Bracelets", ["bracelet"]),

    # Quest Items - very generic, keep near end
    ("Quest Items", "Quest Items", ["greegree", "sigil", "seal of passage"]),

    # Miscellaneous - catchall at the end
    ("Miscellaneous", "Tools", ["hammer", "chisel", "knife", "saw", "needle", "tinderbox", "spade", "rake", "trowel", "axe"]),
    ("Miscellaneous", "Containers", ["bucket", "jug", "vial", "pot", "bowl", "basket", "sack", "pouch"]),
]
