# STM-U7 — Schema v2: community-catalog model
**Depends on:** U6 merged.

**Decision (Justin, chat, 2026-09-24):** Stemma is a community-maintained hobbyist catalog, closer to TMDB or a library catalog than a graded body of evidence. Contributing should have low friction.

## Summary of the change
- Drop per-claim evidence items and the four evidence tiers.
- Drop structured disputes and the `lineage.status` field.
- Replace them with one flat, categorized source list per card.
- Simplify the site to match:
  - No tier badges, tier legend, or disputed toggle.
  - Uniform graph and map lines.
  - Sources shown as a quiet list at the bottom of each strain page.

## 1. Card schema v2 (rewrite `docs/schema.md` to exactly this)
- One JSON file per card at `catalog/strains/<id>.json`.
- The filename stem must equal `id`.
- Keys appear in this order:

| Field | Required | Type / values | Notes |
|---|---|---|---|
| `id` | always | kebab-case | **Permanent.** Never renamed. |
| `name` | always | string | |
| `aliases` | optional | string[] | Defaults to `[]`. Used by search. |
| `kind` | always | `landrace` \| `cultivar` \| `cut` | |
| `status` | always | `stub` \| `draft` \| `reviewed` | A stub needs only the always-required fields. A draft or reviewed card also needs `summary` and at least one source. |
| `summary` | draft+ | string, ≤ 400 chars | Written in our own words. Where accounts differ, say so here in plain prose. |
| `born` | optional | `{year_min, year_max, display}` or `{unknown: true, display}` | Defaults to unknown. |
| `origin` | optional | `{place, country, lat, lon}` or `{unknown: true}` | Coordinates are a region centroid, rounded to 1 decimal place. Defaults to unknown. |
| `breeder` | optional | string or `null` | |
| `parents` | optional | id[] | Defaults to `[]`. Every id must be an existing card. No self-reference and no cycles. An empty list means the strain is a root (landrace) or its parents are unknown. |
| `traditional_label` | optional | `indica` \| `sativa` \| `hybrid` \| `unknown` | |
| `growing` | optional | `{environment, flowering_weeks:{min,max}}` | |
| `sources` | draft+ | Source[] | |
| `updated` | always | `YYYY-MM-DD` | |

**Source shape:** `{ "title": "...", "publisher": "...", "category": "breeder" | "publication" | "database" | "community", "url": "https://..." (optional), "accessed": "YYYY-MM-DD" (optional), "note": "..." (optional) }`

The categories are descriptive labels, not a ranking:
- `breeder`: a breeder or seed company.
- `publication`: books, journals, and press.
- `database`: strain databases and encyclopedias.
- `community`: blogs, forums, and online magazines.

**Validator errors.** The validator fails a card when any of these is violated:
- The JSON must parse.
- The id must be well formed, unique, and equal to the filename stem.
- All always-required fields must be present.
- Every enum field must hold one of its listed values.
- A draft card must have a summary and at least one source.
- The summary must be at most 400 characters.
- Years must fall between 1900 and the current year, with `year_min` ≤ `year_max`.
- Coordinates must be in range and use exactly 1 decimal place.
- Every parent must exist. No card may list itself as a parent, and there may be no cycles.
- Every source must have a title and a valid category.

**Validator warnings:**
- **W1** (kept): a child's `year_max` is earlier than a parent's `year_min`.
- **W3** (new): a `landrace` card lists parents.
- **W2** is dropped.

## 2. Dataset
- `dist/data/stemma.json` becomes `schema_version: 2`.
- Cards are written as they appear in the catalog, with defaults filled in.
- `edges` entries become `{ "child": id, "parent": id }`. There is no `best_tier` and no `disputed`.
- Output stays deterministic.

## 3. Site
- **Strain page:**
  - Remove the tier badges and the Disputed block.
  - Keep the rest of the header: name, aliases, kind, traditional label with its hint, summary, born, origin, breeder, parents, and children.
  - Sources become a compact list at the bottom: linked title, publisher, and a small muted category label. No numbering and no badges.
- **Lineage graph (`tools/lineage.py`):**
  - Draw every line in one edge style.
  - Remove the legend's tier entries, the disputed layer, and its toggle.
  - Keep stubs muted and the current node highlighted. The layout is otherwise unchanged.
- **Timeline:** remove the disputed handling in `family()`. A family is the strain plus all of its ancestors.
- **Map:** draw arcs in one style and remove the tier legend.
- **About page:** rewrite it for the community-catalog framing. Remove all tier and dispute language. Cover:
  - What Stemma is: a community-maintained catalog of strain lineage and history for hobbyists.
  - How sources are categorized, and that the categories are descriptive, not a ranking.
  - That where accounts differ, the card says so.
  - Why indica/sativa is only a traditional label (keep the existing text).
  - "Not medical advice."

## 4. Migration (planner-authorized mechanical edit of `catalog/strains/`)
The executor rule "never author or edit strain facts" still holds. This is a mechanical format conversion only, explicitly authorized by the planner.

Write `tools/migrate_v2.py` (stdlib only), run it once, and commit the result. It applies these mappings:
- **Evidence:** remove `evidence` from `born`, `origin`, and `breeder`.
- **Breeder:** `breeder` becomes its name as a plain string, or `null`.
- **Parents:** `lineage.parents[].id` becomes the top-level `parents` list.
- **Disputes:** remove `lineage.disputes`. Every existing dispute is already described in its card's summary prose. Verify this for `acapulco-gold`, whose summary mentions the Nepalese claim.
- **Source ids:** remove them.
- **Source categories:** add a `category` to every source, chosen by publisher from this table only:
  - `Sensi Seeds`, `Barney's Farm`, `Carters Cannabis` → `breeder`
  - `Springer`, `Pensoft`, `University of California Press`, `Black Cannabis Magazine` → `publication`
  - `Wikipedia`, `Wikipedia (citing The New York Times)`, `Leafly`, `SeedFinder`, `Cannigma` → `database`
  - If a publisher isn't in this table, STOP and report it.
- **Notes:** move each informative evidence `note` onto its source's `note`, deduplicated per source. Drop notes that only restate the tier.
- **Unchanged fields:** `summary`, `name`, `aliases`, `kind`, `status`, `born` years and display, origin place and coordinates, `traditional_label`, `growing`, and `updated` must stay byte-identical.
- **Specific cards:**
  - `nepalese` stays a stub with no parents.
  - `acapulco-gold` keeps an empty `parents` list. Its one disputed edge (to `nepalese`) disappears with the dispute.
- **Fixtures:** convert `tests/fixtures/` to v2 as well. Replace the dispute and tier fixture cases with W3 and category cases.

## 5. Out of scope
- New pages or features.
- Any visual redesign beyond removing the elements listed above.
- Any card content changes beyond the mechanical mapping.

## Acceptance (paste the actual output)
- **Tests:** `python3 tools/run_tests.py` passes. Paste the total.
- **JS syntax:** `node --check site/assets/app.js` passes.
- **Validator:** paste the full output of `python3 tools/validate.py` on the migrated catalog. Expect 13 cards and 0 errors.
- **Migration record:** paste `git diff --stat catalog/strains/`, plus the full migrated `catalog/strains/skunk-1.json` and `catalog/strains/acapulco-gold.json`.
- **Mechanical proof:** paste a script check showing that, for every card, `summary`, `name`, `born`, and origin place and coordinates are unchanged versus `main`.
- **No tier/dispute text in the build:** grep the built `dist/` for `tier`, `documented`, `breeder-claimed`, `folklore`, and `disputed`, and paste the result. Rendered pages should have no matches. Matches inside summaries are fine, but list them.
- **Build:** `python3 tools/build.py` prints 13 strains and **12 edges**. That's one fewer than today, because the disputed Nepalese edge is gone.
