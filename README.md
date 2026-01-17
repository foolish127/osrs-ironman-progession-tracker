# FoolinSlays - OSRS Ironman Tracker

A personal dashboard tracking my Old School RuneScape Ironman account progress.

## 🌐 [View Dashboard](https://foolish127.github.io/osrs-ironman-progession-tracker/)

## Features

- **Skills** — All 23 skills with levels, XP, and progress to next level
- **Bosses** — Kill counts for all bosses
- **Clues** — Clue scroll completions by tier
- **Collection Log** — Expandable categories showing obtained items
- **Combat Achievements** — Progress across all CA tiers
- **Pets** — Pet collection tracking
- **Quests** — Quest completion status (177/177 ✓)
- **Diaries** — Achievement Diary progress by region and tier
- **Goals** — Kanban-style goal tracker

### URL Navigation

Each tab is linkable via URL hash:
- `#skills` `#bosses` `#clues` `#collectionLog` `#combatAchievements` `#pets` `#quests` `#diaries` `#goals`

## Data Sources

| Data | Source |
|------|--------|
| Skills & Boss KC | Official OSRS Hiscores + TempleOSRS API |
| Collection Log | TempleOSRS (requires RuneLite plugin sync) |
| Diaries & Quests | Hardcoded based on current progress |
| Goals | Manual editing of `data/goals.yaml` |

## Setup

1. **Enable GitHub Pages**: Settings → Pages → Deploy from branch → `main` → `/docs`
2. **Trigger update**: Actions → "Update OSRS Stats" → Run workflow
3. **Automatic updates**: Workflow runs every 6 hours

## Customization

Edit `data/goals.yaml` to manage your goals kanban board.

---

*Powered by TempleOSRS API and GitHub Actions*
