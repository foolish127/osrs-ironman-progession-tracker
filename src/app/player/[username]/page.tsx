"use client";
import { useEffect, useState, use } from 'react';
import Link from 'next/link';

const calculateCombatLevel = (s: any) => {
  if (!s) return 0;
  const att = s.attack?.level || 1;
  const str = s.strength?.level || 1;
  const def = s.defence?.level || 1;
  const hp = s.hitpoints?.level || 10;
  const ray = s.ranged?.level || 1;
  const mag = s.magic?.level || 1;
  const pra = s.prayer?.level || 1;

  const base = 0.25 * (def + hp + Math.floor(pra / 2));
  const melee = 0.325 * (att + str);
  const range = 0.325 * (Math.floor(3 * ray / 2));
  const magic = 0.325 * (Math.floor(3 * mag / 2));
  
  return Math.floor(base + Math.max(melee, range, magic));
};

const getProgressColor = (percent: number) => {
  if (percent < 30) return "bg-red-600 shadow-[0_0_8px_rgba(220,38,38,0.8)]";
  if (percent < 70) return "bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.8)]";
  return "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]";
};

const SkillBox = ({ name, level, abbrev, xp }: { name: string; level: number; abbrev: string, xp: number }) => {
  const isMax = level >= 99;
  const progressWidth = isMax ? 100 : (Number(xp) % 130344) / 1303;

  return (
    <div className="bg-[#2b251d]/50 border border-[#1a1712] p-1 flex flex-col relative h-14 shadow-[inset_0px_0px_5px_rgba(0,0,0,0.5)]">
      <div className="flex justify-between items-center h-9 px-1">
        <img 
          src={`https://oldschool.runescape.wiki/images/${name.charAt(0).toUpperCase() + name.slice(1)}_icon.png`} 
          alt={name} 
          className="w-6 h-6 opacity-90 drop-shadow-md" 
        />
        <span className="text-[#ffff00] font-bold text-[13px] tracking-tighter">{abbrev}</span>
        <span className="text-[#ffff00] font-bold text-sm leading-none drop-shadow-[1px_1px_0px_rgba(0,0,0,1)]">{level || '--'}</span>
      </div>
      <div className="absolute bottom-1.5 left-1 right-1 h-[3px] bg-black/60 rounded-full overflow-hidden">
        <div 
          className={`h-full ${isMax ? 'bg-[#00ffff] shadow-[0_0_8px_#00ffff]' : 'bg-[#00ff00] shadow-[0_0_8px_#00ff00]'}`} 
          style={{ width: `${Math.min(progressWidth, 100)}%` }}
        ></div>
      </div>
    </div>
  );
};

const BossBox = ({ name, kc, icon }: { name: string; kc: any; icon: string }) => (
  <div className="flex items-center justify-between bg-black/20 p-2 border border-[#2b251d] rounded-sm hover:bg-black/40 transition-colors">
    <div className="flex items-center gap-2">
      <img src={icon} alt={name} className="w-5 h-5 object-contain" />
      <span className="text-gray-300 text-[10px] font-bold uppercase tracking-tight">{name}</span>
    </div>
    <span className="text-white font-bold text-xs">{kc && kc > 0 ? kc.toLocaleString() : '--'}</span>
  </div>
);

export default function PlayerPage({ params }: { params: Promise<{ username: string }> }) {
  const { username } = use(params);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(false);

    fetch(`/api/proxy?username=${username}`)
      .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then(json => {
        const lines = json.csv.split('\n');
        const skillOrder = [
          'overall', 'attack', 'defence', 'strength', 'hitpoints', 'ranged', 
          'prayer', 'magic', 'cooking', 'woodcutting', 'fletching', 'fishing', 
          'firemaking', 'crafting', 'smithing', 'mining', 'herblore', 'agility', 
          'thieving', 'slayer', 'farming', 'runecraft', 'hunter', 'construction'
        ];

        const skillsObj: any = {};
        skillOrder.forEach((skill, index) => {
          if (lines[index]) {
            const [rank, level, xp] = lines[index].split(',');
            skillsObj[skill] = { level: parseInt(level), xp: parseInt(xp) };
          }
        });

        setData({
          accountName: decodeURIComponent(username),
          skills: skillsObj,
          gains: json.gains || 0,
          collectionLog: json.logStats,
          bosses: json.bossData,
          lastUpdated: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [username]);

  if (loading) return (
    <div className="min-h-screen bg-[#0b0a08] flex items-center justify-center text-[#ff9800] font-bold font-mono text-xl animate-pulse uppercase tracking-[0.3em]">
      Loading Profile...
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-[#0b0a08] flex flex-col items-center justify-center text-[#ff9800] font-bold font-mono">
      <p className="text-2xl mb-4 uppercase">Player Not Found</p>
      <Link href="/" className="text-white underline decoration-[#ff9800] uppercase tracking-widest text-xs">Return to Search</Link>
    </div>
  );

  const skillList = [
    { name: 'Attack', abbrev: 'Atk' }, { name: 'Hitpoints', abbrev: 'Hp' }, { name: 'Mining', abbrev: 'Mine' },
    { name: 'Strength', abbrev: 'Str' }, { name: 'Agility', abbrev: 'Agi' }, { name: 'Smithing', abbrev: 'Smith' },
    { name: 'Defence', abbrev: 'Def' }, { name: 'Herblore', abbrev: 'Herb' }, { name: 'Fishing', abbrev: 'Fish' },
    { name: 'Ranged', abbrev: 'Rng' }, { name: 'Thieving', abbrev: 'Thiev' }, { name: 'Cooking', abbrev: 'Cook' },
    { name: 'Prayer', abbrev: 'Pray' }, { name: 'Crafting', abbrev: 'Craft' }, { name: 'Firemaking', abbrev: 'Fm' },
    { name: 'Magic', abbrev: 'Mage' }, { name: 'Fletching', abbrev: 'Fletch' }, { name: 'Woodcutting', abbrev: 'Wc' },
    { name: 'Runecraft', abbrev: 'Rc' }, { name: 'Slayer', abbrev: 'Slay' }, { name: 'Farming', abbrev: 'Farm' },
    { name: 'Construction', abbrev: 'Con' }, { name: 'Hunter', abbrev: 'Hunt' }, { name: 'Sailing', abbrev: 'Sai' }
  ];

  const totalXp = data.skills?.overall?.xp || 0;
  const cbLevel = calculateCombatLevel(data.skills);

  return (
    <main className="min-h-screen bg-[#0b0a08] bg-[url('https://www.transparenttextures.com/patterns/dark-leather.png')] flex flex-col items-center py-10 px-4 font-mono text-white">
      
      {/* Skills Box */}
      <div className="w-full max-w-[420px] bg-[#3e3529] border-[4px] border-[#2b251d] p-5 shadow-[0_20px_50px_rgba(0,0,0,0.8)] outline outline-1 outline-black/50 mb-6">
        <div className="relative mb-6 border-b border-[#2b251d] pb-4 text-center">
            <h1 className="text-[#ff9800] text-3xl font-black drop-shadow-[2px_2px_0_rgba(0,0,0,1)] uppercase tracking-tighter">
              {data.accountName}
            </h1>
            <span className="text-gray-400 text-[10px] font-bold tracking-tight uppercase">Highscores Overview</span>
        </div>

        <div className="grid grid-cols-3 gap-1.5 bg-black/30 p-1.5 border border-[#2b251d] rounded-sm shadow-inner mb-4">
          {skillList.map(skill => {
            const sData = data.skills?.[skill.name.toLowerCase()];
            return <SkillBox key={skill.name} name={skill.name} abbrev={skill.abbrev} level={sData?.level || 1} xp={sData?.xp || 0} />;
          })}
        </div>

        <div className="flex flex-col items-center leading-tight">
            <div className="text-[#ff9800] text-[14px] font-bold tracking-widest uppercase">
              Combat level: <span className="text-white font-bold ml-1">{cbLevel}</span>
            </div>
            <div className="text-[#ff9800] text-[14px] font-bold tracking-widest flex items-center uppercase">
              Total XP: <span className="text-white font-bold ml-1">{totalXp.toLocaleString()}</span>
              {data.gains > 0 && (
                <span className="text-[#00ff00] text-[11px] ml-2 font-black drop-shadow-[0_0_5px_rgba(0,255,0,0.5)]">
                  +{data.gains.toLocaleString()}
                </span>
              )}
            </div>
            <div className="text-[#ffff00] text-[14px] font-bold tracking-widest uppercase">
              Total level: <span className="text-white font-bold ml-1">{data.skills?.overall?.level || '---'}</span>
            </div>
        </div>
      </div>

      {/* Progression Box */}
      <div className="w-full max-w-[420px] bg-[#3e3529] border-[4px] border-[#2b251d] p-5 shadow-[0_20px_50px_rgba(0,0,0,0.8)] outline outline-1 outline-black/50 mb-6">
        <div className="flex items-center justify-center gap-2 mb-5 border-b border-[#2b251d] pb-2">
          <img src="https://oldschool.runescape.wiki/images/Collection_log_detail.png" alt="Log" className="w-5 h-5" />
          <h3 className="text-[#ff9800] text-[14px] font-bold tracking-[0.2em] uppercase">Account Progression</h3>
        </div>
        
        <div className="space-y-4">
          <div className="flex justify-between items-baseline text-[14px] font-bold tracking-widest uppercase">
            <span className="text-[#ff9800]">Collection Log:</span>
            <div className="flex gap-2 items-baseline">
              <span className="text-white">{data.collectionLog?.obtained} / {data.collectionLog?.total}</span>
              <span className="text-[#ffff00] text-[11px] italic">({data.collectionLog?.percentage}%)</span>
            </div>
          </div>
          <div className="w-full h-3 bg-black/80 border border-[#2b251d] overflow-hidden rounded-full">
            <div className={`h-full transition-all duration-1000 ${getProgressColor(data.collectionLog?.percentage)}`} style={{ width: `${data.collectionLog?.percentage}%` }}></div>
          </div>
        </div>
      </div>

      {/* Bossing Box */}
      <div className="w-full max-w-[420px] bg-[#3e3529] border-[4px] border-[#2b251d] p-5 shadow-[0_20px_50px_rgba(0,0,0,0.8)] outline outline-1 outline-black/50 mb-6">
        <div className="flex items-center justify-center gap-2 mb-4 border-b border-[#2b251d] pb-2">
          <img src="https://oldschool.runescape.wiki/images/Slayer_icon.png" alt="Bossing" className="w-5 h-5" />
          <h3 className="text-[#ff9800] text-[14px] font-bold tracking-[0.2em] uppercase">Bossing & Raids</h3>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <BossBox name="Chambers" kc={data.bosses?.cox} icon="https://oldschool.runescape.wiki/images/Chambers_of_Xeric_logo.png" />
          <BossBox name="Theatre" kc={data.bosses?.tob} icon="https://oldschool.runescape.wiki/images/Theatre_of_Blood_logo.png" />
          <BossBox name="Tombs" kc={data.bosses?.toa} icon="https://oldschool.runescape.wiki/images/Tombs_of_Amascut_logo.png" />
          <BossBox name="Zulrah" kc={data.bosses?.zulrah} icon="https://oldschool.runescape.wiki/images/Zulrah_icon.png" />
          <BossBox name="Vorkath" kc={data.bosses?.vorkath} icon="https://oldschool.runescape.wiki/images/Vorkath_icon.png" />
          <BossBox name="Slayer" kc={data.skills?.slayer?.level} icon="https://oldschool.runescape.wiki/images/Slayer_icon.png" />
        </div>
      </div>

      {/* Navigation */}
      <div className="w-full max-w-[420px] flex gap-2 mt-6">
        <Link href="/" className="flex-1 bg-[#4e4437] border-2 border-[#2b251d] py-3 text-center text-white font-bold text-xs tracking-widest hover:bg-[#5a4f40] transition-colors rounded-sm uppercase shadow-md">New Search</Link>
        <Link href="/checklist" className="flex-1 bg-[#4e4437] border-2 border-[#2b251d] py-3 text-center text-[#ffff00] font-bold text-xs tracking-widest hover:bg-[#5a4f40] transition-colors rounded-sm uppercase shadow-md">Checklist</Link>
      </div>
    </main>
  );
}