import fs from 'fs';

async function getStats() {
  const rsn = 'FoolinSlays';
  console.log(`Deep-syncing ${rsn}...`);

  try {
    // 1. Fetch from WOM (This always works for levels)
    const womRes = await fetch(`https://api.wiseoldman.net/v2/players/${rsn}`);
    const womJson = await womRes.json();
    const skills = womJson.latestSnapshot.data.skills;

    // 2. Fetch from Temple (Adding a timestamp to bypass cache)
    const templeUrl = `https://templeosrs.com/api/player_info.php?player=${rsn}&data=combined&cloginfo=1&t=${Date.now()}`;
    const templeRes = await fetch(templeUrl, {
      headers: { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
      }
    });

    const templeText = await templeRes.text();
    let logObtained = 393; // Use your known value as the default fallback

    if (templeText.trim().startsWith('{')) {
      const templeJson = JSON.parse(templeText);
      logObtained = templeJson.data?.items_obtained || 393;
    }

    const finalData = {
      lastUpdated: new Date().toLocaleString(),
      accountName: rsn,
      skills: skills,
      collectionLog: {
        obtained: logObtained,
        total: 1515,
        percentage: ((logObtained / 1515) * 100).toFixed(2)
      }
    };

    fs.writeFileSync('./public/stats.json', JSON.stringify(finalData, null, 2));
    console.log(`✅ Success! Log: ${logObtained}/1515`);
  } catch (err) {
    console.error("❌ Error:", err.message);
  }
}

getStats();