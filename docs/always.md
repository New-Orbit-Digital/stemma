# Stemma — Always
**STATUS:** Stable project context. Read at the start of every planner and executor session.

## What this is
A web app (mobile-first) where a user enters a cannabis strain name and sees its lineage and history: parents and ancestors back to landraces, when and where it emerged, and a timeline and migration map aggregated across the catalog. It's a fun, educational tool that should be accurate enough to be meaningful to cannabis users who want to learn something.

## Products
- **Stemma**: the scholarly, evidence-backed catalog, and the v1 product. Hosted at `stemma.neworbitdigital.com`.
- **Budlogs**: a future Letterboxd-style social app (log strains, reviews, lists, community "case files" on disputed lineages). Reserved at `budlogs.neworbitdigital.com`. It is out of scope for v1.
- **The seam:** Budlogs reads only Stemma's compiled output (`dist/data/stemma.json`, later a public API). Don't be prescriptive about the split yet, but never let app code read `catalog/` directly.

## Decisions (with dates)
- 2026-09-23 — **Stack:** static site plus repo-stored cards. No database or accounts in v1. Supabase arrives with Budlogs.
- 2026-09-23 — **Cards are JSON; tooling is stdlib-only Python.** This is a planner implementation call. The executor runner has no pip, and JSON avoids a YAML dependency.
- 2026-09-23 — **Evidence tiers**, strongest first:
  1. `genetically-tested`: DNA evidence, e.g. a Phylos genotype report. It verifies the sample, not the name it was sold under.
  2. `documented`: published records.
  3. `breeder-claimed`: the breeder's own account.
  4. `folklore`: community lore.
- 2026-09-23 — **Accuracy rule (v1): honest, not exhaustive.**
  - Every lineage claim cites at least one source and carries a tier.
  - "Unknown" is a valid answer.
  - Disputes are recorded, not resolved.
  - Decade-precision dates are fine.
  - Chemotype, exact dates, and dispute resolution are benched.
- 2026-09-23 — **Stable IDs:** a strain's `id` never changes once merged. It is the URL, the QR target, and the future Budlogs foreign key.
- 2026-09-23 — **v1 scope = seed lineages:** Skunk #1, OG Kush, Haze, GSC, and Blue Dream families, traced back to landraces. Depth before breadth.
- 2026-09-23 — **Sources:** cite Phylos genotype reports, SeedFinder, breeder pages, and published histories. Paraphrase in our own words, never copy text. Check each source's terms before relying on it heavily.

## Roles
- **Justin:** product owner. He authorizes every merge and verifies on the deployed site.
- **Planner (Claude chat, in the Stemma Project):**
  - Designs, writes packets, files issues, adjudicates PRs, and merges once Justin authorizes.
  - Researches and authors catalog cards.
  - Owns implementation-class calls.
- **Executor (Claude GitHub Action):** builds a filed packet on a `claude/*` branch and opens a draft PR.

## The pipe
Planner files an issue (the issue body is the executor prompt), then tags `@claude` → the executor builds on a branch and opens a draft PR → CI runs validate and tests → the planner adjudicates → Justin authorizes → the planner merges → Cloudflare Pages deploys → Justin verifies on `stemma.neworbitdigital.com`.

## Response format (planner)
- Follow the First Minute framework: context → intent → headline, then detail. Conclusions come before reasoning.
- Every message ends with a separated **Actions for Justin** checklist, or "No action needed."
- Record verification evidence in the durable artifact (PR, changelog, `current.md`), not just in chat.
