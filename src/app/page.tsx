"use client";
import { useEffect, useState } from 'react';

// Combat Level Formula
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

const SkillBox = ({ name, level, abbrev, xp }: { name: string; level: number; abbrev: string, xp: number }) => {
  const isMax = level >= 99;
  // Progress within current level (Modulo calculation based on average level XP)
  const progressWidth = isMax ? 100 : (Number(xp) % 130000) / 1300;

  return (
    <div className="bg-[#2b251d]/50 border border-[#1a1712] p-1 flex flex-col relative h-14 shadow-[inset_0px_0px_5px_rgba(0,0,0,0.5)]">
      <div className="flex justify-between items-center h-9 px-1">
        <img 
          src={`https://oldschool.runescape.wiki/images/${name.charAt(0).toUpperCase() + name.slice(1)}_icon.png`} 
          alt={name} 
          className="w-6 h-6 opacity-90 drop-shadow-md" 
        />
        <span className="text-[#ffff00] font-bold text-[13px] uppercase tracking-tighter">{abbrev}</span>
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

export default function Home() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch('/stats.json')
      .then(res => res.json())
      .then(d => setData(d))
      .catch(err => console.error("Error loading stats.json:", err));
  }, []);

  if (!data) return <div className="min-h-screen bg-[#0b0a08] flex items-center justify-center text-[#ff9800] font-bold font-mono uppercase">Fetching Data...</div>;

  const skillList = [
    { name: 'Attack', abbrev: 'ATT' }, { name: 'Hitpoints', abbrev: 'HIT' }, { name: 'Mining', abbrev: 'MIN' },
    { name: 'Strength', abbrev: 'STR' }, { name: 'Agility', abbrev: 'AGI' }, { name: 'Smithing', abbrev: 'SMI' },
    { name: 'Defence', abbrev: 'DEF' }, { name: 'Herblore', abbrev: 'HER' }, { name: 'Fishing', abbrev: 'FIS' },
    { name: 'Ranged', abbrev: 'RAN' }, { name: 'Thieving', abbrev: 'THI' }, { name: 'Cooking', abbrev: 'COO' },
    { name: 'Prayer', abbrev: 'PRA' }, { name: 'Crafting', abbrev: 'CRA' }, { name: 'Firemaking', abbrev: 'FIR' },
    { name: 'Magic', abbrev: 'MAG' }, { name: 'Fletching', abbrev: 'FLE' }, { name: 'Woodcutting', abbrev: 'WOO' },
    { name: 'Runecraft', abbrev: 'RUN' }, { name: 'Slayer', abbrev: 'SLA' }, { name: 'Farming', abbrev: 'FAR' },
    { name: 'Construction', abbrev: 'CON' }, { name: 'Hunter', abbrev: 'HUN' }, { name: 'Sailing', abbrev: 'SAI' }
  ];

  // TOTAL XP CALCULATION: Sums any field containing "xp" in the skills object
  const totalXpRaw = data.skills 
    ? Object.entries(data.skills).reduce((acc, [key, val]: [string, any]) => {
        if (key.toLowerCase() === 'overall') return acc;
        const xp = val.xp || val.XP || val.experience || 0;
        return acc + Number(xp);
      }, 0)
    : 0;

  const cbLevel = calculateCombatLevel(data.skills);

  return (
    <main className="min-h-screen bg-[#0b0a08] bg-[url('https://www.transparenttextures.com/patterns/dark-leather.png')] flex flex-col items-center py-10 px-4 font-mono text-white">
      <div className="w-full max-w-[420px] bg-[#3e3529] border-[4px] border-[#2b251d] p-5 shadow-[0_20px_50px_rgba(0,0,0,0.8)]">
        
        {/* HEADER */}
        <div className="relative mb-6 border-b border-[#2b251d] pb-4">
          <div className="flex items-center justify-center">
            <div className="flex flex-col items-center w-20">
              <img src="/Ironman_Mode_logo.png" style={{ width: '24px' }} alt="Ironman" />
              <span className="text-gray-400 text-[10px] font-bold">Ironman</span>
            </div>
            <div className="flex-1 text-center pr-10">
              <h1 className="text-[#ff9800] text-3xl font-black drop-shadow-[2px_2px_0_rgba(0,0,0,1)]">{data.accountName}</h1>
            </div>
          </div>
        </div>

        {/* SKILL GRID */}
        <div className="grid grid-cols-3 gap-1.5 bg-black/30 p-1.5 border border-[#2b251d] rounded-sm shadow-inner mb-6">
          {skillList.map(skill => {
            const sData = data.skills?.[skill.name.toLowerCase()] || data.skills?.[skill.name.toLowerCase() + 'ing'];
            return <SkillBox key={skill.name} name={skill.name} abbrev={skill.abbrev} level={sData?.level || 0} xp={sData?.xp || 0} />;
          })}
        </div>

        {/* STATS SECTION */}
        <div className="flex flex-col items-center gap-1.5">
            {/* Combat Level - Natural Casing, Orange label */}
            <div className="text-[#ff9800] text-[14px] font-bold tracking-widest">
              Combat Level:&nbsp;<span className="text-white font-bold">{cbLevel}</span>
            </div>
            
            {/* Total XP - Matches Combat Level style */}
            <div className="text-[#ff9800] text-[14px] font-bold tracking-widest">
              Total XP:&nbsp;<span className="text-white">{totalXpRaw.toLocaleString()}</span>
            </div>

            {/* Total Level Bar */}
            <div className="w-full bg-black border-y-2 border-[#4e4437] py-2 flex justify-center items-center shadow-lg mt-1">
              <h2 className="text-[#ffff00] text-2xl font-bold tracking-[0.1em] drop-shadow-[2px_2px_0px_rgba(0,0,0,1)]">
                Total Level: {data.skills?.overall?.level || '---'}
              </h2>
            </div>

            {/* Collection Log - Removed wrapping box, simple centered layout */}
            <div className="w-full mt-4 flex flex-col items-center">
                <div className="flex justify-center items-center mb-2">
                  <span className="text-[#ff9800] text-[12px] font-black tracking-wider">Collection Log:&nbsp;</span>
                  <span className="text-white text-[12px] font-bold">{data.collectionLog?.obtained || 0} / 1515</span>
                </div>
                <div className="w-full max-w-[300px] h-2.5 bg-black/80 rounded-full border border-[#2b251d] overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-[#632a00] to-[#ff9800]" 
                    style={{ width: `${data.collectionLog?.percentage || 0}%` }}
                  ></div>
                </div>
            </div>
        </div>

        {/* BOSS KC */}
        <div className="mt-10 pt-4 border-t border-[#2b251d]">
          <h3 className="text-[#ff9800] text-[11px] font-bold mb-3 tracking-[0.2em] text-center">Boss Killcounts</h3>
          <div className="grid grid-cols-2 gap-x-8 gap-y-2 px-4">
            {data.bosses && Object.entries(data.bosses).slice(0, 6).map(([boss, kc]: any) => (
              <div key={boss} className="flex justify-between items-center text-[12px] border-b border-white/5 pb-1">
                <span className="text-gray-400 capitalize">{boss.replace(/_/g, ' ')}</span>
                <span className="text-[#ffff00] font-bold">{kc}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="mt-8 text-[9px] text-gray-500 text-center font-bold tracking-widest opacity-40">
          Last Synced: {data.lastUpdated}
        </p>
      </div>
    </main>
  );
}