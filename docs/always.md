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

## Scheduled tasks: no failure loops (standing rule, Justin 2026-09-25)
Never let a scheduled task keep spending usage on runs that fail or produce nothing. This overrides any job spec.
- **A failed run** is one that errors, or whose main output is mostly empty because something outside the task blocked it (for example, WebFetch returning `PROVENANCE_REQUIRED` or timing out on most sources, a connector refusing, or CI that won't go clean).
- **One failed run:** say so plainly at the top of the run's output and in its PR or log row. Don't paper over it by leaving most of the work as stubs and calling the run done.
- **Two failed runs in a row, or one run where the blocker is plainly systemic:** disable the task itself (`update_trigger`, `enabled: false`), explain why in `docs/current.md`, and stop. Justin re-enables it once the blocker is fixed.
- **Before starting work,** each run checks whether the previous run of the same task failed for the same reason (its PR, log row, or `current.md`). If the blocker is still there, disable and stop without redoing the work.
- **Any task that schedules retries of itself** caps them (at most 2) and never re-schedules after the cap.

## Decisions (with dates)
- **2026-09-23 — Stack:** a static site plus repo-stored cards. No database or accounts in v1; Supabase arrives with Budlogs.
- **2026-09-23 — Cards are JSON, and tooling is stdlib-only Python.** The executor runner has no pip.
- **2026-09-23 — Stable IDs:** a strain's `id` never changes once merged. It's the URL, the QR target, and the future Budlogs foreign key.
- **2026-09-23 — v1 scope is the seed lineages:** the Skunk #1, OG Kush, Haze, GSC, and Blue Dream families, traced back to landraces. Depth comes before breadth. *Expanded 2026-09-24 by the library pass (below).*
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
- **2026-09-24 — Simple attributes only (Justin).** Effects, flavors, and medical-condition or recommended-activity data stay out: they're subjective and not widely verified. Cards stick to simple, checkable attributes: lineage, breeder, origin, dates, growing, and (with STM-U9) THC/CBD ranges and dominant terpenes.
- **2026-09-24 — Framing (Justin).** Stemma doesn't need to be authoritative. Cards are presented as researched with sources and open to changes.
- **2026-09-24 — Library pass (Justin).** v1 grows from the five seed families to a library of 500+ strains, filled quickly as `draft` cards and merged on a clean pass, with an Opus sample audit. GSC and Blue Dream fold into the library. See `docs/library.md`.
- **2026-09-24 — Model tiers (Justin).** Opus designs, handles messy lineages, and audits. Sonnet does bulk card filling. Haiku is only for status checks. The executor's model is set in `.github/workflows/claude.yml`, which is Justin's hands only.
- **2026-09-25 — Fill paused (Justin).** L1-B fill is disabled at about 215 filled cards, because unattended source fetches are blocked. The remaining stubs wait for a later pass with working source access. See `docs/current.md`.

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
