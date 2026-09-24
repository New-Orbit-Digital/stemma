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
  - Proven working by the U1–U3 executor runs.
- **Executor app:** the "Claude" GitHub App is installed on all org repos. It has read/write on actions, code, issues, PRs, and workflows (Justin's screenshot, 2026-09-23).

### Units
- **STM-U1 (#1): MERGED** as `dbb93b9` via PR #8.
- **STM-U2 (#2): MERGED** as `bd79021` via PR #9.
  - Evidence is in the adjudication comment on #9.
- **STM-U3 (#3): MERGED** as `12ce446` via PR #13 on 2026-09-24.
  - Adjudication: PASS.
    - 58 tests pass.
    - `node --check` exits 0.
    - The SVG is pasted in full on the PR.
    - The planner updated the branch from `main` so CI ran against the real catalog. CI run #20 succeeded.
  - The layout is precomputed at build time in `tools/lineage.py`. The disputed toggle is CSS only.
- **STM-U4 (#4): TRIGGERED** 2026-09-24.
- **STM-U5 (#5):** filed, not triggered.

### Catalog
Main holds 5 cards, all `draft`: `skunk-1`, `afghani-x-colombian-gold`, `acapulco-gold`, `afghani`, and `colombian-gold`.
- **PR #6: MERGED** as `779091d`, on Justin's go.
  - Review follow-ups on #6: generous tiers, an unused source, and the Acapulco Gold dispute.
- **PR #12: MERGED** as `14b44c1`.
  - It supersedes #11, which conflicted after #6 was squash-merged.
  - CI run #17 reported: 5 cards, 0 errors, 0 warnings.

### Hosting: LIVE (2026-09-24)
- **Setup:** Cloudflare Pages project `stemma`, created by Justin in the dashboard.
  - Build command: `python3 tools/build.py`.
  - Output directory: `dist`.
  - Production branch: `main`.
  - The Cloudflare GitHub app is scoped to `stemma` only.
  - URL: `https://stemma-9j6.pages.dev`.
  - Custom domain: `https://stemma.neworbitdigital.com`.
- **Planner deploy check** (2026-09-24 ~01:20 UTC), run from the built-in browser with `fetch`:
  - `stemma-9j6.pages.dev` returns 200 for `/`, `/about/`, `/data/stemma.json`, `/assets/app.js`, and all 5 `/s/<id>/` pages. `/nope/` returns 404.
  - The dataset holds 5 strains and 4 edges, generated `2026-09-24T01:18:42Z`.
  - `/s/skunk-1/` ships a rendered lineage SVG with 5 nodes and the current node highlighted. It carries `noindex`.
  - `stemma.neworbitdigital.com/s/skunk-1/` serves the same page, with nodes Afghani, Colombian Gold, Acapulco Gold, Afghani x Colombian Gold, and Skunk #1. The age notice is present.
- **Not yet verified:** Justin's visual check on a phone, in light and dark mode.

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
- Check runs and combined status return 403 for this connector.
  - The PR's `mergeable_state` is the CI evidence.
  - CI logs can be read through the built-in browser, where GitHub is signed in.
- The cloud sandbox's egress proxy blocks `*.pages.dev` and `neworbitdigital.com`. Deploy checks go through the built-in browser.
- The planner's built-in browser does not share Justin's Cloudflare session. Cloudflare dashboard work is Justin's hands.

## Advance permissions in effect
- **2026-09-24: auto-merge STM-U4 and U5 on a clean PASS.** U3 used this permission.
  - PASS means all of the following:
    - Every acceptance check has actual output posted, and it matches.
    - Scope is respected.
    - No stops were tripped.
    - `mergeable_state` is clean.
  - Expires when U5 merges.
- **2026-09-24 (Justin, chat): the planner merges catalog-card PRs and docs PRs on a clean pass.**
  - A clean pass means a planner review, a clean `mergeable_state` with the validator run in CI, and findings posted on the PR.
  - Standing, until Justin revokes it.

## Next
1. Adjudicate U4. If it passes, merge and trigger U5.
2. Justin checks the live site visually on his phone, in light and dark mode.
3. R1 next:
   - Super Skunk and the Dutch Skunk lines.
   - A `reviewed` pass on the #6 follow-ups.
