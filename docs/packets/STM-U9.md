# STM-U9 — Chemotype fields (cannabinoids, terpenes)
**Depends on:** U8 merged.

**Decision (Justin, chat, 2026-09-24):** Justin surfaced five external cannabis-strain databases
and asked to seed Stemma with more than lineage. `docs/backlog.md` already parked "Chemotype
fields" as v2+ work; this unit adds them. Effects, flavors, and medical-condition data stay out
(Justin, 2026-09-24: subjective and not widely verified; see `docs/always.md`).

## Summary of the change
- Add one new optional card field, `chemotype`, holding cannabinoid ranges (THC, CBD) and a
  dominant-terpene list.
- Purely additive: every existing card validates unchanged with no `chemotype` key.
  `schema_version` stays 2, per the STM-U8 precedent for backward-compatible additions to the
  compiled dataset.
- Schema and tooling only. No card content changes. Populating `chemotype` on real strains is
  separate research work (see `docs/backlog.md`, R6), because the executor rule against authoring
  strain facts still holds.
- Effects, flavors, and medical-condition fields are out. Don't add them.

## 1. Card schema (extend `docs/schema.md`; add this row to the field table, after `growing`)

| Field | Required | Type / values | Notes |
|---|---|---|---|
| `chemotype` | optional | `{thc?, cbd?, dominant_terpenes?}` | Defaults to absent (not modeled). At least one of the three sub-fields must be set if the key is present. |

**`chemotype.thc` / `chemotype.cbd` shape** — same pattern as `born`:
- Known: `{ "min": 18.0, "max": 24.0, "display": "18–24%" }`. `min` and `max` are percent by dry
  weight, `0 ≤ min ≤ max ≤ 100`, each with at most 1 decimal place.
- Unknown: `{ "unknown": true, "display": "..." }`. Use only if a card needs to say something
  (e.g. "trace") without a number; otherwise omit the sub-field entirely.

**`chemotype.dominant_terpenes` shape:** an ordered array, most-dominant first:
`[ { "name": "myrcene", "percent": 0.35 }, { "name": "limonene" } ]`. `name` is required (lowercase,
the terpene's common name). `percent` is optional, because a source doesn't always give one. When
present it is percent by dry weight, `0 ≤ percent ≤ 100`, with at most 2 decimal places (terpene
concentrations run far smaller than cannabinoid ones, so 1 decimal would round real values to zero).

**New validator errors:**
- **E15:** `chemotype` is present but empty (none of `thc`, `cbd`, `dominant_terpenes` set), or a
  `thc`/`cbd` range has `min > max`, a value outside 0–100, or more than 1 decimal place.
- **E16:** a `dominant_terpenes` entry has no `name`, or its `percent` is outside 0–100 or has more
  than 2 decimal places.

**New validator warning:**
- **W4:** `chemotype` is present but no entry in the card's `sources` list has
  `category: "database"`. A nudge, not a rule. Don't fail the card over it.

## 2. Dataset
- `dist/data/stemma.json` keeps `schema_version: 2`. Cards that carry a `chemotype` include it
  as-is in the compiled output; cards that don't omit the key. No changes to `edges`.

## 3. Site
- Strain page: when `chemotype` is present, add one plain-text line under the existing `growing`
  line, e.g. "THC 18–24%, CBD <1%. Dominant terpenes: myrcene, limonene, caryophyllene." No
  badges, charts, or color-coding. The parked visual-design pass hasn't started.
- No graph, timeline, or map changes. No new browse pages for terpenes (that's an
  information-architecture decision: flag it, don't build it).

## 4. Fixtures and tests
- Add fixtures under `tests/fixtures/` (obviously fictional ids) covering: a valid full
  `chemotype`; a valid `chemotype` with only `dominant_terpenes` and no percents; E15 (empty
  `chemotype`); E15 (`min > max`); E16 (bad `percent`); W4 (`chemotype` present, no `database`
  source).
- Extend `tools/validate.py`'s tests and `docs/schema.md`'s error and warning tables with E15, E16,
  and W4, in the same style as the existing rows.
- Add a `chemotype` definition to `schema/strain.schema.json`'s `$defs`, consistent with `born` and
  `growing` there (reference only; `tools/validate.py` stays authoritative).

## 5. Out of scope
- Populating `chemotype` on any real card in `catalog/strains/`.
- Effects, flavors, and medical-condition fields.
- Per-field source citation UI.
- Any visual-design work beyond the one plain-text line above.

## Acceptance (paste the actual output)
- **Tests:** `python3 tools/run_tests.py` passes. Paste the total.
- **Validator, unchanged catalog:** `python3 tools/validate.py` on the current catalog (no card
  carries `chemotype` yet) prints 0 errors and the same warning count as `main`. Paste it.
- **Validator, fixtures:** paste output showing each new fixture triggers exactly the error or
  warning it's meant to, and nothing else.
- **Build:** `python3 tools/build.py` prints the same strain and edge counts as `main`, and
  `dist/data/stemma.json` still reports `"schema_version": 2`.
- **JS syntax:** `node --check site/assets/app.js` passes.
- **Docs:** paste the diff of `docs/schema.md` and `schema/strain.schema.json`.
