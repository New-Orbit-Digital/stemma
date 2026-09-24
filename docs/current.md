# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

**Last close-out:** the overnight planner run, 2026-09-24 (Sprint 2B).

## Headline
- STM-U8 (inline links and browse pages) is merged.
- The 9 existing Skunk-family summaries are rewritten in the house voice, with links.
- The full Haze family is written as draft cards (14 new/upgraded cards, 2 new stubs), sourced and spot-checked against live pages.

**Catalog is now 28 cards** (23 draft, 5 stub), up from 13 last close-out.

## What merged tonight (with evidence)

| PR | What | Merge SHA | Evidence |
|---|---|---|---|
| #33 | **STM-U8**: inline `[[...]]` links, browse pages, `tools/countries.py` | `f36baa6` | See below |
| #34 | Task 2: voice rewrite of the 9 Skunk-family summaries | `c1382fa` | See below |
| #35 | Task 3 (1/3): `haze`, `mexican-sativa`, `thai`, `south-indian`; stubs `silver-pearl`, `chitral`; `northern-lights-5` stub → draft | `c5214b0` | See below |
| #36 | Task 3 (2/3): `northern-lights-5-x-haze`, `nevilles-haze`, `silver-haze`, `jack-herer`, `super-silver-haze`, `amnesia-haze` | `c21ff42` | See below |
| #37 | Task 3 (3/3): `lemon-skunk`, `lemon-haze`, `super-lemon-haze` | `57d3f24` | See below |
| this PR | Close-out docs | — | — |

### #33 (STM-U8) evidence
- Adjudicated PASS at head `1be0e29`; `mergeable_state` clean.
- **Acceptance output posted by the executor:** 205 tests, 0 failures; `node --check` exit 0; real catalog `validate.py` 13 cards/0 errors; `build.py` 13 strains, 12 edges, 13 browse pages (31 pages total); fixture build 12 browse pages with the full markup-form summary rendered; fixture link resolution 374 hrefs checked (72 under `/browse/`), 0 unresolved; per-rule E11–E14 fixture output.
- Scope confirmed via file diff: 24 files, no `catalog/strains/` or `.github/workflows/` changes.
- Judgment calls accepted (7, listed on the PR): new rule ids E12–E14, `TL` added to the country map, breeder slugs left as-is pending the planner's cleanup, origin-country link on the `place` text, bare-prefix default link text, schema docs updated in-unit, slug collisions raise loudly.
- Merged under the standing STM-U8 advance permission (below — now **EXPIRED**).

### #34 (Task 2 voice rewrite) evidence
- All 9 cards' visible-text lengths checked locally against the real `tools/links.py`/`tools/countries.py` logic before push: 217–397 characters, all under the 400 limit.
- Every `[[...]]` link resolves: strain ids, `kind`/`label` enum values, `country` codes present on some card's `origin.country`, and `breeder:Sacred Seeds`/`breeder:Sensi Seeds` matching the cleaned `breeder` fields exactly.
- `skunk-1.breeder` cleaned to `"Sacred Seeds"` (was `"Sacred Seeds (David Watson, aka Sam the Skunkman)"`); the person now appears in the summary prose.
- No facts changed — voice rewrite only. `mergeable_state` clean at merge.

### #35–#37 (Task 3, Haze family) evidence
- Each card's key facts were spot-checked against one live source via WebFetch before writing (a subagent ran 14 fetches). Two corrections came out of that pass and are recorded in the affected cards' own source notes:
  - **Haze's parentage:** SeedFinder's live page describes a three-way Colombian cross, not the four-landrace account — already flagged as disputed in `docs/research/haze.md`; the card states both accounts.
  - **Lemon Skunk's "Citral" parent:** Green House's own live page says Citral has Indian heritage, contradicting SeedFinder's guess that it means Chitral, Pakistan. `chitral` is now a soft, disputed mention in prose, not a structural parent (`parents: ["skunk-1"]` only).
  - Minor softenings also made on `northern-lights-5` (dropped an unconfirmed "founded 1984" detail) and `silver-haze` (Silver Pearl naming attributed to SeedFinder specifically, since Sensi's own page doesn't name it).
- All 14 new/upgraded cards under the 400-character visible-text limit; every link resolves (checked locally before each push).
- `mergeable_state` clean on all three PRs; Cloudflare Pages preview deploys succeeded on #35 (confirms `validate.py`/`build.py` passed on the real catalog).
- Planner defaults applied per `docs/research/haze.md`'s open questions:
  - Haze's Mexican parent: generic `mexican-sativa` (not `acapulco-gold`).
  - Jack Herer parents: Leafly's set (`haze`, `northern-lights-5`, `shiva-skunk`); SeedFinder's alternative (no Shiva Skunk) stated in prose.
  - Amnesia Haze parents: `[]` (unknown), given genuinely disputed origin; `breeder` also left `null` to avoid implying a false connection to `skunk-1`'s unrelated "Sacred Seeds" breeder via Soma's similarly-named company.
  - Northern Lights #5 `kind`: `cut`.
  - Lemon Skunk: one card (the Green House line); DNA Genetics' line mentioned in prose only.
  - Lemon Haze: kept (weakest-sourced card in the family — see morning checklist).
- Stopped after Haze, per instructions. OG Kush not started.

## Justin's morning checklist (Sprint 2B)

### A. Live-site checks (sandbox proxy blocks the site — the planner couldn't check these)
1. **Inline links render** in the Skunk-family and Haze-family summaries: strain links go to `/s/<id>/`, and `breeder`/`kind`/`country`/`label` links go to their `/browse/...` pages.
2. **Browse pages** exist and list the right cards for each dimension, including the new `Haze Brothers`, `Green House Seed Co.`, and `The Seed Bank` breeder pages, and the new `TH`/`IN` country pages.
3. **Strain-header field links**: `breeder`, `kind`, origin country, and `traditional_label` link out on strain pages, including the newly-populated Haze-family pages.
4. **`/browse/` index** lists all dimension values with correct counts (should now include several new breeders and two new countries, TH and IN).

### B. Voice spot-check — 3–4 rewritten Skunk-family summaries
Read for whether the Reference voice landed right:
- `skunk-1` (follows Justin's own `docs/voice.md` sample closely).
- `acapulco-gold` (same — also follows the voice.md sample).
- `afghani-x-colombian-gold` (the "proto-Skunk" unnamed cross — check the hedged tone on the disputed originator).
- `super-skunk` or `shiva-skunk` (shorter, more mechanical cards — check they don't read as dry).

### C. Haze card spot-checks (5, each with its source)
1. **`haze`** — the four-landrace vs. three-way-Colombian dispute. Source: [SeedFinder](https://seedfinder.eu/en/strain-info/haze/unknown-or-legendary).
2. **`jack-herer`** — the Leafly vs. SeedFinder parent-set disagreement (Shiva Skunk in or out). Source: [SeedFinder](https://seedfinder.eu/en/strain-info/jack-herer/sensi-seeds).
3. **`lemon-skunk`** — the Citral/Chitral correction (Indian heritage per the breeder, not confirmed Pakistani). Source: [Green House Seed Co.](https://shop.greenhouseseeds.nl/feminised-cannabis-seeds/lemon-skunk/).
4. **`amnesia-haze`** — the disputed origin and the deliberately empty `parents`/`null` `breeder`. Source: [Soma's Sacred Seeds](https://www.somaseeds.nl/product/amnesia-haze).
5. **`super-silver-haze`** — the three Cup wins and the Roskam/Shantibaba credit dispute. Source: [Green House Seed Co.](https://shop.greenhouseseeds.nl/feminised-cannabis-seeds/super-silver-haze/).

### D. Decisions
1. **Lemon Skunk / Soma naming collision:** is leaving `chitral` out of the structural `parents` (prose-only, disputed) the right call, or should it go back in per the original SeedFinder guess?
2. **Lemon Haze's thin sourcing:** acceptable for v1 as a draft with undocumented breeder/origin, or should it be pulled pending better sources?
3. **Amnesia Haze's `breeder: null`:** agree with keeping it unset to avoid implying a link between Soma's "Sacred Seeds" and Skunk #1's unrelated "Sacred Seeds", or would a distinctly-named breeder value (e.g. "Soma Seeds") be clearer?
4. **Interface direction** — still open, see carried-forward item below.

### Carried forward from the previous checklist (still open)
1. **U7 live-site checks** (tier badges gone, quiet sources list, uniform lineage/map lines, About page copy, the `skunk-1`/`acapulco-gold` migrated-page specifics, timeline/map marker counts) — not yet confirmed done by Justin.
2. **Interface direction:** pick A "Library card", B "Quiet app", C "Field notes", or a mix. See `docs/prep/stemma-interface.md`.
3. **`tools/check_migration.py`:** keep or delete. Still backing the U7 mechanical proof; the planner's default remains to keep it until the next tooling unit.

## State (after tonight)

### Units
- U1–U8 are merged: #8, #9, #13, #15, #19, #21, #27, and #33.
- No executor unit is in flight.

### Catalog
**28 cards** (23 draft, 5 stub), all schema v2 with inline-link markup where applicable.
- **23 drafts:** the original 9 (`skunk-1`, `afghani-x-colombian-gold`, `acapulco-gold`, `afghani`, `colombian-gold`, `super-skunk`, `early-skunk`, `shiva-skunk`, `skunk-kush`, now voice-rewritten) plus 14 new/upgraded tonight (`northern-lights-5`, `haze`, `mexican-sativa`, `thai`, `south-indian`, `northern-lights-5-x-haze`, `nevilles-haze`, `silver-haze`, `jack-herer`, `super-silver-haze`, `amnesia-haze`, `lemon-skunk`, `lemon-haze`, `super-lemon-haze`).
- **5 stubs:** `early-pearl`, `hindu-kush`, `nepalese` (carried over), plus `silver-pearl` and `chitral` (new tonight).
- **None marked `reviewed` yet.** Citations were spot-checked (one live source per card) but not exhaustively verified against every listed source.

### Hosting
- Live on Cloudflare Pages at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`.
- PRs get preview deploys; #35's preview deploy succeeded, confirming the real-catalog build passed.

### Docs
- `docs/voice.md` (house voice, 2a "Reference") and `docs/packets/STM-U8.md` are unchanged tonight — both already merged before this session started.
- `docs/schema.md` and `schema/strain.schema.json` gained the link/E12–E14 rules in #33.
- `docs/backlog.md` updated in this PR: R2 (Haze) moved from "notes done, cards blocked" to "cards written, sourced, and merged."

## Connector facts
- **GitHub connector:** no workflows, administration, or secrets permission. Check runs return 403, so `mergeable_state` is the CI evidence; re-read 30–60s after pushes (this held again tonight — U8 and both catalog PRs went clean within about 2 minutes of push).
- **Sandbox proxy:** blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs. Live checks go to Justin's checklist.
- **Private repo:** `git clone` from the sandbox has no credentials. Use the connector for all reads.
- **Cloudflare dashboard:** Justin's hands only.

## Advance permissions in effect
- **STM-U8:** **EXPIRED.** Merged in #33 on 2026-09-24, per Justin's advance permission (chat, 2026-09-24 ~03:30 UTC): "auto-merge STM-U8 on a clean PASS; after it merges, rewrite the 9 existing draft summaries in the house voice with links, and write the Haze cards from docs/research/haze.md."
- **Task 2 (voice rewrite) and Task 3 (Haze cards):** both executed under the same 2026-09-24 advance permission, now also **EXPIRED** (scope complete — Haze is done, and the planner stopped before OG Kush per instructions).
- **Catalog-card and docs PRs:** the planner merges on a clean pass. Standing.
- **Small fix units:** auto-merge on a clean PASS. Standing.
- **A clean PASS means:** every acceptance check has its actual output posted and each output matches; scope is respected; no stops were tripped; `mergeable_state` is clean.

## Next
1. Justin runs the morning checklist: live-site checks, voice and Haze-card spot-checks, and the decisions above.
2. R3: the OG Kush family — research notes first, then cards once Justin has spot-checked the Haze voice.
3. Optionally, resume STM-U8's visual-pass follow-on once Justin picks an interface direction.
