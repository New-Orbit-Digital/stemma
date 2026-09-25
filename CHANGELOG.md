# Changelog
Append-only, session-grained, newest first. A shipped summary is appended at every close-out.

## 2026-09-25 — Moved to justbost.com/stemma/ (GitHub Pages)
- **Live at `https://justbost.com/stemma/`** from `.github/workflows/pages.yml` (Pages source: GitHub Actions), first deployed at `cee98f2` (#76). The repo went public the same day.
- **Cloudflare becomes a 301:** at base `/`, `build.py` now writes `_redirects` (`/*  https://justbost.com/stemma/:splat  301`), so `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev` forward every path. The subpath build writes none, since a `/*` rule there would loop. Two tests cover this. The Cloudflare project must stay up to keep serving the redirect.
- **Pre-public checks (planner, 2026-09-25):**
  - Secret scan of all history: 179 commits across every branch and `refs/pull/*`, for API-key, token, JWT, private-key, and `service_role` patterns, with 0 hits. No secret-named file was ever committed.
  - Copied-text check: 0 quoted spans of 25+ characters in any summary or source note. 16 cards sampled across the 8 most-cited source sites, checking 6-word shingles against the live source page: 14 share nothing, and 2 share one 6–7-word run each (names and parent lists). The JointCommerce pages rendered only about 250 words, so that comparison is weaker.
- **Live verification (in-app browser, 2026-09-25):**
  - `/`, `s/og-kush/`, `browse/`, `browse/breeder/t-h-seeds/`, `timeline/?family=og-kush`, `map/`, `about/`, `data/stemma.json`, and `screenshot.png` all return 200. A bogus path returns 404.
  - The dataset has 566 strains and 355 edges. Assets load from `/stemma/assets/…`, with 142 CSS rules applied.
  - Search "chem 91" gives 1 match and lands on `/stemma/s/chemdawg/`.
  - The map (`?family=og-kush`) loads Leaflet, 5 markers, 2 arcs, and tiles, and its popups link to `/stemma/s/…`.
  - A fresh tab across the five main pages logged 0 console errors, and every request returned 200.

## 2026-09-25 — STM-H1: a configurable base path
- **The build takes `--base`** (default `/`), normalized to start and end with a slash, so `stemma` and `/stemma/` mean the same thing. It is a URL prefix, not a directory: `--out` is still the site root.
- **`tools/urls.py` is the one place a site URL is spelled.** `build.py`, `browse.py`, `lineage.py`, `links.py`, `origins.py`, and `timeline.py` all route through it instead of hard-coding `/`. The *path* a page is written to and the *URL* it is linked by are now separate spellings; only the URL carries the base.
- **Templates take `{{base}}`**, and the shell writes it onto `<body data-base="…">`, which is where `site/assets/app.js` reads it for `DATA_URL` and its result-row hrefs.
- **`_headers` is Cloudflare's**, so it is written only at base `/`. `site/screenshot.png` is copied when the file exists.
- **`docs/github-pages-workflow.yml`** drafts the Pages deploy for `justbost.com/stemma/`, to be pasted into `.github/workflows/pages.yml`. No CNAME: the org site owns the domain.
- **Nothing changes at `stemma.neworbitdigital.com`.** The base `/` build is byte-identical to the previous one apart from the new `data-base="/"` attribute and app.js's own bytes. The Cloudflare → justbost.com redirect is a later unit.

## 2026-09-24 — Sprint 2A (overnight planner run)
- **STM-U7 merged (#27, `d58b30d`): schema v2, the community-catalog model.**
  - Per-claim evidence tiers and structured disputes are removed.
  - Sources are one flat, categorized list: breeder, publication, database, or community.
  - The site is simplified: no tier badges, a quiet sources list, uniform graph and map lines, and a rewritten About page.
  - All 13 cards were migrated mechanically. Facts are unchanged, as the executor's proof and the planner's field scan both confirm.
  - Build: 13 strains, 12 edges. The disputed Acapulco Gold → Nepalese edge is gone.
- **R2 Haze research notes (#28):** `docs/research/haze.md` covers 15 strains. Cards wait on the house-voice decision.
- **Interface prep (#29):** `docs/prep/stemma-interface.md` offers three directions for Justin to react to.
- **Close-out docs:**
  - current.md, backlog.md, and this changelog.
  - README.md and project-instructions.md updated to the community-catalog model.

## 2026-09-23 — Project kickoff
- Repo seeded by the planner: README, CLAUDE.md, docs tiers (always / current / backlog), card schema spec v1, packets STM-U1 to STM-U5, executor and CI workflows.
- Decisions recorded in `docs/always.md`: static site with repo-stored JSON cards, four evidence tiers, stable strain IDs, stdlib-only tooling, Stemma/Budlogs product split.
