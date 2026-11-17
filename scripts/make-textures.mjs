// Red liquid/swirl hero background (stand-in for the portfolio cover
// texture) from an SVG turbulence filter
//   -> public/media/hero-swirl-1600.webp, hero-swirl-2400.webp
// Replace with a real texture export by dropping assets-src/images/hero-swirl.jpg
// and running `npm run assets` instead.
//
// Usage: node scripts/make-textures.mjs
import sharp from 'sharp';

const BASE = '#E8222B';
const BAND = '#C9151D';
const steps = Array.from({ length: 16 }, (_, i) => i % 2).join(' ');

const svg = (w, h) => `
<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 1600 900" preserveAspectRatio="none">
  <filter id="f" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.0011 0.0019" numOctaves="2" seed="11" result="t"/>
    <feGaussianBlur in="t" stdDeviation="10" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.7 0 0 0 -0.35" result="a"/>
    <feComponentTransfer in="a" result="b"><feFuncA type="discrete" tableValues="${steps}"/></feComponentTransfer>
    <feFlood flood-color="${BAND}" flood-opacity="0.6"/>
    <feComposite in2="b" operator="in" result="stripes"/>
    <feFlood flood-color="${BASE}" result="bg"/>
    <feMerge><feMergeNode in="bg"/><feMergeNode in="stripes"/></feMerge>
  </filter>
  <rect width="1600" height="900" filter="url(#f)"/>
</svg>`;

// Render at 2x then downscale for smooth band edges.
const master = await sharp(Buffer.from(svg(4800, 2700))).png().toBuffer();
for (const w of [1600, 2400]) {
  await sharp(master)
    .resize({ width: w })
    .blur(w / 1000)
    .flatten({ background: BASE })
    .webp({ quality: 72 })
    .toFile(`public/media/hero-swirl-${w}.webp`);
}
console.log('hero texture -> public/media/hero-swirl-{1600,2400}.webp');
