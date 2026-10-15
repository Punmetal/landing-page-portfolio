// Lists every media slot in src/data/projects.ts and whether its file exists,
// and flags images that are still rough stand-ins cropped from the frames.
//
// Usage: npm run assets:check
import { existsSync, readFileSync } from 'node:fs';
import { projects } from '../src/data/projects.ts';

const manifest = JSON.parse(readFileSync('src/data/media-manifest.json', 'utf8'));
const ledgerPath = 'assets-src/images/.standins.json';
const standins = existsSync(ledgerPath) ? JSON.parse(readFileSync(ledgerPath, 'utf8')) : null;
const MIN_WIDTH = 1200; // a 2x export for a ~600px slot

const rows = [];
for (const p of projects) {
  for (const m of p.media) {
    if (m.kind === 'image') {
      const e = manifest[m.name];
      let status = e ? 'ok' : 'MISSING';
      if (e && standins?.[m.name] !== undefined) status = 'stand-in';
      else if (e && e.width < MIN_WIDTH) status = `low-res (${e.width}px)`;
      rows.push([p.no, 'image', `${m.name}.jpg`, status]);
    } else if (m.kind === 'video') {
      const ok = existsSync(`public/media/${m.name}.mp4`);
      rows.push([p.no, 'video', `${m.name}.mp4 (+ .webm)`, ok ? 'ok' : 'MISSING']);
    } else if (m.kind === 'model') {
      const ok = existsSync(`public/media/${m.name}.glb`);
      rows.push([p.no, '3d', `${m.name}.glb`, ok ? 'ok' : 'MISSING']);
    }
  }
}
for (const extra of ['about-portrait']) {
  const e = manifest[extra];
  rows.push(['--', 'image', `${extra}.jpg`, !e ? 'MISSING' : standins?.[extra] !== undefined ? 'stand-in' : 'ok']);
}

const pad = (s, n) => String(s).padEnd(n);
console.log(pad('#', 4) + pad('type', 7) + pad('file', 44) + 'status');
for (const r of rows) console.log(pad(r[0], 4) + pad(r[1], 7) + pad(r[2], 44) + r[3]);
const todo = rows.filter((r) => r[3] !== 'ok');
console.log(`\n${rows.length - todo.length}/${rows.length} final, ${todo.length} still needed`);
if (!standins) console.log('(no stand-in ledger found: run scripts/make-standins.mjs locally to tag stand-ins)');
