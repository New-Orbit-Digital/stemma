# STM-U9 — Schema v3: chemotype fields (cannabinoids, terpenes)
**Depends on:** U8 merged.

**Decision (Justin, chat, 2026-09-24):** Justin surfaced five external cannabis-strain databases
(Cannlytics, an independent "Demarily" aggregator API, Otreeba, the Shannon-Goddard
`cannabis-intelligence-database` GitHub project, and OpenTHC's VDB) and asked to use as much of
their enrichment data as possible to seed Stemma. `docs/backlog.md` already parked "Chemotype
fields" as v2+ work; this unit adds them.

## Summary of the change
- Add one new optional card field, `chemotype`, holding cannabinoid ranges (THC, CBD) and a
  dominant-terpene list.
- Purely additive: every existing card (28 today) validates unchanged with no `chemotype` key.
  `schema_version` stays 2, per the STM-U8 precedent for backward-compatible additions to the
  compiled dataset.
- Schema and tooling only. No card content changes — populating `chemotype` on real strains is
  separate research work (see `docs/backlog.md`, R6), because the executor rule against authoring
  strain facts still holds.
- Effects, flavors, and medical-condition fields (also offered by some of these sources) are
  explicitly OUT of scope — see "Open question" below.

## 1. Card schema v3 (extend `docs/schema.md`; add this row to the field table)

| Field | Required | Type / values | Notes |
|---|---|---|---|
| `chemotype` | optional | `{thc?, cbd?, dominant_terpenes?}` | Defaults to absent (not modeled). At least one of the three sub-fields must be set if the key is present. |

**`chemotype.thc` / `chemotype.cbd` shape** — same pattern as `born`:
- Known: `{ "min": 18.0, "max": 24.0, "display": "18–24%" }`. `min` and `max` are percent by dry
  weight, `0 ≤ min ≤ max ≤ 100`, each with at most 1 decimal place.
- Unknown: `{ "unknown": true, "display": "..." }` — use only if a card needs to say something
  (e.g. "trace") without a number; otherwise just omit the sub-field entirely.

**`chemotype.dominant_terpenes` shape:** an ordered array, most-dominant first:
`[ { "name": "myrcene", "percent": 0.35 }, { "name": "limonene" } ]`. `name` is required (lowercase,
the terpene's common name). `percent` is optional — a source doesn't always give one — and when
present is percent by dry weight, `0 ≤ percent ≤ 100` with at most 2 decimal places (terpene
concentrations run far smaller than cannabinoid ones, so 1 decimal would round real values to zero).

**New validator errors:**
- **E15:** `chemotype` is present but empty (none of `thc`, `cbd`, `dominant_terpenes` set), or a
  `thc`/`cbd` range has `min > max`, a value outside 0–100, or more than 1 decimal place.
- **E16:** a `dominant_terpenes` entry has no `name`, or its `percent` is outside 0–100 or has more
  than 2 decimal places.

**New validator warning:**
- **W4:** `chemotype` is present but no entry in the card's `sources` list has
  `category: "database"`. Chemotype numbers come from lab/aggregator data, not breeder pages or
  forum posts, so this is a nudge, not a rule — don't fail the card over it.

## 2. Dataset
- `dist/data/stemma.json` keeps `schema_version: 2`. Cards that carry a `chemotype` include it
  as-is in the compiled output; cards that don't just omit the key. No changes to `edges`.

## 3. Site
- Strain page: when `chemotype` is present, add a plain-text line under the existing `growing`
  line — e.g. "THC 18–24%, CBD <1%. Dominant terpenes: myrcene, limonene, caryophyllene." No
  badges, no charts, no color-coding — matches the quiet-list treatment sources already get, and
  the parked visual-design pass still hasn't started.
- No graph, timeline, or map changes. No new browse pages for terpenes (that's a real
  information-architecture decision — flag it, don't build it, if it comes up).

## 4. Fixtures and tests
- Add `tests/fixtures/example-chemotype.json` (or extend an existing fixture) covering: a valid
  full `chemotype`, a valid `chemotype` with only `dominant_terpenes` and no percents, an E15 case
  (empty `chemotype`), an E15 case (`min > max`), an E16 case (bad `percent`), and a W4 case
  (`chemotype` present, no `database` source).
- Extend `tools/validate.py`'s own test coverage and `docs/schema.md`'s error table with E15, E16,
  and W4, in the same style as the existing rows.
- Update `schema/strain.schema.json`'s `$defs` with a `chemotype` definition, consistent with how
  `born` and `growing` are already expressed there (reference only — `tools/validate.py` stays
  authoritative, per the file's own header).

## 5. Out of scope
- Populating `chemotype` on any real strain card (`catalog/strains/*.json`) — that's R6 in
  `docs/backlog.md`, a research unit, not this build unit.
- Effects, flavors, and medical-condition fields.
- Any per-field source citation UI beyond the card-level source list that already exists.
- Any visual-design work beyond the one plain-text line described above.

## Open question — surfaced, not decided here
Two of the five sources Justin found (Demarily, Shannon-Goddard) also carry **effects**,
**flavors**, and **medical-condition / recommended-activity** tags. `docs/voice.md`'s
banned-habits list explicitly excludes "effects, and medical claims" from card *prose*. Whether a
separate structured field (outside the summary, like `chemotype`) fits Stemma's reference-catalog
framing — or whether it reads too much like a dispensary menu — is a real product call. This unit
doesn't add those fields. If Justin wants them, that's a follow-up packet.

## Acceptance (paste the actual output)
- **Tests:** `python3 tools/run_tests.py` passes. Paste the total.
- **Validator, unchanged catalog:** `python3 tools/validate.py` on the current 28 cards (none carry
  `chemotype` yet) prints 0 errors and the same warning count as before this change. Paste it.
- **Validator, fixtures:** paste the validator's output against `tests/fixtures/`, showing every
  new fixture triggers exactly the error/warning it's meant to and nothing else.
- **Build:** `python3 tools/build.py` prints the same strain and edge counts as on `main` before
  this change, and `dist/data/stemma.json` still reports `"schema_version": 2`.
- **JS syntax:** `node --check site/assets/app.js` passes.
- **Docs:** paste the diff of `docs/schema.md` and `schema/strain.schema.json` showing the new
  field, error codes, and warning documented.
