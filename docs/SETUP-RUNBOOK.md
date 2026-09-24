# Setup runbook (Justin's hands)
Each step is something the planner cannot reach through its connectors.

Chat's GitHub connector is the "Claude Github MCP Connector" app. It has no workflows, administration, or secrets permission, so everything below stays manual.

## 1. Create the repo — DONE 2026-09-23
`New-Orbit-Digital/stemma`, private, README-initialized.

## 2. Workflow files — DONE 2026-09-23
Justin created `.github/workflows/ci.yml` and `claude.yml` in the web UI.

Future workflow changes: the planner drafts the full file, and Justin pastes it in the web UI (Edit → Commit). Watch the path: type the filename into the `.github/workflows/` folder, not the full path again.

## 3. Executor pipe — DONE 2026-09-23
- The "Claude" GitHub App is installed on all org repos.
- `CLAUDE_CODE_OAUTH_TOKEN` is an org-level Actions secret, generated with `claude setup-token`.
- A repo-level secret with the same name overrides it, which is why ads-agent is unaffected.
- Never paste the token into chat.

## 4. Branch protection — DONE 2026-09-23
`main`: PR required, 0 approvals, no bypass.

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
