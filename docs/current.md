# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## Sprint plan (Justin, chat, 2026-09-24)
The total v1 goal is the 5 seed families traced to their landraces, roughly 80–100 cards. Work runs in sprints. Each sprint ends at a **stop point**, where the planner halts and prepares **one bulk verification checklist** for Justin's single pass.

| Sprint | Scope | Stop point |
|---|---|---|
| 1 | v1 features (through U6) and the **Skunk family** | **REACHED 2026-09-24 ~02:01 UTC.** Awaiting Justin's verification pass. |
| 2 | Haze and OG Kush families | ~40 cards |
| 3 | GSC and Blue Dream families | ~80–100 cards, then launch readiness |

**Launch readiness** comes after Sprint 3:
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Trademark check on "Stemma".
- Age-notice copy.

### Sprint 1 rules (Justin, chat, 2026-09-24)
- **Cards ship as `draft` mid-sprint.** They merge on a clean CI pass, with every claim sourced and tiered.
- **Small fix units.** The planner may auto-merge small fix units on a clean PASS. New features wait for Justin's go.
- **Functionality before aesthetics.** See `always.md`.

## Sprint 1 stop point: bulk verification checklist
This checklist was posted to Justin in chat on 2026-09-24. Results get recorded here when he replies.

**A. Phone click-through** on `https://stemma.neworbitdigital.com`:
1. **Search.** Type "skunk 1" and confirm it finds Skunk #1. Type "shiva" and confirm it finds Shiva Skunk. Type something absent, like "blue dream", and confirm the page says "Not in the catalog yet."
2. **Strain page.** On `/s/skunk-1/`, confirm the graph shows the 3 roots plus the proto-Skunk cross above Skunk #1, with 4 children below: Super Skunk, Early Skunk, Shiva Skunk, and Skunk Kush. Tapping a node should navigate. Check the "See on timeline" and "See on map" links.
3. **Disputed toggle.** On `/s/acapulco-gold/`, tick "Show disputed links" and confirm a Nepalese link appears.
4. **Timeline.** On `/timeline/`, confirm the undated strip holds the landraces and undated crosses. Open `/timeline/?family=shiva-skunk` and confirm only Shiva Skunk and its ancestors show.
5. **Map.** On `/map/`, confirm the markers are Afghanistan, Colombia, Guerrero MX, Santa Cruz US, and the Netherlands. Open `/map/?family=super-skunk` and confirm lines run from Santa Cruz and Afghanistan to the Netherlands.
6. **Shared link.** Send yourself `/map/?family=skunk-1`, open it, and confirm it opens already filtered.

**B. Card spot-checks.** Open each card and its first source:
- `skunk-1`: parentage vs. Sensi Seeds' "Sam the Skunkman" interview.
- `super-skunk`: the 1990 launch, from the Sensi product page.
- `shiva-skunk`: released in 1987 as NL#5xSK#1, from the Sensi product page.
- `acapulco-gold`: Guerrero origin, the 1964 US record, and the Nepalese dispute, all from Wikipedia.
- `colombian-gold`: Santa Marta / Caribbean coast, from the UC Press listing for Britto's *Marijuana Boom*.

**C. Decisions:** posted in chat as a batched block.

## State (2026-09-24)
- **Repo:** `New-Orbit-Digital/stemma`.
  - `main` is at `84d1e93`.
  - `main` is protected: PR required, no bypass.
- **Workflows:** `ci.yml` and `claude.yml`, both Justin's.
- **Executor secret:** org-level `CLAUDE_CODE_OAUTH_TOKEN`, proven by the U1–U6 runs.

### Units: all six MERGED
| Unit | PR | Squash | Key evidence |
|---|---|---|---|
| U1 tooling | #8 | `dbb93b9` | validator, build, test runner |
| U2 site | #9 | `bd79021` | 32 tests; serve/fetch 200s |
| U3 graph | #13 | `12ce446` | 58 tests; CI run #20 on the real catalog |
| U4 timeline | #15 | `2a59f95` | 95 tests; live `?family=` filter hides the correct rows |
| U5 map | #19 | `cf18d75` | 149 tests; live Leaflet 1.9.4; tiles, markers, and 1 arc before this sprint's cards |
| U6 cache-busting + Leaflet SRI | #21 | `8c465a7` | 153 tests; live check below |

**Live check after U6** (2026-09-24 ~01:57 UTC, built-in browser):
- `/assets/app.js?v=3f74ce9c08` is served with `cache-control: public, max-age=31536000, immutable`.
- HTML is served with `max-age=0, must-revalidate`.
- Both Leaflet tags carry `integrity`, and Leaflet loads with those checks on.
- The page also loads a Cloudflare Web Analytics beacon (`static.cloudflareinsights.com`). This comes from Pages or zone settings, not the repo. See the decision block.

### Catalog: 13 cards (9 draft, 4 stub)
- **Drafts:**
  - `skunk-1`
  - `afghani-x-colombian-gold`
  - `acapulco-gold`: disputed, with a Nepalese folklore claim.
  - `afghani`
  - `colombian-gold`
  - `super-skunk` (#18)
  - `early-skunk`, `shiva-skunk`, and `skunk-kush` (#22)
- **Stubs:** `early-pearl`, `northern-lights-5`, `hindu-kush`, and `nepalese`.
- **#6 review follow-ups:** closed in #23.
  - Acapulco Gold dispute recorded.
  - Truncated labels shortened.
  - Unused sources now cited.
  - The generous `documented` tiers on Leafly, Barney's Farm, and Cannigma are left for the `reviewed` pass.
- **Live dataset** (`generated 2026-09-24T02:00:30Z`):
  - 13 strains and 13 edges, 1 of them disputed.
  - Pages for search, about, timeline, map, and sample strains all return 200.
  - The map draws 11 interactive layers.
- **Known data gap:** `afghani-x-colombian-gold` has no sourced origin, so the Afghanistan and Colombia lines to California can't be drawn.

### Hosting: LIVE
- Cloudflare Pages project `stemma`, served at `stemma-9j6.pages.dev` and `stemma.neworbitdigital.com`.
- Each PR now also gets a Cloudflare preview deploy check.

## Connector facts
- **GitHub.**
  - The GitHub App has no workflows, administration, or secrets permission.
  - Check runs and combined status return 403, so `mergeable_state` and the built-in browser serve as CI evidence.
  - Step logs don't always render in the browser.
- **Sandbox proxy.** It blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs. Live checks and SRI hashing go through the built-in browser.
- **Cloudflare.** The dashboard is Justin's hands only; the built-in browser doesn't share his Cloudflare session.

## Advance permissions in effect
- **Catalog-card and docs PRs:** the planner merges on a clean pass. Standing, until revoked.
- **Small fix units:** auto-merge on a clean PASS. Sprint 1 only; renew for Sprint 2.
- **Expired:** the unit-level permissions for U3–U6. All four merged.

## Next
1. Justin's bulk verification pass. Record the results here.
2. On Justin's go, start Sprint 2: the Haze and OG Kush families.
