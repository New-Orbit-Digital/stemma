# Stemma — Backlog
Durable standing work. `[blocker]` = gates other work.

## Build units (executor packets; files in docs/packets/)
- ~~STM-U1–U6~~ MERGED: tooling, site, graph, timeline, map, and cache-busting. See `current.md`.
- ~~STM-U7~~ MERGED 2026-09-24 (#27): schema v2, the community-catalog model. Tiers and disputes are dropped, sources are categorized, and the site is simplified.
- ~~STM-U8~~ MERGED 2026-09-24 (#33): inline `[[...]]` links, browse pages, `tools/countries.py`.
- **STM-U8 visual pass (proposed)** — still waits on Justin's interface direction (`docs/prep/stemma-interface.md`).
- **STM-U9 (issue #41)** — a `chemotype` field for cannabinoid (THC/CBD) ranges and dominant
  terpenes. Purely additive; `schema_version` stays 2, per the U8 precedent. See
  `docs/packets/STM-U9.md`. The first executor run errored at 0s (2026-09-24 ~14:23 UTC, before the
  usage rollover); re-triggered ~16:10 UTC. Its PR needs Justin's go. Unblocks R6.

## Research units (planner sessions, cards via PR)
- **R1** — Skunk family. Done for Sprint 1 (13 cards, migrated to v2 in U7, voice-rewritten with links in Sprint 2B / #34).
- **R2** — Haze family. **DONE 2026-09-24 (#35, #36, #37): 14 new/upgraded draft cards + 2 new stubs (`silver-pearl`, `chitral`), written in the house voice with inline links, and merged.**
  - Each card's key facts were spot-checked against one live source before writing; corrections are noted in the affected cards' own source lists (see `current.md`).
  - Status is `draft`, not `reviewed` — a full citation check against every listed source (not just the one spot-checked) is still needed before any card can move to `reviewed`.
  - Two modelling calls got planner defaults that Justin should confirm (see `current.md`'s morning checklist): the Lemon Skunk / Chitral parentage, and Amnesia Haze's disputed origin (`parents: []`, `breeder: null`).
- **R3** — OG Kush family. Scheduled planner run (Opus), 2026-09-24 16:45 UTC.
- ~~**R4** — GSC family.~~ Folded into L1 (Justin, 2026-09-24).
- ~~**R5** — Blue Dream family.~~ Folded into L1 (Justin, 2026-09-24).
- **L1 — Library pass (500+ strains).** Opus worklist, then Sonnet fill batches of 25, with an Opus
  sample audit. Scheduled 2026-09-24 to start after R3 closes out. See `docs/library.md`.
- **R6 — Chemotype enrichment (proposed, blocked on STM-U9 merging).** Populate `chemotype` on
  existing and future cards from original sources (breeder and seed-bank pages, SeedFinder, Leafly,
  AllBud, lab-data pages), cited and paraphrased like every other fact. L1 fills chemotype
  opportunistically once U9 merges; R6 is the dedicated pass afterwards.

### External strain databases (Justin found 2026-09-24; planner live-checked the same day)
**Working rule:** treat these as finder indexes. Use them to locate the original page, verify
against that page, cite it, and paraphrase. Don't bulk-import their data.
- **Demarily** (`api.demarily.dev`, free tier, no signup). The live records are much thinner than
  its launch post: OG Kush, Blue Dream, and Chemdawg all return `lineage: "Unknown"`,
  `breeder: "Unknown"`, and empty terpenes. It does carry THC/CBD point values and a `source_url`
  back to the original AllBud or Leafly page. Reachable with WebFetch; the sandbox proxy blocks it
  for `curl`. Useful as a name index that points to originals.
- **Cannabis Intelligence Database** (Shannon-Goddard / Loyal9). The code is MIT, but the data has
  its own `DATA_LICENSE.md`. At every tier it prohibits sharing the data publicly and "creating
  competing cannabis strain databases." Stemma is a public strain database, so **don't use it**.
  (An earlier note here called it MIT-licensed and self-hostable. That was wrong.)
- **Otreeba.** Has a genetics field and standardized breeder data. API-key-gated; pricing and
  terms unconfirmed.
- **Cannlytics** (`docs.cannlytics.com`). Cannabinoid and terpene data only. No lineage, and no
  documented license or bulk export.
- **OpenTHC VDB** (`openthc.org`, GPL-3.0, actively maintained). An open strain-identity registry,
  close in spirit to Stemma. Field detail unconfirmed; worth a manual look as a naming reference.

## Hosting
- DONE 2026-09-24: Cloudflare Pages `stemma` on `stemma.neworbitdigital.com`.
- Check: the live pages load a `static.cloudflareinsights.com` beacon even though Web Analytics is off (Justin, 2026-09-24). A likely source is the zone's Real User Monitoring setting. Needs a dashboard look; low priority.

## Tooling
- `tools/check_migration.py` (added in U7) backs the U7 mechanical proof. Keep it or delete it at the next tooling unit. Still open as of Sprint 2B.

## Site copy (small)
- A short framing line for the About page and strain pages, e.g. "Researched from cited sources;
  open to corrections." Needs a small executor unit. No corrections channel exists yet.

## Parked: visual design (decided 2026-09-24, Justin)
- Functionality comes first. The aesthetic pass comes later, in a clean, simple, elegant direction in the spirit of Claude's UI.
- The planner's suggestions are in `docs/prep/stemma-interface.md` (2026-09-24): options A, B, and C, awaiting Justin.
- Deferred items:
  - Light-mode review.
  - An on-site theme toggle.
  - Graph label styling.

## Out (decided)
- **Effects, flavors, and medical-condition / recommended-activity data** (Justin, 2026-09-24).
  Subjective and not widely verified. See `docs/always.md`.

## Parked (v2+)
- **Evidence tiers and structured disputes** (removed in U7, 2026-09-24). Revisit only if wanted, possibly as Budlogs "case files".
- **Budlogs:** accounts, logs, reviews, lists, and lineage-as-diary. Supabase. Justin isn't ready to think about its interface yet.
- **Dispensary QR pilot.** Check state cannabis marketing rules first.
- **Public Stemma API.**
- **Payment-processor check** before any paid Budlogs feature.
- **Name:** staying with "Stemma" for now (Justin, 2026-09-24). A Teradata data-catalog product uses the same name.
