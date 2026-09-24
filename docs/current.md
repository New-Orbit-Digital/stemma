# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## State (2026-09-24)
- **Repo:** `New-Orbit-Digital/stemma`.
  - Kickoff commit `9bc9263`.
  - `main` is protected: PR required, 0 approvals, no bypass. Set by Justin.
- **Workflows on `main`:** `.github/workflows/ci.yml` and `claude.yml`.
  - Created by Justin in the web UI.
  - Verified at the correct path by a planner directory read on 2026-09-23.
- **Executor secret:** `CLAUDE_CODE_OAUTH_TOKEN` added as an ORG secret by Justin.
  - Proven working by the U1 and U2 executor runs.
- **Executor app:** the "Claude" GitHub App is installed on all org repos, with read/write on actions, code, issues, PRs, and workflows (Justin's screenshot, 2026-09-23).
- **Units:**
  - **STM-U1 (#1): MERGED** as `dbb93b9` via PR #8.
  - **STM-U2 (#2): MERGED** as `bd79021` via PR #9 on 2026-09-24.
    - Planner adjudication: PASS. Evidence is in the adjudication comment on #9.
    - Build: 6 strains, 7 edges, 9 pages. Tests: 32 pass, 0 failures. `node --check` exits 0. Serve and fetch: 200 on `/`, `/about/`, and a strain page. `mergeable_state` was clean.
    - Amendment applied: `--path` (no `--catalog`), and `--out` is the site root, with the dataset at `<out>/data/stemma.json`.
    - Accepted judgment calls: root-relative links, and a build-time card list on the index for no-JS readers and crawlers.
    - Deployed-site verification: pending Justin, once hosting exists.
  - **STM-U3 (#3): TRIGGERED** 2026-09-24.
  - **STM-U4 (#4) and STM-U5 (#5):** filed, not triggered.
- **Draft PR #6:** R1 batch 1, 5 cards.
  - The branch was updated from `main`, so CI now runs the real validator.
  - Catalog PR: labeled needs-justin. The planner never merges it.
- **Hosting:** not yet set up. U2 is now merged, so the Cloudflare Pages setup can proceed. That's Justin's hands.
  - Build command: `python3 tools/build.py`.
  - Output directory: `dist`.

## Connector facts (verified 2026-09-23 from Justin's screenshots)
- Chat's GitHub connector authenticates as the GitHub App "Claude Github MCP Connector".
  - It has read/write on code, discussions, issues, PRs, and projects, and read on actions and metadata.
  - It has NO workflows, administration, or secrets permission. Anthropic sets those; Justin cannot raise them. The connector PAT is not used.
- Chat therefore CANNOT:
  - Write `.github/workflows/*`.
  - Create repos.
  - Set branch protection.
  - Manage secrets.
- These stay Justin's hands.
- Check runs return 403 for this connector. The PR's `mergeable_state` is used as the CI evidence.

## Advance permissions in effect
- **2026-09-24 — Auto-merge STM-U3, U4, and U5 on a clean PASS.**
  - The U2 permission was used and has expired.
  - PASS means: every acceptance check has its actual output posted and matching, scope is respected, no stops were tripped, and `mergeable_state` is clean.
  - Excluded: catalog-card PRs and docs PRs. Those are Justin's to merge.
  - Expires when U5 merges.

## Next
1. Adjudicate the U3 PR when it's up. If it passes, merge, then trigger U4, then U5, one at a time.
2. Note PR #6's CI result on the PR, and leave it for Justin.
3. R1 batch 2:
   - Afghani and Colombian Gold, from primary or strong secondary sources only.
   - Then Super Skunk and the Dutch Skunk lines.
4. Hosting: Cloudflare Pages setup (Justin's hands).
