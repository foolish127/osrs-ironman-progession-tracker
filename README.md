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
| **Bank Value** | GE API | Prices updated from your bank.txt |
| **Potion Storage Value** | GE API | Prices updated from your YAML |

**Requirements for Collection Log/Pets automation:**
- Install **TempleOSRS plugin** in RuneLite
- Enable **auto-sync** in plugin settings
- Sync your collection log at least once

### ❌ Manual (You edit these files)

These require manual updates when things change:

| Data | File to Edit | When to Update |
|------|--------------|----------------|
| **Combat Achievements** | `data/combat_achievements.yaml` | When you complete a task |
| **Quests** | `data/quests.yaml` | When you complete a quest |
| **Achievement Diaries** | `data/diaries.yaml` | When you complete a diary tier |
| **Goals** | `data/goals.yaml` | When you set/complete goals |
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
│   ├── bank.json               # Auto-generated from bank.txt + GE prices
│   ├── potion_storage.json     # Auto-generated from YAML + GE prices
│   ├── combat_achievements.yaml # Manual
│   ├── quests.yaml             # Manual
│   ├── diaries.yaml            # Manual
│   ├── goals.yaml              # Manual
│   ├── drops.yaml              # Manual
│   ├── pets.yaml               # Manual (for dates only)
│   ├── collection_log.yaml     # Manual (for dates only)
│   ├── potion_storage.yaml     # Manual
│   └── bank.txt                # Manual (RuneLite bank export)
├── docs/                       # GitHub Pages site
│   ├── index.html              # Main dashboard
│   └── data/                   # Copied from /data by workflow
└── scripts/
    ├── update_stats.py         # Main update script
    └── update_bank.py          # Bank processing script
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

### Bank Export (`data/bank.txt`)
1. In RuneLite, use Bank plugin's "Export" feature
2. Paste contents into `data/bank.txt`
3. Commit and push - workflow will calculate values

---

## Setup

1. **Enable GitHub Pages**: Settings → Pages → Source → `main` branch → `/docs` folder
2. **Set Bank Password** (optional): Settings → Secrets → Add `BANK_PASSWORD_HASH`
3. **Trigger first update**: Actions → "Update OSRS Stats" → Run workflow

---

## Forcing an Update

The workflow runs automatically every 6 hours. To force an immediate update:
1. Go to **Actions** tab
2. Click **"Update OSRS Stats"**
3. Click **"Run workflow"**

Or just push any change to the repo.

---

*Powered by TempleOSRS API, Official OSRS Hiscores, and GitHub Actions*
