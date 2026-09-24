# Stemma — Backlog
Durable standing work. `[blocker]` = gates other work.

## Build units (executor packets; files in docs/packets/)
- ~~STM-U1–U6~~ MERGED: tooling, site, graph, timeline, map, and cache-busting. See `current.md`.
- ~~STM-U7~~ MERGED 2026-09-24 (#27): schema v2, the community-catalog model. Tiers and disputes are dropped, sources are categorized, and the site is simplified.
- **STM-U8 (proposed)** — Visual pass. Waits on Justin's interface direction (`docs/prep/stemma-interface.md`).

## Research units (planner sessions, cards via PR)
- **R1** — Skunk family. Done for Sprint 1 (13 cards, migrated to v2 in U7).
- **R2** — Haze family. **Notes done 2026-09-24 (#28, `docs/research/haze.md`): 15 strains.**
  - `[blocker]` Cards wait on Justin's house-voice decision.
  - Also needs stubs for `silver-pearl` and `chitral`.
  - Modelling calls with defaults are listed in the notes.
  - Citations must be checked before any card goes `reviewed`.
- **R3** — OG Kush family. Not started.
- **R4** — GSC family.
- **R5** — Blue Dream family.

## Hosting
- DONE 2026-09-24: Cloudflare Pages `stemma` on `stemma.neworbitdigital.com`.
- Check: the live pages load a `static.cloudflareinsights.com` beacon even though Web Analytics is off (Justin, 2026-09-24). A likely source is the zone's Real User Monitoring setting. Needs a dashboard look; low priority.

## Tooling
- `tools/check_migration.py` (added in U7) backs the U7 mechanical proof. Keep it or delete it at the next tooling unit.

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
- **Chemotype fields.**
- **Public Stemma API.**
- **Payment-processor check** before any paid Budlogs feature.
- **Name:** staying with "Stemma" for now (Justin, 2026-09-24). A Teradata data-catalog product uses the same name.
