# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

**Last update:** the planner (scheduled R3 run), 2026-09-24 ~17:10 UTC. **Sprint 2 stop point.**

## Headline
- **R3 (OG Kush family) is done and merged:** 17 new cards and 1 upgrade across #43, #44, and #45, each merged on `mergeable_state: clean`.
- **The catalog is 45 cards:** 39 draft and 6 stub, all schema v2 in the house voice with inline links.
- **Sprint 2 is at its stop point.** Justin's bulk-verification checklist is below.
- **Sprint 3 is the L1 library pass.** GSC and Blue Dream are folded in as worklist entries (`docs/library.md`). The L1-A worklist task is already scheduled for **2026-09-24 18:30 UTC**, and it starts on its own once it sees this stop point. To hold Sprint 3, pause that scheduled task before 18:30 UTC.

## What merged this run (evidence)
| PR | Cards | Merge evidence |
|---|---|---|
| #43 R3 (1/3) roots | `hindu-kush` (stub → draft); new `pakistani-kush`, `lemon-thai`, `chemdawg`, `chemdawg-d`, `chemdawg-4`; new stubs `hawaiian`, `sour-diesel` | `unstable` → `clean` at head `ba68d42`; squash `840cda4` |
| #44 R3 (2/3) OG Kush and cuts | new `og-kush`, `sfv-og`, `tahoe-og`, `ghost-og`, `bubba-kush`; `[[og-kush]]` links added to three parent cards | `unstable` → `clean` at head `217e621`; squash `6ceb4ab` |
| #45 R3 (3/3) descendants | new `fire-og`, `larry-og`, `headband`, `kosher-kush`, `master-kush`; `hindu-kush` links onward | `unstable` → `clean` at head `6e2ef45`; squash `b452909` |

- **Source checks:** every draft had at least one source checked live with WebFetch before it was written. Each card's "Planner-verified" source note records what that source confirmed.
- **Country codes:** none were added. AF, PK, US, and NL were already in `tools/countries.py`.
- **Planner calls, per the populate-first rule:**
  - **OG Kush** is a `cut`. Its parents are the commonly repeated three-way: Chemdawg, Lemon Thai, and Pakistani Kush. Leafly's Hindu Kush variant gets one clause. `breeder` is null because no organization bred it; Matt "Bubba" Berger and Josh D are named in the prose.
  - **Chemdawg, Chem D, and Chem 4** are sibling `cut`s from the same 1991 bag seed, so each has `parents: []`. Their breeder is "Chemdog".
  - **Tahoe OG** is a cut of OG Kush, and `breeder` is null. The one attribution found ("Ganja Guru") was single-source, and the name collides with another figure.
  - **Unknown fields:** a field is `unknown` only where no source gave a value. That covers Headband's born and origin; Kosher Kush, Larry OG, and Master Kush's born; Ghost OG's and Chem 4's origin; and Lemon Thai's born and origin.
- **Unused branch:** `planner/r3-og-kush-3-descendants` was cut by mistake and never used. It has no PR and is safe to delete.

## Sprint 2 bulk verification (Justin)
**A. Live pages** (at `stemma.neworbitdigital.com`; the sandbox can't reach the site)
- [ ] `/s/og-kush/`: the lineage graph shows 3 parents (Chemdawg, Lemon Thai, Pakistani Kush), and the inline links work.
- [ ] `/s/hindu-kush/`: now a full card, no longer "not yet cataloged". It lists Skunk Kush and Master Kush as children, and its summary links to OG Kush.
- [ ] `/s/chemdawg/` and `/s/sfv-og/`: the timeline and map include Florida, Los Angeles, and Massachusetts points.
- [ ] New browse pages:
  - [ ] `/browse/kind/cut/`, which is new because this is the first time the `cut` kind appears
  - [ ] `/browse/country/pk/`
  - [ ] `/browse/breeder/the-cali-connection/`
  - [ ] `/browse/breeder/dna-genetics/`
  - [ ] `/browse/breeder/chemdog/`
  - [ ] `/browse/breeder/white-label/`
- [ ] `/browse/`: the index counts reflect 45 cards.
- [ ] Search: `Chem 91`, `Lemon Larry`, and `Old World Paki Kush` each find their card by alias.

**B. OG Kush spot-checks** (the card against its source)
- [ ] `og-kush`: Florida origin in the early 1990s, reaching LA in 1996. Check against [LA Weekly](https://www.laweekly.com/og-kush-a-quarter-century-of-gas/) and [Leafly](https://www.leafly.com/strains/og-kush).
- [ ] `chemdawg`: bought at a 1991 Deer Creek show, with 13 seeds; Chem 91 was the first keeper. Check against [High Times](https://hightimes.com/grow/25-years-of-chem-dog/).
- [ ] `bubba-kush`: LA, 1996, OG Kush crossed with a "Bubba" from Florida. Check against [Leafly's 25th-anniversary piece](https://www.leafly.com/news/strains-products/bubba-kush-strain-anniversary-shopping).
- [ ] `kosher-kush`: an LA clone, later sold as seed by DNA Genetics; Cup wins in 2010 and 2011. Check against [Leafly](https://www.leafly.com/strains/kosher-kush).
- [ ] `master-kush`: from White Label, bred from two Hindu Kush lines; High Life Cup gold in 2004. Check against [Sensi Seeds](https://sensiseeds.com/en/feminized-seeds/white-label/master-kush).

**C. Decisions (only what needs you)**
1. **Can a grower's moniker go in `breeder`?** This run put "Chemdog" in `breeder` for the Chem line, but left OG Kush and Bubba Kush null, with the people named in the prose (they carried and spread the cuts rather than breeding them). L1 will hit this often. The planner's default is to keep doing exactly this unless you say otherwise.
2. **Sprint 3 go.** L1-A (the Opus worklist) is scheduled for 18:30 UTC today and will then enable the fill and audit tasks. Let it run, or pause the "Stemma L1-A" scheduled task if you want to verify Sprint 2 first.

## Still open (carried forward)
1. **STM-U9 (#42), chemotype fields:** the executor's draft PR is open and needs your go to merge. It unblocks R6, and L1 fills chemotype only after it merges.
2. **U7 live-site checks:** likely covered by your Sprint 2B live pass, but not confirmed item by item. Low priority.
3. **Interface direction:** A "Library card", B "Quiet app", C "Field notes", or a mix. See `docs/prep/stemma-interface.md`.
4. **`tools/check_migration.py`:** keep or delete. The planner keeps it by default until the next tooling unit.
5. **Cloudflare Insights beacon** on live pages even though Web Analytics is off. This is a dashboard look, and low priority (see backlog).

## Sprint plan
| Sprint | Scope | Status |
|---|---|---|
| 1 | v1 features (U1–U6) and the Skunk family | VERIFIED |
| 2 | U7 and U8, then the Haze and OG Kush families | 2A/2B VERIFIED. **2C (R3 OG Kush) MERGED**, awaiting Justin's bulk verification |
| 3 | L1 library pass (500+ strains; GSC and Blue Dream fold in) | L1-A scheduled for 2026-09-24 18:30 UTC |

**Launch readiness:**
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Age-notice copy.

## State
- **Units:** U1–U8 are merged (#8, #9, #13, #15, #19, #21, #27, and #33). STM-U9 is open as #42 and awaiting Justin.
- **Catalog:** 45 cards: 39 draft and 6 stub (`hawaiian` and `sour-diesel` are new; four earlier stubs remain, including `chitral` and `silver-pearl`).
- **Hosting:** live at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`. PRs get preview deploys.

## Connector facts
- **GitHub connector:**
  - It has no workflows, administration, or secrets permission.
  - Check runs and commit status return 403, so `mergeable_state` is the CI evidence. It can sit at `unstable` for 3–4 minutes before it turns `clean`, so re-read it every 30–60 seconds.
- **Sandbox proxy:** it blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs. Live checks go to Justin, or to the built-in browser when it's linked.
- **Private repo:** `git clone` has no credentials, so use the connector.
- **Cloudflare dashboard:** Justin's hands only.

## Advance permissions in effect
- **Catalog-card and docs PRs:** the planner merges on a clean pass. Standing.
- **Small fix units:** auto-merge on a clean PASS. Standing.
- **L1 library pass:** merge library stub, fill-batch, audit-fix, and library docs PRs on a clean pass (Justin, 2026-09-24). Expires at the L1 stop point. See `docs/library.md`.
- **R3 (OG Kush family): EXPIRED.** Its scope is done (#43–#45).
- **A clean PASS means:**
  - Every acceptance check has its actual output posted, and each output matches.
  - Scope is respected.
  - No stops were tripped.
  - `mergeable_state` is clean.

## Next
1. **Justin:** run the Sprint 2 bulk verification above, and answer the two decisions.
2. **18:30 UTC:** the L1-A worklist runs, unless Justin pauses it. Then the fill batches (Sonnet, hourly) and the audit (Opus, every 3 hours) run until the L1 stop point.
