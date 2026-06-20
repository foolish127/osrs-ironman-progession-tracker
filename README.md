# FoolinSlays - OSRS Ironman Tracker

Automated tracking of my OSRS Ironman progress.

## 🌐 [View Dashboard](https://foolish127.github.io/osrs-ironman-progession-tracker/)

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

- **`scripts/suggest_drops.py`** — lists recently obtained collection-log items
  not yet in `data/drops.yaml` so you don't forget to log notable drops. Runs in
  CI (prints to the Actions log) and locally. Never auto-edits your data.
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
├── data/                       # Source of truth for all data
│   ├── skills.json             # Auto-generated
│   ├── bosses.json             # Auto-generated
│   ├── clues.json              # Auto-generated
│   ├── collection_log.json     # Auto-generated from TempleOSRS
│   ├── pets.json               # Auto-generated from collection log
│   ├── bank.json               # Generated locally (git-ignored, private)
│   ├── potion_storage.json     # Auto-generated from YAML + GE prices
│   ├── combat_achievements.yaml # Manual
│   ├── quests.yaml             # Manual
│   ├── diaries.yaml            # Manual
│   ├── drops.yaml              # Manual
│   ├── pets.yaml               # Manual (for dates only)
│   ├── collection_log.yaml     # Manual (for dates only)
│   ├── potion_storage.yaml     # Manual
│   └── bank.txt                # Manual, LOCAL-ONLY (git-ignored, private)
├── index.html                  # Dashboard (deployed to GitHub Pages by the workflow)
└── scripts/
    ├── update_stats.py         # Main update script (runs in CI)
    └── update_bank.py          # Bank processing script (run locally only)
```

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
