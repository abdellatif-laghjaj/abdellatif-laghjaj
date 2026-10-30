// Writes city/data.json with made-up contributions so the renderer can be
// tried without a token. The GitHub Action uses scripts/fetch.mjs instead.
import { writeFileSync } from 'node:fs';

let s = 2026102;
const rnd = () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

const today = new Date(2026, 9, 29);
const start = new Date(2026, 9, 29 - today.getDay() - 364);
const season = [1.15, 1.4, 1.4, 1.35, 1.3, 0.85, 0.85, 0.9, 1.0, 1.25, 1.2, 1.1];
const burst = {};
let nb = 0;
while (nb < 7) { const k = 2 + Math.floor(rnd() * 50); if (!burst[k]) { burst[k] = true; nb++; } }

const weeks = [];
for (let w = 0; w < 53; w++) {
  const col = [];
  for (let d = 0; d < 7; d++) {
    const date = new Date(start.getFullYear(), start.getMonth(), start.getDate() + w * 7 + d);
    if (date > today) { col.push({ date: date.toISOString().slice(0, 10), count: null }); continue; }
    const wk = d > 0 && d < 6;
    let base = (wk ? 3.4 : 1.2) * season[date.getMonth()];
    if (burst[w]) base *= 2.4;
    const zero = rnd() < (wk ? 0.13 : 0.4);
    let c = zero ? 0 : Math.round(base * (0.25 + rnd() * 1.5));
    if (c > 24) c = 24;
    col.push({ date: date.toISOString().slice(0, 10), count: c });
  }
  weeks.push(col);
}

const names = 'JanFebMarAprMayJunJulAugSepOctNovDec';
const months = [];
for (let w = 0; w < 53; w++) {
  const m = new Date(weeks[w][0].date + 'T12:00:00').getMonth();
  const prev = w > 0 ? new Date(weeks[w - 1][0].date + 'T12:00:00').getMonth() : -1;
  if (w === 0 || m !== prev) {
    if (w === 0 && new Date(weeks[1][0].date + 'T12:00:00').getMonth() !== m) continue;
    months.push({ w, t: names.substr(m * 3, 3) });
  }
}

writeFileSync(new URL('../city/data.json', import.meta.url), JSON.stringify({ login: 'bulletchicken', generated: new Date().toISOString(), weeks, months }, null, 0));
console.log('wrote city/data.json');
