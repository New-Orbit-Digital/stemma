# Stemma — Library audit log (L1-C)
**STATUS:** Append-only log. One row per L1-C audit run. Spec: `docs/library.md`, section L1-C.

The L1-C guard reads the last row: an audit runs only if a `Library batch` or sweep PR has merged since then.

| Date (UTC) | PRs covered | Cards sampled | Passes | Fixes | Rule changes |
|---|---|---|---|---|---|
| 2026-09-24 21:35 | #53 (Library batch 1, merged 21:18). Fixes in #54. | 5 rechecked against their cited sources: gsc, blue-dream, durban-poison, biscotti, lemon-cherry-gelato. All 25 cards also read for voice and catalog consistency. | 2 of 5 (durban-poison, biscotti) | Sample: gsc (breeder/origin prose vs its cited source), blue-dream (grow environment, missing link), lemon-cherry-gelato (breeder, origin, date given by both cited sources). Consistency: sour-diesel and silver-pearl (cataloged parents missing from `parents`), mac, gary-payton, cherry-pie, gelato (missing first-mention links). | Added two fill rules: cross-check names against the catalog; keep grow data out of the summary. Watching (2 cases, below threshold): writing "unknown"/"unconfirmed" when the cited source names a breeder or origin. |
