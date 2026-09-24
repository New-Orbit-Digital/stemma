# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

**Last update:** the planner (scheduled L1-A worklist run), 2026-09-24 ~19:10 UTC. **Sprint 3 (L1 library pass) is running.**

## Headline
- **L1-A (worklist) is done and merged.** 481 new stub cards across #47–#51, each merged on `mergeable_state: clean`. No existing card was edited.
- **The catalog is 526 cards:** 39 draft and 487 stub.
- **The fill queue is `docs/library/batches.json`:** 20 batches (19 of 25, the last of 12), 487 ids: the 481 new stubs plus the 6 older stubs. Seed families come first (batches 1–10, GSC and Blue Dream at the head of batch 1), then everything else by how widely known it is.
- **L1-B (fill, Sonnet, hourly) and L1-C (audit, Opus, every 3 hours) are enabled** and run until the L1 stop point (`docs/library.md`).
- **Sprint 2 bulk verification is still open for Justin** (below). L1 doesn't depend on it.

## L1 status
| Step | State |
|---|---|
| L1-A worklist | **Done** (this run). Stubs #47–#51; `batches.json` and `audit.md` in the docs PR that carries this file. |
| L1-B fill | Enabled. Claims the lowest free batch each hour via a `planner/library-batch-<n>` branch. |
| L1-C audit | Enabled. Logs to `docs/library/audit.md`. Writes Justin's L1 stop-point checklist here when every batch is filled and audited. |

## What merged this run (evidence)
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

**Source-access note for L1-B and L1-C:** in this unattended run, WebFetch of `leafly.com` and `en.wikipedia.org` timed out on an approval prompt nobody answered. `seedfinder.eu`, `sensiseeds.com`, and `allbud.com` fetched without a prompt. Fill runs are unattended too, so they'll lean on breeder pages, SeedFinder, and AllBud unless Leafly and Wikipedia are approved at site scope.

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
- [ ] `/browse/`: the index counts reflect the catalog (526 cards after L1-A; 45 before it).
- [ ] Search: `Chem 91`, `Lemon Larry`, and `Old World Paki Kush` each find their card by alias.

**B. OG Kush spot-checks** (the card against its source)
- [ ] `og-kush`: Florida origin in the early 1990s, reaching LA in 1996. Check against [LA Weekly](https://www.laweekly.com/og-kush-a-quarter-century-of-gas/) and [Leafly](https://www.leafly.com/strains/og-kush).
- [ ] `chemdawg`: bought at a 1991 Deer Creek show, with 13 seeds; Chem 91 was the first keeper. Check against [High Times](https://hightimes.com/grow/25-years-of-chem-dog/).
- [ ] `bubba-kush`: LA, 1996, OG Kush crossed with a "Bubba" from Florida. Check against [Leafly's 25th-anniversary piece](https://www.leafly.com/news/strains-products/bubba-kush-strain-anniversary-shopping).
- [ ] `kosher-kush`: an LA clone, later sold as seed by DNA Genetics; Cup wins in 2010 and 2011. Check against [Leafly](https://www.leafly.com/strains/kosher-kush).
- [ ] `master-kush`: from White Label, bred from two Hindu Kush lines; High Life Cup gold in 2004. Check against [Sensi Seeds](https://sensiseeds.com/en/feminized-seeds/white-label/master-kush).

**C. Decisions (only what needs you)**
1. **Can a grower's moniker go in `breeder`?** R3 put "Chemdog" in `breeder` for the Chem line, but left OG Kush and Bubba Kush null, with the people named in the prose (they carried and spread the cuts rather than breeding them). L1 will hit this often. The default is to keep doing exactly this unless you say otherwise.

## Still open (carried forward)
1. **STM-U9 (#42), chemotype fields:** the executor's draft PR is open and needs your go to merge. It unblocks R6, and L1 fills chemotype only after it merges.
2. **U7 live-site checks:** likely covered by your Sprint 2B live pass, but not confirmed item by item. Low priority.
3. **Interface direction:** A "Library card", B "Quiet app", C "Field notes", or a mix. See `docs/prep/stemma-interface.md`.
4. **`tools/check_migration.py`:** keep or delete. The planner keeps it by default until the next tooling unit.
5. **Cloudflare Insights beacon** on live pages even though Web Analytics is off. This is a dashboard look, and low priority (see backlog).
6. **Unused branches:** `planner/r3-og-kush-3-descendants` (from R3) and the merged `planner/library-stubs-1` … `-5` branches are safe to delete.

## Sprint plan
| Sprint | Scope | Status |
|---|---|---|
| 1 | v1 features (U1–U6) and the Skunk family | VERIFIED |
| 2 | U7 and U8, then the Haze and OG Kush families | 2A/2B VERIFIED. **2C (R3 OG Kush) MERGED**, awaiting Justin's bulk verification |
| 3 | L1 library pass (500+ strains; GSC and Blue Dream fold in) | **L1-A MERGED** (#47–#51). L1-B fill and L1-C audit running |

**Launch readiness:**
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Age-notice copy.

## State
- **Units:** U1–U8 are merged (#8, #9, #13, #15, #19, #21, #27, and #33). STM-U9 is open as #42 and awaiting Justin.
- **Catalog:** 526 cards: 39 draft and 487 stub. The 487 stubs are exactly the ids in `docs/library/batches.json`.
- **Hosting:** live at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`. PRs get preview deploys.

## Connector facts
- **GitHub connector:**
  - It has no workflows, administration, or secrets permission.
  - Check runs and commit status return 403, so `mergeable_state` is the CI evidence. It can sit at `unstable` for 3–4 minutes before it turns `clean`, so re-read it every 30–60 seconds.
  - `push_files` handles 100 files per commit without trouble (L1-A stub PRs).
  - Stub-only PRs read `clean` almost at once (2026-09-24). If the audit sees a red CI run on `main`, suspect that `clean` was read before checks registered.
- **Sandbox proxy:** it blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs. Live checks go to Justin, or to the built-in browser when it's linked.
- **WebFetch in unattended runs:** a domain that needs approval times out rather than waiting (seen for `leafly.com` and `en.wikipedia.org` on 2026-09-24). Pre-approved domains, such as SeedFinder, Sensi Seeds, and AllBud, work.
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
1. **L1-B** fills one batch per hour (about 20 hours for the queue, then sweeps for anything left as a stub). **L1-C** audits every 3 hours and writes the L1 stop-point checklist here at the end.
2. **Justin:** the Sprint 2 bulk verification and the breeder-moniker decision above, whenever convenient. Optionally, approve `leafly.com` and `en.wikipedia.org` for WebFetch at site scope so fill runs can use them.
