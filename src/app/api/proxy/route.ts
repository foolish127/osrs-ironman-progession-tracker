import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const username = searchParams.get('username')?.toLowerCase();

  if (!username) return NextResponse.json({ error: 'No username' }, { status: 400 });

  try {
    console.log(`--- Fetching data for: ${username} ---`);

    // 1. OSRS Highscores
    const osrsRes = await fetch(`https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=${username}`);
    if (!osrsRes.ok) {
      console.log("Highscores error: Player might not exist on Jagex side.");
      throw new Error('Highscores failed');
    }
    const csv = await osrsRes.text();

    // 2. Collection Log
    let logStats = { obtained: 0, total: 1515, percentage: 0 };
    try {
      const logRes = await fetch(`https://api.collectionlog.net/collectionlog/user/${username}`);
      const logData = await logRes.json();
      if (logData?.collectionLog) {
        logStats = {
          obtained: logData.collectionLog.totalObtained || 0,
          total: logData.collectionLog.totalItems || 1515,
          percentage: Math.floor((logData.collectionLog.totalObtained / logData.collectionLog.totalItems) * 100)
        };
      }
    } catch (e) {
      console.log("Collection Log not found for this player (normal).");
    }

    // 3. Supabase Logic
    const totalXp = parseInt(csv.split('\n')[0].split(',')[2]);
    const { error: dbError } = await supabase.from('player_snapshots').insert({
      username,
      total_xp: totalXp,
      skills_json: { csv }
    });

    if (dbError) console.log("Supabase Insert Error:", dbError.message);

    // Calculate Gains
    const startOfToday = new Date();
    startOfToday.setHours(0,0,0,0);
    const { data: oldSnap } = await supabase
      .from('player_snapshots')
      .select('total_xp')
      .eq('username', username)
      .gte('timestamp', startOfToday.toISOString())
      .order('timestamp', { ascending: true })
      .limit(1);

    const gains = (oldSnap && oldSnap.length > 0) ? totalXp - oldSnap[0].total_xp : 0;

    // Boss Data Extraction
    const lines = csv.split('\n');
    const bossData = {
      cox: lines[44]?.split(',')[1] || 0,
      tob: lines[80]?.split(',')[1] || 0,
      toa: lines[81]?.split(',')[1] || 0,
      vorkath: lines[79]?.split(',')[1] || 0,
      zulrah: lines[84]?.split(',')[1] || 0,
    };

    return NextResponse.json({ csv, gains, logStats, bossData });

  } catch (error: any) {
    console.error("API Proxy Route Error:", error.message);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}