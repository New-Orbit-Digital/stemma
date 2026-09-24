# Stemma — Library audit log (L1-C)
**STATUS:** Append-only log. One row per L1-C audit run. Spec: `docs/library.md`, section L1-C.

The L1-C guard reads the last row: an audit runs only if a `Library batch` or sweep PR has merged since then.

| Date (UTC) | PRs covered | Cards sampled | Passes | Fixes | Rule changes |
|---|---|---|---|---|---|
