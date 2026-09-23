# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## State (2026-09-23)
- Repo `New-Orbit-Digital/stemma` created by Justin.
- **Kickoff commit `9bc9263` on `main`:** docs, schema, packets, and runbook.
  - Verified: push returned the ref, and the file tree was confirmed via the connector.
- **Issues #1 to #5 filed:** STM-U1 to U5.
  - None has been triggered; none tags the executor yet.
- **Operating model recorded in `docs/always.md`:** chat steers the connectors; gated actions need Justin's go or an advance permission.
- **Workflows NOT on `main`:** the push of `.github/workflows/claude.yml` and `ci.yml` was refused with a 403, "Resource not accessible by integration," on 2026-09-23.
  - Cause: the connector token lacks the Workflows permission.
  - Both files are staged by the planner and ready to push.
- **Pipe NOT yet stood up.** It needs:
  - The connector Workflows permission.
  - The Claude GitHub App with access to this repo.
  - The `CLAUDE_CODE_OAUTH_TOKEN` Actions secret.
  - Branch protection on `main`, applied after the workflow push.
- **Hosting not yet set up:** a Cloudflare Pages project plus a CNAME for `stemma.neworbitdigital.com`. Do this after STM-U2 merges.

## Advance permissions in effect
- None.

## Next
1. Once Justin grants Workflows: push both workflow files, then Justin turns on branch protection.
2. Once the app and secret are in place: trigger #1 (STM-U1). That run doubles as the pipe proof.
3. Research session R1 (Skunk #1 family) runs in parallel. Cards arrive as planner PRs and must pass the validator once U1 lands.
