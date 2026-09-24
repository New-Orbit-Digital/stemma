# Stemma — Always
**STATUS:** Stable project context. Read at the start of every planner and executor session.

## What this is
Stemma is a mobile-first web app. A user enters a cannabis strain name and sees its lineage and history:
- its parents and ancestors, back to landraces
- when and where it emerged
- a timeline and a migration map, aggregated across the catalog

It's a fun, educational tool for hobbyists.

## Products
- **Stemma** is a community-maintained strain catalog in the spirit of TMDB or a library catalog, and it's the v1 product. It's hosted at `stemma.neworbitdigital.com`.
  - The "scholarly" feel is in the name and the aesthetic only: simple, clean, and elegant, like Claude's own UI.
  - It isn't an evidence-grading body, and contributing to it should have low friction.
- **Budlogs** is a future Letterboxd-style social app: log strains, write reviews, make lists. It's reserved at `budlogs.neworbitdigital.com` and is out of scope for v1.
- **The seam:** Budlogs reads only Stemma's compiled output (`dist/data/stemma.json`, later a public API). Don't be prescriptive about the split yet, but never let app code read `catalog/` directly.

## Operating model (2026-09-23, Justin ruling)
Claude chat is the central surface. Justin ideates, plans, and decides in chat, and chat then drives the connectors to act on his behalf.

**Chat does these without asking:**
- File and trigger packet issues.
- Push docs and planner-authored cards to branches, and open or comment on PRs.
- Read repo state.

**Chat needs Justin's explicit go first:**
- Merging a PR.
- Repo-level actions: creating, renaming, or archiving repos, and changing settings or permissions.
- Anything touching production data.
- Anything that spends money or publishes publicly.

Once Justin says go in chat, chat executes. The connector's approval prompt is the second gate.

**Advance permission:**
- Justin may authorize specific actions ahead of time.
- The planner records each advance permission in `docs/current.md` with its scope.
- A permission expires when its scope is done.

**Justin's hands only:**
- Secrets.
- GitHub App installs.
- Branch protection.
- Hosting and DNS dashboards.

These ship as exact step lists. Justin also remains the verification gate on the deployed site.

## Decisions (with dates)
- **2026-09-23 — Stack:** a static site plus repo-stored cards. No database or accounts in v1; Supabase arrives with Budlogs.
- **2026-09-23 — Cards are JSON, and tooling is stdlib-only Python.** The executor runner has no pip.
- **2026-09-23 — Stable IDs:** a strain's `id` never changes once merged. It's the URL, the QR target, and the future Budlogs foreign key.
- **2026-09-23 — v1 scope is the seed lineages:** the Skunk #1, OG Kush, Haze, GSC, and Blue Dream families, traced back to landraces. Depth comes before breadth.
- **2026-09-23 — Sources:** paraphrase in our own words, never copy text. Check each source's terms before relying on it heavily.
- **2026-09-24 — Functionality before aesthetics (Justin).** Build and verify features first. The visual pass comes later. Planner verification checks behaviour, not looks.
- **2026-09-24 — Community-catalog model (Justin). This replaces the 2026-09-23 evidence-tier and dispute rules.**
  - Cards carry one flat source list. Each source has a descriptive category: `breeder`, `publication`, `database`, or `community`. The categories are not a ranking.
  - There are no per-claim evidence tiers and no structured disputes. Where accounts differ, the summary says so in plain prose.
  - Sources are shown quietly, not as prominent badges.
  - "Unknown" is still a valid answer, and decade-precision dates are fine.
  - Implemented by STM-U7. The tiers and disputes are parked in the backlog.
- **2026-09-24 — Name:** keep "Stemma" for now (Justin).
- **2026-09-24 — House voice:** 2a "Reference", with inline links (Justin). See `docs/voice.md`.
- **2026-09-24 — Populate first, don't adjudicate (Justin).** The primary goal is filled cards.
  - Check facts against a source.
  - Don't invest in weighing theories or disputes.
  - Use the commonly cited account.
  - Don't leave fields empty just to dodge a conflict.
- **2026-09-24 — Same-name breeders (Justin).** When two distinct breeders share an exact name, disambiguate the way film or music databases do: add location in parentheses, or failing that, founding year. See `docs/voice.md`.

## Roles
- **Justin:** product owner and verification gate. He gives the go on gated actions, directly or in advance.
- **Planner (Claude chat, in the Stemma Project):**
  - Designs the work, writes packets, files and triggers issues, adjudicates PRs, and merges on Justin's go.
  - Researches and authors catalog cards.
  - Owns implementation-class calls.
- **Executor (Claude GitHub Action):** builds a filed packet on a `claude/*` branch and opens a draft PR.

## The pipe
1. The planner files an issue (the issue body is the executor prompt) and tags `@claude`.
2. The executor builds on a branch and opens a draft PR.
3. CI runs validation and tests.
4. The planner adjudicates the PR.
5. Justin gives the go, or has pre-authorized it.
6. The planner merges.
7. Cloudflare Pages deploys.
8. Justin verifies on `stemma.neworbitdigital.com`.

## Response format (planner)
- Follow the First Minute framework: context → intent → headline, then detail. Conclusions come before reasoning.
- End every message with a separated **Actions for Justin** checklist, or "No action needed."
- Record verification evidence in the durable artifact (PR, changelog, `current.md`), not just in chat.
