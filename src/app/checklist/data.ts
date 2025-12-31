export interface ChecklistItem {
  id: string;
  name: string;
  source: string;
  rate: string;
  type: 'Skill' | 'Item' | 'Total Level' | 'Quest';
  category: 'Early Game' | 'Mid Game' | 'Late Game' | 'End Game';
}

export const MASTER_CHECKLIST: ChecklistItem[] = [
  // --- AUTO-GENERATED TOTAL LEVELS ---
  ...Array.from({ length: 22 }, (_, i) => ({
    id: `total_${(i + 1) * 100}`,
    name: `Total Level ${(i + 1) * 100}`,
    source: 'Account Progress',
    rate: 'N/A',
    type: 'Total Level' as const,
    category: (i + 1) * 100 < 1000 ? 'Early Game' : (i + 1) * 100 < 1700 ? 'Mid Game' : 'Late Game' as any
  })),
  { id: 'total_max', name: 'Max Total 2277', source: 'The Ultimate Grind', rate: 'N/A', type: 'Total Level', category: 'End Game' },

  // --- 99 SKILLS ---
  { id: '99_atk', name: '99 Attack', source: 'Combat', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_str', name: '99 Strength', source: 'Combat', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_def', name: '99 Defence', source: 'Combat', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_hp', name: '99 Hitpoints', source: 'Combat', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_rng', name: '99 Ranged', source: 'Combat', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_mag', name: '99 Magic', source: 'Combat', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_pra', name: '99 Prayer', source: 'Gilded Altar', rate: '13M XP', type: 'Skill', category: 'End Game' },
  { id: '99_rc', name: '99 Runecraft', source: 'GOTR', rate: '13M XP', type: 'Skill', category: 'End Game' },
  { id: '99_con', name: '99 Construction', source: 'Mahogany Homes', rate: '13M XP', type: 'Skill', category: 'End Game' },
  { id: '99_agi', name: '99 Agility', source: 'Rooftops', rate: '13M XP', type: 'Skill', category: 'End Game' },
  { id: '99_herb', name: '99 Herblore', source: 'Potions', rate: '13M XP', type: 'Skill', category: 'End Game' },
  { id: '99_thie', name: '99 Thieving', source: 'Ardy Knights', rate: '13M XP', type: 'Skill', category: 'Mid Game' },
  { id: '99_craft', name: '99 Crafting', source: 'Glassblowing', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_flet', name: '99 Fletching', source: 'Darts', rate: '13M XP', type: 'Skill', category: 'Mid Game' },
  { id: '99_slay', name: '99 Slayer', source: 'Slayer Masters', rate: '13M XP', type: 'Skill', category: 'End Game' },
  { id: '99_hunt', name: '99 Hunter', source: 'Chins', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_min', name: '99 Mining', source: 'MLM', rate: '13M XP', type: 'Skill', category: 'End Game' },
  { id: '99_smith', name: '99 Smithing', source: 'Blast Furnace', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_fish', name: '99 Fishing', source: 'Barb Fishing', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_cook', name: '99 Cooking', source: 'Wines', rate: '13M XP', type: 'Skill', category: 'Early Game' },
  { id: '99_fm', name: '99 Firemaking', source: 'Wintertodt', rate: '13M XP', type: 'Skill', category: 'Early Game' },
  { id: '99_wc', name: '99 Woodcutting', source: 'Redwoods', rate: '13M XP', type: 'Skill', category: 'Late Game' },
  { id: '99_farm', name: '99 Farming', source: 'Tree Runs', rate: '13M XP', type: 'Skill', category: 'Mid Game' },

  // --- LADLOR CHART MILESTONES ---
  { id: 'b_gloves', name: 'Barrows Gloves', source: 'Quest: RFD', rate: 'Guaranteed', type: 'Quest', category: 'Early Game' },
  { id: 'd_scim', name: 'Dragon Scimitar', source: 'Quest: MM1', rate: 'Guaranteed', type: 'Item', category: 'Early Game' },
  { id: 'f_torso', name: 'Fighter Torso', source: 'Barbarian Assault', rate: 'Guaranteed', type: 'Item', category: 'Early Game' },
  { id: 'd_def', name: 'Dragon Defender', source: 'Warriors Guild', rate: '1/100', type: 'Item', category: 'Early Game' },
  { id: 'fcape', name: 'Fire Cape', source: 'Fight Caves', rate: '1/1', type: 'Item', category: 'Early Game' },
  { id: 'trident', name: 'Trident (Seas)', source: 'Kraken', rate: '1/200', type: 'Item', category: 'Mid Game' },
  { id: 'blowpipe', name: 'Toxic Blowpipe', source: 'Zulrah', rate: '1/1024', type: 'Item', category: 'Late Game' },
  { id: 'bowfa', name: 'Bow of Faerdhinen', source: 'Corrupted Gauntlet', rate: '1/400', type: 'Item', category: 'Late Game' },
  { id: 'dwh', name: 'Dragon Warhammer', source: 'Lizardman Shamans', rate: '1/3000', type: 'Item', category: 'Late Game' },
  { id: 'fang', name: 'Osmumten\'s Fang', source: 'ToA', rate: '1/3.4 Purp', type: 'Item', category: 'Late Game' },
  { id: 'tbow', name: 'Twisted Bow', source: 'CoX', rate: '1/1000', type: 'Item', category: 'End Game' },
  { id: 'scythe', name: 'Scythe of Vitur', source: 'ToB', rate: '1/175', type: 'Item', category: 'End Game' },
  { id: 'shadow', name: 'Tumeken\'s Shadow', source: 'ToA', rate: '1/24 Purp', type: 'Item', category: 'End Game' },
  { id: 'infernal', name: 'Infernal Cape', source: 'Inferno', rate: '1/1', type: 'Item', category: 'End Game' },
];