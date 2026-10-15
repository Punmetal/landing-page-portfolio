// 3D pipeline: assets-src/3d/<name>.glb (exported from Blender, glTF Binary)
//   -> public/media/<name>.glb  Draco-compressed, textures resized to <=2048
//      and converted to WebP, unused data pruned.
// Uses the gltf-transform CLI through npx (downloaded on first run).
//
// Usage: npm run assets:3d
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const SRC = 'assets-src/3d';
const OUT = 'public/media';
if (!existsSync(SRC)) {
  console.log(`No ${SRC}/ folder. Export GLB files from Blender there first.`);
  process.exit(0);
}
mkdirSync(OUT, { recursive: true });

for (const file of readdirSync(SRC).filter((f) => f.toLowerCase().endsWith('.glb'))) {
  const input = join(SRC, file);
  const output = join(OUT, file.toLowerCase());
  console.log(`→ ${file}`);
  execFileSync(
    'npx',
    ['--yes', '@gltf-transform/cli@4', 'optimize', input, output,
     '--compress', 'draco', '--texture-compress', 'webp', '--texture-size', '2048'],
    { stdio: 'inherit', shell: process.platform === 'win32' },
  );
  const kb = (n) => `${Math.round(statSync(n).size / 1024)} KB`;
  console.log(`  ${kb(input)} -> ${kb(output)}`);
}
