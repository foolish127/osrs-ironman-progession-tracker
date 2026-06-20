# Roadmap & Idea Backlog

Captured from early planning notes (`Temporary/ideas.md`) and the original
`AccountProgress.xlsx` spreadsheet so nothing is lost once that scratch folder
is cleared. Most of the original plan is already built — this file tracks what
*isn't* yet, plus reference checklists.

---

## Unbuilt feature ideas

### 1. Leagues-style master task checklist — all regions  *(wanted — primary idea)*
Import the full **OSRS Leagues task list** as a permanent account-progression
checklist you can tick off. Key difference from an actual league: in a league
you pick only a few regions, but on the main account **every region is in
scope**, so include all zones/areas at once.

- **Data:** a new `league_tasks.yaml` grouped by **region/area** and **tier**
  (Easy / Medium / Hard / Elite / Master), each task with name, points, and a
  done flag. Source from the OSRS Wiki Leagues task tables — reuse the scraping
  pattern in `scripts/update_wiki_refs.py`.
- **Auto vs manual:** auto-complete what the existing data already proves —
  boss KC, skill levels, notable drops, CA completions, quest completions —
  using the same `check: () => …` helper pattern the Gearing tab already has;
  leave the rest as manual checkboxes (like the CA tab).
- **UI:** a new "Leagues" / "Tasks" tab mirroring the Combat Achievements tab —
  totals (tasks done + points), with per-region and per-tier breakdowns.
- **Note:** Leagues task sets change each league; pick one comprehensive recent
  league (e.g. the latest Trailblazer/Raging Echoes list) as the base.

### 2. Historical snapshots / progress over time  *(wanted)*
Show account progression over time (e.g. a timeline or trend), not just the
current snapshot.

- **Constraint:** much of the data is manually entered and `update_stats.py`
  intentionally skips unchanged writes, so there's no per-run history stored.
- **Feasible approach:** derive a timeline from the **dates already in the
  data** — collection-log item dates, combat-achievement completion dates, and
  notable-drop dates — and render "what was obtained when." This needs no new
  automation; it reuses fields the YAML files already carry.
- Optional later: a lightweight periodic snapshot of headline numbers
  (total level, CA points, clog count) committed by CI for true trend lines.

### 3. Settings / include–exclude page  *(idea — uncertain, low priority)*
A settings view to include/exclude content from progress calculations
(e.g. "I don't PvP" / "I'm skipping the Inferno") so completion % reflects only
the content you actually intend to do. Noted for consideration; not committed.

---

## Gear progression (reference)

The **Gearing tab is already built** as a 4-phase, auto-tracked progression
(Early / Mid / Late / End Game, ~40 milestones checked against real
drops/skills/quests/CA/pet/clog data — see `app.js`). The staged gear checklist
from the old spreadsheet (`Temporary/*spreadsheet.png`) is the source material
for it. Total-level→phase bands from the spreadsheet (Total Level 100…2200
mapped Early→End) are **not** represented and could optionally feed a
total-level progress view.

---

## Goals checklist (reference — from the spreadsheet, mostly already achieved)

Preserved here in case a granular "account goals" checklist is wanted later
(would fit a future `goals.yaml`). Many are already done in-game.

**Easy:** Graceful outfit (260 marks), Fairy rings, Magic secateurs,
Ardougne cloak 1, Bird house trapping, Dorgeshuun crossbow, Climbing boots,
Elemental/Mind shield, Ava's attractor, Protection prayers (43 Prayer),
finish all F2P quests, High Level Alchemy, Alfred Grimhand's Barcrawl,
Amulet of strength, Fremennik Trials, Iban's Staff, Ardougne cloak 2,
herb-run teleports (Camelot, Explorer's ring 2, Kourend, Ectophial,
Farming Guild, Trollheim).

**Medium:** Dragon Scimitar, Dragon Battleaxe, Salve Amulet, Fighter Torso,
Prayer Potions, Black Mask, Rune Crossbow, Proselyte Armour, Magic Shortbow,
Dragon Defender, Helm of Neitiznot, Void Knight equipment, Broad Bolts,
Barrows Gloves, Ancient Magicks, STASH (medium), Herb Sack, Amulet of Glory,
Anglers Outfit, Lumberjack Outfit, Medium Diary, Ectoplasmator, Holy Wrench,
Bone Crusher, Piety, Construction 55, Karambwan Fishing, Ava's accumulator.

**Hard:** Slayer Helm (i), Elite Void Knight equipment, Dragon Boots,
Abyssal Whip, Imbued God Cape, Teleport-to-house tablets, Lunar Spellbook,
Ranger Boots, Rune pouch, Blessed dragonhide armour, Fire Cape,
Super potion set, Crystal Shield, Infinity Boots, Hard Diary, Barrows gearsets,
Zombie axe, Amulet of Fury, relevant God Books, Dagannoth Imbued Rings,
Trident of the Seas, Combat (base 85+ stats), Quest Cape, Ava's assembler,
Gauntlet (first unique), Dragon sword (COX / Vasa Nistirio).

---

## Archived source

`AccountProgress.xlsx` (original master spreadsheet — sheets: To Do,
CollectionLog, CA's, Quests, Other, CA Links, CL Links) seeded the YAML data
and dashboard. Its content is migrated; keep the file as a historical backup
outside the project if desired.
