# Stemma — Backlog
Durable standing work. `[blocker]` = gates other work.

## Build units (executor packets; files in docs/packets/)
- [blocker] **STM-U1** — Catalog tooling: validator, dataset build, and test runner.
- [blocker] **STM-U2** — Site scaffold: search, strain pages, about page, and age notice. Depends on U1.
- **STM-U3** — Lineage graph on strain pages. Depends on U2.
- **STM-U4** — Timeline page. Depends on U2.
- **STM-U5** — Origin/migration map page. Depends on U2.

## Research units (planner sessions, cards via PR)
- **R1** — Skunk #1 family (incl. Afghani, Colombian, Acapulco Gold roots).
- **R2** — Haze family.
- **R3** — OG Kush family (incl. Chemdawg lineage disputes).
- **R4** — GSC family.
- **R5** — Blue Dream family.

## Hosting (Justin-assisted)
- Cloudflare Pages project on this repo.
  - Build command: `python3 tools/build.py`
  - Output directory: `dist`
- Custom domain `stemma.neworbitdigital.com`.

## Parked (v2+)
- **Budlogs:** accounts, logs, reviews, lists, and lineage-as-diary ("you've logged 6 descendants of Skunk #1"). Supabase.
- **Case files:** community-submitted evidence on disputed lineages, with moderation.
- **Dispensary QR pilot.** Check state cannabis marketing rules first.
- **Chemotype fields:** THC/CBD dominance and dominant terpenes.
- **Public Stemma API.**
- Payment-processor check before any paid Budlogs feature.
- Trademark check on "Stemma" before public launch. Stemma, a data-catalog software product acquired by Teradata, exists.
