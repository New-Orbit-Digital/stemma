# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## Sprint plan (Justin, chat, 2026-09-24)
The total v1 goal is the 5 seed families traced to their landraces: about 80–100 cards. The work runs in sprints. Each sprint ends at a **stop point**. At the stop point, the planner halts, prepares **one bulk verification checklist**, and Justin verifies everything in a single pass.

| Sprint | Scope | Stop point |
|---|---|---|
| **1 (active)** | Finish v1 features (U5 map, U6 cache fix), and complete the **Skunk family** (~15 cards) | U5 and U6 merged and live, and the Skunk family complete |
| 2 | Haze and OG Kush families | ~40 cards |
| 3 | GSC and Blue Dream families | ~80–100 cards, then launch readiness |

**Launch readiness (after Sprint 3):**
- A `reviewed` pass on the cards.
- Drop `noindex`.
- A trademark check on "Stemma".
- Age-notice copy.

**Bulk verification checklist (prepared at each stop point).** Justin's single pass covers:
- Click through the site on his phone: search, a strain page, the graph, the timeline and map filters, and a shared `?family=` URL.
- Spot-check about 5 planner-chosen cards against their sources.
- Answer one batched decision block.

### Sprint 1 rules (Justin, chat, 2026-09-24)
- **Cards ship as `draft` mid-sprint.** They merge on a clean CI pass with every claim sourced and tiered. Justin spot-checks a sample at the stop point. The upgrade to `reviewed` happens in launch readiness.
- **Small fix units.** The planner may design, file, and auto-merge small fix/hardening units that it discovers. These are bug fixes that add no new feature or product surface, merged on a clean PASS. New features wait for Justin's go.
- **Functionality before aesthetics.** See `always.md`. Verification checks behaviour, not looks.

## State (2026-09-24)
- **Repo:** `New-Orbit-Digital/stemma`.
  - `main` is protected: PR required, 0 approvals, no bypass. Set by Justin.
- **Workflows on `main`:** `.github/workflows/ci.yml` and `claude.yml`, both created by Justin.
- **Executor secret:** `CLAUDE_CODE_OAUTH_TOKEN` is an ORG secret, proven by the U1–U4 runs.
- **Executor app:** the "Claude" GitHub App is installed on all org repos.

### Units
- **STM-U1 (#1): MERGED** as `dbb93b9` (#8).
- **STM-U2 (#2): MERGED** as `bd79021` (#9).
- **STM-U3 (#3): MERGED** as `12ce446` (#13).
  - CI run #20 against the real catalog passed.
- **STM-U4 (#4): MERGED** as `2a59f95` (#15).
  - Tests: 95 pass.
  - Bar counts: 4 bars for 4 dated cards in fixtures, and 1 bar for 1 dated card in the real catalog.
  - **Live check (2026-09-24):**
    - `/timeline/?family=afghani-x-colombian-gold` shows 3 of 5 rows. `acapulco-gold` and `skunk-1` are hidden.
    - The "See on timeline" link is present on strain pages.
    - This only works after a forced asset refresh. See U6.
- **STM-U5 (#5): TRIGGERED** 2026-09-24.
- **STM-U6 (#17): FILED.** Asset cache-busting.
  - The custom domain serves `/assets/*` with `max-age=14400`, so after a deploy returning browsers ran stale JS and CSS against new HTML.
  - Trigger after U5 merges.

### Catalog: 6 cards, all `draft`
- `skunk-1`, `afghani-x-colombian-gold`, and `acapulco-gold` (#6), with the follow-ups listed on #6.
- `afghani` and `colombian-gold` (#12).
- `super-skunk` (#18, CI run #28 passed). All evidence is breeder-claimed (Sensi Seeds). The Afghan parent is generic.

### Hosting: LIVE
- **Deployment:** Cloudflare Pages project `stemma`, from `main`, with build command `python3 tools/build.py` and output directory `dist`.
- **URLs:** `https://stemma-9j6.pages.dev` and `https://stemma.neworbitdigital.com`.
- **First deploy check (2026-09-24 ~01:20 UTC):**
  - All pages return 200.
  - The dataset held 5 strains and 4 edges.
  - `/s/skunk-1/` renders its 5-node graph on both domains.
- **Justin's phone check (2026-09-24):**
  - The Skunk #1 page renders in dark mode.
  - The graph fits the screen, so it doesn't scroll, and the page doesn't scroll sideways.
  - Light mode is deferred under functionality-first.

## Connector facts
- **GitHub connector:**
  - It authenticates as the GitHub App "Claude Github MCP Connector".
  - It has no workflows, administration, or secrets permission.
  - So chat cannot write `.github/workflows/*`, create repos, set branch protection, or manage secrets.
- **CI evidence:**
  - Check runs and combined status return 403, so the PR's `mergeable_state` is the CI evidence.
  - CI job pages can be read in the built-in browser (GitHub is signed in there). Step logs don't always expand.
- **Sandbox network:** the egress proxy blocks `*.pages.dev` and `neworbitdigital.com`. Deploy checks go through the built-in browser.
- **Cloudflare:** the built-in browser does not share Justin's Cloudflare session. Dashboard work is Justin's hands.

## Advance permissions in effect
- **Auto-merge STM-U5 on a clean PASS** (2026-09-23/24). Expires when U5 merges.
- **Auto-merge STM-U6 on a clean PASS** (Justin: "go on u6", 2026-09-24 ~01:37 UTC). Expires when U6 merges.
- **Catalog-card and docs PRs:** the planner merges on a clean pass (2026-09-24). Standing, until Justin revokes it.
- **Small fix units:** the planner designs, files, and auto-merges them on a clean PASS (2026-09-24). Standing for Sprint 1; renew per sprint.
- **PASS** for any unit means all of the following:
  - Every acceptance check has actual output posted, and it matches.
  - Scope is respected.
  - No stops were tripped.
  - `mergeable_state` is clean.

## Next
1. Adjudicate U5, then merge. Trigger U6; adjudicate and merge it.
2. Finish the Skunk family:
   - The Dutch Skunk lines (Sensi's Early Skunk, Shiva Skunk, Skunk Kush, and others).
   - The #6 follow-ups: tiers, the unused source, the Acapulco Gold dispute, and shorter `born.display` strings.
3. At the stop point, post the bulk verification checklist to Justin.
