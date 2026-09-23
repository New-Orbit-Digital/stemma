# STM-U3 — Lineage graph on strain pages
**Depends on:** U2 merged.

## Goal
In `#lineage-graph` on each strain page, render this strain's ancestors back to its roots (up to 6 generations) and its direct children, as a top-to-bottom layered diagram. Roots go at the top; the current strain is highlighted.

## Spec
- **Rendering:** hand-rolled SVG with a layered layout, meaning a rank by longest path from the current node plus simple ordering to reduce crossings. No library. If you judge a library is required, STOP and propose one (with name and pinned version) rather than adding it.
- **Edge styling by `best_tier`:**
  - `genetically-tested` and `documented`: solid lines.
  - `breeder-claimed`: dashed lines.
  - `folklore`: dotted lines.
  - Disputed edges (`disputed: true`): a distinct accent colour, hidden behind a "show disputed" toggle that is off by default.
- **Nodes:** show the name and a short born display. Clicking a node navigates to that strain's page. Stubs are visually muted.
- **Mobile:** the diagram scrolls horizontally inside its container, and the page itself never scrolls sideways. Tap targets are at least 40px.
- **Legend:** a small legend explaining the line styles.
- **No new data fields.** Use `data/stemma.json` edges only.

## Acceptance
- Unit tests for the layout function, written as pure JS logic mirrored in Python or tested via build-time precomputation. Choose one and state which. Cover: a simple cross, a backcross (the same ancestor reached twice renders once), and a disputed edge hidden by default.
- `python3 tools/run_tests.py` all pass. `node --check` passes on the changed JS.
- Screenshots aren't possible. Instead, paste the generated SVG markup for one fixture strain from a build-time render, or describe the check you ran.
