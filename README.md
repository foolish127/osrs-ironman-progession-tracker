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
- **Bank** — Password-protected bank value tracker (hidden tab)

### URL Navigation

Each tab is linkable via URL hash:
- `#skills` `#bosses` `#clues` `#clog` `#ca` `#pets` `#quests` `#diaries` `#goals`

## Data Sources

| Data | Source |
|------|--------|
| Skills & Boss KC | Official OSRS Hiscores + TempleOSRS API |
| Collection Log | TempleOSRS (requires RuneLite plugin sync) |
| Diaries & Quests | Hardcoded based on current progress |
| Goals | Manual editing of `data/goals.yaml` |
| Bank | Manual export from Bank Memory RuneLite plugin |

## Setup

1. **Enable GitHub Pages**: Settings → Pages → Deploy from branch → `main` → `/docs`
2. **Trigger update**: Actions → "Update OSRS Stats" → Run workflow
3. **Automatic updates**: Workflow runs every 6 hours

## Bank Tab Security

The bank tab is password-protected. The password is stored as a GitHub Secret (never in your code).

### Setting Up Password Protection

1. **Choose a password** — any text you want (e.g., `MySecretBank123`)

2. **Add it as a GitHub Secret:**
   - Go to your repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `BANK_PASSWORD_HASH`
   - Value: your password (e.g., `MySecretBank123`)
   - Click "Add secret"

3. **Run the workflow** to deploy with password protection active

### Accessing the Bank Tab

Click "Bank" in the navigation, or go to: `https://foolish127.github.io/osrs-ironman-progession-tracker/#bank`

Enter your password when prompted.

### Updating Bank Data

1. In RuneLite, use the Bank Memory plugin to export your bank
2. Save to `data/bank.txt` (this file is gitignored — never committed)
3. Run the workflow manually to process and deploy
4. The processed `bank.json` will be generated with GE prices

## Customization

Edit `data/goals.yaml` to manage your goals kanban board.

---

*Powered by TempleOSRS API and GitHub Actions*
