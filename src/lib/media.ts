// Build-time helpers for media that may not exist yet.
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import manifest from '../data/media-manifest.json';

type Entry = { width: number; height: number; sizes: number[] };
const images = manifest as Record<string, Entry>;

export const hasPublic = (file: string) => existsSync(join(process.cwd(), 'public', 'media', file));

export const imageEntry = (name: string): Entry | undefined => images[name];

/** URL of the largest WebP of an image, for posters. */
export const posterUrl = (name?: string) => {
  const e = name ? images[name] : undefined;
  return e ? `/media/${name}-${Math.max(...e.sizes)}.webp` : undefined;
};
