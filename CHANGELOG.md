# Changelog
Append-only, session-grained, newest first. A shipped summary is appended at every close-out.

## 2026-09-24 — Sprint 2A (overnight planner run)
- **STM-U7 merged (#27, `d58b30d`): schema v2, the community-catalog model.**
  - Per-claim evidence tiers and structured disputes are removed.
  - Sources are one flat, categorized list: breeder, publication, database, or community.
  - The site is simplified: no tier badges, a quiet sources list, uniform graph and map lines, and a rewritten About page.
  - All 13 cards were migrated mechanically. Facts are unchanged, as the executor's proof and the planner's field scan both confirm.
  - Build: 13 strains, 12 edges. The disputed Acapulco Gold → Nepalese edge is gone.
- **R2 Haze research notes (#28):** `docs/research/haze.md` covers 15 strains. Cards wait on the house-voice decision.
- **Interface prep (#29):** `docs/prep/stemma-interface.md` offers three directions for Justin to react to.
- **Close-out docs:**
  - current.md, backlog.md, and this changelog.
  - README.md and project-instructions.md updated to the community-catalog model.

## 2026-09-23 — Project kickoff
- Repo seeded by the planner: README, CLAUDE.md, docs tiers (always / current / backlog), card schema spec v1, packets STM-U1 to STM-U5, executor and CI workflows.
- Decisions recorded in `docs/always.md`: static site with repo-stored JSON cards, four evidence tiers, stable strain IDs, stdlib-only tooling, Stemma/Budlogs product split.
