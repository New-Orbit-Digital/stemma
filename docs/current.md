# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## Sprint plan (Justin, chat, 2026-09-24)
The v1 goal is the 5 seed families traced back to landraces, roughly 80–100 cards. Work runs in sprints. Each sprint ends at a stop point, where the planner halts and Justin does one bulk verification pass.

| Sprint | Scope | Status |
|---|---|---|
| 1 | v1 features (U1–U6) and the Skunk family | **VERIFIED by Justin, 2026-09-24: "all pass."** |
| 2 | U7 (schema v2), then the Haze and OG Kush families | **ACTIVE.** Runs overnight 2026-09-24 in a fresh scheduled session. |
| 3 | GSC and Blue Dream families | ~80–100 cards, then launch readiness |

**Launch readiness:**
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Age-notice copy.

### Sprint 1 verification (Justin, 2026-09-24)
- **A. Phone click-through: all pass.** Search, the Skunk #1 graph and its scrolling, the disputed toggle, the timeline and map filters, and a shared `?family=` URL.
- **B. Card spot-checks: all pass.** `skunk-1`, `super-skunk`, `shiva-skunk`, `acapulco-gold`, and `colombian-gold`.
- **C. Decisions:**
  1. **Web Analytics:** Justin reports it was already off. The page still loads a `static.cloudflareinsights.com` beacon. It's logged in the backlog for a low-priority dashboard look.
  2. **Sources:** categorize them rather than rank them. De-emphasize source and badge presentation. See `always.md` (community-catalog model).
  3. **Folklore/authority distinctions:** these create too much friction. Simplify, and park tiers and disputes in the backlog. This is implemented by STM-U7.
  4. **Research sprints:** they're decision-free, so they may run unattended.
  5. **Name:** keep "Stemma" for now.

## Sprint 2 rules (Justin, chat, 2026-09-24)
**U7 first.**
- It's filed as an issue and triggered.
- It auto-merges on a clean PASS.
- It's then checked live.

**Research cards:**
- Write them in schema v2, and only after U7 merges.
- Merge them as `draft` on clean CI.
- Every card needs a summary and at least one categorized source.

**Tonight's usage cap:**
- Stop after U7 plus the Haze family, not the full sprint. This keeps usage down.
- Then write the prep doc described below and post the checklist.

**Prep doc for the morning (no decisions taken):**
- Stemma interface suggestions: a clean direction in the spirit of Claude's UI.
- Justin isn't ready to think about the Budlogs interface. Budlogs work stays non-UI only.

**Small fix units:** still allowed. Auto-merge on a clean PASS.

## State (2026-09-24)
**Units:**
- U1–U6 are merged. See PRs #8, #9, #13, #15, #19, and #21.
- U6 was checked live: assets are served `immutable` and versioned, HTML revalidates, and Leaflet loads with SRI.
- **U7:** the packet is `docs/packets/STM-U7.md`. The issue and trigger follow this docs PR.

**Catalog:** 13 cards, schema v1 until U7 migrates them.
- 9 drafts:
  - `skunk-1`
  - `afghani-x-colombian-gold`
  - `acapulco-gold`
  - `afghani`
  - `colombian-gold`
  - `super-skunk`
  - `early-skunk`
  - `shiva-skunk`
  - `skunk-kush`
- 4 stubs:
  - `early-pearl`
  - `northern-lights-5`
  - `hindu-kush`
  - `nepalese`

**Hosting:** live on Cloudflare Pages at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`. PRs get preview deploys.

## Connector facts
- **GitHub connector:**
  - No workflows, administration, or secrets permission.
  - Check runs and status return 403, so `mergeable_state` is the CI evidence.
  - CI logs can be read in the built-in browser when the desktop is linked. Step logs don't always render.
- **Sandbox proxy:**
  - It blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs.
  - Live checks need the built-in browser. When that isn't available, defer them to Justin's checklist.
- **Cloudflare dashboard:** Justin's hands only.

## Advance permissions in effect
- **STM-U7:** auto-merge on a clean PASS (Justin, 2026-09-24). Expires when U7 merges.
- **Catalog-card and docs PRs:** the planner merges on a clean pass. Standing.
- **Small fix units:** auto-merge on a clean PASS. Renewed for Sprint 2.
- **A clean PASS means:**
  - Every acceptance check has its actual output posted, and each output matches.
  - Scope is respected.
  - No stops were tripped.
  - `mergeable_state` is clean.

## Next (overnight, fresh scheduled session)
1. File and trigger STM-U7. Adjudicate it and merge it.
2. Haze family research in schema v2. Merge on clean CI.
3. Write the Stemma interface suggestions prep doc as `docs/prep/stemma-interface.md`.
4. Stop. Post a summary and a Sprint 2A checklist for Justin, then update this file.
