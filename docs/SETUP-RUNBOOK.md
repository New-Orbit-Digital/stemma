# Setup runbook (Justin's hands)
Each step is something the planner cannot reach through its connectors.

## 1. Create the repo — DONE 2026-09-23
`New-Orbit-Digital/stemma`, private, README-initialized. The planner pushed the initial contents the same day.

## 2. Give the connector access
Connector token (fine-grained PAT, resource owner = New-Orbit-Digital):
1. Edit the token → Repository access → add `stemma`.
2. Grant these permissions:
   - Contents: read & write
   - Workflows: read & write (needed to push `.github/workflows/`)
   - Issues: read & write
   - Pull requests: read & write
   - Actions: read
   - Metadata: read
3. Do NOT grant Administration or Secrets. Branch protection is the merge gate, and the planner must not be able to change it.

## 3. Executor pipe
1. Org Settings → GitHub Apps → Claude → Configure. Make sure `stemma` is included (skip this if the app is on all repos).
2. Repo Settings → Secrets and variables → Actions → New secret: `CLAUDE_CODE_OAUTH_TOKEN`. Use the same value as ads-agent, or make it an org-level secret shared with both repos.

## 4. Branch protection (do this after the planner's workflow push)
Repo Settings → Branches → Add rule for `main`:
- Require a pull request.
- Required approvals: 0.
- Do not allow bypassing.

## 5. Hosting (after STM-U2 merges)
1. Cloudflare → Workers & Pages → Create → Pages → Connect to Git. Pick `New-Orbit-Digital/stemma`.
2. Build settings:
   - Framework preset: None.
   - Build command: `python3 tools/build.py`
   - Output directory: `dist`
   - Environment variable: `PYTHON_VERSION=3.12`
3. Open Custom domains → add `stemma.neworbitdigital.com`.
   - If neworbitdigital.com's DNS is on Cloudflare, it creates the record for you.
   - If not, add a CNAME `stemma` → `<project>.pages.dev` at your DNS host.
4. Budlogs: nothing yet. `budlogs.neworbitdigital.com` stays unused until v2.
