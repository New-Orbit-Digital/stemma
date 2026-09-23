# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## State (2026-09-23)
- Repo `New-Orbit-Digital/stemma` created by Justin.
- **Kickoff commit `9bc9263` on `main`:** docs, schema, packets, and runbook.
  - Verified: push returned the ref, and the file tree was confirmed via the connector.
- **Issues #1 to #5 filed:** STM-U1 to U5.
  - None has been triggered; none tags the executor yet.
- **Draft PR #6:** R1 batch 1, 5 cards. It waits on the U1 validator.
- **Operating model recorded in `docs/always.md`:** chat steers the connectors; gated actions need Justin's go or an advance permission.
- **Workflows NOT on `main`: still refused after Justin's token update.**
  - 2026-09-23: 403 "Resource not accessible by integration" on both the git-trees push and a single-file contents PUT to `.github/workflows/ci.yml`.
  - Justin edited the connector PAT (Administration + Workflows RW) before these attempts.
  - Hypothesis, not verified: the wording "by integration" points to an app/OAuth token rather than a fine-grained PAT. Either the connector does not authenticate with the edited PAT, or a pending org approval hasn't taken effect.
  - Workaround chosen: Justin creates the two workflow files in the GitHub web UI.
- **Pipe NOT yet stood up.** It needs:
  - The workflow files on `main`.
  - The Claude GitHub App with access to this repo.
  - The `CLAUDE_CODE_OAUTH_TOKEN` Actions secret.
  - Branch protection on `main`.
- **Hosting not yet set up:** a Cloudflare Pages project plus a CNAME for `stemma.neworbitdigital.com`. Do this after STM-U2 merges.

## Advance permissions in effect
- None.

## Next
1. Workflow files land on `main`, via the web UI or after the connector auth is fixed. Then branch protection, the secret, and app coverage.
2. Trigger #1 (STM-U1). That run doubles as the pipe proof.
3. R1 batch 2 (landrace cards, Super Skunk, Dutch Skunk lines) runs in parallel.
