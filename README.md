# FoolinSlays - OSRS Ironman Tracker

Automated tracking of my OSRS ironman and group-ironman progress.

## 🌐 [View Dashboard](https://foolish127.github.io/osrs-ironman-progession-tracker/)

---

## Accounts

Two accounts are tracked, switchable from the dropdown in the dashboard header:

| Account | Data directory | Hiscores board |
|---|---|---|
| **FoolinSlays** (ironman) | `data/` | ironman |
| **GIM Foolin** (group ironman, solo) | `data/gim/` | main (`HISCORES_VARIANT=hiscore_oldschool`) |

`update_stats.py` runs once per account in CI. To target the GIM account locally:

```bash
OSRS_DATA_DIR=data/gim RSN="GIM Foolin" HISCORES_VARIANT=hiscore_oldschool python scripts/update_stats.py
```

Planning notes live alongside the data as plain markdown: **[Ironman.md](Ironman.md)**
(maxing, boss order, remaining elite diary tasks, AFK methods) and
**[GIM.md](GIM.md)** (Sailing, guide-parity gaps, Thieving plan).

---

## Data Sources: Automated vs Manual

### ✅ Automated (Updates every 6 hours)

These update automatically - **no action needed** from you:

| Data | Source | Notes |
|------|--------|-------|
| **Skills** | Official Hiscores | Levels, XP, ranks |
| **Boss KC** | Official Hiscores | Kill counts for all bosses |
| **Clue Scrolls** | Official Hiscores | Completion counts |
| **Collection Log** | TempleOSRS API | Items obtained/missing |
| **Pets** | TempleOSRS API | Extracted from collection log |
| **CA points** | Official Hiscores | Live Combat Achievement point total + rank (task list stays manual) |
| **Collections logged** | Official Hiscores | Unique collection slots + rank |

**Requirements for Collection Log/Pets automation:**
- Install **TempleOSRS plugin** in RuneLite
- Enable **auto-sync** in plugin settings
- Sync your collection log at least once

> **Note on quests / diaries / CA tasks:** there is no clean public OSRS API for
> task-level data (the only source, WikiSync, asks not to be used by third
> parties), so those stay manually edited. Only the CA **point total** is
> automated, from the hiscores.

### 🛠️ Helper scripts

- **Drops "to log" callout** — the **Drops tab** shows a live banner (and a count
  badge on the Drops nav tab) listing recently obtained collection-log items not
  yet in `data/drops.yaml`. It self-clears once you log them. `scripts/suggest_drops.py`
  is an optional CLI version of the same check. Nothing is ever auto-added.
- **Targets tab** — everything you haven't got yet, in two sub-tabs. *Collection
  log* ranks missing items by how common they are across WikiSync players
  (`wiki_comp_rates.json`); *Combat achievements* ranks uncompleted tasks the same
  way (`wiki_ca_table.json`). Each opens with a **top-10 banner** — CA by points
  still available per monster, clog by items missing per source — and the chips
  filter the table below.
- **`scripts/update_bank_local.ps1`** — refreshes your private bank values
  locally; can be scheduled via Windows Task Scheduler (instructions inside the
  file) to keep `bank.json` current hands-off without ever touching the cloud.

### 🔒 Local-only (Private — never published)

Your bank is **private**. `data/bank.txt` and the generated `data/bank.json`
are git-ignored and are **never committed or published** to the live site.
Run `python scripts/update_bank.py` **locally** to price your bank, then open
`index.html` locally to view the Bank tab. On the public dashboard the Bank tab
simply shows a "private" notice.

### ❌ Manual (You edit these files)

These require manual updates when things change:

| Data | File to Edit | When to Update |
|------|--------------|----------------|
| **Combat Achievements** | `data/combat_achievements.yaml` | When you complete a task |
| **Quests** | `data/quests.yaml` | When you complete a quest |
| **Achievement Diaries** | `data/diaries.yaml` | When you complete a diary tier |
| **Diary tasks** | `data/diary_tasks.yaml` | Delete a task once it's done - the Diaries tab shows what's left |
| **Notable Drops** | `data/drops.yaml` | When you get a notable drop |
| **Bank Export** | `data/bank.txt` | When you want updated bank values |
| **Potion Storage** | `data/potion_storage.yaml` | When storage changes significantly |

### 📅 Date Preservation

Your manually-entered dates in YAML files are **never overwritten** by automation:
- Collection log dates from `collection_log.yaml` are preserved
- Pet dates from `pets.yaml` are preserved
- The automation only fills in dates for NEW items

---

## File Structure

```
├── data/                       # Source of truth - FoolinSlays (ironman)
│   ├── skills.json             # Auto-generated
│   ├── bosses.json             # Auto-generated
│   ├── clues.json              # Auto-generated
│   ├── collection_log.json     # Auto-generated from TempleOSRS
│   ├── pets.json               # Auto-generated from collection log
│   ├── combat_achievements.json / quests.json   # Auto-generated from the YAML
│   ├── bank.json               # Generated locally (git-ignored, private)
│   ├── potion_storage.json     # Auto-generated from YAML + GE prices
│   ├── combat_achievements.yaml # Manual
│   ├── quests.yaml             # Manual
│   ├── diaries.yaml            # Manual (tier completion)
│   ├── diary_tasks.yaml        # Manual - delete a task once it's done
│   ├── drops.yaml              # Manual
│   ├── pets.yaml               # Manual (dates + notes)
│   ├── collection_log.yaml     # Manual (dates + the missing-item scaffold)
│   ├── clog_categories.yaml    # Collection-log category list
│   ├── league_tasks.yaml       # Built by build_league_tasks.py
│   ├── potion_storage.yaml     # Manual
│   ├── seed_vault.json         # Manual
│   ├── wiki_comp_rates.json    # Scraped - clog completion rates (Targets tab)
│   ├── wiki_ca_table.json      # Scraped - CA table w/ monster + points (Targets tab)
│   ├── bank.txt                # Manual, LOCAL-ONLY (git-ignored, private)
│   └── gim/                    # Same layout for GIM Foolin (no bank/potion storage)
├── Ironman.md                  # Maxing plan, elite diary tasks, AFK methods
├── GIM.md                      # Sailing plan, guide-parity gaps, Thieving plan
├── index.html                  # Dashboard markup (deployed to GitHub Pages)
├── styles.css                  # Dashboard styles
├── app.js                      # Dashboard logic
├── pyproject.toml              # Ruff + pytest config (stdlib-only runtime)
├── scripts/
│   ├── update_stats.py         # Main update script (runs in CI, once per account)
│   ├── update_bank.py          # Bank processing script (run locally only)
│   ├── update_bank_local.ps1   # Scheduled local bank refresh
│   ├── osrs_utils.py           # Shared helpers (HTTP+retry, dates, YAML parsing)
│   ├── osrs_config.py          # Config tables (categories, pet names, exclusions)
│   ├── validate_data.py        # Validates generated JSON shape (CI gate)
│   ├── suggest_drops.py        # Suggests drops.yaml entries (log only)
│   ├── build_diary_tasks.py    # Re-scrapes diary_tasks.yaml (see warning below)
│   ├── build_league_tasks.py   # Builds league_tasks.yaml
│   ├── untradeable_values.py   # Untradeable item values for the bank
│   └── update_wiki_refs.py     # Experimental wiki scraper (not in CI)
└── tests/                      # pytest unit tests for the parsing/merge logic
```

> ⚠️ **`build_diary_tasks.py` re-scrapes the wiki and rewrites `diary_tasks.yaml`
> from scratch**, which would restore every task you've deleted. Only run it when
> the wiki adds new diary tasks, and expect to re-delete your completed ones.

---

## How to Update Manual Data

### Notable Drops (`data/drops.yaml`)
```yaml
  - boss: Cerberus
    kc: 168
    item: Primordial crystal
    date: 1/15/2026
    droprate: 512          # Add this to track in luck summary
```

### Combat Achievements (`data/combat_achievements.yaml`)
```yaml
Easy:
  completed:
    - Task Name | 2026-01-15    # Date is optional
  not_completed:
    - Another Task
```

### Diaries (`data/diaries.yaml`)
```yaml
Ardougne:
  easy: completed
  medium: completed
  hard: completed
  elite:                        # Leave blank if not done
```

### Bank Export (`data/bank.txt`) — local only, private
1. In RuneLite, use Bank plugin's "Export" feature
2. Paste contents into `data/bank.txt` (git-ignored — never committed)
3. Run `python scripts/update_bank.py` locally to generate `data/bank.json`
4. Open `index.html` locally to view priced bank values

> Bank data is intentionally never pushed or published. GitHub Pages is static
> and can't do server-side auth, so the only way to keep a bank truly private is
> to not publish it.

---

## Development

The runtime uses only the Python standard library — no install needed to run the
scripts. For linting and tests:

```bash
pip install ruff pytest      # or: pip install -e ".[dev]"
ruff check scripts tests     # lint
pytest -q                    # unit tests
```

CI runs `ruff` + `pytest` on every push and **blocks deployment if either fails**,
then runs `update_stats.py` **once per account**, validates the generated JSON
for both, and deploys the dashboard (`index.html` + `styles.css` + `app.js`) to
GitHub Pages.

---

## Setup

1. **Enable GitHub Pages**: Settings → Pages → Source → **GitHub Actions**
2. **Trigger first update**: Actions → "Update OSRS Stats" → Run workflow

---

## Forcing an Update

The workflow runs automatically every 6 hours. To force an immediate update:
1. Go to **Actions** tab
2. Click **"Update OSRS Stats"**
3. Click **"Run workflow"**

Or just push any change to the repo.

---

*Powered by TempleOSRS API, Official OSRS Hiscores, and GitHub Actions*
