# STM-U5 — Origin and migration map
**Depends on:** U2 merged.

## Goal
Add `dist/map/index.html`: each strain with an origin plotted at its region centroid. For a selected family, draw parent-to-child arcs to show how genetics moved, for example Afghanistan → California → Amsterdam.

## Spec
- **Library:** Leaflet 1.9.4 from cdnjs (pinned: CSS and JS), with OpenStreetMap standard tiles and the required attribution. This library is pre-approved; no others.
- **Markers:** cluster markers that share a centroid into one marker with a list popup, hand-rolled with no plugin.
- **Arcs:** curved polylines. Arrowheads are optional.
- **Filter:** a family filter works like U4, reflected in the URL as `?family=<id>`.
- **Strain pages:** each strain page gets a "See on map" link.
- **Unknown origins:** strains with unknown origin are listed under the map as "Origin unknown".

## Acceptance
- Tests cover: the family arc set equals the ancestor edges with both endpoints located, and shared-centroid grouping works.
- All tests pass. `node --check` passes.
- Fetch the built `/map/` via the local server and paste the status code. Confirm that the Leaflet script tag pins version 1.9.4.
