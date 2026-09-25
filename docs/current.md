# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

**Last update:** the planner (chat, on Justin's go), 2026-09-25 ~04:00 UTC. **Sprint 3 (L1 library pass): fill PAUSED, winding down to the L1 stop point.**

## L1-B fill paused (Justin, 2026-09-25)
- **Why:** unattended WebFetch now returns `PROVENANCE_REQUIRED` on nearly every source, SeedFinder included (it worked on 2026-09-24). Batch 7 (#64) filled only 2 of 25 cards, and the batch-6 audit (#67) couldn't recheck 4 of its 7 samples. More hourly runs would mostly spend usage producing stubs.
- **Done:** the fill task (`trig_01QhFK1ZkXZR3F8eydJQEZxa`) is **disabled**. Batch 5 (#59) was merged on `clean` (head `f869687`, squash `d1cbaaa`).
- **Filled and merged:** batches 1, 2, 3, 5, 6, and 8. Batch 4 (#62) is filled and was reading `unstable` at 03:57 UTC; merge it on `clean`. Batch 7 (#64) carries 2 filled cards; merge on `clean`, and its 23 stubs stay stubs.
- **Catalog after these:** roughly 215 draft cards; the rest (~340) stay stubs for a later pass once source access works.
- **L1-C audit stays enabled** for one more pass: it audits the newly merged batches (4, 5, 7, 8), then does the close-out in `docs/library.md` L1-C step 5 (checklist here, then disables itself). Batches 9–20 are not being filled, so the close-out treats them as out of scope for this L1 stop point, not as unaudited batches.
- **Standing rule added to `docs/always.md`:** scheduled tasks must never loop on failures. Two failed runs in a row, or one plainly systemic blocker, means the task disables itself and reports here.

## Headline
- **L1-A (worklist) is done and merged.** 481 new stub cards across #47–#51, each merged on `mergeable_state: clean`. No existing card was edited.
- **The catalog was 526 cards after L1-A** (39 draft, 487 stub). Fill batches added parent stubs; the validator read 547 cards on 2026-09-25.
- **The fill queue is `docs/library/batches.json`:** 20 batches (19 of 25, the last of 12). Batches 1–8 were claimed; 9–20 are parked with the fill pause.
- **L1-B (fill) is disabled. L1-C (audit, Opus, every 3 hours)** runs one more pass and closes out.
- **Sprint 2 bulk verification is still open for Justin** (below). L1 doesn't depend on it.

## L1 status
| Step | State |
|---|---|
| L1-A worklist | **Done.** Stubs #47–#51; `batches.json` and `audit.md` in #52. |
| L1-B fill | **Paused / disabled 2026-09-25** (source access blocked). Batches 1–8 claimed; 9–20 parked. |
| L1-C audit | Enabled for the final pass. Logs to `docs/library/audit.md`, writes Justin's L1 stop-point checklist here, then disables itself. |

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
7. **Resuming the fill (batches 9–20, ~340 stubs):** needs working unattended source access first.

## Sprint plan
| Sprint | Scope | Status |
|---|---|---|
| 1 | v1 features (U1–U6) and the Skunk family | VERIFIED |
| 2 | U7 and U8, then the Haze and OG Kush families | 2A/2B VERIFIED. **2C (R3 OG Kush) MERGED**, awaiting Justin's bulk verification |
| 3 | L1 library pass (500+ strains; GSC and Blue Dream fold in) | **L1-A MERGED.** L1-B **paused** at ~215 filled (2026-09-25). L1-C final audit and close-out pending |

**Launch readiness:**
- A `reviewed` pass on all cards.
- Drop `noindex`.
- Age-notice copy.

## State
- **Units:** U1–U8 are merged (#8, #9, #13, #15, #19, #21, #27, and #33). STM-U9 is open as #42 and awaiting Justin.
- **Catalog:** 547 cards per the validator (2026-09-25); roughly 215 draft once batches 4 and 7 merge, the rest stubs.
- **Hosting:** live at `stemma.neworbitdigital.com` and `stemma-9j6.pages.dev`. PRs get preview deploys.

## Connector facts
- **GitHub connector:**
  - It has no workflows, administration, or secrets permission.
  - Check runs and commit status return 403, so `mergeable_state` is the CI evidence. It can sit at `unstable` for 3–4 minutes before it turns `clean`, so re-read it every 30–60 seconds.
  - `push_files` handles 100 files per commit without trouble (L1-A stub PRs).
  - Stub-only PRs read `clean` almost at once (2026-09-24). If the audit sees a red CI run on `main`, suspect that `clean` was read before checks registered.
- **Sandbox proxy:** it blocks `*.pages.dev`, `neworbitdigital.com`, and cdnjs. Live checks go to Justin, or to the built-in browser when it's linked.
- **WebFetch in unattended runs:** as of 2026-09-25, most fetches return `PROVENANCE_REQUIRED` with nobody there to approve. Don't schedule source-dependent work unattended until this is resolved.
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
1. **Merge** #62 (batch 4), #64 (batch 7, 2 cards), and #67 (batch-6 audit fixes) on `clean`.
2. **L1-C** runs its final pass (next at 06:19 UTC), audits the new batches, writes the L1 stop-point checklist here, and disables itself.
3. **Justin:** one bulk verification pass (Sprint 2 plus the L1 checklist), the decisions above, and STM-U9's go.
