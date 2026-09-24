# STM-U7 — Schema v2: community-catalog model
**Depends on:** U6 merged. **Decision:** Justin, chat, 2026-09-24. Stemma is a community-maintained hobbyist catalog, like TMDB or a library catalog, not a graded body of evidence. Contributing should have low friction.

## Summary of the change
- **Drop** per-claim evidence items and the four evidence tiers.
- **Drop** structured disputes and the `lineage.status` field.
- **Tag sources by category instead of ranking them.** A card carries one flat source list.
- **Simplify the site to match:**
  - no tier badges, tier legend, or disputed toggle
  - uniform graph and map lines
  - sources as a quiet list at the bottom of each strain page

## 1. Card schema v2 (rewrite `docs/schema.md` to exactly this)
This is one JSON file per card at `catalog/strains/<id>.json`. The filename stem must equal `id`. Keys appear in this order:

| Field | Required | Type / values | Notes |
|---|---|---|---|
| `id` | always | kebab-case | **Permanent.** Never renamed. |
| `name` | always | string | |
| `aliases` | optional | string[] | Defaults to `[]`. Search uses it. |
| `kind` | always | `landrace` \| `cultivar` \| `cut` | |
| `status` | always | `stub` \| `draft` \| `reviewed` | A stub needs only the always-required fields. A draft or reviewed card also needs `summary` and at least one source. |
| `summary` | draft+ | string, ≤ 400 chars | In our own words. Where accounts differ, say so here in plain prose. |
| `born` | optional | `{year_min, year_max, display}` or `{unknown: true, display}` | Defaults to unknown. |
| `origin` | optional | `{place, country, lat, lon}` or `{unknown: true}` | Coordinates are a region centroid, 1 decimal place. Defaults to unknown. |
| `breeder` | optional | string or `null` | |
| `parents` | optional | id[] | Defaults to `[]`. Every id must be a card. No self-reference and no cycles. An empty list means a root (a landrace) or simply unknown. |
| `traditional_label` | optional | `indica` \| `sativa` \| `hybrid` \| `unknown` | |
| `growing` | optional | `{environment, flowering_weeks:{min,max}}` | |
| `sources` | draft+ | Source[] | |
| `updated` | always | `YYYY-MM-DD` | |

**Source:** `{ "title": "...", "publisher": "...", "category": "breeder" | "publication" | "database" | "community", "url": "https://..." (optional), "accessed": "YYYY-MM-DD" (optional), "note": "..." (optional) }`

The categories are descriptive labels, not a ranking:
- `breeder`: the breeder or a seed company.
- `publication`: books, journals, and press.
- `database`: strain databases and encyclopedias.
- `community`: blogs, forums, and online magazines.

**Validator rules (errors):**
- The JSON parses.
- The id is well formed, unique, and matches the filename.
- All always-required fields are present.
- Enum values are valid.
- Draft cards have a summary and at least one source.
- Summary length is ≤ 400.
- Years fall in 1900..current, with min ≤ max.
- Coordinates are in range, at 1 decimal place.
- Every parent exists, with no self-parent and no cycles.
- Every source has a title and a valid category.

**Warnings:**
- W1: a child's `year_max` is earlier than a parent's `year_min`. This rule is kept.
- W3: a `landrace` lists parents.

Drop W2.

## 2. Dataset
`dist/data/stemma.json` becomes `schema_version: 2`. Each card is written as it appears in the catalog, with defaults filled in. Each entry in `edges` becomes `{ "child": id, "parent": id }`, with no `best_tier` and no `disputed`. The output stays deterministic.

## 3. Site
- **Strain page:**
  - Remove the tier badges and the Disputed block.
  - Keep the rest of the header: name, aliases, kind, traditional label with its hint, summary, born, origin, breeder, parents, and children.
  - Sources become a compact list at the bottom: title (linked), publisher, and a small muted category label. No numbering, no badges.
- **Lineage graph (`tools/lineage.py`):**
  - Use one edge style for all lines.
  - Remove the legend's tier entries and the disputed layer and toggle.
  - Stubs stay muted. The current node stays highlighted.
  - All other layout behaviour is unchanged.
- **Timeline:** remove the disputed handling in `family()`. A family is the strain plus all of its ancestors.
- **Map:** arcs use one style. Remove the tier legend.
- **About page:** rewrite it for the community-catalog framing:
  - What Stemma is: a community-maintained catalog of strain lineage and history for hobbyists.
  - How sources are categorized, and that categories are descriptive, not a ranking.
  - That where accounts differ, the card says so.
  - Why indica/sativa is a traditional label. Keep the existing text.
  - "Not medical advice."
  - Remove all tier and dispute language.

## 4. Migration (planner-authorized mechanical edit of `catalog/strains/`)
The executor rule "never author or edit strain facts" still holds. This is a **mechanical format conversion only**, explicitly authorized by the planner. Write `tools/migrate_v2.py` (stdlib only), run it once, and commit the result. The mapping:
- Remove `evidence` from `born`, `origin`, and `breeder`. `breeder` becomes the name string, or `null`.
- `lineage.parents[].id` becomes `parents`.
- Delete `lineage.disputes` outright. Every existing dispute is already described in its card's summary prose. Verify that for `acapulco-gold`: its summary mentions the Nepalese claim.
- Remove source `id`s.
- Add `category` by publisher, using this table and nothing else:
  - `Sensi Seeds`, `Barney's Farm`, `Carters Cannabis` → `breeder`
  - `Springer`, `Pensoft`, `University of California Press`, `Black Cannabis Magazine` → `publication`
  - `Wikipedia`, `Wikipedia (citing The New York Times)`, `Leafly`, `SeedFinder`, `Cannigma` → `database`
  - If any publisher is not in this table, STOP and report it.
- Lift each evidence `note` that carries information into its source's `note`, deduplicated per source. Drop any note that just restates the tier.
- Leave `summary`, `name`, `aliases`, `kind`, `status`, `born` years and display, origin place and coordinates, `traditional_label`, `growing`, and `updated` byte-identical.
- `nepalese` stays a stub with no parents. `acapulco-gold`'s `parents` stays empty.
- Convert `tests/fixtures/` to v2 too. Replace the dispute and tier fixture cases with W3 and category cases.

## 5. Out of scope
No new pages or features, no visual redesign beyond removing the elements above, and no card content changes other than the mechanical mapping.

## Acceptance (paste the actual output)
- **Tests:** `python3 tools/run_tests.py` all pass. Paste the total.
- **JS:** `node --check site/assets/app.js`.
- **Validation:** `python3 tools/validate.py` on the migrated catalog. Paste the full output. Expect 13 cards and 0 errors.
- **Migration record:** `git diff --stat catalog/strains/`, plus the full migrated `catalog/strains/skunk-1.json` and `catalog/strains/acapulco-gold.json`.
- **Mechanical proof:** a script check, pasted, showing that for every card the `summary`, `name`, `born`, and origin place and coordinates are unchanged against `main`.
- **Absence checks:** grep the built `dist/` for `tier`, `documented`, `breeder-claimed`, `folklore`, and `disputed`, and paste the result. Expect no matches in rendered pages. Word matches inside summaries are acceptable; list them.
- **Build:** `python3 tools/build.py` prints 13 strains and 13 edges.
