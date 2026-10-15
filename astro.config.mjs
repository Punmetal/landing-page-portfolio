import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.vercel.app', // [TODO] real domain; keep in sync with src/data/site.ts
  compressHTML: true,
  build: { inlineStylesheets: 'auto' },
});
