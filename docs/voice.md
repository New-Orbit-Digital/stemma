# Stemma — House voice
**STATUS:** Contract for all card prose. Chosen by Justin on 2026-09-24: voice **2a, "Reference"**.

## The voice in one line
Write like a good encyclopedia entry. Say what the strain is, where and when it came from, and what it came from, as plain facts, with links to everything Stemma catalogs.

**Modeled on** the lead section of Wikipedia's *Cabernet Sauvignon* article, in these ways:
- It states parentage as fact.
- Superseded or competing accounts are handled with past-to-present phrasing ("was long said to…"; "some sources place…").
- Both proper nouns and concepts are linked inline.

## Priority: populate, don't adjudicate (Justin, 2026-09-24)
- **The goal is filled cards, not an authority.** Check facts against a source, but don't spend effort weighing theories or chasing disputes.
- **Pick the commonly cited account and move on.** Record a competing account only if it's commonly repeated, and then in one short clause.
- **Don't leave fields empty just to avoid a possible conflict.** Fill the breeder, origin, and date with the commonly cited values. Use "unknown" only when no source gives a value.

## Rules
1. **Open with identity.** The first sentence is "**X** is a [kind] …". It says what the strain is, who made it (if known), and where and when.
2. **State lineage as fact.** For example, "A cross of [[a]] and [[b]]…". Don't qualify it unless the sources actually disagree.
3. **Mention disagreement once, plainly, if at all.** Give it one clause or sentence, such as "Some sources place its origin in…" or "Other accounts describe it as…". Don't adjudicate and don't hedge every clause.
4. **Be specific instead of using adjectives.** A year, a place, or a name beats "legendary", "iconic", or "potent".
5. **Trust the reader.** Use the field's vocabulary (landrace, backcross, phenotype, cut) without defining it, and link it instead.
6. **Keep it to 2–4 sentences.** The visible text is 400 characters or less (link markup doesn't count).
7. **Paraphrase.** Never copy a source's wording.
8. **Write in the third person and past tense for history.** Use the present tense only for what the strain is.

## Banned habits
- **Hedged openers:** "widely regarded as", "often considered", "associated with", "is said to be" (unless you're reporting a specific account).
- **Unsourced superlatives:** "most famous", "one of the best", "iconic".
- **Rhythm filler:** lists of three written for cadence, and colon setups ("The cross behind X: …").
- **Summing-up closers:** "…making it a cornerstone of modern breeding." End on a fact.
- **Reader-directed moves:** rhetorical questions, "fun fact", "interestingly", "notably", and second person.
- **Marketing and effects language:** taste and smell adjectives (skunky, dank, earthy notes), effects, and medical claims.

## Links (requires STM-U8)
Link the **first mention** of anything Stemma catalogs. Don't link the card's own name.

| Markup | Links to |
|---|---|
| `[[skunk-1]]` | the strain page, using the card's name as the link text |
| `[[skunk-1\|Skunk #1]]` | the strain page, with custom link text |
| `[[breeder:Sensi Seeds]]` | the browse page for that breeder |
| `[[kind:landrace\|landrace]]` | the browse page for that kind |
| `[[country:MX\|Mexico]]` | the browse page for that origin country |
| `[[label:sativa\|sativa]]` | the browse page for that traditional label |

- **Breeder names:** a breeder name in a link must exactly match the `breeder` field of at least one card.
- **Clean `breeder` values:** keep `breeder` to the organization's name (for example "Sacred Seeds"), and put people in the prose.

## Same-name breeders (Justin, 2026-09-24)
Handle these the way film databases handle two films with one title, or music databases handle two bands with one name:
- **Disambiguate only when two distinct breeders share an exact name.** Add a qualifier in parentheses: **location** first (for example "Sacred Seeds (Santa Cruz)"), otherwise **founding year** (for example "Sacred Seeds (1985)").
- **Apply it to both entries at once.** Update every card that uses either name, including its `[[breeder:…]]` links.
- **Leave distinct full names alone.** If the names already differ (for example "Soma's Sacred Seeds" and "Sacred Seeds"), use each organization's own name as-is.

## Samples
> **Skunk #1** is a [[kind:cultivar|hybrid]] developed by the [[breeder:Sacred Seeds]] collective near Santa Cruz, California, in the mid-to-late 1970s. A cross of [[afghani]] and [[colombian-gold]] was later bred with [[acapulco-gold]] to shorten flowering. Seeds reached the Netherlands in 1982, and it is among the most widely used parents in modern breeding.

> **Acapulco Gold** is a [[kind:landrace|landrace]] traditionally grown in the mountains of Guerrero, [[country:MX|Mexico]], named for the brownish-gold color of its cured flowers. It was first recorded in the United States in 1964. Some sources place its origin in neighboring Oaxaca; others describe it as a cross with [[nepalese]] stock.
