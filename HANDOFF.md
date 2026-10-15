# HANDOFF

_Last updated: 2026-10-15 (cloud session). Branch: `claude/amazing-gauss-wbx2iv`. Nothing merged to `main` yet._

## Status

Full page is built and running on stand-in images cropped from the portfolio frames.
Not deployed. Repo is private. Site carries `noindex` until Pun approves going public.

### Done
- Astro static site, self-hosted Archivo Black + IBM Plex Sans Thai, no analytics or trackers
- Sections: Hero (red swirl, PORTFOLIO wordmark, CTAs) → About → Experience / Skills & Tools /
  Education → Selected work (bookshelf) → 7 project sections → Contact (red block, back to top)
- Content from Drive frames (port-beta-6). Decisions applied:
  - Project 02 title follows the poster: **Startup Standup Comedy**
  - All projects use the heading **My Role**
  - Sybil Husky description = the bullets from the frame
  - Enter to Start summary rewritten from first person (same facts):
    "Created artwork for social media posts, events, and video projects, including illustrations,
    infographics, posters, banners, and motion graphics."
  - No skill-level numbers, no hobbies, no "4+ years"
  - Contact: email, LinkedIn, Behance. **Phone not shown.**
- Asset pipeline: images (WebP/AVIF, 2 sizes, manifest), video (MP4+WebM+poster), 3D (Draco GLB),
  stand-in cropper, missing-asset report (`npm run assets:check`)
- Lazy video slot and lazy `<model-viewer>` slot both tested end-to-end with sample files
  (removed afterwards); click-to-load embed facade component ready (not used yet)
- Responsive check at 360 / 768 / 1440: no horizontal scroll
- README with setup, pipeline and deploy notes

### Lighthouse (local `astro preview`, Lighthouse 12)

| Run | Performance | Accessibility | Best Practices | SEO |
| --- | --- | --- | --- | --- |
| Mobile, as shipped (noindex) | 100 | 100 | 100 | 69* |
| Mobile, noindex removed | 100 | 100 | 100 | 100 |
| Desktop, noindex removed | 100 | 100 | 100 | 100 |

Mobile: FCP 1.0 s, LCP 1.3 s, TBT 0 ms, CLS 0.008.
\*SEO 69 is only the intentional `noindex`. Scores are with small stand-in images; re-run on the
Vercel preview once the real 2x exports are in (heavier images will cost some Performance).

## Next
1. Pun exports real assets (list below) → `npm run assets` → re-check layout and Lighthouse
2. Set up Vercel project with Deployment Protection (ask Pun first)
3. Optional: try Archivo **expanded** width for the wordmark (closer to the cover typography)
4. Rights confirmation before any public URL (below)

## Design changes after first review
- Project index is now a CSS 3D **bookshelf** (cloth-bound books, chrome-foil title stamped on the cloth;
  hover lifts, 1st click turns it cover-out, 2nd click goes to the project; open book tilts with
  the cursor like the ID card; even gaps on both sides of the open book; touch = cover scroller)
- About photo replaced by a hanging **holographic ID card** (name, "Visual Designer"), foil and
  glare follow the cursor, idle sway, glossy metallic rim; reduced-motion users get a static card
- Grain texture removed. **Light mode** added (follows the OS by default; the switch in the nav
  saves the visitor's choice in localStorage). Red hero/contact stay red in both themes.
  Lighthouse mobile: dark 100/100, light 99–100/100 (Perf/A11y)

- Hero and Contact red backgrounds are a **live WebGL liquid** (slow looping domain-warped bands,
  ~30fps at 0.6x resolution, paused off-screen). Skipped on software rendering (no GPU) and
  starts after load, so Lighthouse stays 100; static swirl image is the fallback.
  Test it in headless/no-GPU browsers with `?liquid=force`.
- Spine text back to black ink, debossed

- Wordmark + section headings (About me, Experience, Skills & Tools, Education, Selected work)
  use **BBH Bartle** (self-hosted, latin, ~8KB). It is very wide, so each heading is sized from its
  container with `--fit` (longest word width in em) and capped at the old size

- **Project showcase = 16:9 slides on desktop (≥1200px)**, traced from the PDF pages. Box
  coordinates live in `src/data/layouts.ts` (1280×720 page pixels) and also drive the stand-in
  crops. Pages: 01 K2O 2 + Motion & 3D, 02 1 + Motion, 03–05 1 each, 06 2 + Motion, 07 2 + Motion & 3D.
  Each slide fits the viewport; if text ever runs long the slide grows rather than clipping.
  Below 1200px the same markup stacks (text, then images in 2 columns). Real exports: export each
  image at 2× its box size with the same aspect ratio (see README › Adding media)

- **Sticky nav** slides in after the hero (hidden over Contact): current project "03 / 07 …"
  with a jump back to the shelf, section links, theme switch. Phones: brand + project + switch
- **Lightbox**: every placed project image is a button that opens it full-screen (native
  `<dialog>`); arrows/swipe step through that project's images, Esc/× closes, focus returns

## Open questions
- [ ] Sybil Husky: who is the client / project owner? Notion says "real work" but no name.
- [ ] OK to show the contact line "Open to Visual, Graphic, Digital and UI / Web design roles."?
      (taken from Career Goals in Notion)
- [ ] Skills chips come from the Resume in Notion (supporting source). Keep?
- [ ] Hero texture is generated in code. Is there an original swirl texture file from the cover?
- [ ] Wordmark font: keep Archivo Black or switch to Archivo expanded?
- [ ] Domain for Vercel / OG URLs (`[TODO]` in `astro.config.mjs` and `src/data/site.ts`)

## [CHECK RIGHTS] — confirm before publishing publicly
| Project | Client / owner | Notes |
| --- | --- | --- |
| 01 K2O Songkran Music Festival | S2O Festival | Artist photos (BUS, DAOU, FIFTY FIFTY, KISS OF LIFE, LNGSHOT, RIIZE), sponsor logos |
| 02 Startup Standup Comedy | Enter to Start | Event KV with Crypto Meetup Thailand logo, speaker photos |
| 03 Thumbnails & Posters | MollageBKK / Netflix Thailand | Netflix branding, talent photos, MasterChef Thailand |
| 04 Visual Content Design | Enter to Start | Includes one **Binance TH** post (FIFA World Cup game) |
| 05 Infographic | Enter to Start | Public-figure photos (Saylor, Musk, Biden) in the Bitcoin timeline |
| 07 Sybil Husky | [TODO] | NFT project, confirm owner and permission |
| Experience | Binance TH, MollageBKK, S2O, Enter to Start | Company names listed in the timeline |

## Missing assets (what Pun still needs to provide)

Run `npm run assets:check` for the live list. Every image is currently a **rough stand-in**
cropped from the 1280px frames (many are only 160–430px wide, so they look soft on screen).

**Images: export from Figma at 2x into `assets-src/images/`, same names:**
- `about-portrait.jpg` (higher-res portrait)
- 01: `01-k2o-kv`, `01-k2o-poster-{bus,daou,fiftyfifty,kissoflife,lngshot,riize}`, `01-k2o-logo`,
  `01-k2o-logo-water`, `01-k2o-merch-{tee,tiedye,black,wristbands}`, `01-k2o-map`
- 02: `02-standup-{kv,banners,billboard,wall-posters,poster-mockup,logo}`
- 03: `03-thumbs-{poster-ice,poster-jail,netflix-snow,masterchef,netflix-codex,netflix-whats,netflix-playback,netflix-backstage,netflix-yaya}`
- 04: `04-content-{post-tree-of-alpha,post-luck,webtoon,chatgpt,mortgage,dnft,buyback,layer2,call-center,credit-card,binance-worldcup}`
- 05: `05-info-{bitcoin-timeline,documentaries,ev-sales,ethereum,investing,pixar}`
- 06: `06-16p-{cover,spread-green,spread-purple,spread-blue,spread-yellow,characters,all-spreads}`
- 07: `07-sybil-{logo,environment,tiers,landing}`

**Video (MOV/MP4 into `assets-src/video/`):**
- `01-k2o-teaser` · `02-standup-motion` · `06-16p-flip` (book flip-through) · `07-sybil-prototype`

**3D (GLB from Blender into `assets-src/3d/`):**
- `01-k2o-logo.glb` · `07-sybil-card.glb`


**Other:**
- Rights confirmation (table above)
- Decision on phone number (currently hidden)

## Notes for the next session
- Large Drive originals cannot be pulled through the Drive connector (base64 too big for the
  session). Stand-ins came from the 1280px copies in the Notion Portfolio Library.
- `assets-src/` is git-ignored. To regenerate stand-ins on another machine, put the frames in
  `assets-src/frames/frame-<n>.jpg` and run `npm run assets:standins && npm run assets`.
