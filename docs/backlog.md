# Stemma — Backlog
Durable standing work. `[blocker]` = gates other work.

## Build units (executor packets; files in docs/packets/)
- ~~STM-U1~~ Catalog tooling. MERGED (#8).
- ~~STM-U2~~ Site scaffold. MERGED (#9).
- ~~STM-U3~~ Lineage graph. MERGED (#13).
- ~~STM-U4~~ Timeline page. MERGED (#15).
- **STM-U5** — Origin/migration map page. Triggered on 2026-09-24.
- **STM-U6** — Asset cache-busting (fingerprinted `?v=` URLs plus `_headers`). Depends on U5.
  - Fixes stale CSS/JS on the custom domain after deploys (4h zone cache on static files).

## Research units (planner sessions, cards via PR)
- **R1** — Skunk #1 family. Five cards are in, all `draft`.
  - Next: Super Skunk and the Dutch Skunk lines.
  - Then a `reviewed` pass on the #6 follow-ups: tiers, the unused source, the Acapulco Gold dispute, and shorter `born.display` strings that the graph truncates.
- **R2** — Haze family.
- **R3** — OG Kush family (incl. Chemdawg lineage disputes).
- **R4** — GSC family.
- **R5** — Blue Dream family.

## Hosting
- DONE 2026-09-24: Cloudflare Pages project `stemma` (`stemma-9j6.pages.dev`) on custom domain `stemma.neworbitdigital.com`. Evidence is in `current.md`.

## Parked: visual design (decided 2026-09-24, Justin)
- Functionality comes first. The aesthetic pass waits until the Budlogs UI surface is scoped, so both products get designed together.
- Items parked here:
  - Light-mode review.
  - An on-site light/dark toggle.
  - Graph label truncation styling.
  - Overall visual polish.

## Parked (v2+)
- **Budlogs:** accounts, logs, reviews, lists, and lineage-as-diary ("you've logged 6 descendants of Skunk #1"). Supabase.
- **Case files:** community-submitted evidence on disputed lineages, with moderation.
- **Dispensary QR pilot.** Check state cannabis marketing rules first.
- **Chemotype fields:** THC/CBD dominance and dominant terpenes.
- **Public Stemma API.**
- Payment-processor check before any paid Budlogs feature.
- Trademark check on "Stemma" before public launch. Stemma, a data-catalog software product acquired by Teradata, exists.
