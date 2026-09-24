# STM-U6 — Asset cache-busting
**Depends on:** U5 merged.

## Why
The planner found this on the live site on 2026-09-24, after U4 deployed.
- On `stemma.neworbitdigital.com`, `/assets/style.css` and `/assets/app.js` are served with `cache-control: public, max-age=14400` (4 hours). This comes from the zone's static-file cache setting.
- HTML and `/data/stemma.json` are served with `max-age=0, must-revalidate`.
- So after a deploy, a returning browser can pair new HTML with up to 4 hours of stale CSS and JS.
- **Observed:** `/timeline/?family=…` loaded the new page with the pre-U4 `app.js` (6752 bytes, served from cache) and the pre-U4 `style.css`. The family filter silently did nothing.
- Once both assets were re-fetched, the filter worked: 3 of 5 rows shown for `afghani-x-colombian-gold`.
- `stemma-9j6.pages.dev` serves assets with `max-age=0`, so it isn't affected.

## Deliverables
1. **Fingerprinted asset URLs.**
   - `tools/build.py` computes a short content hash for each file it copies into `dist/assets/`: the first 10 hex characters of its sha256.
   - Every page references the asset as `/assets/<name>?v=<hash>`. Use the template placeholder mechanism (`{{css_href}}`, `{{js_href}}`, or equivalent). Don't hand-edit the pages.
   - The hash must change whenever the file's bytes change, and must stay the same across rebuilds of unchanged files. The deterministic-build rule still holds.
2. **`dist/_headers`** (the Cloudflare Pages headers file), written by the build:
   - `/assets/*`: `Cache-Control: public, max-age=31536000, immutable`. Safe, because every reference is versioned.
   - Leave HTML and data at Pages' default. Don't add rules for them.
3. **Leaflet stays pinned and unversioned by us.** The cdnjs URLs from U5 keep their exact version and must not get a `?v=`.
4. **Test** (`tests/test_site.py` or a new file):
   - Every `/assets/` reference in every built page carries `?v=`, and its value equals the hash of the built file.
   - Changing a byte in `site/assets/app.js` changes the hash, checked in a temp copy.
   - `_headers` exists and contains the `/assets/*` rule.

## Out of scope
Visual design changes, file renaming (query-string versioning is enough), and any Cloudflare dashboard setting.

## Acceptance (paste the actual output)
- `python3 tools/run_tests.py` passes. Paste the total.
- `node --check site/assets/app.js` passes.
- Build the fixtures with `--out /tmp/dist` and paste:
  - `grep -o 'assets/[a-z.]*?v=[0-9a-f]*' /tmp/dist/index.html /tmp/dist/timeline/index.html`
  - `sha256sum /tmp/dist/assets/*`
  - `cat /tmp/dist/_headers`
- Build twice and show that the `?v=` values are identical.
