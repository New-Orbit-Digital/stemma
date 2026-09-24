# Stemma interface: suggestions for Justin to react to
**STATUS:** Prep doc. These are suggestions only.

- Nothing here is decided, and nothing here changes the site.
- Written by the planner, overnight 2026-09-24.
- Scope: the Stemma interface only. Budlogs UI is out of scope.

**Brief** (always.md, backlog "Parked: visual design"):
- A clean, simple, elegant look, in the spirit of Claude's own UI.
- The "scholarly" feel lives in the name and the aesthetic, not in badges.
- Sources are shown quietly.
- Functionality comes first. This is the later visual pass.

## What "in the spirit of Claude's UI" means here
Six qualities carry over:
1. **Warm neutrals, not pure white or black.**
   - Light mode uses a paper-toned background; dark mode a soft charcoal.
   - Text is a warm near-black, never #000.
2. **One accent colour, used sparingly.** It marks links, focus rings, and the current node in the graph. Everything else is neutral.
3. **Type does the work.**
   - A readable serif or humanist sans for body text, at a generous size (17–18px on mobile).
   - Line length is capped around 65–70 characters.
   - Hierarchy comes from size and weight, not colour or boxes.
4. **Space instead of borders.**
   - Sections are separated by whitespace and the occasional hairline rule.
   - No cards-inside-cards, no drop shadows, no pill badges.
5. **Quiet motion.** Short fades (about 150ms) on disclosure and hover, and nothing bouncy. Respect `prefers-reduced-motion`.
6. **Small, muted metadata.** Dates, categories, and "updated" lines are small, in a secondary text colour, and stay out of the way.

---

## Option A: "Library card"
A calm, reading-first page. The catalog feels like a well-set reference book.

**Typography:**
- Body in a text serif. Candidates on Google Fonts: Source Serif 4, Literata, or Newsreader.
- UI chrome (search, nav, labels) in a quiet sans: Inter or the system UI stack.
- Strain names set large in the serif, weight 500–600, with a slightly tightened letter-spacing.

**Layout (strain page):**
- The name, then one muted line: aliases · kind · traditional label.
- The summary as a single lead paragraph at a slightly larger size.
- A two-column "facts" list on wide screens (Born / Origin / Breeder / Parents / Children). It stacks on mobile.
- The lineage graph gets its own full-width band.

**Sources:** an unnumbered list at the foot of the page, under a small-caps "Sources" label.
- Each line reads: *Title* — Publisher, followed by a tiny muted category word (breeder · database …).
- Links are underlined only on hover.

**Colour:**

| | Light | Dark |
|---|---|---|
| Background | #FAF9F5 | #1F1E1C |
| Text | #2B2A27 | — |
| Secondary text | #6B6862 | — |
| Accent | one warm clay/terracotta | lighter for contrast |

**Why:** it fits the "library catalog" framing in always.md most literally.

**Risk:** a serif body can feel slow on phones. Test it at 17px.

## Option B: "Quiet app"
A sans-serif, app-like interface. It's closest in feel to the Claude chat UI itself, and fastest to scan on a phone.

**Typography:**
- One family throughout: Inter, or the system stack for zero font weight.
- Names at 28–32px, weight 600. Body at 16–17px.
- Tabular numbers for years and flowering weeks.

**Layout:**
- The search bar is the home screen's only strong element, centred with generous top space, like the Claude new-chat screen.
- Strain pages use a single column with sections under small uppercase labels (LINEAGE, ORIGIN, SOURCES) in the secondary colour.

**Sources:** collapsed by default behind a quiet "Sources (4)" disclosure row. Expanded, it's the same one-line-per-source list as Option A.
- This is the quietest option.
- The trade-off: sources are one tap away rather than visible.

**Colour:** the same warm neutrals as A. The accent is used only for links and the current graph node.

**Why:** it's the most mobile-native and has the lowest visual weight.

**Risk:** it can read as generic. Personality has to come from the lineage graph and the map.

## Option C: "Field notes"
Option A's reading quality with a light touch of natural-history character, without decoration for its own sake.

**Typography:**
- A serif for names and summaries.
- A monospace or small-caps sans for data (years, coordinates, category labels), as if typed onto a specimen label.
  - Candidates: IBM Plex Mono or JetBrains Mono, for the data only.

**Layout:**
- A thin "specimen label" block under the name holds kind, born, origin, and traditional label in the mono face, aligned in two columns.
- The lineage graph uses thin, ink-like strokes.
- Landrace roots sit at the bottom like a rootstock.

**Sources:** the footer list is set in the mono face at a small size, like a bibliography slip. Categories appear as lowercase words, not badges.

**Colour:** the same warm neutrals. The accent is a muted botanical green instead of clay.

**Why:** it gives Stemma a distinct identity that suits lineage and history, while staying restrained.

**Risk:** a second typeface adds weight and a risk of whimsy. It needs discipline to stay elegant.

---

## Shared recommendations, whichever option
These are the planner's view; Justin decides.
- **Keep one accent colour** and use it for the current node in the graph, links, and focus. The graph edges stay neutral grey (U7 already made them uniform).
- **Make sources quiet but present.** Put them at the foot of the page, one line each, with the category as a small muted word. No numbering, no icons.
  - Option B's collapsed list is the only real variant here.
- **Dark mode first-class.** Test contrast on the muted secondary text; it's the usual failure point.
- **Summary before data.** The one-paragraph summary is the page's voice. It should sit directly under the name, above any metadata. This pairs with the house-voice decision.
- **Stubs:** render them as a muted "not yet cataloged" line with the name only, and style them the same way in the graph.
- **Fonts:** at most two families, self-hosted or loaded from Google Fonts only. Check the cache-busting (U6) and the CSP if one is added.
- **No new features in the visual pass.** It is restyling only, so the verified behaviour from Sprint 1 and U7 stays intact.

## Suggested next step (if Justin wants one)
1. Pick A, B, or C, or a mix: for example A's typography with B's collapsed sources.
2. The planner then writes a small packet (STM-U8, a visual pass). It would contain:
   - CSS tokens (colours, type scale, spacing).
   - Strain-page layout only.
   - Acceptance by Justin's eye on a PR preview deploy.
