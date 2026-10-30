# Commit City

This folder is what builds the city at the top of the profile README one level up.

A night-time New York built from your GitHub contribution graph.

- One building per day. Height = commits that day.
- Days with no commits become parks.
- Weekdays are avenues. Months are cross streets. The weekend lives across the river, joined by bridges.
- Lit windows, water towers, rooftop HVAC, fire escapes, neon signs, billboards with your name, taxis with headlights, traffic lights, a ferry, a moon.
- The camera flies down the avenue, then along the river past the skyline, and loops.

The city is rendered by a GitHub Action every morning and committed as `city/commit-city.webp` (an animated WebP, a few MB) plus `city/commit-city.png` (a still, for anything that can't play WebP). The README just shows an image.

## Put it in your profile README

These files already live in this profile repo. The README one level up shows the image with:

```html
<p align="center">
  <picture>
    <source srcset="./city/commit-city.webp" type="image/webp">
    <img src="./city/commit-city.png" alt="Commit City: my last 52 weeks of commits as a night-time city" width="100%">
  </picture>
</p>
```

Then run the workflow once from the Actions tab (`Commit City` → `Run workflow`). It fetches your contributions, renders 150 frames in headless Chromium, builds the loop with ffmpeg and commits it. After that it runs daily.

The Action's own `GITHUB_TOKEN` is enough for public contributions. If you want private contributions counted too, add a personal token with `read:user` as a repository secret and pass it as `GITHUB_TOKEN` in the workflow.

## Run it locally

```bash
npm install
pip install playwright pillow && python -m playwright install chromium
node scripts/synthetic.mjs            # or: GITHUB_TOKEN=... node scripts/fetch.mjs
python scripts/render.py --single 0.6 --out out/test     # one frame to look at
python scripts/render.py --frames 150 --out out/frames   # the whole loop
python scripts/assemble.py                               # -> city/commit-city.webp + .png (add --gif for a GIF too)
```

To watch it live in a browser: `npm run preview` and open `http://localhost:8080/city/index.html`.

## Files

- `city/city.js` — the scene. Buildings, streets, bridges, cars, camera path. All the knobs are at the top.
- `city/index.html` — loads it.
- `scripts/fetch.mjs` — contributions → `city/data.json`.
- `scripts/synthetic.mjs` — fake data for trying it without a token.
- `scripts/render.py` — frames via Playwright (software WebGL, works on any CI runner).
- `scripts/assemble.py` — frames → animated WebP, poster PNG, optional GIF.
- `.github/workflows/commit-city.yml` — the nightly rebuild.
