import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.vercel.app', // [TODO] real domain; keep in sync with src/data/site.ts
  compressHTML: true,
  build: { inlineStylesheets: 'auto' },
  // model-viewer (~1MB) is a lazily imported chunk, only fetched when a 3D slot is visible
  vite: { build: { chunkSizeWarningLimit: 1200 } },
});
