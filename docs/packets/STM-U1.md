# STM-U1 — Catalog tooling: validator, dataset build, test runner
**Depends on:** nothing. **Blocks:** U2 to U5 and all research merges.

## Context
The catalog is one JSON card per strain in `catalog/strains/`. The contract is `docs/schema.md`; read it completely before starting. Tooling is stdlib-only Python 3.12, with no third-party imports.

## Deliverables
1. **`tools/validate.py`**
   - Loads every `catalog/strains/*.json` and enforces every rule in `docs/schema.md`.
   - Takes an optional `--path <dir>` argument, so tests can point it at fixture directories.
   - **Rule ids** (every error line must start with its id, for example `E05 catalog/strains/x.json: parent 'y' not found`):
     - **E01** — JSON parse failure.
     - **E02** — `id` is malformed, doesn't match the filename, or duplicates another card.
     - **E03** — a required field for the card's status is missing, or an enum value is invalid.
     - **E04** — an evidence item's `source` doesn't resolve to the card's `sources`, or source ids are duplicated.
     - **E05** — a parent or dispute-parent id doesn't exist as a card, or a card lists itself.
     - **E06** — the lineage graph has a cycle. Report the cycle path.
     - **E07** — a lineage status/parents rule is broken (the table in schema.md).
     - **E08** — a non-unknown claim has no evidence.
     - **E09** — a born-range rule is broken (`year_min ≤ year_max`, both within 1900 to the current year).
     - **E10** — `lat`/`lon` are out of range or have more than 1 decimal place.
     - **E11** — `summary` exceeds 400 characters.
     - **W1** and **W2** — the warnings in schema.md. Printed, but they don't fail the run.
   - Exit code is 0 when there are no errors (warnings allowed) and 1 otherwise.
   - Always ends with a summary line: `N cards, E errors, W warnings`.
2. **`tools/build.py`**
   - Runs validation first and aborts with exit code 1 if there are errors.
   - Writes `dist/data/stemma.json` exactly as specified in schema.md's "Compiled dataset" section.
   - Strains are sorted by id. Edges are sorted by (child, parent, disputed).
   - `best_tier` is the highest-ranked tier among that parent's evidence items.
   - Creates `dist/` if missing.
   - For U1, emit only the data file. The site comes in U2.
3. **`tools/run_tests.py`**
   - Stdlib `unittest` discovery over `tests/`.
   - Prints the totals and exits nonzero on any failure.
4. **`tests/`**
   - Fixtures under `tests/fixtures/valid/`: at least 5 cards covering a root landrace, a known cross, a partial, a disputed card, and a stub. All ids must be `fixture-*`.
   - One invalid fixture directory per error rule under `tests/fixtures/invalid/E01/` through `E11/`, each isolating that rule.
   - Tests assert: the valid set passes; each invalid set fails with its rule id present in the output; W1 is reported without failing; `build.py` output is deterministic (build twice, compare with `generated` excluded); and the edge `best_tier` values are right.

## Out of scope
- Don't write any real strain cards.
- Don't touch `docs/`, `CLAUDE.md`, or the workflows.

## Acceptance (paste the actual output into the PR)
- `python3 tools/validate.py` on the empty real catalog → exit 0, `0 cards, 0 errors, 0 warnings`.
- `python3 tools/validate.py --path tests/fixtures/valid` → exit 0.
- `python3 tools/run_tests.py` → all pass. Paste the total.
- `python3 tools/build.py` → exit 0 and `dist/data/stemma.json` exists. Paste its first 20 lines.
- `grep -rE "^(import|from) " tools/` shows stdlib modules only.

## Stops
- If any rule in schema.md is ambiguous enough that two implementations would disagree, STOP and report the ambiguity instead of choosing.
