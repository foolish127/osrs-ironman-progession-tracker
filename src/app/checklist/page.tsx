"use client";
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { MASTER_CHECKLIST, ChecklistItem } from './data';

type Status = 'not-completed' | 'completed' | 'skipped';

export default function ChecklistPage() {
  const [statuses, setStatuses] = useState<Record<string, Status>>({});
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem('osrs_giant_checklist');
    if (saved) setStatuses(JSON.parse(saved));
  }, []);

  const toggleStatus = (id: string) => {
    const current = statuses[id] || 'not-completed';
    let next: Status = 'completed';
    if (current === 'completed') next = 'skipped';
    else if (current === 'skipped') next = 'not-completed';

    const newStatuses = { ...statuses, [id]: next };
    setStatuses(newStatuses);
    localStorage.setItem('osrs_giant_checklist', JSON.stringify(newStatuses));
  };

  const getStatusStyle = (status: Status) => {
    if (status === 'completed') return 'bg-green-900/40 text-green-400 border-green-500';
    if (status === 'skipped') return 'bg-yellow-900/40 text-yellow-400 border-yellow-500';
    return 'bg-black/40 text-gray-500 border-[#2b251d]';
  };

  const getTypeStyle = (type: string) => {
    switch(type) {
      case 'Skill': return 'text-cyan-400 bg-cyan-900/20';
      case 'Total Level': return 'text-purple-400 bg-purple-900/20';
      case 'Quest': return 'text-orange-400 bg-orange-900/20';
      default: return 'text-gray-400 bg-gray-800/20';
    }
  };

  const categories: ChecklistItem['category'][] = ['Early Game', 'Mid Game', 'Late Game', 'End Game'];

  const filteredList = MASTER_CHECKLIST.filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.source.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.searchTerms?.includes(searchTerm.toLowerCase())
  );

  return (
    <main className="min-h-screen bg-[#0b0a08] flex flex-col items-center py-10 px-4 font-mono">
      <div className="w-full max-w-[950px] bg-[#1a1712] border-2 border-[#2b251d] p-6 shadow-2xl">
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b border-[#2b251d] pb-6 gap-4">
          <div>
            <h1 className="text-[#ff9800] text-3xl font-black uppercase italic tracking-tight">Master Progression</h1>
            <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest mt-1">Status: Not Done → Done → Skipped</p>
          </div>
          
          <div className="flex w-full md:w-auto gap-2">
            <input 
              type="text" 
              placeholder="Search goals..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-black border border-[#2b251d] px-4 py-2 text-[#ff9800] text-sm font-bold focus:outline-none focus:border-[#ff9800] w-full md:w-64"
            />
            <Link href="/" className="bg-[#2b251d] px-4 py-2 border border-gray-700 text-white text-[10px] font-bold uppercase hover:bg-black transition-all flex items-center">Back</Link>
          </div>
        </div>

        <div className="space-y-12">
          {categories.map(cat => {
            const itemsInCat = filteredList.filter(i => i.category === cat);
            if (itemsInCat.length === 0) return null;

            return (
              <section key={cat}>
                <h2 className="text-[#ff9800] text-[11px] font-black uppercase tracking-[0.4em] mb-4 bg-[#2b251d] px-3 py-1 inline-block border-l-4 border-[#ff9800]">
                  {cat}
                </h2>
                <div className="overflow-hidden border-t border-[#2b251d]">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="text-gray-500 text-[10px] uppercase text-left border-b border-[#2b251d]">
                        <th className="p-4">Goal</th>
                        <th className="p-4 text-center">Type</th>
                        <th className="p-4">Source / Requirement</th>
                        <th className="p-4 text-right">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#2b251d]">
                      {itemsInCat.map((item) => (
                        <tr key={item.id} className="hover:bg-white/[0.02] transition-colors">
                          <td className="p-4 align-middle">
                            <div className="flex items-center gap-3">
                                {item.type === 'Skill' && (
                                    <img 
                                        src={`https://oldschool.runescape.wiki/images/${item.name.split(' ')[1]}_icon.png`} 
                                        className="w-5 h-5" 
                                        alt="" 
                                    />
                                )}
                                <div className="text-white font-bold text-sm">{item.name}</div>
                            </div>
                          </td>
                          <td className="p-4 align-middle text-center">
                            <span className={`text-sm py-1.5 font-bold uppercase tracking-tighter w-[130px] inline-block ${getTypeStyle(item.type)}`}>
                              {item.type}
                            </span>
                          </td>
                          <td className="p-4 align-middle text-gray-500 text-sm italic">{item.source}</td>
                          <td className="p-4 align-middle text-right">
                            <button 
                              onClick={() => toggleStatus(item.id)}
                              className={`px-3 py-1.5 border text-sm font-black uppercase transition-all min-w-[130px] ${getStatusStyle(statuses[item.id])}`}
                            >
                              {statuses[item.id] ? statuses[item.id].replace('-', ' ') : 'Not Done'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            );
          })}
        </div>
      </div>
    </main>
  );
}