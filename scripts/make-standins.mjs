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

const FRAMES = 'assets-src/frames';
const OUT = 'assets-src/images';
const LEDGER = join(OUT, '.standins.json'); // { name: byteSize } of files this script wrote
const INSET = 4; // trim rounded-corner edges

// [frame, name, x0, y0, x1, y1] in frame pixels
const CROPS = [
  ['1', 'about-portrait', 0, 0, 487, 720],

  ['4a', '01-k2o-kv', 325, 45, 668, 472],
  ['4a', '01-k2o-poster-bus', 678, 45, 862, 277],
  ['4a', '01-k2o-poster-daou', 869, 45, 1053, 277],
  ['4a', '01-k2o-poster-fiftyfifty', 1060, 45, 1245, 277],
  ['4a', '01-k2o-poster-kissoflife', 678, 284, 862, 515],
  ['4a', '01-k2o-poster-lngshot', 869, 284, 1053, 515],
  ['4a', '01-k2o-poster-riize', 1060, 284, 1245, 515],
  ['4a', '01-k2o-logo', 325, 483, 493, 667],
  ['4a', '01-k2o-logo-water', 500, 483, 668, 667],
  ['4b', '01-k2o-merch-tee', 50, 110, 300, 645],
  ['4b', '01-k2o-merch-tiedye', 313, 108, 563, 410],
  ['4b', '01-k2o-merch-black', 313, 430, 563, 645],
  ['4b', '01-k2o-merch-wristband', 575, 108, 768, 240],
  ['4b', '01-k2o-merch-wristbands', 575, 253, 768, 645],
  ['4b', '01-k2o-map', 810, 115, 1243, 653],

  ['5', '02-standup-kv', 323, 38, 700, 508],
  ['5', '02-standup-logo', 323, 522, 480, 677],
  ['5', '02-standup-banners', 712, 38, 918, 395],
  ['5', '02-standup-billboard', 930, 38, 1243, 395],
  ['5', '02-standup-wall-posters', 712, 410, 997, 675],
  ['5', '02-standup-poster-mockup', 1008, 410, 1243, 675],

  ['6', '03-thumbs-poster-ice', 325, 25, 710, 572],
  ['6', '03-thumbs-netflix-snow', 723, 25, 1004, 183],
  ['6', '03-thumbs-poster-jail', 723, 193, 1004, 695],
  ['6', '03-thumbs-masterchef', 1016, 25, 1230, 307],
  ['6', '03-thumbs-netflix-codex', 1016, 318, 1230, 435],
  ['6', '03-thumbs-netflix-whats', 1016, 446, 1230, 563],
  ['6', '03-thumbs-netflix-playback', 1016, 573, 1230, 692],
  ['6', '03-thumbs-netflix-backstage', 325, 587, 512, 692],
  ['6', '03-thumbs-netflix-yaya', 521, 587, 710, 692],

  ['7', '04-content-post-tree-of-alpha', 320, 36, 556, 352],
  ['7', '04-content-post-luck', 320, 368, 556, 684],
  ['7', '04-content-webtoon', 578, 36, 786, 244],
  ['7', '04-content-chatgpt', 797, 36, 1006, 244],
  ['7', '04-content-mortgage', 1017, 36, 1226, 244],
  ['7', '04-content-dnft', 578, 255, 786, 464],
  ['7', '04-content-buyback', 797, 255, 1006, 464],
  ['7', '04-content-layer2', 1017, 255, 1226, 464],
  ['7', '04-content-call-center', 578, 475, 786, 684],
  ['7', '04-content-credit-card', 797, 475, 1006, 684],
  ['7', '04-content-binance-worldcup', 1017, 475, 1226, 684],

  ['8', '05-info-bitcoin-timeline', 310, 45, 812, 675],
  ['8', '05-info-documentaries', 820, 50, 1066, 355],
  ['8', '05-info-ev-sales', 820, 365, 1066, 675],
  ['8', '05-info-ethereum', 1071, 48, 1236, 248],
  ['8', '05-info-investing', 1071, 258, 1236, 420],
  ['8', '05-info-pixar', 1071, 470, 1236, 675],

  ['9a', '06-16p-cover', 315, 52, 722, 412],
  ['9a', '06-16p-characters', 315, 423, 722, 670],
  ['9a', '06-16p-spread-green', 735, 52, 1018, 295],
  ['9a', '06-16p-spread-purple', 1023, 52, 1241, 295],
  ['9a', '06-16p-spread-blue', 735, 308, 948, 566],
  ['9a', '06-16p-spread-yellow', 955, 308, 1241, 566],
  ['9c', '06-16p-all-spreads', 40, 60, 1240, 660],

  ['10a', '07-sybil-logo', 320, 65, 832, 380],
  ['10a', '07-sybil-environment', 846, 65, 1222, 380],
  ['10a', '07-sybil-tiers', 320, 408, 1222, 655],
  ['10b', '07-sybil-landing', 0, 0, 1280, 720],
];

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
  const inset = name === '07-sybil-landing' || name === 'about-portrait' ? 0 : INSET;
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
