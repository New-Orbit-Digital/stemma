# Strain Card Schema — v1
**STATUS:** Contract. The validator (STM-U1) enforces it; changes go through the planner.
Machine-readable reference: `schema/strain.schema.json`. Where the two differ, this doc wins.

## File layout
- One card per strain at `catalog/strains/<id>.json`.
- The filename stem must equal `id`.
- UTF-8, 2-space indent, keys in the order shown below.

## Card fields
| Field | Required | Type / values | Notes |
|---|---|---|---|
| `id` | always | kebab-case `[a-z0-9]+(-[a-z0-9]+)*` | **Permanent.** Never renamed after merge. |
| `name` | always | string | Display name, e.g. `Skunk #1` |
| `aliases` | draft+ | string[] | Other names; used by search. May be empty. |
| `kind` | always | `landrace` \| `cultivar` \| `cut` | A landrace is a regional traditional population. A cultivar is a bred variety. A cut is a clone-only selection. |
| `status` | always | `stub` \| `draft` \| `reviewed` | See the status rules below. |
| `summary` | draft+ | string, ≤ 400 chars | Our own words. Never copied text. |
| `born` | draft+ | Born object | When it emerged. |
| `origin` | draft+ | Origin object | Where it emerged. |
| `breeder` | optional | `{name, evidence[]}` or `null` | |
| `lineage` | draft+ | Lineage object | |
| `traditional_label` | draft+ | `indica` \| `sativa` \| `hybrid` \| `unknown` | A traditional label only; the site explains its limits. |
| `growing` | optional | `{environment, flowering_weeks:{min,max}}` | `environment`: `indoor` \| `outdoor` \| `both` \| `unknown` |
| `sources` | draft+ | Source[] | Every `evidence.source` must resolve here. |
| `updated` | always | `YYYY-MM-DD` | |

### Born
One of two shapes:
- **Known:** `{ "year_min": 1975, "year_max": 1979, "display": "late 1970s", "evidence": [...] }`. Here `year_min ≤ year_max`, and both fall within 1900 to the current year.
- **Unknown:** `{ "unknown": true, "display": "traditional" }`, typical for landraces. It needs no evidence.

### Origin
`{ "place": "Northern California, USA", "country": "US", "lat": 39.5, "lon": -121.5, "evidence": [...] }`
- `lat` and `lon` are an approximate region centroid, rounded to 1 decimal place, never a precise location.
- An origin with `{ "unknown": true }` needs no other fields.

### Lineage
`{ "status": ..., "parents": [...], "disputes": [...] }`

| `status` | Meaning | Rule |
|---|---|---|
| `root` | A landrace: the tree stops here. | `kind` must be `landrace`, and `parents` must be empty. |
| `known` | All parents are identified. | At least 1 parent. Use 1 for a selection or cut, 2 for a cross. |
| `partial` | One parent is known and the other is not. | Exactly 1 parent. |
| `unknown` | Nothing is credible. | `parents` must be empty. |
| `disputed` | Competing accounts exist. | `disputes` must be non-empty. `parents` holds the best-supported account. |

- **Parent:** `{ "id": "afghani", "evidence": [...] }`. The id must be an existing card, and a card cannot list itself. The lineage graph must have no cycles.
- **Dispute:** `{ "claim": "short description", "parents": ["id-a", "id-b"], "evidence": [...] }`. Dispute parent ids must also exist as cards.
- **Backcrosses** are expressed by listing the parent cross and the backcrossed parent as the two parents.

### Evidence item
`{ "tier": "documented", "source": "s1", "note": "optional context" }`

| Tier | Rank | Meaning |
|---|---|---|
| `genetically-tested` | 4 | DNA evidence, such as a Phylos genotype report. It verifies the tested sample, not the name the sample was sold under. Use `note` to record the sample's name. |
| `documented` | 3 | Contemporaneous or published records: books, magazines, interviews, seed catalogs. |
| `breeder-claimed` | 2 | The breeder's own account. |
| `folklore` | 1 | Community lore with no stronger backing. Good content, and labeled as such. |

- Any claim that isn't marked unknown needs at least one evidence item. Claims are `born`, `origin`, `breeder`, each parent, and each dispute.

### Source
`{ "id": "s1", "title": "...", "publisher": "...", "url": "https://...", "accessed": "YYYY-MM-DD" }`
- The `url` is optional for print sources.
- Source ids must be unique within the card.

## Status rules
- **`stub`:** only `id`, `name`, `kind`, `status`, and `updated` are required. Stubs let a lineage end at a strain we haven't researched yet. Stubs render as "not yet cataloged."
- **`draft`:** all draft+ fields are required, and evidence rules apply.
- **`reviewed`:** same as draft, plus the planner has checked every citation against its source.

## Warnings (reported, not failures)
- **W1:** a child's `year_max` is earlier than a parent's `year_min`. The dates are fuzzy, so flag it rather than fail.
- **W2:** a `draft` or `reviewed` card has no evidence item stronger than `folklore`.

## Compiled dataset (the Budlogs seam)
`python3 tools/build.py` writes `dist/data/stemma.json`:
```json
{
  "schema_version": 1,
  "generated": "ISO-8601 UTC",
  "strains": [ /* every card, sorted by id */ ],
  "edges": [ { "child": "id", "parent": "id", "best_tier": "documented", "disputed": false } ]
}
```
- Output is deterministic apart from `generated`.
- Edges cover main parents (`disputed: false`) and dispute parents (`disputed: true`).

## Example card
```json
{
  "id": "example-cross",
  "name": "Example Cross",
  "aliases": [],
  "kind": "cultivar",
  "status": "draft",
  "summary": "Illustrative card showing every field. Not a real strain.",
  "born": { "year_min": 1980, "year_max": 1989, "display": "1980s", "evidence": [ { "tier": "breeder-claimed", "source": "s1" } ] },
  "origin": { "place": "Northern California, USA", "country": "US", "lat": 39.5, "lon": -121.5, "evidence": [ { "tier": "documented", "source": "s2" } ] },
  "breeder": { "name": "Example Seeds", "evidence": [ { "tier": "breeder-claimed", "source": "s1" } ] },
  "lineage": {
    "status": "disputed",
    "parents": [ { "id": "parent-a", "evidence": [ { "tier": "documented", "source": "s2" } ] }, { "id": "parent-b", "evidence": [ { "tier": "documented", "source": "s2" } ] } ],
    "disputes": [ { "claim": "Some growers say the second parent was Parent C", "parents": ["parent-a", "parent-c"], "evidence": [ { "tier": "folklore", "source": "s3" } ] } ]
  },
  "traditional_label": "hybrid",
  "growing": { "environment": "indoor", "flowering_weeks": { "min": 8, "max": 9 } },
  "sources": [
    { "id": "s1", "title": "Breeder product page", "publisher": "Example Seeds", "url": "https://example.com", "accessed": "2026-09-23" },
    { "id": "s2", "title": "Book or magazine", "publisher": "Example Press" },
    { "id": "s3", "title": "Forum thread", "publisher": "Example Forum", "url": "https://example.com/t/1", "accessed": "2026-09-23" }
  ],
  "updated": "2026-09-23"
}
```
