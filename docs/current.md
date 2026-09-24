# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

**Last close-out:** the overnight planner run, 2026-09-24 (Sprint 2A).

## Headline
- STM-U7 (schema v2, the community-catalog model) is merged.
- The Haze family research notes are merged.
- The Stemma interface prep doc is merged.

**No cards were written tonight.** Per Justin (about 02:55 UTC), Haze card prose waits until he picks a house voice. The notes are ready to turn into cards once that's decided.

## What merged tonight (with evidence)

| PR | What | Merge SHA | Evidence |
|---|---|---|---|
| #27 | **STM-U7**: schema v2 (closes #26) | `d58b30d` | See below |
| #28 | R2 Haze research notes, `docs/research/haze.md` | `8fc0f04` | `mergeable_state` clean; docs only |
| #29 | Interface prep, `docs/prep/stemma-interface.md` | `0780368` | `mergeable_state` clean; docs only |
| this PR | Close-out docs | — | — |

### #27 evidence
- Clean PASS, adjudicated at head `e49fc59` (adjudication comment on #27).
- **Acceptance output posted by the executor:**
  - Tests: 155, 0 failures.
  - `node --check`: exit 0.
  - Validator: `13 cards, 0 errors, 0 warnings`.
  - Build: `13 strains, 12 edges`.
  - Mechanical proof: `13 cards compared against 2e7ccc2, 0 with changed facts`.
  - Tier/dispute grep: only the word "documented" inside colombian-gold's summary prose.
- **Planner's independent check:** every catalog patch was scanned for aliases, kind, status, traditional_label, growing, and updated. Only whitespace and comma reflow changed; all values are the same.
- Merged under the STM-U7 advance permission, which has now expired.
- **Judgment calls accepted:**
  1. Acapulco Gold's dispute note was dropped along with the dispute.
  2. Super Skunk's multiple notes per source were joined into one.

## Sprint plan

| Sprint | Scope | Status |
|---|---|---|
| 1 | v1 features (U1–U6) and the Skunk family | **VERIFIED** by Justin, 2026-09-24 |
| 2 | U7, then the Haze and OG Kush families | **2A done:** U7 merged, Haze notes ready. **Cards are blocked on the voice decision.** OG Kush not started, per tonight's usage cap. |
| 3 | GSC and Blue Dream families | ~80–100 cards, then launch readiness |

**Launch readiness:**
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Age-notice copy.

## Justin's morning checklist (Sprint 2A)

### A. Live-site checks of U7
Check these on `stemma.neworbitdigital.com`. The sandbox proxy blocks the site, so the planner couldn't check it.
1. **No tier badges** anywhere on strain pages, and no "Disputed" block.
2. **Quiet sources list** at the bottom of a strain page. Each entry shows:
   - a linked title
   - the publisher
   - a small muted category word
   It has no numbers or badges.
3. **Uniform lines:**
   - The lineage graph uses one edge style with no tier legend and no disputed toggle.
   - The map arcs are one style with no tier legend.
4. **About page:**
   - It uses the community-catalog framing: categories are descriptive, not a ranking; accounts can differ; and indica/sativa is only a traditional label.
   - It includes "not medical advice."
   - It has no tier or dispute language.
5. **Migrated pages:**
   - `/s/skunk-1/`: 4 sources, 2 breeder and 2 database; parents are Afghani x Colombian Gold and Acapulco Gold.
   - `/s/acapulco-gold/`: no parents, the Nepalese edge is gone, and the summary still mentions the Nepalese claim; 3 sources.
6. **Timeline and map** still load and filter. The map should show 5 markers and 6 arcs.

### B. Decisions that came up
1. **House voice for card prose.** This is the blocker for the Haze cards.
2. **Interface direction.** Pick A "Library card", B "Quiet app", C "Field notes", or a mix. See `docs/prep/stemma-interface.md`.
3. **Haze modelling calls.** These are in the open questions at the end of `docs/research/haze.md`. The planner's defaults apply unless Justin overrides them.
   - Haze's Mexican parent: generic `mexican-sativa`, or `acapulco-gold`?
   - Jack Herer's parents: the Leafly set or the SeedFinder set?
   - Amnesia Haze: unknown parents, or Soma's landraces?
   - Lemon Skunk: one card or two?
   - Northern Lights #5: a `cut` or a `cultivar`?
   - Lemon Haze: keep it or drop it?
4. **`tools/check_migration.py`:**
   - Keep it or delete it.
   - It isn't in the packet, but it backs the U7 mechanical proof.
   - The planner's default is to keep it until the next tooling unit.

## State (after tonight)

### Units
- U1–U7 are merged: #8, #9, #13, #15, #19, #21, and #27.
- No executor unit is in flight.

### Catalog
13 cards, now in **schema v2**. There are no new cards tonight.
- **9 drafts:**
  - `skunk-1`
  - `afghani-x-colombian-gold`
  - `acapulco-gold`
  - `afghani`
  - `colombian-gold`
  - `super-skunk`
  - `early-skunk`
  - `shiva-skunk`
  - `skunk-kush`
- **4 stubs:**
  - `early-pearl`
  - `northern-lights-5`
  - `hindu-kush`
  - `nepalese`

### Research
- `docs/research/haze.md`: 15 strains.
  - 12 new ids.
  - 1 stub to upgrade (`northern-lights-5`).
  - Haze-link notes for `colombian-gold`.
- Two more stubs are needed: `silver-pearl` and `chitral`.
- Citations have not been checked yet. That's required before any card is marked `reviewed`.

### Hosting
- Live on Cloudflare Pages at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`.
- PRs get preview deploys.

### Docs
- `README.md` and `docs/project-instructions.md` were updated in this PR to the community-catalog model. They previously said "evidence-backed" and "cited and tiered".
- **Justin:** if the Project's instructions were pasted from the old file, re-paste them.

## Connector facts
- **GitHub connector:**
  - No workflows, administration, or secrets permission.
  - Check runs and status return 403, so `mergeable_state` is the CI evidence.
  - `unstable` shows while checks are pending. Re-read after 30–60 seconds; #29 went clean after about 2 minutes.
- **Sandbox proxy:**
  - It blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs.
  - Live checks go to Justin's checklist unless the built-in browser is available.
- **Private repo:** `git clone` from the sandbox has no credentials. Use the connector for all reads.
- **Cloudflare dashboard:** Justin's hands only.

## Advance permissions in effect
- **STM-U7:** EXPIRED. U7 merged in #27 on 2026-09-24.
- **Catalog-card and docs PRs:** the planner merges on a clean pass. Standing.
- **Small fix units:** auto-merge on a clean PASS. Renewed for Sprint 2.
- **A clean PASS means:**
  - Every acceptance check has its actual output posted, and each output matches.
  - Scope is respected.
  - No stops were tripped.
  - `mergeable_state` is clean.

## Next
1. Justin runs the morning checklist and picks a house voice and an interface direction.
2. Write the Haze cards from `docs/research/haze.md` in the chosen voice. Status is `draft`, with a planner check of each citation. Merge on clean CI.
3. R3: the OG Kush family, research notes first if the voice is still open.
4. Optionally, STM-U8: a visual pass from the chosen interface direction.
