# Stemma — Current
**STATUS:** Volatile state. Rewritten at every close-out.

## State (2026-09-23)
- Repo `New-Orbit-Digital/stemma` created by Justin. The planner pushed the initial docs, schema, and packets on 2026-09-23.
- **Pipe NOT yet stood up.** It needs:
  - The Claude GitHub App with access to this repo.
  - The `CLAUDE_CODE_OAUTH_TOKEN` Actions secret.
  - Branch protection on `main`.
  - The connector's access to the repo, including the Workflows permission.
- Packets drafted in `docs/packets/`: STM-U1 to STM-U5. Filed as issues once the pipe is up.
- Hosting not yet set up: a Cloudflare Pages project plus a CNAME for `stemma.neworbitdigital.com`. Do this after STM-U2 merges, since there's nothing to build before then.

## Next
1. Stand up the pipe and prove it with STM-U1, the catalog tooling.
2. Run research session R1 (Skunk #1 family) in parallel. Cards go in via planner PRs and must pass the validator once U1 lands.
3. STM-U2, the site scaffold, then Pages hosting.
