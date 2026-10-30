// Pulls the last year of contributions from GitHub's GraphQL API and writes
// city/data.json in the shape the renderer expects.
//
//   GITHUB_TOKEN=... GITHUB_LOGIN=bulletchicken node scripts/fetch.mjs
//
// The default GITHUB_TOKEN of an Action is enough for public contributions.
// Use a personal token (read:user) if you want private contributions counted.
import { writeFileSync } from 'node:fs';

const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
const login = process.env.GITHUB_LOGIN || process.env.GITHUB_REPOSITORY_OWNER || 'bulletchicken';
if (!token) { console.error('GITHUB_TOKEN is not set'); process.exit(1); }

const query = `query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}`;

const res = await fetch('https://api.github.com/graphql', {
  method: 'POST',
  headers: { 'Authorization': `bearer ${token}`, 'Content-Type': 'application/json', 'User-Agent': 'commit-city' },
  body: JSON.stringify({ query, variables: { login } })
});
const json = await res.json();
if (json.errors) { console.error(JSON.stringify(json.errors, null, 2)); process.exit(1); }
const cal = json.data.user.contributionsCollection.contributionCalendar;

// Normalise to 53 columns of 7 days (Sunday first), future days as null.
const todayStr = new Date().toISOString().slice(0, 10);
let weeks = cal.weeks.map(w => {
  const col = Array.from({ length: 7 }, () => ({ date: null, count: null }));
  w.contributionDays.forEach(d => { col[d.weekday] = { date: d.date, count: d.contributionCount }; });
  return col;
});
// GitHub returns the current partial week last; fill empty slots in the first week as blanks too
weeks = weeks.slice(-53);
while (weeks.length < 53) weeks.unshift(Array.from({ length: 7 }, () => ({ date: null, count: null })));
weeks.forEach(col => col.forEach(c => { if (c.date && c.date > todayStr) c.count = null; }));

const names = 'JanFebMarAprMayJunJulAugSepOctNovDec';
const monthOf = col => { const d = col.find(c => c.date); return d ? new Date(d.date + 'T12:00:00').getMonth() : -1; };
const months = [];
for (let w = 0; w < 53; w++) {
  const m = monthOf(weeks[w]);
  if (m < 0) continue;
  const prev = w > 0 ? monthOf(weeks[w - 1]) : -1;
  if (w === 0 || m !== prev) {
    if (w === 0 && monthOf(weeks[1]) !== m) continue;
    months.push({ w, t: names.substr(m * 3, 3) });
  }
}

writeFileSync(new URL('../city/data.json', import.meta.url), JSON.stringify({ login, generated: new Date().toISOString(), total: cal.totalContributions, weeks, months }));
console.log(`wrote city/data.json for ${login}: ${cal.totalContributions} contributions`);
