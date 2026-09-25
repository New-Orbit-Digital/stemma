# Stemma — Library pass (L1)
**STATUS:** Job spec. Decided by Justin, 2026-09-24. Read it with `docs/always.md`, `docs/voice.md`, and `docs/schema.md`.

## Goal
- Catalog **500+ strains** as `draft` cards, quickly and at low usage.
- **GSC and Blue Dream fold in.** They are worklist entries, not separate R4/R5 sessions.
- **Framing:** researched with sources, open to changes. Populate first; don't adjudicate.
- **Simple attributes only:** no effects, flavors, aroma or taste words, or medical claims.

## Model tiers (Justin, 2026-09-24)
| Job | Model | Why |
|---|---|---|
| **L1-A Worklist** (one session) | Opus | Card ids are permanent, so choosing and deduplicating them is expensive to get wrong. |
| **L1-B Fill batches** (one batch per session) | Sonnet | Repetitive and well specified, and the validator catches format errors. |
| **L1-C Audit** (recurring) | Opus | Judges sources and voice, and fixes rules rather than single cards. |
| **Executor units** | Set in `.github/workflows/claude.yml` | Changing it is Justin's hands only. |

## Advance permission (Justin, 2026-09-24)
- **Merge on a clean pass:** library stub PRs, fill-batch PRs, audit-fix PRs, and library docs PRs.
- **What counts as clean:** `mergeable_state` is `clean`. `unstable` means CI is still pending, so re-read it 30–60 seconds after each push.
- **Expiry:** this permission ends when L1 reaches its stop point.

## Hard constraints (every L1 session)
- **Never touch:** `.github/workflows`, secrets, or `tools/`. A missing country code gets logged, not added.
- **Never rename an existing `id`.**
- **Reads and writes go through the GitHub connector.** `git clone` has no credentials.
- **Live-site checks** (`*.pages.dev`, `neworbitdigital.com`) are blocked by the sandbox. Leave them for Justin.
- **Don't use the Cannabis Intelligence Database** (Shannon-Goddard / Loyal9) at all. Its data license bans building a competing strain database.
- **External databases are finder indexes only.** This covers Demarily, Otreeba, and Cannlytics. Cite the original page, never the index.

## L1-A — Worklist (Opus, one session)
0. **Wait for R3.** Check that `docs/current.md` shows R3 closed out at the Sprint 2 stop point and no `planner/*` PR is open. If not, schedule a one-shot retry 30 minutes later with the same prompt, then stop.
1. **Choose about 500–550 strains.**
   - Start with the rest of the five seed families, including GSC and Blue Dream.
   - Then add the most widely known strains overall.
   - Draw candidates from Leafly's popular and top-strain lists, SeedFinder, Cannabis Cup winner lists, Wikipedia strain articles, major breeder catalogs, and Demarily's name index.
   - Prefer strains that appear in several of these.
2. **Deduplicate** against the existing catalog and within the list.
   - Normalize spellings (Chemdawg / Chem Dog / Chemdog, "#4" / "No. 4", "OG" spacing).
   - Give each strain one `id`; spelling variants go in `aliases`.
   - Give a numbered pheno or cut its own card only when it's commonly treated as distinct (for example Chemdawg 4, or GSC's Thin Mint cut).
3. **Record the basics for each entry:** a permanent kebab-case `id`, `name`, `aliases`, and a best-guess `kind`. Nothing else.
4. **Commit them as stub cards.**
   - Stubs carry only `id`, `name`, `aliases`, `kind`, `status: "stub"`, and `updated`.
   - Use PRs of 100 files or fewer, and merge each on a clean pass.
   - Never edit an existing card.
5. **Write `docs/library/batches.json`** as `{ "batches": [ { "n": 1, "ids": [ ... ] }, ... ] }`.
   - Use batches of 25.
   - Order them seed families first, then by how widely known each strain is.
   - Include the existing stubs that still need filling.
6. **Create `docs/library/audit.md`** with an empty audit table.
7. **Update `docs/current.md`:** add the L1 status and this advance permission. Merge that docs PR, then stop.

## L1-B — Fill one batch (Sonnet)
0. **Guard.** If `docs/library/batches.json` isn't on `main`, stop at once: the worklist isn't ready.
1. **Claim a batch.**
   - Take the lowest batch `n` that has no branch `planner/library-batch-<n>` and no PR titled `Library batch <n>`.
   - Claim it by creating that branch from `main` before you do anything else. If creation fails, try the next batch.
   - If no batch is left, run a **sweep** instead: claim `planner/library-sweep-<k>` and fill up to 25 cards that are still stubs.
   - If nothing is left at all, go to step 5.
2. **Fill each card** in the batch that is still a stub:
   - **Check at least one live source** with WebFetch before you write. Try the breeder or seed-bank page first, then SeedFinder, Leafly, AllBud, and Wikipedia. A Demarily `source_url` may lead you to an original page; cite that page.
   - **Fill these fields:**
     - `kind` (you may correct the stub's guess)
     - `summary`, per `voice.md`: 2–4 sentences, at most 400 visible characters, linking first mentions
     - `born`
     - `origin` (its country must be in `tools/countries.py`; otherwise leave origin unknown and note it)
     - `breeder`
     - `parents`
     - `traditional_label`
     - `growing`, if the source gives it
     - `sources` (`category`, `url`, `accessed`)
     - `updated`
     - `status: "draft"`
   - **Parents must be existing ids.** First search every card's `name` and `aliases` on `main`. If a parent is truly missing, add a stub for it in the same PR. The sweep fills it later.
   - **Chemotype:** fill it only if `docs/schema.md` already documents `chemotype` (STM-U9 has merged) and a source you already opened gives THC/CBD or dominant terpenes. Don't go looking for it separately.
   - **If no source can be found,** leave the card as a stub and note it in the PR.
3. **Open one PR titled `Library batch <n>`.**
   - The body lists the cards filled, the cards left as stubs (with reasons), and any new parent stubs.
4. **Merge it on a clean pass.**
   - If it isn't clean after 3 reads, look for the usual causes: E05 (a parent id), E13 (a link target), E11 (length), E14 (a country code).
   - Fix what you can. Revert any card you can't fix to a stub, note it, and merge the rest.
   - If a stub file conflicts with one that another batch just merged, use theirs.
5. **If there's no work left,** disable this scheduled task with `update_trigger` (`enabled: false`; the trigger id is in your prompt) and stop.

## L1-C — Audit (Opus, recurring)
0. **Guard.** If no `Library batch` or sweep PR has merged since the last row in `docs/library/audit.md`, stop.
1. **Sample** about 1 card in 10 from each newly merged batch, with at least 2 per batch.
   - Recheck each against its cited source with WebFetch, and against `voice.md` and the rules above.
2. **Fix errors** in a PR titled `Library audit fixes <date>`, and merge it on a clean pass.
3. **Turn repeat problems into rules.**
   - If a problem shows up in 3 or more sampled cards, add a line under "Fill rules — learned" below, in a docs PR, so later batches follow it.
   - If a problem makes merged cards wrong at scale (for example, systematically wrong parents), disable the fill task (`enabled: false`), explain why in `docs/current.md`, and stop. Justin gets the push notification.
4. **Log a row** in `docs/library/audit.md`: date, PRs covered, cards sampled, passes, fixes, and rule changes.
5. **Close out.** Once the fill task is disabled or finished and every batch is audited:
   - Write Justin's L1 stop-point checklist into `docs/current.md`.
     - The card counts by status.
     - About 10 spot-check links, each with its source.
     - Only the decisions that truly need him.
   - Disable this audit task.

## Stop point
L1 ends at the audit's stop-point checklist. Don't start R6 (the chemotype-only pass) or anything else.

## Fill rules — learned
The audit appends here. L1-B follows these on every card.

1. **Cross-check every name against the catalog** (L1-C 2026-09-24, batch 1: 7 of 25 cards). Before you write a summary, search `name` and `aliases` on `main` for every strain it mentions, and the `breeder` values for every breeder it names. Link each one that has a card or a matching `breeder` at its first mention. If the summary names a strain's parents and they have cards, they go in `parents`. Never leave `parents` empty while the prose names a cataloged cross. (Seen: sour-diesel, silver-pearl, blue-dream, mac, gary-payton, cherry-pie, gelato. Still missed in batches 2–3, mostly inside "some accounts instead…" clauses and brand mentions: thin-mint-gsc, blue-cookies, northern-lights, cereal-milk, georgia-pie. Alternate accounts get links too.)
2. **Keep grow data out of the summary** (L1-C 2026-09-24, batch 1: 6 of 25 cards). Flowering times, plant heights, and indoor/outdoor suitability belong in `growing`. The summary spends its 400 characters on identity, origin, lineage, and history. (Seen: chitral, nepalese, durban-poison, early-pearl, silver-pearl, white-runtz. Merged cards aren't reworked for this alone.)
3. **Fill the commonly cited value; don't park it in "unknown"** (L1-C 2026-09-25, batches 1–3: 8 cards). If a source you opened gives a place, parents, breeder, or date, fill the field with it and put any competing account in one clause of prose. Record where the strain was bred, not where it was later sold or stabilized. If you can write a decade or year range in `born.display`, use the known shape with `year_min`/`year_max`, never `unknown: true`. A cross with one unidentified parent lists the known parent alone (for example Skunk #1 × unknown indica → `["skunk-1"]`). (Seen: gsc, lemon-cherry-gelato, northern-lights, green-crack, alien-og, candyland, oreoz, stardawg.)
4. **No flavor, aroma, or texture words, even to explain a cross** (L1-C 2026-09-25, batch 2: 5 cards). "Cookie sweetness", "citrus genetics", "dessert profile", "keeping its flavor", and "resin-dense" are all out. Say what was crossed, by whom, and when; leave out why it tastes a certain way. (Seen: london-pound-cake, tropicana-cookies, animal-cookies, animal-mints, tangie.)
5. **Write lineage as a whole sentence** (L1-C 2026-09-25, batch 2: 4 cards). "It is a cross of [[a]] and [[b]]." or "A cross of [[a]] and [[b]], it …", never a verbless fragment such as "A cross of [[a]] and [[b]], developed over several generations." (Seen: ak-47, blueberry, skywalker-og, purple-kush. Merged cards aren't reworked for this alone.)
6. **Reuse the catalog's breeder spelling** (L1-C 2026-09-25, batches 1–3: 3 cards). Before setting `breeder`, search existing `breeder` values on `main` and reuse an exact match. Use the breeding company's name, not a retail brand and not a strain name: "Cookie Fam Genetics" (not "Cookies"), "Grand Daddy Purp" (not "Grand Daddy Purple"). A brand can still be named in prose, linked as `[[breeder:Cookie Fam Genetics|Cookies]]`. (Seen: london-pound-cake, biscotti, candyland. Batch 4 also wrote "T.H. Seeds" where batch 8 had "T.H.Seeds". Both slug to `t-h-seeds`, so `build.py` aborted.)
7. **Merge only on `clean`, and check a stuck PR yourself** (L1-C 2026-09-25: 5 PRs). `unstable` means a check is pending *or has failed*, so it is never a merge state. From #56 (an unresolvable `[[breeder:Dutch Passion]]` link) until #65, main failed CI, and #57, #61, #63, and #66 merged on top of it anyway. Production deploys failed for about 5.5 hours. If your PR still reads `unstable` after 3 reads, run the checks yourself:
   - With `get_file_contents`, list `catalog/strains`, `tools`, and `site` on your branch, with fields `name` and `download_url`.
   - Curl those URLs.
   - Run `python3 tools/validate.py` and `python3 tools/build.py --out /tmp/dist`. `build.py` also catches errors that `validate.py` misses, such as two breeder spellings with the same slug.

   Fix what's in your cards. If the failure is outside your PR, leave the PR open, say so in its body, and stop. Don't merge.
8. **Search aliases on current `main` before adding a parent stub** (L1-C 2026-09-25, batches 5, 6, and 8: 3 cases). `chem-d` was created twice (#61, then #66), even though `chemdawg-d` carries the alias "Chem D", and both times it had to be deleted and its parents repointed. Before adding any stub, search every card's `name` and `aliases` on current `main`, not your branch's base, normalizing case, spacing, "#", and Dawg/Dog. Check near-spellings within your own batch too. (Seen: chem-d twice; batch 5's `lemonade` stub beside its own `lemonnade` card. `private-reserve-og`/`og-18` is a worklist duplicate, left for Justin.)
