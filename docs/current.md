# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## State (2026-09-24)
- **Repo:** `New-Orbit-Digital/stemma`.
  - Kickoff commit `9bc9263`.
  - `main` is protected: PR required, 0 approvals, no bypass. Set by Justin.
- **Workflows on `main`:** `.github/workflows/ci.yml` and `claude.yml`.
  - Created by Justin in the web UI.
  - Verified at the correct path by a planner directory read on 2026-09-23.
- **Executor secret:** `CLAUDE_CODE_OAUTH_TOKEN` is an ORG secret, added by Justin.
  - Proven working by the U1 and U2 executor runs.
- **Executor app:** the "Claude" GitHub App is installed on all org repos. It has read/write on actions, code, issues, PRs, and workflows (Justin's screenshot, 2026-09-23).

### Units
- **STM-U1 (#1): MERGED** as `dbb93b9` via PR #8.
- **STM-U2 (#2): MERGED** as `bd79021` via PR #9 on 2026-09-24.
  - Planner adjudication: PASS. The evidence is in the adjudication comment on #9.
    - Build: 6 strains, 7 edges, 9 pages.
    - Tests: 32 pass, 0 failures.
    - `node --check`: exit 0.
    - Serve and fetch: 200s.
    - `mergeable_state`: clean.
  - `--path` (no `--catalog`). `--out` is the site root, with the dataset at `<out>/data/stemma.json`.
  - Accepted judgment calls:
    - Root-relative links.
    - A build-time card list on the index.
  - Deployed-site verification: pending Justin, once hosting is live.
- **STM-U3 (#3): TRIGGERED** 2026-09-24.
- **STM-U4 (#4) and STM-U5 (#5):** filed, not triggered.

### Catalog
- **PR #6: MERGED** as `779091d` on 2026-09-24, on Justin's go in chat.
  - Cards: `skunk-1`, `afghani-x-colombian-gold`, and `acapulco-gold` as drafts; `afghani` and `colombian-gold` as stubs.
  - Review follow-ups are listed on #6: generous tiers, an unused source, and the Acapulco Gold dispute.
- **PR #11:** R1 batch 2, which takes Afghani and Colombian Gold from stub to draft.

### Hosting
- Cloudflare Pages setup is in progress (2026-09-24). The planner drives the dashboard in Justin's browser, and Justin authorizes GitHub.
  - Build command: `python3 tools/build.py`.
  - Output directory: `dist`.
  - Domain: `stemma.neworbitdigital.com`.

## Connector facts (verified 2026-09-23 from Justin's screenshots)
- Chat's GitHub connector authenticates as the GitHub App "Claude Github MCP Connector".
  - It has read/write on code, discussions, issues, PRs, and projects.
  - It has read on actions and metadata.
  - It has NO workflows, administration, or secrets permission.
- Chat therefore CANNOT:
  - Write `.github/workflows/*`.
  - Create repos.
  - Set branch protection.
  - Manage secrets.
- Check runs and combined status return 403 for this connector. The PR's `mergeable_state` is the CI evidence.

## Advance permissions in effect
- **2026-09-24: auto-merge STM-U3, U4, and U5 on a clean PASS.**
  - PASS means:
    - Every acceptance check has actual output posted, and it matches.
    - Scope is respected.
    - No stops were tripped.
    - `mergeable_state` is clean.
  - Expires when U5 merges.
- **2026-09-24 (Justin, chat): the planner merges catalog-card PRs and docs PRs on a clean pass.**
  - Clean pass means:
    - The planner has reviewed the PR.
    - `mergeable_state` is clean, with the validator run in CI.
    - Review findings are posted on the PR.
  - Standing, until Justin revokes it.

## Next
1. Finish the Cloudflare Pages setup. Then Justin verifies the deployed site.
2. Adjudicate the U3 PR. If it passes, merge it, then trigger U4, then U5.
3. Merge #11 once CI is clean.
4. R1 next:
   - Super Skunk and the Dutch Skunk lines.
   - A `reviewed` pass on the #6 follow-ups.
