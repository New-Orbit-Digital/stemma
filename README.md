# Stemma

An evidence-backed catalog of cannabis strain lineage and history. Enter a strain, see where it came from: parents, ancestors back to landraces, when and where it emerged, and how sure we are about each claim.

- **Stemma** (this repo, v1): the catalog plus a static site at `stemma.neworbitdigital.com`.
- **Budlogs** (future, v2): a Letterboxd-style social app for logging strains, reserved at `budlogs.neworbitdigital.com`. Budlogs consumes Stemma's compiled dataset (`dist/data/stemma.json`) the way Letterboxd consumes TMDB.

## How it's organized
- `catalog/strains/<id>.json`: one card per strain. Format: [docs/schema.md](docs/schema.md).
- `tools/`: stdlib-only Python. `validate.py` checks cards, `build.py` compiles the dataset and site into `dist/`.
- `site/`: plain HTML templates plus one stylesheet and one script. `build.py` substitutes `{{placeholder}}` values into them; the site reads only `data/stemma.json` at runtime.
- `docs/`: `always.md` (stable context), `current.md` (volatile state), `backlog.md`, `schema.md`, `packets/` (executor units).
- `CLAUDE.md`: executor working notes. `CHANGELOG.md`: shipped history.

## Commands
```
python3 tools/validate.py     # check the catalog
python3 tools/build.py        # compile the site and dataset into dist/
python3 tools/run_tests.py    # run the test suite
```
`--path` picks a different card directory and `--out` a different output directory, e.g.
`python3 tools/build.py --path tests/fixtures/valid --out /tmp/dist`.
