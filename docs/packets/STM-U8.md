# STM-U8 — Inline links and browse pages
**Depends on:** U7 merged.

**Decisions (Justin, chat, 2026-09-24):**
- Card prose links inline, the way Wikipedia does.
- Links to anything that isn't a strain go to a results page filtered to that dimension, so every link points at something Stemma catalogs.
- See `docs/voice.md`.

## Deliverables

### 1. Summary link markup
The build renders these forms inside `summary`:

| Markup | Renders as a link to |
|---|---|
| `[[<id>]]` | `/s/<id>/`, with the card's `name` as the text |
| `[[<id>\|text]]` | `/s/<id>/`, with that text |
| `[[breeder:<name>]]` or `[[breeder:<name>\|text]]` | `/browse/breeder/<slug>/` |
| `[[kind:<kind>\|text]]` | `/browse/kind/<kind>/` |
| `[[country:<CC>\|text]]` | `/browse/country/<cc>/` (lowercase ISO-2) |
| `[[label:<label>\|text]]` | `/browse/label/<label>/` |

- **Slug:** the name, lowercased, with runs of non-alphanumerics turned into `-` and leading and trailing `-` stripped.
- **Escaping:** HTML-escape all text before inserting the links.
- **Scope:** the markup applies only in `summary`.

### 2. Validator
Add these checks, keeping the existing rule-id style:
- **Malformed markup.** Unbalanced `[[`/`]]`, an empty target, or an unknown prefix is an **error**.
- **Unresolved targets.** Each link target must resolve, or it's an **error**:
  - **Strain id:** a card with that id exists.
  - **`breeder:`** at least one card's `breeder` equals the name exactly.
  - **`kind:`** and **`label:`** the value is a valid enum value.
  - **`country:`** at least one card has that `origin.country`, and the code is in `tools/countries.py`.
- **Summary length.** The 400-character limit now counts the **visible text**, with the markup reduced to its display text.

### 3. `tools/countries.py`
- An ISO-2 to English-name map, stdlib only.
- Cover at least: AF, CO, MX, US, NL, IN, TH, JM, NP, PK, JP, CA, ES, GB, FR, DE, LB, MA, BR, ZA, VN, LA, KH, CN, and AU.
- An `origin.country` code that isn't in the map is a validator **error**, so the map grows deliberately.

### 4. Browse pages (static, generated at build time)
All browse pages reuse the search results list style. Each row shows the name as a link, the kind, and the born display.
- **Dimension pages.** Build one page for every value that at least one card has:
  - `/browse/breeder/<slug>/`
  - `/browse/kind/<kind>/`
  - `/browse/country/<cc>/`
  - `/browse/label/<label>/`
- **Page contents:**
  - A heading of the form `Breeder · Sensi Seeds` (or `Kind · Landrace`, `Origin · Mexico`, `Label · Sativa`).
  - A card count.
  - The matching cards, sorted by name.
- **`/browse/` index:** one short list per dimension, where each value links to its page and shows its count.
- Add a **Browse** item to the masthead.

### 5. Strain pages
- **Field links.** The `breeder`, `kind`, origin country, and `traditional_label` fields in the strain header link to their browse pages.
- **Summary.** The summary renders its inline links.

### 6. Dataset
- Keep `summary` as the raw text with markup, since that's the source of truth.
- Add `summary_plain`: the visible text, without markup.
- Keep `schema_version: 2`, because the change is additive.

### 7. Tests
Cover:
- Each markup form, rendering and escaping included.
- Validator errors for:
  - unknown ids, breeders, countries, and enum values
  - malformed markup
  - over-length visible text
- Visible-length counting.
- One browse page per occurring value, with correct membership and counts.
- That every internal link in `dist/` resolves. The existing test already does this; make sure it covers `/browse/`.
- Strain-header field links.

Add fixtures under `tests/fixtures/` whose summaries use each markup form.

## Out of scope
- Card content. The planner rewrites summaries after this merges.
- Search changes.
- New dimensions beyond the four.
- Visual design.

## Acceptance (paste the actual output)
- **Tests:** `python3 tools/run_tests.py` passes. Paste the total.
- **JS:** `node --check site/assets/app.js`.
- **Real catalog:** paste the output of `python3 tools/validate.py` and `python3 tools/build.py`. Include the count of browse pages written.
- **Fixtures:** build the fixtures and paste the file list under `browse/`, plus the rendered summary HTML from one fixture strain page that uses every markup form.
- **Fixture link resolution:** paste proof, a test name or a script's output, that every `href` beginning with `/` in the fixture build resolves to a file.
