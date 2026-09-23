# Stemma — Claude Code Working Notes
**STATUS:** Live project document. The executor reads this automatically on every run.

## What this repo is
- The Stemma strain-lineage catalog (`catalog/strains/*.json`).
- Stdlib-only Python tooling (`tools/`).
- A static site compiled into `dist/` and hosted on Cloudflare Pages at `https://stemma.neworbitdigital.com`.
- Context: `docs/always.md`. State: `docs/current.md`. Card contract: `docs/schema.md`.

## The pipe
- **Repo home:** `github.com/New-Orbit-Digital/stemma`, the org repo. Never create a same-named repo under the personal `NewOrbitDigital` account.
- **`main` is protected:** PR required, no direct pushes.
- **Flow:**
  1. The planner files an issue tagging `@claude`. The issue body IS the executor prompt.
  2. The executor builds on a `claude/issue-N-*` branch and opens a DRAFT PR in the same run.
  3. CI runs.
  4. The planner adjudicates.
  5. Justin authorizes.
  6. The planner merges.
  7. Pages deploys.
  8. Justin verifies on the deployed site.

## Standing executor rules
- **Step 0: restore and verify the checkout.** Confirm you are on a branch cut from current `main` and the tree is clean (report `git log -1 --oneline`). If you can't, STOP and report.
- **Execute, don't plan.** If the packet leaves a real design choice open, surface it instead of picking silently.
- **A tripped STOP is a stop.** Halt and report, even if you think the trip is spurious.
- **Acceptance criteria are the contract.** Run every machine check the packet lists and paste the actual output in the PR. Never claim a result you did not run.
- **A pushed branch gets a draft PR in the same run** (`gh pr create --draft`), titled for the unit and closing the issue. If PR creation is refused, say so in the run report.
- **Post results on the PR, not the issue** (`gh pr comment`).
- **No new dependencies.**
  - Tooling is stdlib-only Python 3. There's no pip in the runner.
  - Front-end libraries only when a packet names them, loaded from cdnjs or jsDelivr at a pinned exact version.
- **Tests:** `python3 tools/run_tests.py` (stdlib `unittest`) is the one way to run the suite. Don't use pytest.
- **Verification is Justin's job.** Report what you did and what the checks printed. Don't declare features "verified."
- **Secrets are placeholders.** Always write `<SECRET_NAME>`, never a real value.

## Catalog rules for the executor
- **Never author or edit strain facts** in `catalog/strains/`. Card content is planner research.
- Test fixtures live under `tests/fixtures/` and must be obviously fictional (`example-*`, `fixture-*` ids).
- **Strain `id`s are permanent.** No tool may rename or regenerate them.

## Front-end conventions
- Vanilla HTML, CSS, and JS. No framework or bundler.
- Mobile-first; light and dark mode via `prefers-color-scheme`.
- The site reads only `data/stemma.json` (the Budlogs seam). It never reads `catalog/` at runtime.
- Prefer inline CSS in the page over JS-patching styles. This is a standing anti-footgun from the framework.

## Anti-footguns (from the framework, attested across projects)
- **After `git rm`, a multi-pathspec `git add`** that re-lists the removed path aborts atomically and silently drops the others. Stage survivors separately.
- **`git commit -- <path>` cannot commit an untracked file.** Run `git add <path>` first.
- **Declares "fixed" without exercising it.** Run the check; paste the output.
- **Subdivides categories to rationalize a different approach** than the one specified. Don't; surface the choice.

## Updating this doc
Updated by the planner directly, or through a planner-filed issue. Justin does not hand-edit it.
