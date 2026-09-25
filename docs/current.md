# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

**Last update:** the L1-C auditor (scheduled, Opus), 2026-09-25 ~06:50 UTC. **Sprint 3 (L1 library pass) is at its STOP POINT.** The fill task and the audit task are both disabled. Justin's checklist is below.

## L1 stop point: Justin's checklist (L1-C close-out, 2026-09-25)
**What happened:** batches 1–8 were claimed and filled. Batch 7 got only 2 of its 25 cards before unattended source fetches were blocked, and the fill was paused (#68). Every merged batch has been audited: batch 1 (#54), batches 2–3 (#58), batches 6 and 8 (#65, #67), and batches 4, 5, and 7 (#70). Batches 9–20 were never filled, so they're out of scope for this stop point.

**Caveat on the last audit:** it couldn't recheck any card against its cited source. WebFetch returned `PROVENANCE_REQUIRED` on every attempt. Batches 4, 5, and 7 were audited for voice and catalog consistency only. Their 8 sampled cards are the first 8 spot-checks in B below, so your spot-check stands in for the source recheck.

### A. Catalog counts (validator on `main` after #70: 566 cards, 0 errors, 0 warnings)
| Status | Cards | Notes |
|---|---|---|
| `draft` | **216** | 39 from before L1, plus 177 filled in L1 (batches 1–6 and 8 in full, and 2 cards from batch 7). |
| `stub` | **350** | 23 left in batch 7, 287 in the parked batches 9–20, and 40 parent stubs that fill batches added outside the queue (a later sweep's work). |
| `reviewed` | **0** | A `reviewed` pass is a launch-readiness item. |

- **Breeder browse pages:** 73. #70 merged three near-duplicate spellings.

### B. Spot-checks (card against its cited source)
Open `stemma.neworbitdigital.com/s/<id>/` and compare it with the source.
- [ ] `big-bud`: Skunk #1 × Northern Lights, US 1980s, stabilized by Sensi, Cannabis Cup indica win. Check against [Sensi Seeds](https://sensiseeds.com/en/cannabis-seeds/sensi-seeds/big-bud). The summary's "Afghan-type indica and a skunk plant" clause reads oddly beside the listed parents.
- [ ] `g13`: Afghani clone, acquired by Neville Schoenmakers in Portland in 1986; the Mississippi legend is noted. Check against [JointCommerce](https://www.jointcommerce.com/blog/g13-strain-origin-a-comprehensive-strain-guide).
- [ ] `critical-mass`: Afghani × Skunk #1 by Mr. Nice Seedbank, late 1990s, with the Critical Bilbo phenotype. Check against [Mr. Nice](https://mrnice.com/product/critical-mass/).
- [ ] `cheetah-piss`: bred by LIT Farms; parents Lemonade, Gelato (#42), and London Pound Cake (97). Check against [Strainpedia](https://www.strainpedia.com/cheetah-piss/). Also check whether the parent is Cookies' "Lemonnade" (decision C3).
- [ ] `purple-thai`: Highland Oaxacan Gold × Chocolate Thai (DJ Short), with Anesia's landrace account noted. Check against [Anesia Seeds](https://anesiaseeds.com/product/purple-thai-landraces/) and [SeedFinder: Flo](https://seedfinder.eu/en/strain-info/flo/dj-short).
- [ ] `white-tahoe-cookies`: The White × Tahoe OG × GSC by Kush4Breakfast/Archive, with Emerald Cup placings in 2017 and 2018. Check against [SeedFinder](https://seedfinder.eu/en/strain-info/white-tahoe-cookies/archive-seed-bank).
- [ ] `kandy-kush`: OG Kush × Trainwreck by Reserva Privada. Check against [Strainpedia](https://www.strainpedia.com/kandy-kush/).
- [ ] `the-white`: a Krome clone-only ("Triangle"), second in Indica at the 2009 IC 420 Growers Cup. Check against [SeedFinder](https://seedfinder.eu/en/strain-info/the-white/clone-only-strains).
- [ ] `cinderella-99`: Jack Herer × Shiva Skunk, Mr. Soul / Brothers Grimm, mid-1990s. Check against [Brothers Grimm](https://brothersgrimmseeds.com/cinderella-99-official-history/).
- [ ] `golden-goat`: an accidental Topeka cross, a Hawaiian × Romulan male on an Island Sweet Skunk female. Check against [This Is Topeka](https://thisistopeka.com/2025/10/golden-goat-topekas-happy-accident-that-became-a-cannabis-legend/).
- [ ] **Live pages for #70's breeder merge:**
  - `/browse/breeder/the-cali-connection/` now also lists alien-og and pre-98-bubba-kush.
  - `/browse/breeder/t-h-seeds/` lists mk-ultra, ultra-sour, and french-cookies.
  - `/browse/breeder/cali-connection/`, `/th-seeds/`, and `/soma-seeds/` no longer exist.

### C. Decisions (only what needs you; defaults hold if you say nothing)
1. **Grower monikers in `breeder`.** This extends Sprint 2 decision C1 below. L1 kept people and brands out of `breeder` and in the prose: DJ Short (blueberry, flo, purple-thai), Berner/Cookies (snowman), Chang (f1-durban). *Default: keep that.*
2. **Parent lists longer than 2.** This extends C2 below. Now also white-tahoe-cookies, obama-runtz, and cheetah-piss (3 each), on top of ak-47 (4), gg4, trainwreck, original-diesel, dream-queen, and blue-mystic. *Default: leave as is.*
3. **Possible duplicate cards.**
   - `lemonade` (a stub) vs `lemonnade` (Cookies' spelling).
   - `private-reserve-og` vs `og-18`.
   - *Default: leave both pairs.* Ids are permanent, so merging would mean repointing parents and deleting a stub.
4. **Resuming the fill** (287 queued stubs in batches 9–20, the 23 left in batch 7, and 40 parent stubs) needs two things: working unattended source access (approve WebFetch for the source domains, or run the fill attended), and a new advance permission, because the L1 one expires at this stop point. *Default: parked.*

## Headline
- **L1 is at its stop point.** 216 draft cards and 350 stubs (566 total). Every merged fill batch has been audited, and 9 learned fill rules are recorded in `docs/library.md` for any future pass.
- **Both L1 scheduled tasks are disabled:** fill (`trig_01QhFK1ZkXZR3F8eydJQEZxa`, since #68) and audit (`trig_01XdK4C7R8udhJnwU3F6QPXo`, at this close-out). Nothing in L1 runs on a schedule now.
- **Justin:** the checklist above, the Sprint 2 bulk verification below, and STM-U9's go.
- **Don't start R6** (the chemotype-only pass) or anything else without Justin's go.

## L1 status
| Step | State |
|---|---|
| L1-A worklist | **Done.** Stubs in #47–#51; `batches.json` and `audit.md` in #52. |
| L1-B fill | **Stopped at the L1 stop point.** Paused and disabled 2026-09-25 (#68): source access blocked. Batches 1–6 and 8 were filled; batch 7 got 2 of 25; batches 9–20 are parked. |
| L1-C audit | **Done; disabled 2026-09-25 ~06:50 UTC.** Five audit rows in `docs/library/audit.md`; fixes in #54, #58, #65, #67, and #70. |

## What merged in L1-A (evidence)
| PR | Contents | Merge evidence |
|---|---|---|
| #47 Library stubs (1/5) | 100 stubs: seed-family heads (GSC, Blue Dream, GG4, Skywalker OG, Northern Lights, Cheese, Purple Haze, …) | `clean` at head `7643712`; squash `f029e3f` |
| #48 Library stubs (2/5) | 100 stubs: seed-family depth (Cookies line, DJ Short line, OG/Chem/Diesel line, Sensi and Dutch classics) | `clean` at head `dc9401d`; squash `8f95b08` |
| #49 Library stubs (3/5) | 100 stubs: Skunk and Haze tail, then the most widely known strains | `clean` at head `e3137bb`; squash `e573e32` |
| #50 Library stubs (4/5) | 100 stubs: known strains, continued | `clean` at head `fd2bebb`; squash `d2735d9` |
| #51 Library stubs (5/5) | 81 stubs: remaining strains and regional landraces | `clean` at head `fe1b695`; squash `3c28efb` |

- **Merge evidence caveat:** each stub PR read `clean` within seconds of opening, unlike R3's 3–4 minutes at `unstable`, and #51 stayed `clean` on a re-read 2.5 minutes later. Commit status returns 403, so the Actions result itself wasn't visible. Supporting evidence: every PR's Cloudflare preview deploy succeeded, and a git blob-hash spot check of 26 pushed stubs (the trickiest aliases, non-ASCII names, and each PR's last file) matched the local files byte for byte.

**Worklist calls (L1-A, planner):**
- **Dedupe:** every new name and alias was normalized (case, `#`/`No.`, spacing and punctuation, Dawg/Dog, Sherbet/Sherbert) and checked against all 45 existing cards and within the list. There were no collisions. Spelling variants are aliases, never separate cards.
- **Brand-safe ids:** `gsc` (aliases Girl Scout Cookies, Cookies) and `gg4` (aliases Gorilla Glue #4, Gorilla Glue, Original Glue, Glue) follow the breeders' post-dispute names and Leafly's current pages, so the permanent id never carries a disputed trademark.
- **Numbered phenos and cuts with their own card:** `gelato-33`, `gelato-41`, `gsc-forum-cut`, `thin-mint-gsc`, `platinum-gsc`, `pre-98-bubba-kush`, `707-headband` (distinct from `headband`), and `northern-lights` (distinct from `northern-lights-5`). **Folded into one card:** Bruce Banner #3 into `bruce-banner`; UK, Exodus, and Big Buddha Cheese into `cheese`; Daywrecker into `original-diesel`; Maui Waui into `maui-wowie`.
- **Same name, different things:** `mazar` (Dutch Passion cultivar) and `mazar-i-sharif` (landrace) are separate. `afghani-1` (Sensi's selection) is separate from the `afghani` landrace.
- **`kind` is a best guess.** L1-B may correct it. Clone-only selections are `cut`, regional populations are `landrace`, and everything else is `cultivar`.
- **Existing stubs in the queue:** `sour-diesel`, `hawaiian`, `silver-pearl`, `early-pearl`, `chitral`, and `nepalese` all sit in batch 1.

**Source-access note:** on 2026-09-24, unattended WebFetch of `leafly.com` and `en.wikipedia.org` timed out on an approval prompt nobody answered, while `seedfinder.eu`, `sensiseeds.com`, and `allbud.com` worked. By 2026-09-25 ~03:00 UTC, nearly every source (SeedFinder included) returned `PROVENANCE_REQUIRED`. This is what paused the fill.

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
- [ ] `/browse/`: the index counts reflect the catalog.
- [ ] Search: `Chem 91`, `Lemon Larry`, and `Old World Paki Kush` each find their card by alias.

**B. OG Kush spot-checks** (the card against its source)
- [ ] `og-kush`: Florida origin in the early 1990s, reaching LA in 1996. Check against [LA Weekly](https://www.laweekly.com/og-kush-a-quarter-century-of-gas/) and [Leafly](https://www.leafly.com/strains/og-kush).
- [ ] `chemdawg`: bought at a 1991 Deer Creek show, with 13 seeds; Chem 91 was the first keeper. Check against [High Times](https://hightimes.com/grow/25-years-of-chem-dog/).
- [ ] `bubba-kush`: LA, 1996, OG Kush crossed with a "Bubba" from Florida. Check against [Leafly's 25th-anniversary piece](https://www.leafly.com/news/strains-products/bubba-kush-strain-anniversary-shopping).
- [ ] `kosher-kush`: an LA clone, later sold as seed by DNA Genetics; Cup wins in 2010 and 2011. Check against [Leafly](https://www.leafly.com/strains/kosher-kush).
- [ ] `master-kush`: from White Label, bred from two Hindu Kush lines; High Life Cup gold in 2004. Check against [Sensi Seeds](https://sensiseeds.com/en/feminized-seeds/white-label/master-kush).

**C. Decisions (only what needs you)**
1. **Can a grower's moniker go in `breeder`?** R3 put "Chemdog" in `breeder` for the Chem line, but left OG Kush and Bubba Kush null, with the people named in the prose (they carried and spread the cuts rather than breeding them). L1 will hit this often. The default is to keep doing exactly this unless you say otherwise.
2. **Parent lists longer than 2** (ak-47 has 4; gg4, trainwreck, original-diesel, dream-queen, blue-mystic have 3) against schema's "2 for a cross." Flagged by the audits; left as they are pending your call.

## Still open (carried forward)
1. **STM-U9 (#42), chemotype fields:** the executor's draft PR is open and needs your go to merge. It unblocks R6.
2. **U7 live-site checks:** likely covered by your Sprint 2B live pass, but not confirmed item by item. Low priority.
3. **Interface direction:** A "Library card", B "Quiet app", C "Field notes", or a mix. See `docs/prep/stemma-interface.md`.
4. **`tools/check_migration.py`:** keep or delete. The planner keeps it by default until the next tooling unit.
5. **Cloudflare Insights beacon** on live pages even though Web Analytics is off. This is a dashboard look, and low priority (see backlog).
6. **Unused branches:** `planner/r3-og-kush-3-descendants` (from R3) and the merged `planner/library-stubs-1` … `-5` branches are safe to delete.
7. **Resuming the fill:** see L1 checklist C4.
8. **Merged L1 branches** (`planner/library-batch-*`, `planner/library-audit-*`, `planner/library-audit-log-*`, `planner/fill-pause-and-loop-rule`) are also safe to delete.

## Sprint plan
| Sprint | Scope | Status |
|---|---|---|
| 1 | v1 features (U1–U6) and the Skunk family | VERIFIED |
| 2 | U7 and U8, then the Haze and OG Kush families | 2A/2B VERIFIED. **2C (R3 OG Kush) MERGED**, awaiting Justin's bulk verification |
| 3 | L1 library pass (500+ strains; GSC and Blue Dream fold in) | **AT STOP POINT (2026-09-25).** 216 draft and 350 stub. Every merged batch audited. Awaiting Justin's L1 checklist |

**Launch readiness:**
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Age-notice copy.

## State
- **Units:** U1–U8 are merged (#8, #9, #13, #15, #19, #21, #27, and #33). STM-U9 is open as #42 and awaiting Justin.
- **Catalog:** 566 cards per the validator after #70 (2026-09-25): 216 draft, 350 stub, 0 reviewed.
- **Hosting:** live at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`. PRs get preview deploys.

## Connector facts
- **GitHub connector:**
  - It has no workflows, administration, or secrets permission.
  - Check runs and commit status return 403, so `mergeable_state` is the CI evidence. It can sit at `unstable` for 3–4 minutes before it turns `clean`, so re-read it every 30–60 seconds.
  - `push_files` handles 100 files per commit without trouble (L1-A stub PRs).
  - Stub-only PRs read `clean` almost at once (2026-09-24). If the audit sees a red CI run on `main`, suspect that `clean` was read before checks registered.
- **Sandbox proxy:** it blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs. Live checks go to Justin, or to the built-in browser when it's linked.
- **WebFetch in unattended runs:** as of 2026-09-25, most fetches return `PROVENANCE_REQUIRED` with nobody there to approve. Don't schedule source-dependent work unattended until this is resolved. Still true at the L1-C close-out (2026-09-25 ~06:40 UTC, 3 of 3 fetches blocked).
- **Private repo:** `git clone` has no credentials, so use the connector.
- **Cloudflare dashboard:** Justin's hands only.

## Advance permissions in effect
- **Catalog-card and docs PRs:** the planner merges on a clean pass. Standing.
- **Small fix units:** auto-merge on a clean PASS. Standing.
- **L1 library pass: EXPIRED** at the L1 stop point (2026-09-25). This close-out docs PR was its last use. Resuming the fill needs a new go (L1 checklist C4).
- **R3 (OG Kush family): EXPIRED.** Its scope is done (#43–#45).
- **A clean PASS means:**
  - Every acceptance check has its actual output posted, and each output matches.
  - Scope is respected.
  - No stops were tripped.
  - `mergeable_state` is clean.

## Next
1. **Justin:** one bulk verification pass (Sprint 2 plus the L1 checklist), the decisions above, and STM-U9's go.
2. **Nothing is scheduled.** R6 and any fill resume wait for Justin.
