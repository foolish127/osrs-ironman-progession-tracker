
        let currentGearStyle = 'melee';

        function switchGearStyle(style) {
            currentGearStyle = style;
            document.querySelectorAll('#gearing .gear-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('#gearing .gear-tab[data-style="' + style + '"]').forEach(t => t.classList.add('active'));
            ['gpane-melee','gpane-ranged','gpane-magic'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.classList.toggle('active', id === 'gpane-' + style);
            });
            ['gupg-melee','gupg-ranged','gupg-magic'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.classList.toggle('active', id === 'gupg-' + style);
            });
            if (typeof currentAccount !== 'undefined' && currentAccount && currentAccount.id === 'gim') renderGimGearing(style);
        }

        // GIM gear progression targets, by combat style and game stage. Shown on the
        // Gearing tab only for the GIM account (which has no live gear); the Ironman
        // keeps its own static gear tables in #gear-im.
        const GIM_GEAR = {
            melee: {
                slots: ['Head','Cape','Neck','Weapon','Shield','Body','Legs','Hands','Feet','Ring'],
                low:  { Head:'Helm of neitiznot', Cape:'Obsidian cape', Neck:'Amulet of glory', Weapon:'Dragon scimitar', Shield:'Rune defender', Body:'Rune platebody / Fighter torso', Legs:'Rune platelegs', Hands:'Combat bracelet', Feet:'Dragon boots', Ring:'Warrior ring (i)' },
                mid:  { Head:'Serpentine helm', Cape:'Fire cape', Neck:'Amulet of fury', Weapon:'Abyssal whip / tentacle', Shield:'Dragon defender', Body:'Fighter torso', Legs:'Obsidian platelegs', Hands:'Barrows gloves', Feet:'Dragon boots', Ring:'Berserker ring (i)' },
                end:  { Head:'Neitiznot faceguard', Cape:'Infernal cape', Neck:'Amulet of torture', Weapon:'Ghrazi rapier', Shield:'Avernic defender', Body:'Bandos chestplate', Legs:'Bandos tassets', Hands:'Ferocious gloves', Feet:'Primordial boots', Ring:'Ultor ring' },
                late: { Head:'Torva full helm', Cape:'Infernal cape', Neck:'Amulet of rancour', Weapon:'Scythe of vitur', Shield:'Avernic defender', Body:'Torva platebody', Legs:'Torva platelegs', Hands:'Ferocious gloves', Feet:'Primordial boots', Ring:'Ultor ring' },
            },
            ranged: {
                slots: ['Head','Cape','Neck','Weapon','Ammo','Body','Legs','Hands','Feet','Ring'],
                low:  { Head:'Archer helm', Cape:"Ava's accumulator", Neck:'Amulet of glory', Weapon:'Magic shortbow (i)', Ammo:'Rune / amethyst arrows', Body:"Black d'hide body", Legs:"Black d'hide chaps", Hands:"Black d'hide vambraces", Feet:'Snakeskin boots', Ring:'Archers ring (i)' },
                mid:  { Head:"Karil's coif", Cape:"Ava's assembler", Neck:'Amulet of fury', Weapon:'Toxic blowpipe / Rune crossbow', Ammo:'Dragon darts / ruby+diamond bolts (e)', Body:'Armadyl chestplate', Legs:'Armadyl chainskirt', Hands:'Barrows gloves', Feet:'Ranger boots', Ring:'Archers ring (i)' },
                end:  { Head:'Armadyl helmet', Cape:"Ava's assembler", Neck:'Necklace of anguish', Weapon:'Toxic blowpipe + Zaryte crossbow', Ammo:'Dragon darts / dragon bolts (e)', Body:'Armadyl chestplate', Legs:'Armadyl chainskirt', Hands:'Zaryte vambraces', Feet:'Pegasian boots', Ring:'Venator ring' },
                late: { Head:'Masori mask (f)', Cape:"Dizana's quiver", Neck:'Necklace of anguish', Weapon:'Twisted bow', Ammo:'Dragon arrows', Body:'Masori body (f)', Legs:'Masori chaps (f)', Hands:'Zaryte vambraces', Feet:'Pegasian boots', Ring:'Venator ring' },
            },
            magic: {
                slots: ['Head','Cape','Neck','Weapon','Shield','Body','Legs','Hands','Feet','Ring'],
                low:  { Head:'Farseer helm / Mystic hat', Cape:'God cape', Neck:'Amulet of magic', Weapon:'Trident of the seas', Shield:'Unholy book', Body:'Mystic robe top', Legs:'Mystic robe bottom', Hands:'Combat bracelet', Feet:'Infinity boots', Ring:'Seers ring (i)' },
                mid:  { Head:"Ahrim's hood", Cape:'Imbued god cape', Neck:'Occult necklace', Weapon:'Trident of the swamp', Shield:"Mage's book / Tome of fire", Body:"Ahrim's robetop", Legs:"Ahrim's robeskirt", Hands:'Barrows gloves', Feet:'Eternal boots', Ring:'Seers ring (i)' },
                end:  { Head:'Ancestral hat', Cape:'Imbued god cape', Neck:'Occult necklace', Weapon:'Sanguinesti staff', Shield:"Elidinis' ward", Body:'Ancestral robe top', Legs:'Ancestral robe bottom', Hands:'Tormented bracelet', Feet:'Eternal boots', Ring:'Magus ring' },
                late: { Head:'Ancestral hat', Cape:'Imbued god cape', Neck:'Occult necklace', Weapon:"Tumeken's shadow", Shield:"Elidinis' ward (f)", Body:'Ancestral robe top', Legs:'Ancestral robe bottom', Hands:'Tormented bracelet', Feet:'Eternal boots', Ring:'Magus ring' },
            },
        };

        function renderGimGearing(style) {
            currentGearStyle = style || currentGearStyle;
            const host = document.getElementById('gear-gim');
            if (!host) return;
            const g = GIM_GEAR[currentGearStyle];
            if (!g) { host.innerHTML = ''; return; }
            const stages = [['low','Low level'],['mid','Midgame'],['end','Endgame'],['late','Late game']];
            const esc = (typeof escapeTargets === 'function') ? escapeTargets : (s => s);
            const rows = g.slots.map(slot => {
                const cells = stages.map(([k]) => {
                    const v = g[k] && g[k][slot];
                    return `<td>${v ? esc(v) : '<span class="gdash">-</span>'}</td>`;
                }).join('');
                return `<tr><td>${slot}</td>${cells}</tr>`;
            }).join('');
            const label = currentGearStyle.charAt(0).toUpperCase() + currentGearStyle.slice(1);
            host.innerHTML = `
                <div class="gear-section-label">Gear progression targets - ${label}</div>
                <div class="gear-table-wrap">
                <table class="gear-table">
                <thead><tr><th>Slot</th>${stages.map(([,l]) => `<th>${l}</th>`).join('')}</tr></thead>
                <tbody>${rows}</tbody>
                </table>
                </div>`;
        }

        function applyGearAccountView() {
            const im = document.getElementById('gear-im');
            const gim = document.getElementById('gear-gim');
            const isGim = (typeof currentAccount !== 'undefined' && currentAccount && currentAccount.id === 'gim');
            if (im) im.style.display = isGim ? 'none' : '';
            if (gim) gim.style.display = isGim ? '' : 'none';
            if (isGim) renderGimGearing(currentGearStyle);
        }

        // Bank data is intentionally kept private: bank.json is never published
        // to the live site, so the Bank tab only has data when index.html is
        // opened locally alongside the data/ folder.

        const SKILL_ORDER = ['Attack','Hitpoints','Mining','Strength','Agility','Smithing','Defence','Herblore','Fishing','Ranged','Thieving','Cooking','Prayer','Crafting','Firemaking','Magic','Fletching','Woodcutting','Runecraft','Slayer','Farming','Construction','Hunter','Sailing'];
        const SKILL_ICONS = {};
        SKILL_ORDER.forEach(s => SKILL_ICONS[s] = `https://oldschool.runescape.wiki/images/${s}_icon.png`);

        function formatNumber(n) {
            if (n >= 1e9) return (n/1e9).toFixed(1) + 'B';
            if (n >= 1e6) return (n/1e6).toFixed(1) + 'M';
            if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
            return n.toLocaleString();
        }

        function formatDate(iso) {
            if (!iso) return '—';
            // TempleOSRS uses "YYYY-MM-DD HH:MM:SS"; normalize the space to 'T' so
            // browsers don't return Invalid Date.
            const d = new Date(String(iso).replace(' ', 'T'));
            if (isNaN(d)) return String(iso);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
        }

        function formatShortDate(dateStr) {
            if (!dateStr) return '';
            // Take just the date part (drop any " HH:MM:SS" from TempleOSRS timestamps).
            const [year, month, day] = String(dateStr).split(' ')[0].split('-').map(Number);
            if (!year || !month || !day) return String(dateStr);
            const d = new Date(year, month - 1, day);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        }

        // Accounts you can switch between (each has its own data folder).
        const ACCOUNTS = [
            { id: 'main', label: 'FoolinSlays', dir: './data', type: 'Ironman', badge: 'https://oldschool.runescape.wiki/images/Ironman_chat_badge.png' },
            { id: 'gim', label: 'GIM Foolin', dir: './data/gim', type: 'Group Ironman', badge: 'https://oldschool.runescape.wiki/images/Group_ironman_chat_badge.png' },
        ];
        let currentAccount = ACCOUNTS.find(a => a.id === localStorage.getItem('account')) || ACCOUNTS[0];

        let clogData = null;
        let caData = null;
        let petsData = null;
        let cluesData = null;
        let questsData = null;
        let diariesData = null;
        let skillsData = null;
        let bossesData = null;
        let clogCategories = null;
        let diaryTasksData = null;
        let wikiCompData = null;
        let wikiCATableData = null;
        let milestonesData = null;

        // Collection-log data comes from data/collection_log.json, which CI builds
        // from the TempleOSRS API (server-side, every 6h + on push) and merges with
        // manually-entered dates from collection_log.yaml. Calling Temple directly
        // from the browser was removed: it is blocked by CORS, and when it did run
        // it discarded the manual dates.

        async function loadData() {
            const D = currentAccount.dir;  // account-specific data folder

            // Reset per-account state first, so switching to an account that is
            // missing a data file shows "—"/empty rather than the prior account's values.
            clogData = caData = petsData = cluesData = questsData = diariesData = null;
            skillsData = bossesData = milestonesData = clogCategories = null;
            diaryTasksData = null;
            dropsData = [];
            ['totalLevel', 'totalXp', 'combatLevel', 'count99s', 'clogCount', 'caTasks',
             'petCount', 'clueCount', 'bossKcCard', 'questCount', 'diaryCount']
                .forEach(id => { const el = document.getElementById(id); if (el) el.textContent = '—'; });
            const [skillsRes, bossesRes, cluesRes, clogRes, caRes, petsRes, questsRes, diariesRes, dropsRes, clogCatRes, diaryTasksRes] = await Promise.all([
                fetch(`${D}/skills.json`).then(r=>r.json()).catch(()=>null),
                fetch(`${D}/bosses.json`).then(r=>r.json()).catch(()=>null),
                fetch(`${D}/clues.json`).then(r=>r.json()).catch(()=>null),
                fetch(`${D}/collection_log.json`).then(r=>r.json()).catch(()=>null),
                fetch(`${D}/combat_achievements.json`).then(r=>r.json()).catch(()=>null),
                fetch(`${D}/pets.json`).then(r=>r.json()).catch(()=>null),
                fetch(`${D}/quests.json`).then(r=>r.json()).catch(()=>null),
                fetch(`${D}/diaries.yaml`).then(r=>r.text()).catch(()=>null),
                fetch(`${D}/drops.yaml`).then(r=>r.text()).catch(()=>null),
                fetch(`${D}/clog_categories.yaml`).then(r=>r.ok?r.text():null).catch(()=>null),
                fetch(`${D}/diary_tasks.yaml`).then(r=>r.ok?r.text():null).catch(()=>null)
            ]);
            diaryTasksData = parseDiaryTasks(diaryTasksRes);

            if (clogCatRes) {
                clogCategories = clogCatRes.split('\n')
                    .map(l => l.trim())
                    .filter(l => l && !l.startsWith('#') && l.includes(':'))
                    .map(l => {
                        const [name, val] = l.split(':');
                        const [obt, tot] = (val || '').split('/').map(n => parseInt(n.trim(), 10) || 0);
                        return { name: name.trim(), obtained: obt, total: tot };
                    });
            }

            if (skillsRes?.rsn) {
                document.getElementById('playerName').textContent = skillsRes.rsn;
                document.getElementById('lastUpdated').textContent = formatDate(skillsRes.updated);
            }

            if (skillsRes?.milestones) {
                const m = skillsRes.milestones;
                milestonesData = m;
                document.getElementById('totalLevel').textContent = m.total_level?.toLocaleString() || '—';
                document.getElementById('totalXp').textContent = formatNumber(m.total_xp || 0);
                document.getElementById('combatLevel').textContent = m.combat_level || '—';
                document.getElementById('count99s').textContent = `${m.skills_99||0}/${m.num_skills||24}`;
            }

            if (clogRes?.collection_log) {
                clogData = clogRes.collection_log;
                clogData.rsn = clogRes.rsn || 'FoolinSlays';
                clogData.collections = mergeClogCollections(clogData.collections);
                document.getElementById('clogCount').textContent = `${clogData.total_obtained}/${clogData.total_items}`;
            }

            if (caRes?.combat_achievements) {
                caData = caRes.combat_achievements;
                document.getElementById('caTasks').textContent = `${caData.total_completed}/${caData.total_tasks}`;
            }

            if (petsRes?.pets) {
                petsData = petsRes.pets;
                document.getElementById('petCount').textContent = `${petsData.total_obtained}/${petsData.total_pets}`;
            }

            if (cluesRes?.clues) {
                cluesData = cluesRes.clues;
                const allClues = cluesData['Clue Scrolls (all)'];
                const totalClues = allClues ? allClues.count : 0;
                document.getElementById('clueCount').textContent = totalClues.toLocaleString();
            }

            if (questsRes?.quests) {
                questsData = questsRes.quests;
                document.getElementById('questCount').textContent = `${questsData.total_completed}/${questsData.total_quests}`;
            }

            if (skillsRes?.skills) {
                skillsData = skillsRes.skills;
                renderSkills(skillsRes.skills);
            }
            if (bossesRes?.bosses) {
                bossesData = bossesRes.bosses;
                renderBosses(bossesRes.bosses);
            }
            renderClues();
            renderCollectionLog();
            renderCombatAchievements();
            renderPets();
            renderQuests();
            renderDiaries(diariesRes);
            renderDrops(dropsRes);
            // Targets reference data (wiki_comp_rates/wiki_ca_table) is loaded
            // lazily on first Targets-tab open — see ensureTargetsData().
            renderTargets();
            renderProgress();
            applyGearAccountView();
        }

        // Year-month key ("2026-06") from an ISO or M/D/YYYY date string.
        function ymKey(s) {
            if (!s) return null;
            s = String(s).trim();
            let m = s.match(/^(\d{4})-(\d{1,2})/);
            if (m) return `${m[1]}-${String(+m[2]).padStart(2, '0')}`;
            m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
            if (m) return `${m[3]}-${String(+m[1]).padStart(2, '0')}`;
            return null;
        }

        function renderProgress() {
            const container = document.getElementById('progressContainer');
            if (!container) return;

            const TIER_PTS = { Easy: 1, Medium: 2, Hard: 3, Elite: 4, Master: 5, Grandmaster: 6 };
            const clog = {}, ca = {}, caPts = {}, drop = {};

            if (clogData?.collections) {
                for (const coll of Object.values(clogData.collections)) {
                    for (const it of (coll.obtained || [])) {
                        const k = ymKey(it.date);
                        if (k) clog[k] = (clog[k] || 0) + 1;
                    }
                }
            }
            if (caData?.tiers) {
                for (const [tier, t] of Object.entries(caData.tiers)) {
                    for (const task of (t.completed || [])) {
                        const k = ymKey(task.date);
                        if (k) { ca[k] = (ca[k] || 0) + 1; caPts[k] = (caPts[k] || 0) + (TIER_PTS[tier] || 1); }
                    }
                }
            }
            for (const d of (dropsData || [])) {
                const k = ymKey(d.date);
                if (k) drop[k] = (drop[k] || 0) + 1;
            }

            const months = [...new Set([...Object.keys(clog), ...Object.keys(ca), ...Object.keys(drop)])].sort();
            if (months.length === 0) {
                container.innerHTML = '<div class="empty-state">No dated progress data yet.</div>';
                return;
            }

            const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            const label = k => { const [y, m] = k.split('-'); return `${MON[+m - 1]} ${y}`; };
            const maxClog = Math.max(1, ...months.map(m => clog[m] || 0));
            const maxCa = Math.max(1, ...months.map(m => ca[m] || 0));
            const maxDrop = Math.max(1, ...months.map(m => drop[m] || 0));
            const sum = o => Object.values(o).reduce((a, b) => a + b, 0);

            const bar = (val, max, cls) =>
                `<div class="prog-track"><div class="prog-fill ${cls}" style="width:${(val / max) * 100}%"></div></div><span class="prog-num">${val}</span>`;

            let html = `
                <div class="prog-summary">
                    <div class="summary-item"><div class="summary-value" style="color:#3fb950">${sum(clog)}</div><div class="summary-label">Clog slots</div></div>
                    <div class="summary-item"><div class="summary-value" style="color:#58a6ff">${sum(ca)}</div><div class="summary-label">CAs (${sum(caPts)} pts)</div></div>
                    <div class="summary-item"><div class="summary-value" style="color:var(--accent-gold)">${sum(drop)}</div><div class="summary-label">Notable drops</div></div>
                    <div class="summary-item"><div class="summary-value">${months.length}</div><div class="summary-label">Months tracked</div></div>
                </div>
                <div class="prog-legend">
                    <span><span class="prog-dot clog"></span>Collection log</span>
                    <span><span class="prog-dot ca"></span>Combat achievements</span>
                    <span><span class="prog-dot drop"></span>Notable drops</span>
                </div>`;

            html += months.map(m => `
                <div class="prog-row">
                    <div class="prog-month">${label(m)}</div>
                    <div class="prog-bars">
                        <div class="prog-line">${bar(clog[m] || 0, maxClog, 'clog')}</div>
                        <div class="prog-line">${bar(ca[m] || 0, maxCa, 'ca')}</div>
                        <div class="prog-line">${bar(drop[m] || 0, maxDrop, 'drop')}</div>
                    </div>
                </div>`).join('');

            container.innerHTML = html;
        }

        function renderSkills(skills) {
            const grid = document.getElementById('skillsGrid');
            grid.innerHTML = SKILL_ORDER.map(name => {
                const s = skills[name] || { level: 1, xp: 0 };
                const isMaxed = s.level >= 99;
                const prog = s.progress?.progress || 0;
                const progClass = prog < 33 ? 'low' : prog < 66 ? 'mid' : 'high';
                return `<div class="skill-item ${isMaxed ? 'maxed' : ''}">
                    <img src="${SKILL_ICONS[name]}" alt="${name}" class="skill-icon">
                    <div class="skill-info">
                        <div class="skill-name">${name}</div>
                        <div class="skill-level ${isMaxed ? 'maxed' : ''}">${s.level}</div>
                        <div class="skill-xp">${formatNumber(s.xp)} XP</div>
                        ${!isMaxed ? `<div class="skill-progress"><div class="skill-progress-fill ${progClass}" style="width:${prog}%"></div></div>` : ''}
                    </div>
                </div>`;
            }).join('');

            // XP bar chart beneath the grid: every skill, highest XP first.
            const chart = document.getElementById('skillXpChart');
            if (chart) {
                const sorted = SKILL_ORDER
                    .map(name => ({ name, xp: skills[name]?.xp || 0, level: skills[name]?.level || 1 }))
                    .sort((a, b) => b.xp - a.xp);
                const maxXp = sorted[0]?.xp || 1;
                // Colour each bar by level on a red->yellow->green scale,
                // normalised across the account's own min/max levels.
                const levels = sorted.map(s => s.level);
                const minLvl = Math.min(...levels), maxLvl = Math.max(...levels);
                const hue = lvl => (maxLvl > minLvl ? (lvl - minLvl) / (maxLvl - minLvl) : 1) * 120;
                chart.innerHTML = '<h3>📈 Experience by Skill</h3>' + sorted.map(s => `
                    <div class="skill-bar">
                        <img src="${SKILL_ICONS[s.name]}" alt="${s.name}" class="skill-bar-icon">
                        <span class="skill-bar-name">${s.name}</span>
                        <div class="skill-bar-track"><div class="skill-bar-fill" style="width:${(s.xp / maxXp) * 100}%;background:hsl(${hue(s.level)},65%,45%)"></div></div>
                        <span class="skill-bar-xp">${formatNumber(s.xp)}</span>
                    </div>`).join('');
            }
        }

        function renderBosses(bosses) {
            const sorted = Object.entries(bosses).filter(([_,d])=>d.kc>0).sort((a,b)=>b[1].kc-a[1].kc);
            
            // Calculate total KC for stat card
            const totalKc = sorted.reduce((sum, [_, d]) => sum + d.kc, 0);
            const formatKc = (kc) => {
                if (kc >= 1000000) return (kc / 1000000).toFixed(1) + 'M';
                if (kc >= 1000) return (kc / 1000).toFixed(1) + 'K';
                return kc.toLocaleString();
            };
            document.getElementById('bossKcCard').textContent = formatKc(totalKc);
            
            // Render bar chart (top 15 bosses)
            const maxKc = sorted.length > 0 ? sorted[0][1].kc : 1;
            const top15 = sorted.slice(0, 15);
            const barChartContainer = document.getElementById('bossBarChart');
            barChartContainer.innerHTML = `
                <h3>📊 Top Kill Counts</h3>
                ${top15.map(([name, data]) => {
                    const percentage = (data.kc / maxKc) * 100;
                    return `
                        <div class="boss-bar">
                            <span class="boss-bar-name" title="${name}">${name}</span>
                            <div class="boss-bar-track">
                                <div class="boss-bar-fill" style="width: ${percentage}%"></div>
                            </div>
                            <span class="boss-bar-kc">${data.kc.toLocaleString()}</span>
                        </div>
                    `;
                }).join('')}
            `;
            
            document.getElementById('bossGrid').innerHTML = sorted.map(([n,d])=>
                `<div class="boss-item"><span class="boss-name">${n}</span><span class="boss-kc">${d.kc.toLocaleString()} KC</span></div>`
            ).join('');
        }

        function renderClues() {
            const grid = document.getElementById('cluesGrid');
            if (!cluesData) {
                grid.innerHTML = '<div class="empty-state">Clue scroll data not available</div>';
                return;
            }

            const BASE = 'https://oldschool.runescape.wiki/images/';
            const tiers = [
                { key: 'Clue Scrolls (all)',      tier: 'all',      icon: BASE + 'Reward_casket_(hard)_detail.png',     label: 'All Caskets' },
                { key: 'Clue Scrolls (beginner)', tier: 'beginner', icon: BASE + 'Reward_casket_(beginner)_detail.png', label: 'Beginner' },
                { key: 'Clue Scrolls (easy)',     tier: 'easy',     icon: BASE + 'Reward_casket_(easy)_detail.png',     label: 'Easy' },
                { key: 'Clue Scrolls (medium)',   tier: 'medium',   icon: BASE + 'Reward_casket_(medium)_detail.png',   label: 'Medium' },
                { key: 'Clue Scrolls (hard)',     tier: 'hard',     icon: BASE + 'Reward_casket_(hard)_detail.png',     label: 'Hard' },
                { key: 'Clue Scrolls (elite)',    tier: 'elite',    icon: BASE + 'Reward_casket_(elite)_detail.png',    label: 'Elite' },
                { key: 'Clue Scrolls (master)',   tier: 'master',   icon: BASE + 'Reward_casket_(master)_detail.png',   label: 'Master' },
            ];

            const allCount = cluesData['Clue Scrolls (all)']?.count || 0;

            grid.innerHTML = tiers.map(({ key, tier, icon, label }) => {
                const count = cluesData[key]?.count || 0;
                const pct = allCount > 0 ? Math.min(100, (count / allCount) * 100) : 0;
                return `
                <div class="clue-card ${tier}">
                    <div class="clue-header">
                        <img class="clue-icon" src="${icon}" alt="${label}" onerror="this.style.display='none'">
                        <span class="clue-label">${label}</span>
                        <span class="clue-count">${count.toLocaleString()}</span>
                    </div>
                    <div class="clue-bar-track">
                        <div class="clue-bar-fill" style="width:${tier === 'all' ? 100 : pct}%"></div>
                    </div>
                </div>`;
            }).join('');
        }

        function mergeClogCollections(collections) {
            // TempleOSRS splits multi-tag items into their own categories
            // (e.g. "Abyssal Sire, All Pets", "Abyssal Sire, Slayer"). Group each
            // under its first tag so a boss's pet/slayer items share one collapsible.
            const merged = {};
            for (const [name, coll] of Object.entries(collections || {})) {
                const primary = name.split(',')[0].trim();
                const m = merged[primary] || (merged[primary] = { obtained: [], missing: [], _o: new Set(), _m: new Set() });
                for (const it of (coll.obtained || [])) {
                    const k = (it.name || '').toLowerCase();
                    if (!m._o.has(k)) { m._o.add(k); m.obtained.push(it); }
                }
                for (const it of (coll.missing || [])) {
                    const k = (typeof it === 'string' ? it : it.name || '').toLowerCase();
                    if (!m._m.has(k)) { m._m.add(k); m.missing.push(it); }
                }
            }
            for (const m of Object.values(merged)) {
                m.obtained_count = m.obtained.length;
                m.total_count = m.obtained_count + m.missing.length;
                delete m._o; delete m._m;
            }
            return merged;
        }

        function renderCollectionLog(searchTerm = '', statusFilter = 'all') {
            const container = document.getElementById('clogContainer');
            if (!clogData) {
                container.innerHTML = '<div class="empty-state">Collection log data not available</div>';
                return;
            }

            // Define category mappings (matching in-game categories)
            const categoryMappings = {
                'Bosses': [
                    'Abyssal Sire', 'Alchemical Hydra', 'Araxxor', 'Barrows', 'Bryophyta',
                    'Callisto', 'Cerberus', 'Chaos Elemental', 'Chaos Fanatic', 'Commander Zilyana',
                    'Corporeal Beast', 'Crazy Archaeologist', 'Dagannoth', 'Duke Sucellus',
                    'General Graardor', 'Giant Mole', 'Grotesque Guardians', 'Hespori', 'Kalphite Queen',
                    'King Black Dragon', 'Kraken', 'Kree', 'K\'ril', 'Lunar Chests',
                    'Nex', 'Nightmare', 'Obor', 'Phantom Muspah', 'Sarachnis', 'Scorpia', 'Scurrius',
                    'Skotizo', 'Sol Heredit', 'Spindel', 'Hueycoatl', 'Leviathan', 'Whisperer',
                    'Thermonuclear', 'Smoke Devil', 'Vardorvis', 'Venenatis', 'Vet\'ion', 'Vorkath',
                    'Zulrah', 'Amoxliatl', 'Artio', 'Calvar', 'Tormented Demons', 'Perilous Moons', 'Yama',
                    'Gauntlet', 'Inferno', 'Fight Caves', 'Colosseum', 'Fortis'
                ],
                'Raids': [
                    'Chambers of Xeric', 'Theatre of Blood', 'Tombs of Amascut'
                ],
                'Clues': [
                    'Treasure Trails', 'Beginner Clue', 'Easy Clue', 'Medium Clue',
                    'Hard Clue', 'Elite Clue', 'Master Clue', 'Shared Clue', 'Shared Treasure'
                ],
                'Minigames': [
                    'Barbarian Assault', 'Brimhaven Agility', 'Castle Wars', 'Fishing Trawler',
                    'Gnome Restaurant', 'Guardians of the Rift', 'Hallowed Sepulchre', 'Last Man Standing',
                    'Magic Training Arena', 'Mahogany Homes', 'Pest Control', 'Rogues',
                    'Shades of Mort', 'Soul Wars', 'Tempoross', 'Tithe Farm', 'Trouble Brewing',
                    'Volcanic Mine', 'Wintertodt', 'Giants\' Foundry', 'Zalcano', 'Mage Arena'
                ],
                'Other': [] // Everything else goes here
            };

            // Calculate category totals
            // Fallback when data/<account>/clog_categories.yaml isn't present:
            // count obtained from the clog data, but use the game-wide category
            // totals (they're the same for every account) so the bars are meaningful.
            function getCategoryStats() {
                const stats = {
                    'Bosses': { obtained: 0, total: 333, icon: '⚔️' },
                    'Raids': { obtained: 0, total: 67, icon: '🏛️' },
                    'Clues': { obtained: 0, total: 611, icon: '📜' },
                    'Minigames': { obtained: 0, total: 257, icon: '🎮' },
                    'Other': { obtained: 0, total: 433, icon: '📦' }
                };

                for (const [collName, coll] of Object.entries(clogData.collections)) {
                    let matched = false;
                    const collNameLower = collName.toLowerCase();

                    // Check each category (except Other which is the default)
                    for (const [catName, patterns] of Object.entries(categoryMappings)) {
                        if (catName === 'Other') continue; // Skip Other, it's the default

                        // Check if collection name contains any pattern
                        const matchesPattern = patterns.some(p => collNameLower.includes(p.toLowerCase()));
                        if (matchesPattern) {
                            stats[catName].obtained += coll.obtained_count || 0;
                            matched = true;
                            break;
                        }
                    }
                    // Default to Other if no match
                    if (!matched) {
                        stats['Other'].obtained += coll.obtained_count || 0;
                    }
                }
                return stats;
            }

            // Prefer the exact in-game counts from data/clog_categories.yaml;
            // fall back to the pattern-matched estimate when it isn't present.
            const CAT_ICONS = { Bosses: '⚔️', Raids: '🏛️', Clues: '📜', Minigames: '🎮', Other: '📦' };
            const categoryStats = clogCategories?.length
                ? Object.fromEntries(clogCategories.map(c => [c.name, { obtained: c.obtained, total: c.total, icon: CAT_ICONS[c.name] || '📦' }]))
                : getCategoryStats();
            const pct = ((clogData.total_obtained / clogData.total_items) * 100).toFixed(1);
            
            // Helper to get wiki image URL
            function getItemImageUrl(itemName) {
                // Use wiki's standard image naming convention
                const formatted = encodeURIComponent(itemName.replace(/ /g, '_'));
                return `https://oldschool.runescape.wiki/images/${formatted}.png`;
            }
            
            // Build overview HTML
            let html = `
                <div class="clog-overview">
                    <div class="clog-overview-title">Collection Log – Overview for ${clogData.rsn || 'FoolinSlays'}</div>
                    <div class="clog-categories">
                        ${Object.entries(categoryStats).map(([name, stats]) => {
                            const catPct = stats.total > 0 ? (stats.obtained / stats.total * 100) : 0;
                            return `
                            <div class="clog-category">
                                <div class="clog-category-icon">${stats.icon}</div>
                                <div class="clog-category-name">${name}</div>
                                <div class="clog-category-count"><span class="obtained">${stats.obtained}</span>/${stats.total}</div>
                                <div class="clog-category-bar"><div class="clog-category-bar-fill" style="width:${catPct}%"></div></div>
                            </div>`;
                        }).join('')}
                    </div>
                    <div class="clog-total">
                        <div class="clog-total-bar">
                            <div class="clog-total-bar-fill" style="width:${pct}%"></div>
                            <div class="clog-total-text">Collections Logged: ${clogData.total_obtained}/${clogData.total_items}</div>
                        </div>
                    </div>
                    ${clogData.recent_items?.length > 0 ? `
                    <div class="clog-latest">
                        <div class="clog-latest-title">Latest Collections</div>
                        <div class="clog-latest-items">
                            ${clogData.recent_items.slice(0, 12).map(item => {
                                const safeChar = item.name.charAt(0).replace(/'/g, '');
                                const dateLabel = formatShortDate(item.date);
                                const tip = `${item.name}${dateLabel ? ' · ' + dateLabel : ''}`.replace(/"/g, '&quot;');
                                return `
                                <div class="clog-latest-item" data-tooltip="${tip}">
                                    <img src="${getItemImageUrl(item.name)}" alt="${item.name.replace(/"/g, '&quot;')}" onerror="this.style.display='none'; this.parentElement.innerHTML='${safeChar}';">
                                </div>`;
                            }).join('')}
                        </div>
                    </div>` : ''}
                </div>`;

            // Progress section
            html += `
                <div class="progress-section">
                    <div class="progress-header">
                        <span class="progress-title">Collection Log Progress</span>
                        <span class="progress-stats"><span class="obtained">${clogData.total_obtained}</span> <span class="total">/ ${clogData.total_items}</span></span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
                    <div class="progress-percentage">${pct}%</div>
                </div>`;
            
            html += `<div class="search-filter">
                    <input type="text" class="search-input" id="clogSearch" placeholder="Search items or collections..." value="${searchTerm}">
                    <select class="filter-select" id="clogFilter">
                        <option value="all" ${statusFilter==='all'?'selected':''}>All Items</option>
                        <option value="obtained" ${statusFilter==='obtained'?'selected':''}>Obtained Only</option>
                        <option value="missing" ${statusFilter==='missing'?'selected':''}>Missing Only</option>
                    </select>
                </div>
                <div id="clogList"></div>`;
            
            container.innerHTML = html;
            
            document.getElementById('clogSearch').addEventListener('input', e => renderClogList(e.target.value, document.getElementById('clogFilter').value));
            document.getElementById('clogFilter').addEventListener('change', e => renderClogList(document.getElementById('clogSearch').value, e.target.value));
            
            renderClogList(searchTerm, statusFilter);
        }

        function renderClogList(searchTerm, statusFilter) {
            const list = document.getElementById('clogList');
            const search = searchTerm.toLowerCase();
            let html = '';

            for (const [collName, coll] of Object.entries(clogData.collections).sort((a,b) => a[0].localeCompare(b[0]))) {
                let obtained = coll.obtained || [];
                let missing = coll.missing || [];
                
                if (search) {
                    if (!collName.toLowerCase().includes(search)) {
                        obtained = obtained.filter(i => (i.name || i).toLowerCase().includes(search));
                        missing = missing.filter(i => (i.name || i).toLowerCase().includes(search));
                    }
                }
                
                let items = [];
                if (statusFilter === 'all' || statusFilter === 'obtained') {
                    items = items.concat(obtained.map(i => ({ name: i.name || i, date: i.date, obtained: true })));
                }
                if (statusFilter === 'all' || statusFilter === 'missing') {
                    items = items.concat(missing.map(i => ({ name: i.name || i, obtained: false })));
                }
                
                if (items.length === 0) continue;
                
                html += `<div class="collection">
                    <div class="collection-header" onclick="this.parentElement.classList.toggle('expanded')">
                        <span class="collection-name">${escapeTargets(collName)}</span>
                        <span class="collection-count"><span class="obtained">${coll.obtained_count}</span> <span class="total">/ ${coll.total_count}</span></span>
                    </div>
                    <div class="collection-items">
                        <div class="item-list">
                            ${items.map(i => `<div class="item ${i.obtained ? 'obtained' : 'missing'}">
                                <span class="item-check">${i.obtained ? '✓' : '○'}</span>
                                <span class="item-name">${escapeTargets(i.name)}</span>
                                ${i.date ? `<span class="item-date">${formatShortDate(i.date)}</span>` : ''}
                            </div>`).join('')}
                        </div>
                    </div>
                </div>`;
            }
            
            list.innerHTML = html || '<div class="empty-state">No items match your search</div>';
        }

        function renderCombatAchievements(searchTerm = '', statusFilter = 'all') {
            const container = document.getElementById('caContainer');
            if (!caData) {
                container.innerHTML = '<div class="empty-state">Combat achievements data not available</div>';
                return;
            }

            const pct = ((caData.total_points / caData.max_points) * 100).toFixed(1);
            const tierColors = { Easy: '#3fb950', Medium: '#58a6ff', Hard: '#a371f7', Elite: '#d4a84b', Master: '#f85149', Grandmaster: '#ff7b72' };
            
            // CA tier unlock thresholds (from OSRS Wiki - updated)
            const tierUnlocks = [
                { name: 'Easy', points: 38, rewards: ['Ghommal\'s hilt 1', '5% easy clue boost', '+5 boss task kills'] },
                { name: 'Medium', points: 148, rewards: ['Ghommal\'s hilt 2', '5% medium clue boost', '+10 boss task kills'] },
                { name: 'Hard', points: 394, rewards: ['Ghommal\'s hilt 3', 'Unlimited GWD teles', 'GWD private instances'] },
                { name: 'Elite', points: 1038, rewards: ['Ghommal\'s hilt 4', '5% elite clue boost', 'Cannon holds 60'] },
                { name: 'Master', points: 1878, rewards: ['Ghommal\'s hilt 5', 'Red slayer helmet'] },
                { name: 'Grandmaster', points: 2618, rewards: ['Ghommal\'s hilt 6', 'Green slayer helmet'] }
            ];
            
            // Find current and next tier
            let currentTier = null;
            let nextTier = null;
            for (let i = 0; i < tierUnlocks.length; i++) {
                if (caData.total_points >= tierUnlocks[i].points) {
                    currentTier = tierUnlocks[i];
                } else {
                    nextTier = tierUnlocks[i];
                    break;
                }
            }
            
            // Official CA points pulled live from the hiscores (auto-updated every run)
            const officialCaPoints = milestonesData?.ca_points;
            const officialCaRank = milestonesData?.ca_rank;

            let html = '';
            if (officialCaPoints != null) {
                html += `
                <div class="progress-section" style="border-color: var(--accent-blue);">
                    <div class="progress-header">
                        <span class="progress-title">⚔️ CA Points <span style="color:var(--text-muted);font-weight:normal;font-size:0.75rem;">live from hiscores</span></span>
                        <span class="progress-stats"><span class="obtained" style="color:var(--accent-blue);">${officialCaPoints.toLocaleString()}</span>${officialCaRank > 0 ? ` <span class="total">· rank #${officialCaRank.toLocaleString()}</span>` : ''}</span>
                    </div>
                </div>`;
            }

            html += `
                <div class="progress-section">
                    <div class="progress-header">
                        <span class="progress-title">Overall Progress <span style="color:var(--text-muted);font-weight:normal;font-size:0.75rem;">from your task list</span></span>
                        <span class="progress-stats"><span class="obtained">${caData.total_points}</span> <span class="total">/ ${caData.max_points} points</span></span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
                    <div class="progress-percentage">${pct}% · ${caData.total_completed}/${caData.total_tasks} tasks</div>
                </div>`;
            
            // Tier unlock progress
            if (nextTier) {
                const prevPoints = currentTier ? currentTier.points : 0;
                const pointsInTier = caData.total_points - prevPoints;
                const pointsNeeded = nextTier.points - prevPoints;
                const tierPct = ((pointsInTier / pointsNeeded) * 100).toFixed(1);
                const pointsRemaining = nextTier.points - caData.total_points;
                
                html += `
                <div class="progress-section" style="margin-top: 1rem;">
                    <div class="progress-header">
                        <span class="progress-title">Next Unlock: <span style="color:${tierColors[nextTier.name]}">${nextTier.name} Tier</span></span>
                        <span class="progress-stats"><span class="obtained">${caData.total_points}</span> <span class="total">/ ${nextTier.points} points</span></span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${tierPct}%;background:${tierColors[nextTier.name]}"></div></div>
                    <div class="progress-percentage">${pointsRemaining} points to go</div>
                    <div class="tier-rewards">
                        <span class="rewards-label">Unlocks:</span> ${nextTier.rewards.join(' · ')}
                    </div>
                </div>`;
            } else {
                html += `
                <div class="progress-section" style="margin-top: 1rem; border-color: var(--accent-gold);">
                    <div class="progress-header">
                        <span class="progress-title" style="color: var(--accent-gold);">🏆 Grandmaster Tier Unlocked!</span>
                    </div>
                    <div class="tier-rewards">All Combat Achievement rewards unlocked</div>
                </div>`;
            }
            
            // Tier overview
            html += `
                <div class="tier-overview">
                    <div class="tier-overview-title">Tier Unlocks</div>
                    <div class="tier-overview-grid">
                        ${tierUnlocks.map(tier => {
                            const unlocked = caData.total_points >= tier.points;
                            return `<div class="tier-badge ${unlocked ? 'unlocked' : ''}" style="border-color:${tierColors[tier.name]}">
                                <span class="tier-badge-name" style="color:${unlocked ? tierColors[tier.name] : 'var(--text-muted)'}">${tier.name}</span>
                                <span class="tier-badge-points">${tier.points} pts</span>
                                ${unlocked ? '<span class="tier-badge-check">✓</span>' : ''}
                            </div>`;
                        }).join('')}
                    </div>
                </div>`;
            
            // Recent activity
            if (caData.recent_tasks?.length > 0) {
                html += `<div class="recent-activity">
                    <div class="recent-title">🏆 Recent Completions</div>
                    <div class="recent-list">
                        ${caData.recent_tasks.slice(0, 5).map(task => `
                            <div class="recent-item">
                                <div><span class="recent-item-name">${escapeTargets(task.name)}</span> <span class="recent-item-source">${escapeTargets(task.tier)}</span></div>
                                <span class="recent-item-date">${formatShortDate(task.date)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>`;
            }
            
            html += `<div class="search-filter">
                <input type="text" class="search-input" id="caSearch" placeholder="Search tasks..." value="${searchTerm}">
                <select class="filter-select" id="caFilter">
                    <option value="all" ${statusFilter==='all'?'selected':''}>All Tasks</option>
                    <option value="completed" ${statusFilter==='completed'?'selected':''}>Completed Only</option>
                    <option value="not_completed" ${statusFilter==='not_completed'?'selected':''}>Remaining Only</option>
                </select>
            </div>`;
            
            const search = searchTerm.toLowerCase();
            
            for (const [tierName, tier] of Object.entries(caData.tiers)) {
                let completed = tier.completed || [];
                let notCompleted = tier.not_completed || [];
                
                if (search) {
                    completed = completed.filter(t => (t.name || t).toLowerCase().includes(search));
                    notCompleted = notCompleted.filter(t => (t.name || t).toLowerCase().includes(search));
                }
                
                let tasks = [];
                if (statusFilter === 'all' || statusFilter === 'completed') {
                    tasks = tasks.concat(completed.map(t => ({ name: t.name || t, date: t.date, done: true })));
                }
                if (statusFilter === 'all' || statusFilter === 'not_completed') {
                    tasks = tasks.concat(notCompleted.map(t => ({ name: t.name || t, done: false })));
                }
                
                if (tasks.length === 0 && search) continue;
                
                const tierPct = tier.total_count > 0 ? ((tier.completed_count / tier.total_count) * 100) : 0;
                const color = tierColors[tierName] || '#888';
                
                html += `<div class="ca-tier">
                    <div class="ca-tier-header" onclick="this.parentElement.classList.toggle('expanded')">
                        <span class="ca-tier-name ${tierName.toLowerCase()}">${tierName} (${tier.points_per_task} pt${tier.points_per_task > 1 ? 's' : ''})</span>
                        <div class="ca-tier-stats">
                            <span><span style="color:${color}">${tier.completed_count}</span> / ${tier.total_count}</span>
                            <div class="ca-tier-progress"><div class="ca-tier-progress-fill" style="width:${tierPct}%;background:${color}"></div></div>
                        </div>
                    </div>
                    <div class="ca-tier-tasks">
                        <div class="item-list">
                            ${tasks.map(t => `<div class="item ${t.done ? 'obtained' : 'missing'}">
                                <span class="item-check">${t.done ? '✓' : '○'}</span>
                                <span class="item-name">${escapeTargets(t.name)}</span>
                                ${t.date ? `<span class="item-date">${formatShortDate(t.date)}</span>` : ''}
                            </div>`).join('')}
                        </div>
                    </div>
                </div>`;
            }
            
            container.innerHTML = html;
            
            document.getElementById('caSearch').addEventListener('input', e => renderCombatAchievements(e.target.value, document.getElementById('caFilter').value));
            document.getElementById('caFilter').addEventListener('change', e => renderCombatAchievements(document.getElementById('caSearch').value, e.target.value));
        }

        // ── Leagues task tracker ──────────────────────────────────────────
        const LEAGUE_TIERS = ['easy', 'medium', 'hard', 'elite', 'master'];
        const LEAGUE_TIER_POINTS = { easy: 10, medium: 30, hard: 80, elite: 200, master: 400 };
        function renderPets() {
            const container = document.getElementById('petsContainer');
            if (!petsData) {
                container.innerHTML = '<div class="empty-state">Pets data not available</div>';
                return;
            }

            const pct = ((petsData.total_obtained / petsData.total_pets) * 100).toFixed(1);
            
            let html = `
                <div class="progress-section">
                    <div class="progress-header">
                        <span class="progress-title">🐾 Pet Collection</span>
                        <span class="progress-stats"><span class="obtained">${petsData.total_obtained}</span> <span class="total">/ ${petsData.total_pets}</span></span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
                    <div class="progress-percentage">${pct}%</div>
                </div>
                <div class="search-filter">
                    <input type="text" class="search-input" id="petSearch" placeholder="Search pets...">
                    <select class="filter-select" id="petFilter">
                        <option value="all">All Pets</option>
                        <option value="obtained">Obtained Only</option>
                        <option value="missing">Missing Only</option>
                    </select>
                    <select class="filter-select" id="petSort">
                        <option value="newest">Newest First</option>
                        <option value="oldest">Oldest First</option>
                        <option value="alpha">A → Z</option>
                    </select>
                </div>
                <div class="pets-grid" id="petsGrid"></div>`;
            
            container.innerHTML = html;
            
            document.getElementById('petSearch').addEventListener('input', renderPetGrid);
            document.getElementById('petFilter').addEventListener('change', renderPetGrid);
            document.getElementById('petSort').addEventListener('change', renderPetGrid);
            
            renderPetGrid();
        }

        function renderPetGrid() {
            const grid = document.getElementById('petsGrid');
            const search = document.getElementById('petSearch').value.toLowerCase();
            const filter = document.getElementById('petFilter').value;
            const sort = document.getElementById('petSort').value;
            
            let pets = [];
            
            if (filter === 'all' || filter === 'obtained') {
                pets = pets.concat((petsData.obtained || []).map(p => ({
                    name: p.name || p,
                    date: p.date,
                    source: p.source,
                    notes: p.notes,
                    obtained: true
                })));
            }
            
            if (filter === 'all' || filter === 'missing') {
                pets = pets.concat((petsData.missing || []).map(p => ({
                    name: p.name || p,
                    source: p.source,
                    obtained: false
                })));
            }
            
            if (search) {
                pets = pets.filter(p => 
                    p.name.toLowerCase().includes(search) || 
                    (p.source && p.source.toLowerCase().includes(search)) ||
                    (p.notes && p.notes.toLowerCase().includes(search))
                );
            }
            
            // Sort: obtained always first, then by selected sort within each group
            pets.sort((a, b) => {
                if (a.obtained !== b.obtained) return b.obtained - a.obtained;
                if (sort === 'oldest') {
                    if (!a.date && !b.date) return a.name.localeCompare(b.name);
                    if (!a.date) return 1;
                    if (!b.date) return -1;
                    return a.date.localeCompare(b.date);
                } else if (sort === 'newest') {
                    if (!a.date && !b.date) return a.name.localeCompare(b.name);
                    if (!a.date) return 1;
                    if (!b.date) return -1;
                    return b.date.localeCompare(a.date);
                } else {
                    return a.name.localeCompare(b.name);
                }
            });
            
            grid.innerHTML = pets.map(p => `
                <div class="pet-card ${p.obtained ? 'obtained' : 'missing'}">
                    ${p.notes ? `<div class="pet-tooltip">${escapeTargets(p.notes)}</div>` : ''}
                    <div class="pet-name">${escapeTargets(p.name)}</div>
                    ${p.source ? `<div class="pet-source">${escapeTargets(p.source)}</div>` : ''}
                    ${p.date ? `<div class="pet-date">${formatShortDate(p.date)}</div>` : ''}
                </div>
            `).join('') || '<div class="empty-state">No pets match your search</div>';
        }

        function renderQuests() {
            const container = document.getElementById('questsContainer');
            if (!questsData) {
                container.innerHTML = '<div class="empty-state">Quest data not available</div>';
                return;
            }

            const pct = ((questsData.total_completed / questsData.total_quests) * 100).toFixed(1);
            const mqPct = questsData.total_miniquests
                ? ((questsData.miniquests_completed / questsData.total_miniquests) * 100).toFixed(1)
                : '0.0';

            let html = `
                <div class="progress-section">
                    <div class="progress-header">
                        <span class="progress-title">📜 Quest Progress</span>
                        <span class="progress-stats"><span class="obtained">${questsData.total_completed}</span> <span class="total">/ ${questsData.total_quests}</span></span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
                    <div class="progress-percentage">${pct}%</div>
                </div>
                <div class="progress-section">
                    <div class="progress-header">
                        <span class="progress-title">📖 Miniquests</span>
                        <span class="progress-stats"><span class="obtained">${questsData.miniquests_completed}</span> <span class="total">/ ${questsData.total_miniquests}</span></span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${mqPct}%"></div></div>
                    <div class="progress-percentage">${mqPct}%</div>
                </div>
                <div class="search-filter">
                    <input type="text" class="search-input" id="questSearch" placeholder="Search quests...">
                    <select class="filter-select" id="questFilter">
                        <option value="all">All Quests</option>
                        <option value="completed">Completed</option>
                        <option value="incomplete">Not Completed</option>
                        <option value="f2p">Free-to-play</option>
                        <option value="members">Members</option>
                        <option value="miniquests">Miniquests</option>
                    </select>
                </div>
                <div id="questsList"></div>`;
            
            container.innerHTML = html;
            
            document.getElementById('questSearch').addEventListener('input', renderQuestList);
            document.getElementById('questFilter').addEventListener('change', renderQuestList);
            
            renderQuestList();
        }

        function renderQuestList() {
            const list = document.getElementById('questsList');
            const search = document.getElementById('questSearch').value.toLowerCase();
            const filter = document.getElementById('questFilter').value;
            
            const categories = ['Free-to-play', 'Members', 'Miniquests'];
            let html = '';
            
            categories.forEach(cat => {
                const catData = questsData.categories[cat];
                if (!catData) return;
                
                // Filter by category
                if (filter === 'f2p' && cat !== 'Free-to-play') return;
                if (filter === 'members' && cat !== 'Members') return;
                if (filter === 'miniquests' && cat !== 'Miniquests') return;
                
                let quests = [];
                
                if (filter === 'all' || filter === 'completed' || filter === 'f2p' || filter === 'members' || filter === 'miniquests') {
                    quests = quests.concat((catData.completed || []).map(q => {
                        const item = typeof q === 'string' ? {name: q} : q;
                        return {...item, completed: true};
                    }));
                }
                if (filter === 'all' || filter === 'incomplete' || filter === 'f2p' || filter === 'members' || filter === 'miniquests') {
                    quests = quests.concat((catData.not_completed || []).map(q => {
                        const item = typeof q === 'string' ? {name: q} : q;
                        return {...item, completed: false};
                    }));
                }
                
                // Filter by search
                if (search) {
                    quests = quests.filter(q => q.name.toLowerCase().includes(search));
                }
                
                if (quests.length === 0) return;
                
                // Sort: completed first (by date), then incomplete
                quests.sort((a, b) => {
                    if (a.completed !== b.completed) return b.completed - a.completed;
                    if (a.completed && b.completed && a.date && b.date) return a.date.localeCompare(b.date);
                    return a.name.localeCompare(b.name);
                });
                
                const completedCount = quests.filter(q => q.completed).length;
                
                html += `
                    <div class="collection">
                        <div class="collection-header" onclick="this.parentElement.classList.toggle('expanded')">
                            <span class="collection-name">${cat}</span>
                            <span class="collection-count"><span class="obtained">${completedCount}</span> <span class="total">/ ${catData.completed.length + catData.not_completed.length}</span></span>
                        </div>
                        <div class="collection-items">
                            <div class="item-list">
                                ${quests.map(q => `
                                    <div class="item ${q.completed ? 'obtained' : 'missing'}">
                                        <span class="item-check">${q.completed ? '✓' : '○'}</span>
                                        <span class="item-name">${escapeTargets(q.name)}</span>
                                        ${q.date ? `<span class="item-date">${formatShortDate(q.date)}</span>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>`;
            });
            
            list.innerHTML = html || '<div class="empty-state">No quests match your search</div>';
        }

        // Parse data/<account>/diary_tasks.yaml -> { region: { tier: [tasks] } }.
        function parseDiaryTasks(yaml) {
            if (!yaml) return null;
            const out = {};
            let region = null, tier = null;
            for (const raw of yaml.split('\n')) {
                const s = raw.trim();
                if (!s || s.startsWith('#')) continue;
                const indent = raw.length - raw.trimStart().length;
                if (indent === 0 && s.endsWith(':')) { region = s.slice(0, -1); out[region] = {}; tier = null; }
                else if (indent === 2 && s.endsWith(':') && region) { tier = s.slice(0, -1).toLowerCase(); out[region][tier] = []; }
                else if (s.startsWith('- ') && region && tier) { out[region][tier].push(s.slice(2).trim()); }
            }
            return out;
        }

        function getRemainingTasksHtml() {
            if (!diaryTasksData || !Object.keys(diaryTasksData).length) {
                return '<div class="empty-state">No remaining diary tasks listed.</div>';
            }
            return Object.entries(diaryTasksData).map(([region, tiers]) => {
                const items = [];
                for (const tier of ['easy', 'medium', 'hard', 'elite']) {
                    for (const task of (tiers[tier] || [])) items.push({ tier, task });
                }
                if (!items.length) return '';
                return `
                <div class="task-region">
                    <div class="task-region-header">
                        <span>${region}</span>
                        <span class="task-count">${items.length} task${items.length > 1 ? 's' : ''}</span>
                    </div>
                    <div class="task-items">
                        ${items.map(item => `
                            <div class="task-item">
                                <span>${escapeTargets(item.task)}</span>
                                <span class="task-tier ${item.tier}">${item.tier}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>`;
            }).join('');
        }

        function renderDiaries(yaml) {
            const container = document.getElementById('diariesContainer');
            if (!yaml) {
                container.innerHTML = '<div class="empty-state">No diary data yet.</div>';
                document.getElementById('diaryCount').textContent = '—';
                return;
            }
            const regions = {};
            let currentRegion = null;
            
            // Parse tasks_completed and tasks_total from header
            let tasksCompleted = 0;
            let tasksTotal = 492;
            
            // Parse YAML
            yaml.split('\n').forEach(line => {
                if (!line || line.startsWith('#')) return;
                
                // Check for tasks_completed/tasks_total
                if (line.startsWith('tasks_completed:')) {
                    tasksCompleted = parseInt(line.split(':')[1].trim()) || 0;
                    return;
                }
                if (line.startsWith('tasks_total:')) {
                    tasksTotal = parseInt(line.split(':')[1].trim()) || 492;
                    return;
                }
                
                // Region line (no leading spaces, ends with :)
                if (!line.startsWith(' ') && line.endsWith(':')) {
                    currentRegion = line.slice(0, -1);
                    regions[currentRegion] = { easy: null, medium: null, hard: null, elite: null };
                }
                // Tier line (has leading spaces)
                else if (currentRegion && line.trim().includes(':')) {
                    const [tier, value] = line.trim().split(':').map(s => s.trim());
                    if (['easy', 'medium', 'hard', 'elite'].includes(tier)) {
                        regions[currentRegion][tier] = value || null;
                    }
                }
            });
            
            // Calculate tier stats
            const tiers = ['easy', 'medium', 'hard', 'elite'];
            let tiersCompleted = 0;
            let tiersTotal = 0;
            const tierCounts = { easy: 0, medium: 0, hard: 0, elite: 0 };
            
            Object.values(regions).forEach(region => {
                tiers.forEach(tier => {
                    tiersTotal++;
                    if (region[tier]) {
                        tiersCompleted++;
                        tierCounts[tier]++;
                    }
                });
            });
            
            // Derive task completion from the per-account remaining list, so the count
            // lives in one place (delete a task from diary_tasks.yaml -> count goes up).
            if (diaryTasksData) {
                const remaining = Object.values(diaryTasksData)
                    .reduce((sum, t) => sum + Object.values(t).reduce((a, arr) => a + arr.length, 0), 0);
                tasksTotal = 492;
                tasksCompleted = tasksTotal - remaining;
            }

            const regionCount = Object.keys(regions).length;
            const taskPct = ((tasksCompleted / tasksTotal) * 100).toFixed(1);
            
            // Render
            container.innerHTML = `
                <div class="diaries-summary">
                    <div class="summary-item">
                        <div class="summary-value" style="color: var(--accent-gold)">${tasksCompleted}/${tasksTotal}</div>
                        <div class="summary-label">Tasks (${taskPct}%)</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" style="color: var(--accent-green)">${tiersCompleted}/${tiersTotal}</div>
                        <div class="summary-label">Tiers Complete</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" style="color: #22c55e">${tierCounts.easy}/${regionCount}</div>
                        <div class="summary-label">Easy</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" style="color: #eab308">${tierCounts.medium}/${regionCount}</div>
                        <div class="summary-label">Medium</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" style="color: #f97316">${tierCounts.hard}/${regionCount}</div>
                        <div class="summary-label">Hard</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value" style="color: #06b6d4">${tierCounts.elite}/${regionCount}</div>
                        <div class="summary-label">Elite</div>
                    </div>
                </div>
                
                <div class="progress-section" style="margin-bottom: 1.5rem;">
                    <div class="progress-header">
                        <span class="progress-title">Overall Task Progress</span>
                        <div class="progress-stats"><span class="obtained">${tasksCompleted}</span><span class="total">/${tasksTotal}</span></div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${taskPct}%"></div>
                    </div>
                    <div class="progress-percentage">${taskPct}% complete · ${tasksTotal - tasksCompleted} tasks remaining</div>
                </div>
                
                <div class="diaries-grid">
                    ${Object.entries(regions).map(([name, tiers]) => {
                        const completed = Object.values(tiers).filter(v => v).length;
                        return `
                            <div class="diary-card">
                                <div class="diary-header">
                                    <span>${name}</span>
                                    <span class="diary-count">${completed}/4</span>
                                </div>
                                <div class="diary-tiers">
                                    ${['easy', 'medium', 'hard', 'elite'].map(tier => `
                                        <div class="diary-tier ${tier} ${tiers[tier] ? 'completed' : ''}">
                                            <div class="tier-name">${tier}</div>
                                            <div class="tier-status">${tiers[tier] ? '✓' : '○'}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                
                <div class="remaining-tasks" id="remainingTasks">
                    <div class="remaining-tasks-header" onclick="document.getElementById('remainingTasks').classList.toggle('expanded')">
                        <h3>📋 Remaining Diary Tasks</h3>
                        <span class="toggle">▼</span>
                    </div>
                    <div class="remaining-tasks-list">
                        ${getRemainingTasksHtml()}
                    </div>
                </div>
            `;
            
            // Store for stat card - now shows tasks, not tiers
            diariesData = { completed: tasksCompleted, total: tasksTotal };
            document.getElementById('diaryCount').textContent = `${tasksCompleted}/${tasksTotal}`;
        }

        // Drops Tab
        let dropsData = [];
        let dropsSearchTerm = '';
        let dropsBossFilter = 'all';
        let luckSummaryData = [];

        const getLuckClass = (luck) => {
            if (luck === 0) return 'luck-pending';
            if (luck >= 2) return 'luck-very-spooned';
            if (luck >= 1.2) return 'luck-spooned';
            if (luck >= 0.8) return 'luck-onrate';
            if (luck >= 0.5) return 'luck-dry';
            return 'luck-very-dry';
        };

        const getStatusClass = (status) => {
            if (status === 'Spooned') return 'status-spooned';
            if (status === 'Dry') return 'status-dry';
            if (status === 'In Progress') return 'status-pending';
            return 'status-onrate';
        };
        let pendingDrops = [];

        function parseDropsYaml(yaml) {
            const drops = [];
            const lines = yaml.split('\n');
            let currentDrop = null;
            
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed.startsWith('- boss:')) {
                    if (currentDrop) drops.push(currentDrop);
                    currentDrop = { boss: trimmed.replace('- boss:', '').trim() };
                } else if (currentDrop && trimmed.startsWith('kc:')) {
                    currentDrop.kc = parseInt(trimmed.replace('kc:', '').trim()) || 0;
                } else if (currentDrop && trimmed.startsWith('item:')) {
                    currentDrop.item = trimmed.replace('item:', '').trim();
                } else if (currentDrop && trimmed.startsWith('date:')) {
                    currentDrop.date = trimmed.replace('date:', '').trim() || '';
                } else if (currentDrop && trimmed.startsWith('droprate:')) {
                    currentDrop.droprate = parseInt(trimmed.replace('droprate:', '').trim()) || 0;
                } else if (currentDrop && trimmed.startsWith('notes:')) {
                    currentDrop.notes = trimmed.replace('notes:', '').trim() || '';
                }
            }
            if (currentDrop) drops.push(currentDrop);
            return drops;
        }

        // An item still needs logging if it isn't in drops.yaml AND hasn't been
        // manually dated in collection_log.yaml. Manual dates are date-only
        // ("2026-06-09"); TempleOSRS auto-dates carry a time ("... 15:49:41"), so
        // a ":" in the date means it's still just a raw Temple obtain = unlogged.
        function isUnloggedRecent(it, logged) {
            return it.name
                && !logged.has(it.name.toLowerCase())
                && String(it.date || '').includes(':');
        }

        // Recently obtained collection-log items not yet logged anywhere.
        // Self-clears once you add them to drops.yaml or date them in collection_log.yaml.
        function buildDropsToLogBanner() {
            if (!clogData || !Array.isArray(clogData.recent_items)) return '';
            const logged = new Set(dropsData.map(d => (d.item || '').toLowerCase()));
            const todo = clogData.recent_items.filter(it => isUnloggedRecent(it, logged));
            if (!todo.length) return '';
            return `
                <div class="drops-tolog">
                    <div class="drops-tolog-header">📦 ${todo.length} recently obtained item${todo.length > 1 ? 's' : ''} not yet logged</div>
                    <div class="drops-tolog-items">
                        ${todo.map(it => `
                            <div class="drops-tolog-item">
                                <span class="drops-tolog-name">${escapeTargets(it.name)}</span>
                                <span class="drops-tolog-src">${escapeTargets((it.collection || '').replace(/_/g, ' '))}</span>
                                <span class="drops-tolog-date">${it.date ? formatShortDate(it.date) : ''}</span>
                            </div>
                        `).join('')}
                    </div>
                    <div class="drops-tolog-hint">Add the notable ones to <code>data/drops.yaml</code> with KC + droprate to track luck.</div>
                </div>`;
        }

        // Show a count badge on the Drops nav tab when items await logging.
        function updateDropsBadge() {
            const tab = document.querySelector('.nav-tab[data-tab="drops"]');
            if (!tab) return;
            const logged = new Set(dropsData.map(d => (d.item || '').toLowerCase()));
            const count = (clogData && Array.isArray(clogData.recent_items) ? clogData.recent_items : [])
                .filter(it => isUnloggedRecent(it, logged)).length;
            tab.innerHTML = 'Drops' + (count ? ` <span class="tab-badge">${count}</span>` : '');
        }

        function renderDrops(yaml) {
            const container = document.getElementById('dropsContainer');
            if (!yaml) {
                dropsData = [];
                container.innerHTML = '<div class="empty-state">No drops logged yet.</div>';
                updateDropsBadge();
                return;
            }
            dropsData = parseDropsYaml(yaml);
            const toLogBanner = buildDropsToLogBanner();
            updateDropsBadge();

            if (!dropsData.length) {
                container.innerHTML = toLogBanner +
                    '<div class="empty-state">No drops logged yet.</div>';
                return;
            }

            // Get unique bosses for filter
            const bosses = [...new Set(dropsData.map(d => d.boss))].sort();
            
            // Stats
            const totalDrops = dropsData.length;
            const uniqueBosses = bosses.length;

            // Build luck summary from drops that have droprate defined
            const dropsWithRates = dropsData.filter(d => d.droprate);
            luckSummaryData = dropsWithRates.map(drop => {
                const luck = drop.droprate / drop.kc;
                let status = 'On Rate';
                if (luck > 1.2) status = 'Spooned';
                else if (luck < 0.8) status = 'Dry';
                return {
                    activity: drop.boss,
                    drop: drop.item,
                    droprate: drop.droprate,
                    earned: drop.kc,
                    luck,
                    status,
                    notes: drop.notes || ''
                };
            }).sort((a, b) => b.luck - a.luck);

            // Calculate average luck (excluding nulls)
            const validLuck = luckSummaryData.filter(l => l.luck > 0);
            const avgLuck = validLuck.length ? (validLuck.reduce((s, l) => s + l.luck, 0) / validLuck.length) : 0;

            container.innerHTML = toLogBanner + `
                <div class="drops-summary">
                    <div class="drops-stat">
                        <div class="drops-stat-value">${totalDrops}</div>
                        <div class="drops-stat-label">Total Drops</div>
                    </div>
                    <div class="drops-stat">
                        <div class="drops-stat-value">${uniqueBosses}</div>
                        <div class="drops-stat-label">Sources</div>
                    </div>
                    <div class="drops-stat">
                        <div class="drops-stat-value">${avgLuck.toFixed(1)}x</div>
                        <div class="drops-stat-label">Avg Luck</div>
                    </div>
                    <div class="drops-stat">
                        <div class="drops-stat-value">${luckSummaryData.filter(l => l.status === 'Spooned').length}</div>
                        <div class="drops-stat-label">Spooned</div>
                    </div>
                    <div class="drops-stat">
                        <div class="drops-stat-value">${luckSummaryData.filter(l => l.status === 'Dry').length}</div>
                        <div class="drops-stat-label">Dry</div>
                    </div>
                </div>

                <div class="drops-filters">
                    <input type="text" class="drops-search" id="dropsSearch" placeholder="Search items or bosses..." value="${dropsSearchTerm}">
                    <select class="drops-filter-select" id="dropsBossFilter">
                        <option value="all">All Sources</option>
                        ${bosses.map(b => `<option value="${b}" ${dropsBossFilter === b ? 'selected' : ''}>${b}</option>`).join('')}
                    </select>
                </div>

                <div class="luck-table-container">
                    <h3>🍀 Luck Summary</h3>
                    <table class="luck-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Activity</th>
                                <th>Key Drop</th>
                                <th style="text-align:right">KC</th>
                                <th style="text-align:right">Rate</th>
                                <th style="text-align:right">Luck</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="luckTableBody"></tbody>
                    </table>
                </div>

                <div class="drops-count" id="dropsCount"></div>

                <div class="drops-table-container">
                    <table class="drops-table">
                        <thead>
                            <tr>
                                <th>Source</th>
                                <th style="text-align:right">KC</th>
                                <th>Item</th>
                                <th>Date</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody id="dropsTableBody"></tbody>
                    </table>
                </div>

                <div class="drops-add-section">
                    <h3>➕ Add New Drop</h3>
                    <div class="drops-add-form">
                        <input type="text" class="drops-add-input" id="newDropBoss" placeholder="Boss/Source" list="bossList">
                        <datalist id="bossList">
                            ${bosses.map(b => `<option value="${b}">`).join('')}
                        </datalist>
                        <input type="number" class="drops-add-input" id="newDropKc" placeholder="Kill Count">
                        <input type="text" class="drops-add-input" id="newDropItem" placeholder="Item Name">
                        <input type="text" class="drops-add-input" id="newDropDate" placeholder="Date (M/D/YYYY)">
                        <input type="number" class="drops-add-input" id="newDropRate" placeholder="Drop Rate (e.g. 512)">
                        <input type="text" class="drops-add-input" id="newDropNotes" placeholder="Notes (optional)">
                        <button class="drops-add-btn" id="addDropBtn">Add Drop</button>
                    </div>
                    <div class="drops-yaml-output" id="dropsYamlOutput" style="display:none;">
                        <textarea id="dropsYamlText" readonly></textarea>
                        <button class="copy-btn" id="copyYamlBtn">📋 Copy YAML</button>
                    </div>
                </div>
            `;

            // Event listeners
            document.getElementById('dropsSearch').addEventListener('input', (e) => {
                dropsSearchTerm = e.target.value;
                filterDrops();
            });

            document.getElementById('dropsBossFilter').addEventListener('change', (e) => {
                dropsBossFilter = e.target.value;
                filterDrops();
            });

            document.getElementById('addDropBtn').addEventListener('click', addNewDrop);
            document.getElementById('copyYamlBtn').addEventListener('click', () => {
                const textarea = document.getElementById('dropsYamlText');
                textarea.select();
                document.execCommand('copy');
                document.getElementById('copyYamlBtn').textContent = '✓ Copied!';
                setTimeout(() => document.getElementById('copyYamlBtn').textContent = '📋 Copy YAML', 2000);
            });

            filterDrops();
        }

        function filterDrops() {
            const tbody = document.getElementById('dropsTableBody');
            const luckTbody = document.getElementById('luckTableBody');
            const countEl = document.getElementById('dropsCount');
            const searchLower = dropsSearchTerm.toLowerCase();

            // Filter drops table
            let filtered = dropsData.filter(drop => {
                const matchesSearch = !dropsSearchTerm || 
                    drop.boss.toLowerCase().includes(searchLower) || 
                    drop.item.toLowerCase().includes(searchLower) ||
                    (drop.notes && drop.notes.toLowerCase().includes(searchLower));
                const matchesBoss = dropsBossFilter === 'all' || drop.boss === dropsBossFilter;
                return matchesSearch && matchesBoss;
            });

            // Sort by date descending (most recent first), then by KC descending
            filtered.sort((a, b) => {
                const dateA = a.date ? new Date(a.date) : new Date(0);
                const dateB = b.date ? new Date(b.date) : new Date(0);
                if (dateB - dateA !== 0) return dateB - dateA;
                return b.kc - a.kc;
            });

            countEl.textContent = `Showing ${filtered.length} of ${dropsData.length} drops`;

            tbody.innerHTML = filtered.map(drop => `
                <tr>
                    <td class="boss-col">${escapeTargets(drop.boss)}</td>
                    <td class="kc-col">${drop.kc ? drop.kc.toLocaleString() : '—'}</td>
                    <td class="item-col">${escapeTargets(drop.item)}</td>
                    <td class="date-col ${drop.date ? '' : 'missing'}">${escapeTargets(drop.date || '—')}</td>
                    <td class="notes-col">${escapeTargets(drop.notes || '')}</td>
                </tr>
            `).join('');

            // Filter luck summary table
            let filteredLuck = luckSummaryData.filter(item => {
                const matchesSearch = !dropsSearchTerm || 
                    item.activity.toLowerCase().includes(searchLower) || 
                    item.drop.toLowerCase().includes(searchLower) ||
                    (item.notes && item.notes.toLowerCase().includes(searchLower));
                const matchesBoss = dropsBossFilter === 'all' || item.activity === dropsBossFilter;
                return matchesSearch && matchesBoss;
            });

            // Sort by luck descending
            filteredLuck.sort((a, b) => b.luck - a.luck);

            luckTbody.innerHTML = filteredLuck.map((item, i) => `
                <tr>
                    <td class="rank-col">${i + 1}</td>
                    <td class="activity-col">${escapeTargets(item.activity)}</td>
                    <td class="drop-col">${escapeTargets(item.drop)}</td>
                    <td class="kc-col">${item.earned ? item.earned.toLocaleString() : '—'}</td>
                    <td class="rate-col">1/${item.droprate.toLocaleString()}</td>
                    <td class="luck-col ${getLuckClass(item.luck)}">${item.luck ? item.luck.toFixed(1) + 'x' : '—'}</td>
                    <td class="status-col ${getStatusClass(item.status)}">${item.status}</td>
                </tr>
            `).join('');
        }

        function addNewDrop() {
            const boss = document.getElementById('newDropBoss').value.trim();
            const kc = document.getElementById('newDropKc').value.trim();
            const item = document.getElementById('newDropItem').value.trim();
            const date = document.getElementById('newDropDate').value.trim();
            const droprate = document.getElementById('newDropRate').value.trim();
            const notes = document.getElementById('newDropNotes').value.trim();

            if (!boss || !kc || !item) {
                alert('Please fill in Boss, KC, and Item');
                return;
            }

            const newDrop = { boss, kc: parseInt(kc), item, date };
            if (droprate) newDrop.droprate = parseInt(droprate);
            if (notes) newDrop.notes = notes;
            pendingDrops.push(newDrop);

            // Generate YAML
            const yamlLines = pendingDrops.map(d => {
                let yaml = `
  - boss: ${d.boss}
    kc: ${d.kc}
    item: ${d.item}
    date: ${d.date}`;
                if (d.droprate) yaml += `\n    droprate: ${d.droprate}`;
                if (d.notes) yaml += `\n    notes: ${d.notes}`;
                return yaml;
            }).join('\n');

            document.getElementById('dropsYamlText').value = `# Add to data/drops.yaml:\n${yamlLines}`;
            document.getElementById('dropsYamlOutput').style.display = 'block';

            // Clear inputs
            document.getElementById('newDropBoss').value = '';
            document.getElementById('newDropKc').value = '';
            document.getElementById('newDropItem').value = '';
            document.getElementById('newDropDate').value = '';
            document.getElementById('newDropRate').value = '';

            // Add to displayed data temporarily
            dropsData.push(newDrop);
            filterDrops();
        }

        // Progression Tab
        function renderProgression(dropsYaml) {
            const container = document.getElementById('progressionContainer');
            const drops = dropsYaml ? parseDropsYaml(dropsYaml) : [];
            
            // Helper to check if we have a drop
            const hasDrop = (itemName) => drops.some(d => d.item.toLowerCase().includes(itemName.toLowerCase()));
            const hasAnyDrop = (itemNames) => itemNames.some(n => hasDrop(n));
            
            // Helper to check skill level
            const skillLevel = (name) => skillsData?.[name]?.level || 1;
            const hasSkillLevel = (name, level) => skillLevel(name) >= level;
            
            // Helper to check boss KC
            const bossKc = (name) => {
                if (!bossesData) return 0;
                const boss = Object.entries(bossesData).find(([k]) => k.toLowerCase().includes(name.toLowerCase()));
                return boss ? boss[1].kc : 0;
            };
            const hasBossKc = (name, kc) => bossKc(name) >= kc;
            
            // Helper to check quest completion
            const hasQuest = (name) => {
                if (!questsData?.categories) return false;
                const nameLower = name.toLowerCase();
                for (const cat of Object.values(questsData.categories)) {
                    if (cat.completed) {
                        const found = cat.completed.some(q => {
                            const questName = typeof q === 'string' ? q : q.name;
                            return questName.toLowerCase().includes(nameLower);
                        });
                        if (found) return true;
                    }
                }
                return false;
            };

            // Define milestones for each phase
            const phases = [
                {
                    name: 'Early Game',
                    phase: 'early',
                    icon: '🌱',
                    description: 'Building your foundation',
                    milestones: [
                        { name: 'Fire Cape', detail: 'Fight Caves', check: () => hasDrop('Fire Cape'), type: 'drop' },
                        { name: 'Barrows Gloves', detail: 'Recipe for Disaster', check: () => hasQuest('Recipe for Disaster'), type: 'quest' },
                        { name: 'Fighter Torso', detail: 'Barbarian Assault', check: () => hasDrop('Fighter Torso') || true, type: 'gear' },
                        { name: 'Dragon Defender', detail: 'Warriors Guild', check: () => hasDrop('Dragon Defender') || hasSkillLevel('Attack', 70), type: 'gear' },
                        { name: 'Iban\'s Staff', detail: 'Underground Pass', check: () => hasQuest('Underground Pass') || true, type: 'quest' },
                        { name: 'Berserker Ring', detail: 'Dagannoth Rex', check: () => hasDrop('Berserker Ring'), type: 'drop' },
                        { name: '70 Prayer', detail: 'Piety unlocked', check: () => hasSkillLevel('Prayer', 70), type: 'skill' },
                        { name: '75 Magic', detail: 'Trident access', check: () => hasSkillLevel('Magic', 75), type: 'skill' },
                        { name: 'Full Barrows Set', detail: 'Any brother', check: () => drops.filter(d => d.boss === 'Barrows').length >= 4, type: 'drop' },
                        { name: 'Quest Cape', detail: 'All quests done', check: () => questsData?.total_completed >= 158, type: 'quest' },
                    ]
                },
                {
                    name: 'Mid Game',
                    phase: 'mid',
                    icon: '⚔️',
                    description: 'Gearing up for end game',
                    milestones: [
                        { name: 'Trident of the Seas', detail: 'Kraken', check: () => hasDrop('Trident') || hasBossKc('Kraken', 50), type: 'drop' },
                        { name: 'Abyssal Whip', detail: 'Abyssal Demons', check: () => hasDrop('Abyssal Whip'), type: 'drop' },
                        { name: 'Dragon Warhammer', detail: 'Lizardman Shamans', check: () => hasDrop('Dragon Warhammer'), type: 'drop' },
                        { name: 'Zenyte Jewelry', detail: 'Demonic Gorillas', check: () => hasDrop('Zenyte'), type: 'drop' },
                        { name: 'Occult Necklace', detail: 'Smoke Devils', check: () => hasDrop('Occult') || hasSkillLevel('Slayer', 93), type: 'drop' },
                        { name: '87 Slayer', detail: 'Kraken unlocked', check: () => hasSkillLevel('Slayer', 87), type: 'skill' },
                        { name: '91 Slayer', detail: 'Cerberus unlocked', check: () => hasSkillLevel('Slayer', 91), type: 'skill' },
                        { name: 'Elite Void', detail: 'Pest Control + diaries', check: () => true, type: 'gear' },
                        { name: 'Dragon Pickaxe', detail: 'Wildy bosses', check: () => hasDrop('Dragon Pickaxe'), type: 'drop' },
                        { name: 'Imbued Heart', detail: 'Superior Slayer', check: () => hasDrop('Imbued Heart'), type: 'drop' },
                    ]
                },
                {
                    name: 'Late Game',
                    phase: 'late',
                    icon: '🔮',
                    description: 'High-level PvM unlocks',
                    milestones: [
                        { name: 'Blade of Saeldor', detail: 'Corrupted Gauntlet', check: () => hasDrop('Enhanced crystal weapon seed') || hasDrop('Blade of Saeldor'), type: 'drop' },
                        { name: 'Bowfa', detail: 'Corrupted Gauntlet', check: () => hasDrop('Enhanced crystal weapon seed'), type: 'drop' },
                        { name: 'Full Crystal Armor', detail: '6 armor seeds', check: () => drops.filter(d => d.item.includes('Crystal armour seed')).length >= 6, type: 'drop' },
                        { name: 'Primordial Boots', detail: 'Cerberus', check: () => hasDrop('Primordial crystal'), type: 'drop' },
                        { name: 'Pegasian Boots', detail: 'Cerberus', check: () => hasDrop('Pegasian crystal'), type: 'drop' },
                        { name: 'Eternal Boots', detail: 'Cerberus', check: () => hasDrop('Eternal crystal'), type: 'drop' },
                        { name: 'Infernal Cape', detail: 'The Inferno', check: () => hasDrop('Infernal Cape'), type: 'drop' },
                        { name: 'Tormented Bracelet', detail: 'Zenyte + enchant', check: () => drops.filter(d => d.item.includes('Zenyte')).length >= 2, type: 'gear' },
                        { name: 'Necklace of Anguish', detail: 'Zenyte + enchant', check: () => drops.filter(d => d.item.includes('Zenyte')).length >= 3, type: 'gear' },
                        { name: '95+ Slayer', detail: 'Hydra unlocked', check: () => hasSkillLevel('Slayer', 95), type: 'skill' },
                    ]
                },
                {
                    name: 'End Game',
                    phase: 'end',
                    icon: '👑',
                    description: 'Ultimate goals',
                    milestones: [
                        { name: 'Twisted Bow', detail: 'Chambers of Xeric', check: () => hasDrop('Twisted Bow'), type: 'drop' },
                        { name: 'Scythe of Vitur', detail: 'Theatre of Blood', check: () => hasDrop('Scythe'), type: 'drop' },
                        { name: 'Tumeken\'s Shadow', detail: 'Tombs of Amascut', check: () => hasDrop('Tumeken'), type: 'drop' },
                        { name: 'Torva Armor', detail: 'Nex', check: () => hasAnyDrop(['Torva platebody', 'Torva platelegs', 'Torva helm']), type: 'drop' },
                        { name: 'Masori Armor', detail: 'Tombs of Amascut', check: () => hasAnyDrop(['Masori body', 'Masori chaps', 'Masori mask']), type: 'drop' },
                        { name: 'Max Cape', detail: 'All 99s', check: () => skillsData && Object.values(skillsData).every(s => s.level >= 99), type: 'skill' },
                        { name: 'Grandmaster CAs', detail: 'All GM tasks', check: () => caData?.tiers?.Grandmaster?.completed === caData?.tiers?.Grandmaster?.total, type: 'achievement' },
                        { name: 'All Pets', detail: 'Gotta catch em all', check: () => petsData?.total_obtained >= 50, type: 'collection' },
                        { name: 'Completionist', detail: 'Collection log', check: () => clogData?.total_obtained >= 1400, type: 'collection' },
                        { name: 'All Hard Diaries', detail: 'Every region', check: () => true, type: 'achievement' },
                    ]
                }
            ];

            // Calculate stats
            let totalMilestones = 0;
            let completedMilestones = 0;
            phases.forEach(phase => {
                phase.milestones.forEach(m => {
                    totalMilestones++;
                    m.complete = m.check();
                    if (m.complete) completedMilestones++;
                });
                phase.completed = phase.milestones.filter(m => m.complete).length;
                phase.total = phase.milestones.length;
                phase.percent = Math.round((phase.completed / phase.total) * 100);
            });

            // Determine current phase
            let currentPhase = 'Early Game';
            if (phases[0].percent >= 80) currentPhase = 'Mid Game';
            if (phases[1].percent >= 80) currentPhase = 'Late Game';
            if (phases[2].percent >= 80) currentPhase = 'End Game';

            const overallPercent = Math.round((completedMilestones / totalMilestones) * 100);

            const getTypeIcon = (type) => {
                const icons = { drop: '💎', skill: '📊', quest: '📜', gear: '🛡️', achievement: '🏆', collection: '📚' };
                return icons[type] || '✓';
            };

            container.innerHTML = `
                <div class="progression-header">
                    <h2>Ironman Progression</h2>
                    <p>Currently in: <strong>${currentPhase}</strong></p>
                </div>

                <div class="progression-stats">
                    <div class="prog-stat">
                        <div class="prog-stat-value">${overallPercent}%</div>
                        <div class="prog-stat-label">Overall</div>
                    </div>
                    <div class="prog-stat">
                        <div class="prog-stat-value">${completedMilestones}/${totalMilestones}</div>
                        <div class="prog-stat-label">Milestones</div>
                    </div>
                    <div class="prog-stat">
                        <div class="prog-stat-value">${skillsData ? Object.entries(skillsData).filter(([k, s]) => k !== 'Overall' && s.level >= 99).length : 0}</div>
                        <div class="prog-stat-label">99s</div>
                    </div>
                    <div class="prog-stat">
                        <div class="prog-stat-value">${drops.length}</div>
                        <div class="prog-stat-label">Notable Drops</div>
                    </div>
                    <div class="prog-stat">
                        <div class="prog-stat-value">${petsData?.total_obtained || 0}</div>
                        <div class="prog-stat-label">Pets</div>
                    </div>
                </div>

                <div class="progression-phases">
                    ${phases.map(phase => `
                        <div class="phase ${phase.phase}">
                            <div class="phase-header">
                                <div class="phase-title">
                                    <span class="phase-icon">${phase.icon}</span>
                                    <span class="phase-name">${phase.name}<span>${phase.description}</span></span>
                                </div>
                                <div class="phase-progress">
                                    <div class="phase-progress-bar">
                                        <div class="phase-progress-fill" style="width: ${phase.percent}%"></div>
                                    </div>
                                    <span class="phase-progress-text">${phase.percent}%</span>
                                </div>
                            </div>
                            <div class="phase-content">
                                <div class="milestone-grid">
                                    ${phase.milestones.map(m => `
                                        <div class="milestone ${m.complete ? 'complete' : 'incomplete'}">
                                            <span class="milestone-icon">${m.complete ? '✓' : getTypeIcon(m.type)}</span>
                                            <div class="milestone-info">
                                                <div class="milestone-name">${m.name}</div>
                                                <div class="milestone-detail">${m.detail}</div>
                                            </div>
                                            <span class="milestone-status ${m.complete ? 'done' : ''}">${m.complete ? 'Done' : '—'}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // Direct tab switch
        function switchTabDirect(tabId) {
            document.querySelectorAll('.nav-tab').forEach(x => x.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
            const tab = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
            if (tab) {
                tab.classList.add('active');
                document.getElementById(tabId).classList.add('active');
            }
        }

        // ============== Targets tab ==============
        const TARGETS_TIER_ORDER = ['Easy','Medium','Hard','Elite','Master','Grandmaster'];
        let targetsState = {
            mode: 'clog',           // 'clog' | 'ca'
            clogSearch: '',
            clogSource: '',
            clogSort: 'pct-desc',   // pct-desc | pct-asc | name-asc
            clogHideNA: false,
            caSearch: '',
            caMonster: '',
            caTier: '',
            caType: '',
            caSort: 'pct-desc',     // pct-desc | pct-asc | tier-asc | name-asc
            caHideNA: false,
        };

        function buildTargetsClogRows() {
            if (!clogData || !wikiCompData?.items) return [];
            const norm = s => (s || '').toLowerCase().trim();
            const obtained = new Set();
            for (const c of Object.values(clogData.collections || {})) {
                for (const it of (c.obtained || [])) obtained.add(norm(it.name));
            }
            const seen = new Set();
            const rows = [];
            for (const it of wikiCompData.items) {
                if (obtained.has(norm(it.name))) continue;
                const key = norm(it.name) + '|' + (it.source_display || '');
                if (seen.has(key)) continue;
                seen.add(key);
                rows.push({
                    name: it.name,
                    sourceDisplay: it.source_display || (it.sources || ['Unknown']).join(', '),
                    pct: it.comp_pct,
                    wikiUrl: 'https://oldschool.runescape.wiki/w/' + encodeURIComponent(it.name.replace(/ /g, '_')),
                });
            }
            return rows;
        }

        function buildTargetsCARows() {
            // If wiki CA table data is available, use it (rich rows with monster/desc/type/comp%).
            // Otherwise fall back to caData.tiers.not_completed (just name+tier).
            const norm = s => (s || '').toLowerCase().trim();

            if (wikiCATableData?.tasks && caData?.tiers) {
                // Build set of completed task names from her caData
                const completed = new Set();
                for (const t of Object.values(caData.tiers)) {
                    for (const entry of (t.completed || [])) {
                        const name = typeof entry === 'string' ? entry : entry?.name;
                        if (name) completed.add(norm(name));
                    }
                }
                const ptsByTier = { Easy:1, Medium:2, Hard:3, Elite:4, Master:5, Grandmaster:6 };
                return wikiCATableData.tasks
                    .filter(t => !completed.has(norm(t.name)))
                    .map(t => ({
                        name: t.name,
                        monster: t.monster || 'Miscellaneous',
                        description: t.description || '',
                        type: t.type || '',
                        tier: t.tier || '',
                        points: t.points ?? ptsByTier[t.tier] ?? null,
                        pct: t.comp_pct,
                        wikiUrl: t.wiki_url || ('https://oldschool.runescape.wiki/w/' + encodeURIComponent((t.name||'').replace(/ /g,'_'))),
                    }));
            }

            // Fallback: tier-only data
            if (!caData?.tiers) return [];
            const rows = [];
            for (const tierName of TARGETS_TIER_ORDER) {
                const t = caData.tiers[tierName];
                if (!t) continue;
                const pts = t.points_per_task ?? null;
                for (const entry of (t.not_completed || [])) {
                    const name = typeof entry === 'string' ? entry : entry?.name;
                    if (!name) continue;
                    rows.push({
                        name, monster: '', description: '', type: '',
                        tier: tierName, points: pts, pct: null,
                        wikiUrl: 'https://oldschool.runescape.wiki/w/' + encodeURIComponent(name.replace(/ /g,'_')),
                    });
                }
            }
            return rows;
        }

        function fmtTargetsPct(p) {
            if (p == null) return 'N/A';
            return (p < 1 ? p.toFixed(2) : p.toFixed(1)) + '%';
        }

        function targetsPctClass(p) {
            if (p == null) return '';
            if (p >= 25) return 'targets-pct-easy';
            if (p >= 5)  return 'targets-pct-mid';
            return 'targets-pct-rare';
        }

        function escapeTargets(s) {
            return String(s ?? '').replace(/[&<>"']/g, c => (
                {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
            ));
        }

        function renderTargets() {
            const container = document.getElementById('targetsContainer');
            if (!container) return;

            // Inject once: small per-tab styles. Only first call.
            if (!document.getElementById('targets-styles')) {
                const s = document.createElement('style');
                s.id = 'targets-styles';
                s.textContent = `
                    .targets-sub { display:flex; gap:0; margin-bottom:1.25rem; border-bottom:1px solid var(--border); }
                    .targets-sub-tab { padding:0.6rem 1.1rem; font-size:0.85rem; font-weight:500; color:var(--text-secondary); background:transparent; border:0; cursor:pointer; position:relative; }
                    .targets-sub-tab:hover { color:var(--text-primary); }
                    .targets-sub-tab.active { color:var(--accent-gold); }
                    .targets-sub-tab.active::after { content:''; position:absolute; bottom:-1px; left:0; right:0; height:2px; background:var(--accent-gold); }
                    .targets-controls { display:flex; flex-wrap:wrap; gap:0.75rem; margin-bottom:1rem; align-items:center; }
                    .targets-controls .search-input { flex:1; min-width:220px; }
                    .targets-controls label { display:inline-flex; align-items:center; gap:0.4rem; color:var(--text-secondary); font-size:0.85rem; white-space:nowrap; }
                    .targets-summary { color:var(--text-secondary); font-size:0.85rem; margin-bottom:0.75rem; }
                    .targets-summary a { color:var(--accent-gold); text-decoration:none; }
                    .targets-summary a:hover { text-decoration:underline; }
                    .targets-table { width:100%; border-collapse:collapse; font-size:0.9rem; background:var(--bg-card); border:1px solid var(--border); border-radius:6px; overflow:hidden; }
                    .targets-table thead th { text-align:left; padding:0.7rem 0.9rem; font-weight:600; color:var(--text-muted); font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; border-bottom:1px solid var(--border); background:var(--bg-card); cursor:pointer; user-select:none; }
                    .targets-table thead th:hover { color:var(--text-primary); }
                    .targets-table thead th.sorted { color:var(--accent-gold); }
                    .targets-table tbody td { padding:0.55rem 0.9rem; border-bottom:1px solid var(--border); vertical-align:top; }
                    .targets-table tbody tr:last-child td { border-bottom:0; }
                    .targets-table tbody tr:hover { background:var(--bg-card-hover); }
                    .targets-table tbody td a { color:var(--accent-blue); text-decoration:none; }
                    .targets-table tbody td a:hover { text-decoration:underline; color:var(--accent-gold); }
                    .targets-src { color:var(--text-secondary); font-size:0.85rem; }
                    .targets-pct { font-family:'Fira Code', monospace; text-align:right; white-space:nowrap; font-weight:500; }
                    .targets-pct-easy { color:var(--accent-green); }
                    .targets-pct-mid  { color:var(--accent-gold); }
                    .targets-pct-rare { color:var(--accent-red); }
                    .targets-tier-pill { display:inline-block; padding:0.15rem 0.6rem; border-radius:999px; font-size:0.75rem; font-weight:600; }
                    .targets-tier-Easy        { background:rgba(63,185,80,0.15);  color:var(--accent-green); }
                    .targets-tier-Medium      { background:rgba(212,168,75,0.15); color:var(--accent-gold);  }
                    .targets-tier-Hard        { background:rgba(212,168,75,0.20); color:#e8b86a; }
                    .targets-tier-Elite       { background:rgba(248,81,73,0.15);  color:var(--accent-red);   }
                    .targets-tier-Master      { background:rgba(163,113,247,0.15);color:var(--accent-purple);}
                    .targets-tier-Grandmaster { background:rgba(88,166,255,0.15); color:var(--accent-blue);  }
                    .targets-empty { color:var(--text-secondary); padding:2rem; text-align:center; background:var(--bg-card); border:1px dashed var(--border); border-radius:6px; }
                `;
                document.head.appendChild(s);
            }

            const updatedNote = wikiCompData?.updated
                ? ` Wiki data updated ${new Date(wikiCompData.updated).toLocaleDateString()} (${(wikiCompData.item_count || wikiCompData.items?.length || 0).toLocaleString()} items).`
                : '';

            container.innerHTML = `
                <div class="targets-sub">
                    <button class="targets-sub-tab ${targetsState.mode==='clog'?'active':''}" data-mode="clog">Collection log</button>
                    <button class="targets-sub-tab ${targetsState.mode==='ca'  ?'active':''}" data-mode="ca">Combat achievements</button>
                </div>
                <div class="targets-summary">
                    Items and CAs you haven't done yet, sorted by ease.
                    Comp% = % of all WikiSync players who own the item
                    (<a href="https://oldschool.runescape.wiki/w/Collection_log/Table" target="_blank" rel="noopener">source</a>).
                    ${escapeTargets(updatedNote)}
                </div>
                <div id="targetsBody"></div>
            `;

            container.querySelectorAll('.targets-sub-tab').forEach(b => {
                b.addEventListener('click', () => {
                    targetsState.mode = b.dataset.mode;
                    renderTargets();
                });
            });

            if (targetsState.mode === 'clog') renderTargetsClog();
            else renderTargetsCA();
        }

        function renderTargetsClog() {
            const body = document.getElementById('targetsBody');
            if (!body) return;

            if (!wikiCompData?.items) {
                body.innerHTML = `<div class="targets-empty">
                    Missing <code>data/wiki_comp_rates.json</code>. Run
                    <code>scrape_wiki_comp_rates.py</code> to generate it.
                </div>`;
                return;
            }
            if (!clogData) {
                body.innerHTML = `<div class="targets-empty">Collection log data not loaded.</div>`;
                return;
            }

            const allRows = buildTargetsClogRows();

            // Source dropdown options (count desc, name asc tiebreak)
            const counts = new Map();
            for (const r of allRows) counts.set(r.sourceDisplay, (counts.get(r.sourceDisplay)||0)+1);
            const sourceOpts = [...counts.entries()]
                .sort((a,b) => b[1]-a[1] || a[0].localeCompare(b[0]))
                .map(([n,k]) => `<option value="${escapeTargets(n)}" ${targetsState.clogSource===n?'selected':''}>${escapeTargets(n)} (${k})</option>`)
                .join('');

            // Apply filters
            const q = targetsState.clogSearch.trim().toLowerCase();
            let rows = allRows.filter(r => {
                if (targetsState.clogHideNA && r.pct == null) return false;
                if (targetsState.clogSource && r.sourceDisplay !== targetsState.clogSource) return false;
                if (q && !r.name.toLowerCase().includes(q)) return false;
                return true;
            });

            // Sort
            const sortKey = targetsState.clogSort;
            rows.sort((a,b) => {
                if (sortKey === 'pct-desc' || sortKey === 'pct-asc') {
                    const dir = sortKey === 'pct-desc' ? -1 : 1;
                    const na = a.pct == null, nb = b.pct == null;
                    if (na && nb) return a.name.localeCompare(b.name);
                    if (na) return 1;
                    if (nb) return -1;
                    return (a.pct - b.pct) * dir || a.name.localeCompare(b.name);
                }
                return a.name.localeCompare(b.name);
            });

            const sortedKey =
                sortKey === 'pct-desc' || sortKey === 'pct-asc' ? 'pct'
                : 'name';
            const arrow = sortKey === 'pct-asc' ? ' ▲' : sortKey === 'pct-desc' ? ' ▼' : ' ▲';

            body.innerHTML = `
                <div class="targets-controls">
                    <input type="text" class="search-input" id="targetsClogSearch"
                           placeholder="Search item name…" value="${escapeTargets(targetsState.clogSearch)}">
                    <select class="filter-select" id="targetsClogSource">
                        <option value="">All sources</option>
                        ${sourceOpts}
                    </select>
                    <select class="filter-select" id="targetsClogSort">
                        <option value="pct-desc" ${sortKey==='pct-desc'?'selected':''}>Easiest first (Comp% desc)</option>
                        <option value="pct-asc"  ${sortKey==='pct-asc' ?'selected':''}>Rarest first (Comp% asc)</option>
                        <option value="name-asc" ${sortKey==='name-asc'?'selected':''}>Name A→Z</option>
                    </select>
                    <label>
                        <input type="checkbox" id="targetsClogHideNA" ${targetsState.clogHideNA?'checked':''}>
                        hide N/A
                    </label>
                </div>
                <div class="targets-summary">
                    ${rows.length.toLocaleString()} missing of ${allRows.length.toLocaleString()} tracked items.
                </div>
                ${rows.length === 0
                    ? `<div class="targets-empty">No matching items.</div>`
                    : `<table class="targets-table">
                        <thead><tr>
                            <th data-sort="name" class="${sortedKey==='name'?'sorted':''}">Item${sortedKey==='name'?arrow:''}</th>
                            <th data-sort="source">Source</th>
                            <th data-sort="pct" class="targets-pct ${sortedKey==='pct'?'sorted':''}">Comp%${sortedKey==='pct'?arrow:''}</th>
                        </tr></thead>
                        <tbody>
                            ${rows.map(r => `<tr>
                                <td><a href="${r.wikiUrl}" target="_blank" rel="noopener">${escapeTargets(r.name)}</a></td>
                                <td class="targets-src">${escapeTargets(r.sourceDisplay)}</td>
                                <td class="targets-pct ${targetsPctClass(r.pct)}">${fmtTargetsPct(r.pct)}</td>
                            </tr>`).join('')}
                        </tbody>
                    </table>`
                }
            `;

            document.getElementById('targetsClogSearch').addEventListener('input', e => {
                targetsState.clogSearch = e.target.value; renderTargetsClog();
            });
            document.getElementById('targetsClogSource').addEventListener('change', e => {
                targetsState.clogSource = e.target.value; renderTargetsClog();
            });
            document.getElementById('targetsClogSort').addEventListener('change', e => {
                targetsState.clogSort = e.target.value; renderTargetsClog();
            });
            document.getElementById('targetsClogHideNA').addEventListener('change', e => {
                targetsState.clogHideNA = e.target.checked; renderTargetsClog();
            });
            // Header click sort toggles
            body.querySelectorAll('.targets-table thead th').forEach(th => {
                th.addEventListener('click', () => {
                    const k = th.dataset.sort;
                    if (k === 'pct') {
                        targetsState.clogSort = targetsState.clogSort === 'pct-desc' ? 'pct-asc' : 'pct-desc';
                    } else if (k === 'name') {
                        targetsState.clogSort = 'name-asc';
                    }
                    renderTargetsClog();
                });
            });
        }

        function renderTargetsCA() {
            const body = document.getElementById('targetsBody');
            if (!body) return;

            if (!caData) {
                body.innerHTML = `<div class="targets-empty">Combat achievements data not loaded.</div>`;
                return;
            }

            const allRows = buildTargetsCARows();
            const haveWiki = !!wikiCATableData?.tasks;

            // Build dropdown options from the unfiltered set (count desc, name asc)
            const monsterCounts = new Map();
            const typeCounts = new Map();
            for (const r of allRows) {
                if (r.monster) monsterCounts.set(r.monster, (monsterCounts.get(r.monster)||0)+1);
                if (r.type)    typeCounts.set(r.type, (typeCounts.get(r.type)||0)+1);
            }
            const monsterOpts = [...monsterCounts.entries()]
                .sort((a,b) => b[1]-a[1] || a[0].localeCompare(b[0]))
                .map(([n,k]) => `<option value="${escapeTargets(n)}" ${targetsState.caMonster===n?'selected':''}>${escapeTargets(n)} (${k})</option>`)
                .join('');
            const typeOpts = [...typeCounts.entries()]
                .sort((a,b) => a[0].localeCompare(b[0]))
                .map(([n,k]) => `<option value="${escapeTargets(n)}" ${targetsState.caType===n?'selected':''}>${escapeTargets(n)} (${k})</option>`)
                .join('');

            // Apply filters
            const q = targetsState.caSearch.trim().toLowerCase();
            let rows = allRows.filter(r => {
                if (targetsState.caHideNA && r.pct == null) return false;
                if (targetsState.caMonster && r.monster !== targetsState.caMonster) return false;
                if (targetsState.caTier && r.tier !== targetsState.caTier) return false;
                if (targetsState.caType && r.type !== targetsState.caType) return false;
                if (q) {
                    const hay = [r.name, r.monster, r.description].join(' ').toLowerCase();
                    if (!hay.includes(q)) return false;
                }
                return true;
            });

            // Sort
            const sortKey = targetsState.caSort;
            rows.sort((a,b) => {
                if (sortKey === 'pct-desc' || sortKey === 'pct-asc') {
                    const dir = sortKey === 'pct-desc' ? -1 : 1;
                    const na = a.pct == null, nb = b.pct == null;
                    if (na && nb) return a.name.localeCompare(b.name);
                    if (na) return 1;
                    if (nb) return -1;
                    return (a.pct - b.pct) * dir || a.name.localeCompare(b.name);
                }
                if (sortKey === 'tier-asc') {
                    const ai = TARGETS_TIER_ORDER.indexOf(a.tier);
                    const bi = TARGETS_TIER_ORDER.indexOf(b.tier);
                    return (ai - bi) || a.name.localeCompare(b.name);
                }
                return a.name.localeCompare(b.name);
            });

            const sortArrow = sortKey === 'pct-asc' ? ' ▲' : ' ▼';
            const updatedNote = wikiCATableData?.updated
                ? ` Wiki CA data updated ${new Date(wikiCATableData.updated).toLocaleDateString()} (${wikiCATableData.task_count?.toLocaleString() || allRows.length} tasks).`
                : '';

            body.innerHTML = `
                <div class="targets-controls">
                    <input type="text" class="search-input" id="targetsCaSearch"
                           placeholder="Search task, monster, or description…" value="${escapeTargets(targetsState.caSearch)}">
                    ${haveWiki ? `<select class="filter-select" id="targetsCaMonster">
                        <option value="">All monsters</option>
                        ${monsterOpts}
                    </select>` : ''}
                    <select class="filter-select" id="targetsCaTier">
                        <option value="">All tiers</option>
                        ${TARGETS_TIER_ORDER.map(t =>
                            `<option value="${t}" ${targetsState.caTier===t?'selected':''}>${t}</option>`
                        ).join('')}
                    </select>
                    ${haveWiki ? `<select class="filter-select" id="targetsCaType">
                        <option value="">All types</option>
                        ${typeOpts}
                    </select>` : ''}
                    <select class="filter-select" id="targetsCaSort">
                        ${haveWiki ? `<option value="pct-desc" ${sortKey==='pct-desc'?'selected':''}>Easiest first (Comp% desc)</option>` : ''}
                        ${haveWiki ? `<option value="pct-asc"  ${sortKey==='pct-asc' ?'selected':''}>Rarest first (Comp% asc)</option>` : ''}
                        <option value="tier-asc"  ${sortKey==='tier-asc' ?'selected':''}>Easy → Grandmaster</option>
                        <option value="name-asc"  ${sortKey==='name-asc' ?'selected':''}>Name A→Z</option>
                    </select>
                    ${haveWiki ? `<label>
                        <input type="checkbox" id="targetsCaHideNA" ${targetsState.caHideNA?'checked':''}>
                        hide N/A
                    </label>` : ''}
                </div>
                <div class="targets-summary">
                    ${rows.length.toLocaleString()} uncompleted of ${allRows.length.toLocaleString()} tasks shown.
                    ${haveWiki ? `Comp% = % of WikiSync players who completed the task
                        (<a href="https://oldschool.runescape.wiki/w/Combat_Achievements/All_tasks" target="_blank" rel="noopener">source</a>).${escapeTargets(updatedNote)}`
                    : `Wiki CA data not loaded — run <code>scrape_wiki_ca_table.py</code> for richer info.`}
                </div>
                ${rows.length === 0
                    ? `<div class="targets-empty">No matching tasks.</div>`
                    : `<table class="targets-table">
                        <thead><tr>
                            ${haveWiki ? `<th data-sort="monster">Monster</th>` : ''}
                            <th data-sort="name">Task</th>
                            ${haveWiki ? `<th data-sort="desc">Description</th>` : ''}
                            ${haveWiki ? `<th data-sort="type">Type</th>` : ''}
                            <th data-sort="tier">Tier</th>
                            ${haveWiki ? `<th data-sort="pct" class="targets-pct ${(sortKey==='pct-desc'||sortKey==='pct-asc')?'sorted':''}">Comp%${(sortKey==='pct-desc'||sortKey==='pct-asc')?sortArrow:''}</th>` : `<th class="targets-pct">Pts</th>`}
                        </tr></thead>
                        <tbody>
                            ${rows.map(r => `<tr>
                                ${haveWiki ? `<td class="targets-src">${escapeTargets(r.monster)}</td>` : ''}
                                <td><a href="${r.wikiUrl}" target="_blank" rel="noopener">${escapeTargets(r.name)}</a></td>
                                ${haveWiki ? `<td>${escapeTargets(r.description)}</td>` : ''}
                                ${haveWiki ? `<td class="targets-src">${escapeTargets(r.type)}</td>` : ''}
                                <td><span class="targets-tier-pill targets-tier-${r.tier}">${r.tier}${r.points!=null?` (${r.points} pt${r.points===1?'':'s'})`:''}</span></td>
                                ${haveWiki
                                    ? `<td class="targets-pct ${targetsPctClass(r.pct)}">${fmtTargetsPct(r.pct)}</td>`
                                    : `<td class="targets-pct">${r.points ?? ''}</td>`}
                            </tr>`).join('')}
                        </tbody>
                    </table>`
                }
            `;

            const bind = (id, evt, fn) => {
                const el = document.getElementById(id);
                if (el) el.addEventListener(evt, fn);
            };
            bind('targetsCaSearch',  'input',  e => { targetsState.caSearch  = e.target.value;   renderTargetsCA(); });
            bind('targetsCaMonster', 'change', e => { targetsState.caMonster = e.target.value;   renderTargetsCA(); });
            bind('targetsCaTier',    'change', e => { targetsState.caTier    = e.target.value;   renderTargetsCA(); });
            bind('targetsCaType',    'change', e => { targetsState.caType    = e.target.value;   renderTargetsCA(); });
            bind('targetsCaSort',    'change', e => { targetsState.caSort    = e.target.value;   renderTargetsCA(); });
            bind('targetsCaHideNA',  'change', e => { targetsState.caHideNA  = e.target.checked; renderTargetsCA(); });

            // Header click sort toggles
            body.querySelectorAll('.targets-table thead th').forEach(th => {
                th.addEventListener('click', () => {
                    const k = th.dataset.sort;
                    if (k === 'pct') {
                        targetsState.caSort = targetsState.caSort === 'pct-desc' ? 'pct-asc' : 'pct-desc';
                    } else if (k === 'tier') {
                        targetsState.caSort = 'tier-asc';
                    } else if (k === 'name') {
                        targetsState.caSort = 'name-asc';
                    }
                    renderTargetsCA();
                });
            });
        }

        // The Targets tab's reference tables (~1,700 items + 637 tasks) are large
        // and only used here, so fetch them lazily the first time the tab opens.
        let targetsDataLoaded = false;
        async function ensureTargetsData() {
            if (targetsDataLoaded) return;
            targetsDataLoaded = true;
            const [comp, ca] = await Promise.all([
                fetch('./data/wiki_comp_rates.json').then(r => r.json()).catch(() => null),
                fetch('./data/wiki_ca_table.json').then(r => r.json()).catch(() => null)
            ]);
            wikiCompData = comp;
            wikiCATableData = ca;
            renderTargets();
        }

        // Tab switch (all tabs are open; bank data is simply absent when private)
        function switchTab(tabId) {
            switchTabDirect(tabId);
            if (tabId === 'targets') ensureTargetsData();
        }

        document.querySelectorAll('.nav-tab').forEach(t => t.addEventListener('click', () => {
            const tabId = t.dataset.tab;
            window.location.hash = tabId;
            switchTab(tabId);
        }));

        // Stat card click handlers
        document.querySelectorAll('.stat-card[data-tab]').forEach(card => card.addEventListener('click', () => {
            const tabId = card.dataset.tab;
            window.location.hash = tabId;
            switchTab(tabId);
        }));

        // Handle initial load and back/forward navigation
        function handleHashChange() {
            const hash = window.location.hash.slice(1);
            if (hash && document.getElementById(hash)) {
                switchTab(hash);
            }
        }
        window.addEventListener('hashchange', handleHashChange);
        window.addEventListener('load', handleHashChange);

        // ── Account switcher ──────────────────────────────────────────────
        function applyAccountChrome() {
            const badge = document.getElementById('accountBadge');
            const type = document.getElementById('accountType');
            if (badge) { badge.src = currentAccount.badge; badge.alt = currentAccount.type; }
            if (type) type.textContent = currentAccount.type;
            document.getElementById('playerName').textContent = currentAccount.label;
        }
        function setAccount(id) {
            const acct = ACCOUNTS.find(a => a.id === id);
            if (!acct) return;
            currentAccount = acct;
            localStorage.setItem('account', id);
            applyAccountChrome();
            loadData();
        }
        const accountSelect = document.getElementById('accountSelect');
        if (accountSelect) {
            accountSelect.innerHTML = ACCOUNTS.map(a => `<option value="${a.id}">${a.label}</option>`).join('');
            accountSelect.value = currentAccount.id;
            accountSelect.addEventListener('change', e => setAccount(e.target.value));
        }
        applyAccountChrome();

        loadData();
