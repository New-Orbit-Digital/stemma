# STM-U2 — Site scaffold: search, strain pages, about, age notice
**Depends on:** U1 merged. **Blocks:** U3, U4, U5, and hosting.

## Context
Extend `tools/build.py` so it compiles a static site into `dist/` alongside `dist/data/stemma.json`. Cloudflare Pages will run `python3 tools/build.py` and serve `dist/`. Follow CLAUDE.md's front-end conventions: vanilla HTML/CSS/JS, mobile-first, light/dark mode, and runtime reads only `data/stemma.json`. Strain pages are generated at build time, so each has a permanent URL for QR codes.

## Deliverables
1. **`site/` source templates and assets**
   - Plain HTML files with simple `{{placeholder}}` substitution, done by `build.py` using stdlib string handling.
   - One shared `site/assets/style.css` and `site/assets/app.js`.
2. **`dist/index.html` — search**
   - Name-and-alias typeahead over `data/stemma.json`, case- and punctuation-insensitive. For example, "skunk 1" finds "Skunk #1".
   - Results link to the strain page. When there's no match, say "Not in the catalog yet."
3. **`dist/s/<id>/index.html` — one page per card**
   - Generated at build time, with the card data inlined into the page for the first render.
   - Shows: name and aliases, kind, the traditional label (with a small "what this means" link to About), summary, born display, origin place, breeder, and the parents as links.
   - Children are computed from edges and shown as links.
   - Disputes are shown as a "Disputed" block listing each claim.
   - Every claim shows an evidence-tier badge.
   - A sources list gives title, publisher, and a link.
   - Stub cards render "Not yet cataloged" with parents and children only.
   - Placeholder `<div id="lineage-graph">` is left for U3.
4. **`dist/about/index.html`**
   - What Stemma is, and the four evidence tiers in plain language, including the genetic-testing caveat.
   - Why indica/sativa is a traditional label.
   - How to read disputes.
   - "Not medical advice."
5. **Age notice**
   - A one-time 21+ interstitial on first visit. Acknowledgment is stored in `localStorage` as `stemma_age_ok=1`.
   - It must not block crawlers from reading the HTML, so overlay it with CSS/JS rather than redirecting.
6. **`dist/404.html`** and a `<meta name="robots" content="noindex">` on every page for now, while the catalog is thin.
7. **Build smoke test** — `tests/test_site.py` asserts:
   - Every strain in the dataset has `dist/s/<id>/index.html`.
   - Every internal link in `dist/` resolves to a file.
   - No page references `catalog/`.

## Out of scope
The graph, the timeline, the map, and any JS library.

## Acceptance (paste the actual output)
- Build the valid fixtures into a temp dist with `python3 tools/build.py --catalog tests/fixtures/valid --out /tmp/dist`. Add both flags if they don't exist yet. Paste `find /tmp/dist -type f | sort`.
- `python3 tools/run_tests.py` → all pass. Paste the total.
- `node --check dist/assets/app.js` passes (or the equivalent `site/` path).
- Serve with `python3 -m http.server --directory /tmp/dist 8000` briefly and fetch `/`, `/about/`, and one `/s/<id>/` page with `python3 -c` using urllib. Paste the status codes.
