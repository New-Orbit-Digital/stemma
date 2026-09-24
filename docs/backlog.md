# Stemma — Backlog
`[blocker]` = gates other work.

## Build units (executor packets; files in docs/packets/)
- ~~STM-U1–U6~~ MERGED: tooling, site, graph, timeline, map, and cache-busting. See `current.md`.
- ~~STM-U7~~ MERGED 2026-09-24 (#27): schema v2, the community-catalog model. Tiers and disputes are dropped, sources are categorized, and the site is simplified.
- ~~STM-U8~~ MERGED 2026-09-24 (#33): inline `[[...]]` links, browse pages, `tools/countries.py`.
- **STM-U8 visual pass (proposed)** — still waits on Justin's interface direction (`docs/prep/stemma-interface.md`).
- **STM-U9 (proposed, issue filed 2026-09-24)** — schema v3: a `chemotype` field for cannabinoid
  (THC/CBD) ranges and dominant terpenes. Purely additive; `schema_version` stays 2, per the U8
  precedent. See `docs/packets/STM-U9.md`. Unblocks R6.

## Research units (planner sessions, cards via PR)
- **R1** — Skunk family. Done for Sprint 1 (13 cards, migrated to v2 in U7, voice-rewritten with links in Sprint 2B / #34).
- **R2** — Haze family. **DONE 2026-09-24 (#35, #36, #37): 14 new/upgraded draft cards + 2 new stubs (`silver-pearl`, `chitral`), written in the house voice with inline links, and merged.**
  - Each card's key facts were spot-checked against one live source before writing; corrections are noted in the affected cards' own source lists (see `current.md`).
  - Status is `draft`, not `reviewed` — a full citation check against every listed source (not just the one spot-checked) is still needed before any card can move to `reviewed`.
  - Two modelling calls got planner defaults that Justin should confirm (see `current.md`'s morning checklist): the Lemon Skunk / Chitral parentage, and Amnesia Haze's disputed origin (`parents: []`, `breeder: null`).
- **R3** — OG Kush family. Not started. Research notes first, per the sprint plan.
- **R4** — GSC family.
- **R5** — Blue Dream family.
- **R6 — Chemotype enrichment (proposed, blocked on STM-U9 merging).** Populate `chemotype` on
  existing and future cards using the databases Justin found 2026-09-24:
  - **Demarily** (`api.demarily.dev`) — a solo dev's free-tier aggregator (100 req/day, no
    signup), scraped from Leafly, AllBud, Weedmaps, Hytiva, and SeedFinder. Has lineage, breeder,
    cannabinoid %, and terpene % with real percentages — the richest single source, but check its
    docs' terms before relying on it heavily (standing sourcing rule), and it's a single-maintainer
    project with no durability guarantee.
  - **Shannon-Goddard `cannabis-intelligence-database`** (GitHub, MIT-licensed) — 15,768 strains,
    downloadable CSV, self-hostable. Partial THC/CBD coverage (~2,890 / ~1,268 of 15,768), sativa/
    indica ratios, effects and flavor tags. Its own README calls it a "proof of concept" for a
    successor project — treat as a snapshot, not a live feed.
  - **Otreeba** — has a real "genetic lineage" field and standardized breeder/product data, but is
    API-key-gated with unconfirmed pricing. Needs a pricing check before committing to it.
  - **Cannlytics** (`docs.cannlytics.com`) — cannabinoid and terpene/effect data only, no lineage,
    no documented bulk export or license. Minor enrichment source at best.
  - **OpenTHC / VDB** (`openthc.org`, GPL-3.0, actively maintained) — open-license canonical
    strain/variety identity registry, philosophically closest to Stemma's own community-catalog
    model. Schema/lineage-field detail unconfirmed (site blocks fetching, GitHub README didn't
    surface it) — worth a manual look as a naming/identity authority, separate from chemotype data.
  - All five are `database`-category sources per `docs/schema.md`. Standing rule still applies:
    paraphrase in our own words, never copy text, and check each source's terms before relying on
    it heavily.

## Hosting
- DONE 2026-09-24: Cloudflare Pages `stemma` on `stemma.neworbitdigital.com`.
- Check: the live pages load a `static.cloudflareinsights.com` beacon even though Web Analytics is off (Justin, 2026-09-24). A likely source is the zone's Real User Monitoring setting. Needs a dashboard look; low priority.

## Tooling
- `tools/check_migration.py` (added in U7) backs the U7 mechanical proof. Keep it or delete it at the next tooling unit. Still open as of Sprint 2B.

## Parked: visual design (decided 2026-09-24, Justin)
- Functionality comes first. The aesthetic pass comes later, in a clean, simple, elegant direction in the spirit of Claude's UI.
- The planner's suggestions are in `docs/prep/stemma-interface.md` (2026-09-24): options A, B, and C, awaiting Justin.
- Deferred items:
  - Light-mode review.
  - An on-site theme toggle.
  - Graph label styling.

## Parked (v2+)
- **Evidence tiers and structured disputes** (removed in U7, 2026-09-24). Revisit only if wanted, possibly as Budlogs "case files".
- **Budlogs:** accounts, logs, reviews, lists, and lineage-as-diary. Supabase. Justin isn't ready to think about its interface yet.
- **Dispensary QR pilot.** Check state cannabis marketing rules first.
- **Effects, flavors, and medical-condition / recommended-activity fields (open question, 2026-09-24).** Offered by the Demarily and Shannon-Goddard sources found alongside the chemotype data (STM-U9), but `docs/voice.md`'s banned-habits list excludes effects and medical claims from card prose. Whether a structured field fits the reference-catalog framing is Justin's call — not decided, not built.
- **Public Stemma API.**
- **Payment-processor check** before any paid Budlogs feature.
- **Name:** staying with "Stemma" for now (Justin, 2026-09-24). A Teradata data-catalog product uses the same name.
