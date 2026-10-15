// Self-host the Draco mesh decoder for <model-viewer> (it would otherwise load
// it from www.gstatic.com). Copies the decoder that ships with the installed
// three.js into public/draco/. Runs automatically before dev and build.
import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const SRC = 'node_modules/three/examples/jsm/libs/draco/gltf';
const OUT = 'public/draco';
mkdirSync(OUT, { recursive: true });
for (const f of ['draco_wasm_wrapper.js', 'draco_decoder.wasm']) copyFileSync(join(SRC, f), join(OUT, f));
