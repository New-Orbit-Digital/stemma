# STM-U4 — Timeline page
**Depends on:** U2 merged.

## Goal
Add `dist/timeline/index.html`: every dated strain plotted as a horizontal bar from `year_min` to `year_max` on a shared year axis, grouped visually by decade. Undated strains (`born.unknown`) go in a "Roots and undated" strip at the start.

## Spec
- **Rendering:** hand-rolled SVG, no library.
- **Filter:** a "family" filter. Pick a strain (reusing the search component) to show only it and its ancestors. The selected family is reflected in the URL as `?family=<id>` so it can be shared.
- **Bars:** colour by `kind`. Clicking a bar navigates to the strain page.
- **Strain pages:** each strain page gets a "See on timeline" link to `/timeline/?family=<id>`.
- **Mobile:** the axis scrolls horizontally inside its container.

## Acceptance
- Tests cover: the family filter returns exactly the ancestor set on a fixture graph, and undated strains land in the roots strip.
- All tests pass. `node --check` passes.
- Paste the built timeline page's bar count against the dataset's dated count.
