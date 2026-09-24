# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

**Last update:** the planner, 2026-09-24 ~12:40 UTC, after Justin's Sprint 2B verification.

## Headline
- **Sprint 2B is verified.** Justin confirmed on 2026-09-24:
  - The live checks pass.
  - The voice read passes.
  - The Haze spot-checks are good.
- **Two new rules** (see `docs/always.md` and `docs/voice.md`):
  - Populate first, don't adjudicate.
  - Same-name breeders get a qualifier, the way film databases handle duplicate titles.
- **Card work is paused until Justin's usage rolls over** (about 16:30 UTC on 2026-09-24). A scheduled planner run then does R3.

## Sprint 2B verification (Justin, 2026-09-24)
- **A. Live-site checks: pass.** This covers:
  - Inline links.
  - Browse pages, including the new breeders and TH/IN.
  - Strain-header field links.
  - The `/browse/` index counts.
- **B. Voice read: pass.** Justin read `skunk-1`, `acapulco-gold`, `afghani-x-colombian-gold`, and `shiva-skunk`.
- **C. Haze spot-checks: good.** Justin checked `haze`, `jack-herer`, `lemon-skunk`, `amnesia-haze`, and `super-silver-haze`.
- **D. Decisions:**
  1. **Chitral stays out of Lemon Skunk's parents, as a prose mention only.** Justin isn't concerned with disputed theories.
  2. **Lemon Haze stays as a draft.** Its thin sourcing is fine for v1.
  3. **Amnesia Haze's breeder is now `"Soma's Sacred Seeds"`, set in this PR.** Soma's full name is already distinct from Skunk #1's "Sacred Seeds", so no qualifier is needed. The summary links it with `[[breeder:Soma's Sacred Seeds]]`. Going forward, same-name breeders get a location or year qualifier per `docs/voice.md`.
  4. **The interface direction is still open.** See `docs/prep/stemma-interface.md`.

## Still open (carried forward)
1. **U7 live-site checks.** These were likely covered by Justin's live pass, but he hasn't confirmed them item by item. Low priority.
2. **Interface direction:** A "Library card", B "Quiet app", C "Field notes", or a mix.
3. **`tools/check_migration.py`:** keep or delete. The planner defaults to keeping it until the next tooling unit.

## Sprint plan
| Sprint | Scope | Status |
|---|---|---|
| 1 | v1 features (U1–U6) and the Skunk family | VERIFIED |
| 2 | U7 and U8, then the Haze and OG Kush families | **2A/2B VERIFIED** (U7, U8, and Haze). **2C: R3 OG Kush**, queued after the usage rollover. |
| 3 | GSC and Blue Dream families | Then launch readiness |

**Launch readiness:**
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Age-notice copy.

## State
- **Units:** U1–U8 are merged (#8, #9, #13, #15, #19, #21, #27, and #33). No executor unit is in flight.
- **Catalog:** 28 cards, 23 draft and 5 stub, all in schema v2 and the house voice.
- **Hosting:** live at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`. PRs get preview deploys.

## Connector facts
- **GitHub connector:**
  - It has no workflows, administration, or secrets permission.
  - Check runs return 403, so `mergeable_state` is the CI evidence. Re-read it 30–60 seconds after a push.
- **Sandbox proxy:** it blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs. Live checks go to Justin, or to the built-in browser when it's linked.
- **Private repo:** `git clone` has no credentials, so use the connector.
- **Cloudflare dashboard:** Justin's hands only.

## Advance permissions in effect
- **Catalog-card and docs PRs:** the planner merges on a clean pass. Standing.
- **Small fix units:** auto-merge on a clean PASS. Standing.
- **R3 (OG Kush family) research and cards:** write them in the house voice under the populate-first rule, and merge each on a clean pass (Justin, 2026-09-24). Run it after the usage rollover, and stop at the Sprint 2 stop point with a checklist.
- **A clean PASS means:**
  - Every acceptance check has its actual output posted, and each output matches.
  - Scope is respected.
  - No stops were tripped.
  - `mergeable_state` is clean.

## Next
1. **After ~16:30 UTC:** the scheduled planner run does R3, the OG Kush family. It writes cards directly (no separate notes step, since the voice is settled), then posts the Sprint 2 stop-point checklist.
2. **Then:** Justin's Sprint 2 bulk verification, and the go for Sprint 3 (GSC and Blue Dream).
