# Stemma

A community-maintained catalog of cannabis strain lineage and history. Enter a strain and see where it came from: its parents, its ancestors back to landraces, and when and where it emerged. Each card lists its sources, and where accounts differ, the card says so.

- **Stemma** (this repo, v1): the catalog plus a static site at `stemma.neworbitdigital.com`.
- **Budlogs** (future, v2): a Letterboxd-style social app for logging strains, reserved at `budlogs.neworbitdigital.com`. Budlogs consumes Stemma's compiled dataset (`dist/data/stemma.json`) the way Letterboxd consumes TMDB.

## How it's organized
- `catalog/strains/<id>.json`: one card per strain. Format: [docs/schema.md](docs/schema.md).
- `tools/`: stdlib-only Python. `validate.py` checks cards, `build.py` compiles the dataset and site into `dist/`.
- `site/`: plain HTML templates plus one stylesheet and one script. `build.py` substitutes `{{placeholder}}` values into them; the site reads only `data/stemma.json` at runtime. `{{base}}` is the build's base path — see [Hosting](#hosting).
- `docs/`: `always.md` (stable context), `current.md` (volatile state), `backlog.md`, `schema.md`, `packets/` (executor units), `research/` (research notes), `prep/` (suggestions for Justin).
- `CLAUDE.md`: executor working notes. `CHANGELOG.md`: shipped history.

## Commands
```
python3 tools/validate.py     # check the catalog
python3 tools/build.py        # compile the site and dataset into dist/
python3 tools/run_tests.py    # run the test suite
```
`--path` picks a different card directory and `--out` a different output directory, e.g.
`python3 tools/build.py --path tests/fixtures/valid --out /tmp/dist`.

## Hosting
The same tree builds for either host. `--base` is where the site is mounted, and every internal URL the build emits goes through it (`tools/urls.py`), so nothing is hard-coded to the root.

| Target | Build | Notes |
| --- | --- | --- |
| Cloudflare Pages — `stemma.neworbitdigital.com` | `python3 tools/build.py` (base `/`, the default) | Writes `_headers`, which gives `/assets/*` a one-year immutable cache. |
| GitHub Pages — `justbost.com/stemma/` | `python3 tools/build.py --base /stemma/ --out dist` | A project site, so everything lives under `/stemma/`. No `_headers`: GitHub Pages ignores it. |

`--base` is normalized to start and end with a slash, so `stemma`, `/stemma`, and `/stemma/` all mean the same thing. It is a URL prefix, not a directory: `--out` is still the site root, and the pages are written where they have always been written. The base is also written onto `<body data-base="…">`, which is where `site/assets/app.js` reads it.

The GitHub Pages deploy runs from a workflow the repo does not carry: [`docs/github-pages-workflow.yml`](docs/github-pages-workflow.yml) is the draft to paste into `.github/workflows/pages.yml`.
