#!/usr/bin/env python3
"""
Generate a README.md with formatted progress display from the JSON data files.
"""

import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = Path(__file__).parent.parent / "README.md"
RSN = os.environ.get("RSN", "FoolinSlays")


def load_json(filename: str) -> dict:
    """Load a JSON file from the data directory."""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return {}


def format_number(n: int) -> str:
    """Format large numbers with K/M suffixes."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_stat(value, default="N/A"):
    """Format a stat value, handling None and providing comma formatting for numbers."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return str(value)


def generate_skills_table(skills_data: dict) -> str:
    """Generate a markdown table of skills."""
    if not skills_data or "skills" not in skills_data:
        return "*No skills data available yet.*\n"
    
    skills = skills_data["skills"]
    milestones = skills_data.get("milestones", {})
    
    total_level = format_stat(milestones.get('total_level'))
    total_xp = format_number(milestones.get('total_xp', 0))
    combat_level = milestones.get('combat_level', 'N/A')
    skills_99 = milestones.get('skills_99', 0)
    skills_90 = milestones.get('skills_90', 0)
    
    # Summary stats
    output = f"""### Summary
| Stat | Value |
|------|-------|
| Total Level | **{total_level}** |
| Total XP | **{total_xp}** |
| Combat Level | **{combat_level}** |
| 99s | **{skills_99}/23** |
| 90+ Skills | **{skills_90}/23** |

### All Skills
| Skill | Level | XP | Rank |
|-------|-------|-----|------|
"""
    
    # Sort skills by XP descending, but keep Overall first
    skill_items = [(k, v) for k, v in skills.items()]
    overall = next((item for item in skill_items if item[0] == "Overall"), None)
    other_skills = sorted(
        [item for item in skill_items if item[0] != "Overall"],
        key=lambda x: x[1].get("xp", 0),
        reverse=True
    )
    
    sorted_skills = ([overall] if overall else []) + other_skills
    
    for name, data in sorted_skills:
        level = data.get("level", 1)
        xp = format_number(data.get("xp", 0))
        rank = f"#{data.get('rank', 'N/A'):,}" if data.get("rank", -1) > 0 else "N/A"
        
        # Add emoji for 99s
        level_display = f"**{level}** 🎯" if level >= 99 else str(level)
        
        output += f"| {name} | {level_display} | {xp} | {rank} |\n"
    
    return output


def generate_bosses_table(bosses_data: dict) -> str:
    """Generate a markdown table of boss KCs."""
    if not bosses_data or "bosses" not in bosses_data:
        return "*No boss data available yet.*\n"
    
    bosses = bosses_data["bosses"]
    
    # Sort by KC descending
    sorted_bosses = sorted(bosses.items(), key=lambda x: x[1].get("kc", 0), reverse=True)
    
    # Only show bosses with KC > 0
    active_bosses = [(k, v) for k, v in sorted_bosses if v.get("kc", 0) > 0]
    
    if not active_bosses:
        return "*No boss kills recorded yet.*\n"
    
    output = f"*Showing {len(active_bosses)} bosses with kills*\n\n"
    output += "| Boss | KC | Rank |\n"
    output += "|------|-----|------|\n"
    
    for name, data in active_bosses:
        kc = f"{data.get('kc', 0):,}"
        rank = f"#{data.get('rank', 'N/A'):,}" if data.get("rank", -1) > 0 else "N/A"
        output += f"| {name} | {kc} | {rank} |\n"
    
    return output


def generate_collection_log_section(clog_data: dict) -> str:
    """Generate collection log summary."""
    if not clog_data or "collection_log" not in clog_data:
        return "*No collection log data available yet. Make sure you have the TempleOSRS RuneLite plugin installed and syncing.*\n"
    
    clog = clog_data["collection_log"]
    
    obtained = clog.get("total_obtained", 0)
    total = clog.get("total_items", 0)
    unique = clog.get("unique_obtained", 0)
    unique_total = clog.get("unique_items", 0)
    rank = clog.get("rank", -1)
    
    percentage = (obtained / total * 100) if total > 0 else 0
    unique_pct = (unique / unique_total * 100) if unique_total > 0 else 0
    
    output = f"""| Metric | Progress |
|--------|----------|
| Total Slots | **{obtained:,}** / {total:,} ({percentage:.1f}%) |
| Unique Items | **{unique:,}** / {unique_total:,} ({unique_pct:.1f}%) |
| Rank | **#{rank:,}** |

"""
    
    # Add category breakdown if available
    categories = clog.get("categories", {})
    if categories:
        output += "### Categories\n"
        output += "| Category | Obtained | Total | % |\n"
        output += "|----------|----------|-------|---|\n"
        
        for cat_name, cat_data in sorted(categories.items()):
            if isinstance(cat_data, dict):
                cat_obtained = cat_data.get("obtained", 0)
                cat_total = cat_data.get("total", 0)
                cat_pct = (cat_obtained / cat_total * 100) if cat_total > 0 else 0
                output += f"| {cat_name} | {cat_obtained} | {cat_total} | {cat_pct:.0f}% |\n"
    
    return output


def generate_goals_section(goals_data: dict) -> str:
    """Generate goals tracking section."""
    if not goals_data:
        return "*No goals set yet. Edit `data/goals.yaml` to add your goals!*\n"
    
    output = ""
    
    # Short-term goals
    short_term = goals_data.get("short_term", [])
    if short_term:
        output += "### Short-Term Goals\n"
        for goal in short_term:
            status = "✅" if goal.get("completed", False) else "⬜"
            output += f"- {status} {goal.get('description', 'No description')}\n"
        output += "\n"
    
    # Long-term goals
    long_term = goals_data.get("long_term", [])
    if long_term:
        output += "### Long-Term Goals\n"
        for goal in long_term:
            status = "✅" if goal.get("completed", False) else "⬜"
            progress = goal.get("progress", "")
            progress_str = f" ({progress})" if progress else ""
            output += f"- {status} {goal.get('description', 'No description')}{progress_str}\n"
        output += "\n"
    
    return output


def load_yaml_goals() -> dict:
    """Load goals from YAML file (simple parser for basic YAML)."""
    goals_file = DATA_DIR / "goals.yaml"
    if not goals_file.exists():
        return {}
    
    # Simple YAML-like parser for our specific format
    goals = {"short_term": [], "long_term": []}
    current_section = None
    current_goal = None
    
    with open(goals_file) as f:
        for line in f:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            
            if line == "short_term:":
                current_section = "short_term"
            elif line == "long_term:":
                current_section = "long_term"
            elif line.startswith("  - description:"):
                if current_goal and current_section:
                    goals[current_section].append(current_goal)
                current_goal = {"description": line.split(":", 1)[1].strip().strip('"')}
            elif line.startswith("    completed:"):
                if current_goal:
                    current_goal["completed"] = "true" in line.lower()
            elif line.startswith("    progress:"):
                if current_goal:
                    current_goal["progress"] = line.split(":", 1)[1].strip().strip('"')
    
    if current_goal and current_section:
        goals[current_section].append(current_goal)
    
    return goals


def main():
    # Load all data
    skills_data = load_json("skills.json")
    bosses_data = load_json("bosses.json")
    clog_data = load_json("collection_log.json")
    goals_data = load_yaml_goals()
    
    # Get last update time
    last_update = skills_data.get("updated") or "Never"
    if last_update and last_update != "Never":
        try:
            dt = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
            last_update = dt.strftime("%Y-%m-%d %H:%M UTC")
        except:
            pass
    
    # Generate README
    readme = f"""# 🎮 {RSN} - Ironman Progression Tracker

![Last Updated](https://img.shields.io/badge/Last%20Updated-{last_update.replace(" ", "%20")}-blue)
![Account Type](https://img.shields.io/badge/Account-Ironman-gray)

Automated tracking of my OSRS Ironman progress using data from [TempleOSRS](https://templeosrs.com/player/overview.php?player={RSN}) and the official hiscores.

---

## 🎯 Goals

{generate_goals_section(goals_data)}

---

## 📊 Skills

{generate_skills_table(skills_data)}

---

## ⚔️ Boss Kills

{generate_bosses_table(bosses_data)}

---

## 📚 Collection Log

{generate_collection_log_section(clog_data)}

---

## 🔗 Links

- [TempleOSRS Profile](https://templeosrs.com/player/overview.php?player={RSN})
- [Official Hiscores](https://secure.runescape.com/m=hiscore_oldschool_ironman/hiscorepersonal?user1={RSN})

---

<sub>Last automated update: {last_update}</sub>
<sub>Data sourced from TempleOSRS API and official OSRS Hiscores</sub>
"""
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(readme)
    
    print(f"Generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
