// Image pipeline: assets-src/images/*.{jpg,jpeg,png,webp,tif}
//   -> public/media/<name>-<width>.webp (+ .avif)
//   -> src/data/media-manifest.json  { name: { width, height, sizes: [w...] } }
//
// Two sizes per image (1x / 2x of the largest on-page slot). Never upscales:
// a source narrower than a target width just yields fewer sizes.
//
// Usage: node scripts/optimize-images.mjs [--force]
import sharp from 'sharp';
import { existsSync, mkdirSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { basename, extname, join } from 'node:path';

const SRC = 'assets-src/images';
const OUT = 'public/media';
const MANIFEST = 'src/data/media-manifest.json';
const WIDTHS = [800, 1600];
const FORCE = process.argv.includes('--force');
const NAME_RE = /^(about|hero|og|\d{2}-[a-z0-9]+)(-[a-z0-9]+)*$/;

if (!existsSync(SRC)) {
  console.error(`No ${SRC}/ folder. Export images there first (see README > Asset pipeline).`);
  process.exit(1);
}
mkdirSync(OUT, { recursive: true });

const manifest = {};
const files = readdirSync(SRC).filter((f) => /\.(jpe?g|png|webp|tiff?)$/i.test(f));

for (const file of files) {
  const name = basename(file, extname(file));
  if (!NAME_RE.test(name)) {
    console.warn(`skip ${file}: name does not follow NN-slug-asset convention`);
    continue;
  }
  const input = join(SRC, file);
  const meta = await sharp(input).metadata();
  const sizes = [...new Set(WIDTHS.map((w) => Math.min(w, meta.width)))];

  for (const w of sizes) {
    for (const [fmt, opts] of [
      ['webp', { quality: 80 }],
      ['avif', { quality: 55 }],
    ]) {
      const out = join(OUT, `${name}-${w}.${fmt}`);
      if (!FORCE && existsSync(out) && statSync(out).mtimeMs > statSync(input).mtimeMs) continue;
      await sharp(input).resize({ width: w, withoutEnlargement: true })[fmt](opts).toFile(out);
    }
  }
  manifest[name] = { width: meta.width, height: meta.height, sizes };
}

const sorted = Object.fromEntries(Object.entries(manifest).sort(([a], [b]) => a.localeCompare(b)));
writeFileSync(MANIFEST, JSON.stringify(sorted, null, 2) + '\n');
console.log(`optimized ${Object.keys(sorted).length} images -> ${OUT}, manifest -> ${MANIFEST}`);
