# Strain Card Schema — v2
**STATUS:** Contract. The validator (`tools/validate.py`) enforces it; changes go through the planner.
Machine-readable reference: `schema/strain.schema.json`. Where the two differ, this doc wins.

Stemma is a community-maintained catalog, closer to a library catalog than to a graded body of
evidence. A card records what is known and cites where it came from. Contributing should be low
friction: one card, one source list, no tiers to argue about.

## File layout
- One card per strain at `catalog/strains/<id>.json`.
- The filename stem must equal `id`.
- UTF-8, 2-space indent, keys in the order shown below.

## Card fields
| Field | Required | Type / values | Notes |
|---|---|---|---|
| `id` | always | kebab-case `[a-z0-9]+(-[a-z0-9]+)*` | **Permanent.** Never renamed. |
| `name` | always | string | Display name, e.g. `Skunk #1` |
| `aliases` | optional | string[] | Defaults to `[]`. Used by search. |
| `kind` | always | `landrace` \| `cultivar` \| `cut` | A landrace is a regional traditional population. A cultivar is a bred variety. A cut is a clone-only selection. |
| `status` | always | `stub` \| `draft` \| `reviewed` | A stub needs only the always-required fields. A draft or reviewed card also needs `summary` and at least one source. |
| `summary` | draft+ | string, ≤ 400 **visible** chars | Written in our own words. Where accounts differ, say so here in plain prose. May carry `[[...]]` links; the markup itself does not count against the limit. |
| `born` | optional | `{year_min, year_max, display}` or `{unknown: true, display}` | Defaults to unknown. |
| `origin` | optional | `{place, country, lat, lon}` or `{unknown: true}` | Coordinates are a region centroid, rounded to 1 decimal place. Defaults to unknown. |
| `breeder` | optional | string or `null` | |
| `parents` | optional | id[] | Defaults to `[]`. Every id must be an existing card. No self-reference and no cycles. An empty list means the strain is a root (landrace) or its parents are unknown. |
| `traditional_label` | optional | `indica` \| `sativa` \| `hybrid` \| `unknown` | A traditional label only; the site explains its limits. |
| `growing` | optional | `{environment, flowering_weeks:{min,max}}` | `environment`: `indoor` \| `outdoor` \| `both` \| `unknown` |
| `sources` | draft+ | Source[] | |
| `updated` | always | `YYYY-MM-DD` | |

### Born
One of two shapes:
- **Known:** `{ "year_min": 1975, "year_max": 1979, "display": "late 1970s" }`. Here `year_min ≤ year_max`, and both fall within 1900 to the current year.
- **Unknown:** `{ "unknown": true, "display": "traditional" }`, typical for landraces.

### Origin
`{ "place": "Northern California, USA", "country": "US", "lat": 39.5, "lon": -121.5 }`
- `lat` and `lon` are an approximate region centroid, rounded to 1 decimal place, never a precise location.
- An origin with `{ "unknown": true }` needs no other fields.
- `country` is an ISO 3166-1 alpha-2 code that must be a key in `tools/countries.py` (E14). The map is a
  deliberately partial list: adding a country is an edit someone makes on purpose, and each code that
  a card uses gets a `/browse/country/<cc>/` page.

### Summary links
The summary is the one field that carries markup. `docs/voice.md` is the contract for when to link;
this is the contract for what a link means.

| Markup | Links to |
|---|---|
| `[[<id>]]` | `/s/<id>/`, with that card's `name` as the text |
| `[[<id>\|text]]` | `/s/<id>/`, with that text |
| `[[breeder:<name>]]`, `[[breeder:<name>\|text]]` | `/browse/breeder/<slug>/` |
| `[[kind:<kind>\|text]]` | `/browse/kind/<kind>/` |
| `[[country:<CC>\|text]]` | `/browse/country/<cc>/` |
| `[[label:<label>\|text]]` | `/browse/label/<label>/` |

- **Slug:** the value, lowercased, with runs of non-alphanumerics turned into `-` and the edges stripped.
- **Every target must resolve** (E13): an id names a card, a breeder matches some card's `breeder`
  exactly, a country is in the map *and* is some card's `origin.country`, and a kind or label is a
  value of that field.
- **The 400-character limit counts the visible text**, with each link reduced to its display text.
- Markup anywhere else on a card is just text. Nothing outside `summary` is parsed.

### Parents
A flat list of card ids: `[ "afghani", "colombian-gold" ]`.
- Every id must be an existing card. A card may not list itself, and the graph must have no cycles.
- Use 1 id for a selection or a cut, 2 for a cross.
- **Backcrosses** are expressed by listing the parent cross and the backcrossed parent as the two parents.
- An empty list means the strain is a root, or that its parents are not known. Where accounts of a
  lineage disagree, the card lists the best-supported parents and says so in the `summary` prose.

### Source
`{ "title": "...", "publisher": "...", "category": "breeder" | "publication" | "database" | "community", "url": "https://...", "accessed": "YYYY-MM-DD", "note": "..." }`
- `title` and `category` are required. `url`, `accessed` and `note` are optional; `url` is left off print sources.

The categories are descriptive labels, not a ranking:

| Category | What it covers |
|---|---|
| `breeder` | A breeder or seed company. |
| `publication` | Books, journals, and press. |
| `database` | Strain databases and encyclopedias. |
| `community` | Blogs, forums, and online magazines. |

## Status rules
- **`stub`:** only `id`, `name`, `kind`, `status`, and `updated` are required. Stubs let a lineage end at a strain we haven't researched yet. Stubs render as "not yet cataloged."
- **`draft`:** also needs `summary` and at least one source.
- **`reviewed`:** same as draft, plus the planner has checked every citation against its source.

## Errors (the validator fails the card)
| Rule | What it catches |
|---|---|
| **E01** | The JSON does not parse, or the top-level value is not an object. |
| **E02** | The `id` is malformed, duplicated, or does not equal the filename stem. |
| **E03** | A required field is missing, an enum field holds a value it may not, or a field has the wrong type. A draft with no `summary` or no sources lands here. |
| **E04** | A source has no `title`, or a `category` that is not one of the four. |
| **E05** | A parent id names no card, or the card lists itself. |
| **E06** | The parent graph has a cycle. |
| **E09** | A year is outside 1900..the current year, or `year_min > year_max`. |
| **E10** | A coordinate is out of range, or carries more than 1 decimal place. |
| **E11** | The summary's *visible* text runs past 400 characters. |
| **E12** | The summary's link markup is malformed: an unbalanced `[[` or `]]`, an empty target or text, or an unknown prefix. |
| **E13** | A link target resolves to nothing: no such card, breeder, country, kind, or label. |
| **E14** | An `origin.country` code is not in `tools/countries.py`. |

E07 and E08 were v1 rules for the `lineage.status` table and for per-claim evidence. Both concepts
are gone in v2, so the ids are retired rather than reused.

## Warnings (reported, not failures)
- **W1:** a child's `year_max` is earlier than a parent's `year_min`. The dates are fuzzy, so flag it rather than fail.
- **W3:** a `landrace` card lists parents. Usually a sign the card should be a `cultivar`.

W2 was the v1 "nothing stronger than folklore" warning. It went with the tiers.

## Compiled dataset (the Budlogs seam)
`python3 tools/build.py` writes `dist/data/stemma.json`:
```json
{
  "schema_version": 2,
  "generated": "ISO-8601 UTC",
  "strains": [ /* every card, sorted by id */ ],
  "edges": [ { "child": "id", "parent": "id" } ]
}
```
- Cards are written as they appear in the catalog, with defaults filled in.
- A card that has a `summary` also gets a `summary_plain`: the same prose with every link reduced to
  its display text, for anything that cannot render a link. `summary` stays the raw text with the
  markup, because that is what a card is edited as. The addition keeps `schema_version: 2`.
- Output is deterministic apart from `generated`.

## Example card
```json
{
  "id": "example-cross",
  "name": "Example Cross",
  "aliases": [],
  "kind": "cultivar",
  "status": "draft",
  "summary": "Illustrative card showing every field. Not a real strain. Accounts differ on the second parent: some name Parent C instead, and this sentence is where the card says so.",
  "born": { "year_min": 1980, "year_max": 1989, "display": "1980s" },
  "origin": { "place": "Northern California, USA", "country": "US", "lat": 39.5, "lon": -121.5 },
  "breeder": "Example Seeds",
  "parents": [ "parent-a", "parent-b" ],
  "traditional_label": "hybrid",
  "growing": { "environment": "indoor", "flowering_weeks": { "min": 8, "max": 9 } },
  "sources": [
    { "title": "Breeder product page", "publisher": "Example Seeds", "category": "breeder", "url": "https://example.com", "accessed": "2026-09-23" },
    { "title": "Book or magazine", "publisher": "Example Press", "category": "publication" },
    { "title": "Forum thread", "publisher": "Example Forum", "category": "community", "url": "https://example.com/t/1", "accessed": "2026-09-23", "note": "Where the Parent C account comes from." }
  ],
  "updated": "2026-09-23"
}
```
