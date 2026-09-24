# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## State (2026-09-23)
- **Repo:** `New-Orbit-Digital/stemma`.
  - Kickoff commit `9bc9263`.
  - `main` is protected: PR required, 0 approvals, no bypass. Set by Justin.
- **Workflows on `main`:** `.github/workflows/ci.yml` and `claude.yml`.
  - Created by Justin in the web UI.
  - Verified at the correct path by a planner directory read on 2026-09-23.
- **Executor secret:** `CLAUDE_CODE_OAUTH_TOKEN` added as an ORG secret by Justin.
  - The planner cannot read secrets. The U1 run is the proof.
- **Executor app:** the "Claude" GitHub App is installed on all org repos, with read/write on actions, code, issues, PRs, and workflows (Justin's screenshot, 2026-09-23).
- **Issues #1 to #5:** STM-U1 to U5.
  - **#1 (STM-U1) TRIGGERED 2026-09-23** via an issue comment.
- **Draft PR #6:** R1 batch 1, 5 cards. It waits on the U1 validator.
- **Hosting:** not yet set up. Do it after STM-U2 merges.

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
- Both workflow pushes on 2026-09-23 returned 403 "Resource not accessible by integration". That is explained by the above.

## Advance permissions in effect
- **2026-09-23 — Merge STM-U1's PR on a clean pass.**
  - Clean pass means every acceptance check in #1 has its actual output posted, and each output matches.
  - CI must be green.
  - No tripped stops.
  - Expires when U1 merges.

## Next
1. Adjudicate the U1 PR, and merge under the advance permission if the pass is clean.
2. Re-run CI on PR #6. When it validates, take it out of draft for Justin's go.
3. Trigger #2 (STM-U2).
4. R1 batch 2: the landrace cards, Super Skunk, and the Dutch Skunk lines.
