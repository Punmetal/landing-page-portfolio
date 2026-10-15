// Crops rough stand-in images out of the 1280x720 portfolio frames
// (assets-src/frames/frame-*.jpg) into assets-src/images/ using the final
// naming convention. Real Figma 2x exports dropped into assets-src/images/
// with the same name replace these; this script never overwrites a file
// it did not write itself (tracked by byte size in assets-src/images/.standins.json).
//
// Usage: node scripts/make-standins.mjs
import sharp from 'sharp';
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { layouts } from '../src/data/layouts.ts';

const FRAMES = 'assets-src/frames';
const OUT = 'assets-src/images';
const LEDGER = join(OUT, '.standins.json'); // { name: byteSize } of files this script wrote
const INSET = 4; // trim rounded-corner edges

// Boxes come from the desktop slide layouts (one source of truth):
// [frame, name, x0, y0, x1, y1] in frame pixels
const CROPS = Object.values(layouts).flatMap((slides) =>
  slides.flatMap((slide) =>
    slide.items.filter((it) => 'name' in it).map((it) => [slide.frame, it.name, ...it.box]),
  ),
);

mkdirSync(OUT, { recursive: true });
const ledger = existsSync(LEDGER) ? JSON.parse(readFileSync(LEDGER, 'utf8')) : {};
let made = 0;
let kept = 0;

for (const [frame, name, x0, y0, x1, y1] of CROPS) {
  const out = join(OUT, `${name}.jpg`);
  if (existsSync(out) && statSync(out).size !== ledger[name]) {
    kept++; // a real export already lives here
    delete ledger[name];
    continue;
  }
  // full-bleed page images have no rounded corners to trim
  const inset = x1 - x0 >= 1280 ? 0 : INSET;
  await sharp(join(FRAMES, `frame-${frame}.jpg`))
    .extract({
      left: x0 + inset,
      top: y0 + inset,
      width: x1 - x0 - inset * 2,
      height: y1 - y0 - inset * 2,
    })
    .jpeg({ quality: 92 })
    .toFile(out);
  ledger[name] = statSync(out).size;
  made++;
}

writeFileSync(LEDGER, JSON.stringify(ledger, null, 2));
console.log(`stand-ins: ${made} written, ${kept} real exports left untouched`);

// Open Graph image from the portfolio cover (Frame 0), 1200x630.
await sharp(join(FRAMES, 'frame-0.jpg'))
  .resize(1200, 630, { fit: 'cover' })
  .jpeg({ quality: 82, mozjpeg: true })
  .toFile('public/og.jpg');
console.log('og image -> public/og.jpg');
