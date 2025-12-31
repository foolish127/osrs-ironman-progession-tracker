"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [username, setUsername] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim()) {
      router.push(`/player/${encodeURIComponent(username.trim())}`);
    }
  };

  return (
    <main className="min-h-screen bg-[#0b0a08] bg-[url('https://www.transparenttextures.com/patterns/dark-leather.png')] flex flex-col items-center justify-center px-4 font-mono text-white">
      
      {/* Title Section */}
      <div className="mb-12 text-center">
        <h1 className="text-[#ff9800] text-5xl font-black drop-shadow-[4px_4px_0_rgba(0,0,0,1)] tracking-tighter mb-2 uppercase">
          OSRS Tracker
        </h1>
        <p className="text-gray-400 text-sm font-bold tracking-widest uppercase opacity-60">
          Player Statistics & Progression
        </p>
      </div>

      {/* Search Box */}
      <div className="w-full max-w-[500px] bg-[#3e3529] border-[4px] border-[#2b251d] p-8 shadow-[0_30px_60px_rgba(0,0,0,0.9)] outline outline-1 outline-black/50">
        <form onSubmit={handleSearch} className="space-y-6">
          <div className="space-y-2">
            <label className="text-[#ff9800] text-xs font-bold tracking-[0.2em] uppercase ml-1">
              Search Player
            </label>
            
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter RSN..."
              autoFocus
              autoComplete="off"
              // The '!' prefix forces Tailwind to override any browser defaults
              className="w-full !bg-black !text-white border-2 border-[#ff9800] p-4 text-2xl font-bold focus:outline-none text-center placeholder:text-gray-800"
              // Nuclear style override to kill white backgrounds
              style={{ 
                backgroundColor: 'black', 
                color: 'white', 
                colorScheme: 'dark' 
              }}
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#4e4437] border-2 border-[#2b251d] py-4 text-[#ffff00] font-bold text-lg tracking-widest shadow-[0_4px_10px_rgba(0,0,0,0.5)] hover:bg-[#5a4f40] active:translate-y-0.5 transition-all rounded-sm"
          >
            Track Player
          </button>
        </form>
      </div>

      <footer className="mt-12 text-gray-600 text-[10px] font-bold tracking-widest opacity-40 uppercase">
        Data synced with Old School Highscores
      </footer>
    </main>
  );
}