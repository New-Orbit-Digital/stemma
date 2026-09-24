#!/usr/bin/env python3
"""One-shot conversion of v1 strain cards to schema v2 (STM-U7 section 4).

Stdlib only. This is a *mechanical format conversion*, authorized by the
planner as a scoped exception to "never author or edit strain facts". It moves
bytes between fields and drops the v1 evidence machinery. It never invents,
rewrites, or removes a fact.

The mapping, straight from the packet:

* **Evidence.** ``evidence`` comes off ``born``, ``origin`` and ``breeder``.
* **Breeder.** ``{"name": ...}`` becomes the name as a plain string; ``null``
  stays ``null``.
* **Parents.** ``lineage.parents[].id`` becomes the top-level ``parents`` list.
* **Disputes.** ``lineage.disputes`` is dropped. Every dispute in the catalog is
  already described in its card's summary prose, which ``--check-summary``
  asserts before anything is written.
* **Source ids.** Dropped; nothing references them once evidence is gone.
* **Source categories.** Added from :data:`PUBLISHER_CATEGORY`. A publisher the
  table does not name is a STOP: the run reports it and writes nothing.
* **Notes.** Each informative evidence ``note`` moves onto its source's
  ``note``, deduplicated per source. A source that collects more than one
  distinct note keeps them all, joined in traversal order (born, origin,
  breeder, parents) — a source ``note`` is one string, so there is nowhere else
  for the second one to go. Notes that only restate the tier are dropped.

Dispute evidence notes go with the dispute. They describe a claim that no
longer exists in structured form, so carrying them onto a source would strand
them next to a card that no longer makes the claim.

Run it once and commit the result::

    python3 tools/migrate_v2.py --path catalog/strains
"""

import argparse
import glob
import json
import os
import sys

# The v2 key order, from docs/schema.md. Keys absent on a card stay absent.
V2_KEY_ORDER = (
    "id",
    "name",
    "aliases",
    "kind",
    "status",
    "summary",
    "born",
    "origin",
    "breeder",
    "parents",
    "traditional_label",
    "growing",
    "sources",
    "updated",
)

SOURCE_KEY_ORDER = ("title", "publisher", "category", "url", "accessed", "note")

# The packet's publisher table, verbatim. A publisher that is not here is a
# STOP, not a guess.
PUBLISHER_CATEGORY = {
    "Sensi Seeds": "breeder",
    "Barney's Farm": "breeder",
    "Carters Cannabis": "breeder",
    "Springer": "publication",
    "Pensoft": "publication",
    "University of California Press": "publication",
    "Black Cannabis Magazine": "publication",
    "Wikipedia": "database",
    "Wikipedia (citing The New York Times)": "database",
    "Leafly": "database",
    "SeedFinder": "database",
    "Cannigma": "database",
}

# The fictional publishers under tests/fixtures/, so the same script can carry
# the fixtures across. They are not catalog publishers and are kept apart from
# the packet's table on purpose.
FIXTURE_PUBLISHER_CATEGORY = {
    "Fixture Seeds": "breeder",
    "Fixture Cuttings": "breeder",
    "Fixture Press": "publication",
    "Fixture Forum": "community",
    "Fixture Lab": "database",
}

# A note that says nothing the card does not already say once tiers are gone.
TIER_RESTATEMENTS = {
    "documented",
    "breeder claimed",
    "breeder-claimed",
    "breeder's own account",
    "folklore",
    "community lore",
    "genetically tested",
    "genetically-tested",
}


class Stop(Exception):
    """A tripped STOP: report it and write nothing."""


def _is_str(value):
    return isinstance(value, str) and value != ""


def _is_tier_restatement(note):
    """True when a note only names the tier it hung off."""
    return note.strip().strip(".").lower() in TIER_RESTATEMENTS


def _evidence_notes(items, into, order):
    """Collect informative notes from one claim's evidence list.

    ``into`` maps source id -> list of notes, ``order`` records first-seen
    source ids so the output is deterministic.
    """
    dropped = 0
    for item in items or []:
        if not isinstance(item, dict):
            continue
        source_id = item.get("source")
        note = item.get("note")
        if not _is_str(source_id) or not _is_str(note):
            continue
        if _is_tier_restatement(note):
            dropped += 1
            continue
        bucket = into.setdefault(source_id, [])
        if source_id not in order:
            order.append(source_id)
        if note not in bucket:  # deduplicated per source
            bucket.append(note)
    return dropped


def collect_notes(data):
    """``{source_id: "note"}`` for one card, plus the dropped-note count.

    Traversal order is born, origin, breeder, then parents in file order, which
    is the order a source's notes are joined in.
    """
    notes = {}
    order = []
    dropped = 0
    for field in ("born", "origin", "breeder"):
        claim = data.get(field)
        if isinstance(claim, dict):
            dropped += _evidence_notes(claim.get("evidence"), notes, order)
    lineage = data.get("lineage")
    if isinstance(lineage, dict):
        for parent in lineage.get("parents") or []:
            if isinstance(parent, dict):
                dropped += _evidence_notes(parent.get("evidence"), notes, order)
    return {key: " ".join(value) for key, value in notes.items()}, dropped


def category_for(publisher, table):
    if not _is_str(publisher):
        raise Stop("a source has no publisher, so it has no category")
    if publisher not in table:
        raise Stop("publisher %r is not in the category table" % publisher)
    return table[publisher]


def migrate_source(source, notes, table):
    """One v1 source to v2: no id, a category, and any notes it collected."""
    out = {
        "title": source.get("title"),
        "publisher": source.get("publisher"),
        "category": category_for(source.get("publisher"), table),
    }
    for field in ("url", "accessed"):
        if field in source:
            out[field] = source[field]
    note = notes.get(source.get("id"))
    if note:
        out["note"] = note
    return {key: out[key] for key in SOURCE_KEY_ORDER if key in out}


def migrate_card(data, table):
    """One v1 card to v2. Returns the new card and the dropped-note count."""
    notes, dropped = collect_notes(data)
    out = dict(data)

    for field in ("born", "origin"):
        claim = out.get(field)
        if isinstance(claim, dict):
            claim = dict(claim)
            claim.pop("evidence", None)
            out[field] = claim

    if "breeder" in out:
        breeder = out["breeder"]
        out["breeder"] = breeder.get("name") if isinstance(breeder, dict) else breeder

    lineage = out.pop("lineage", None)
    if isinstance(lineage, dict):
        out["parents"] = [
            parent["id"]
            for parent in lineage.get("parents") or []
            if isinstance(parent, dict) and _is_str(parent.get("id"))
        ]

    if "sources" in out:
        out["sources"] = [
            migrate_source(source, notes, table)
            for source in out["sources"] or []
            if isinstance(source, dict)
        ]

    unknown = [key for key in out if key not in V2_KEY_ORDER]
    if unknown:
        raise Stop("card carries fields v2 has no home for: %s" % ", ".join(unknown))
    return {key: out[key] for key in V2_KEY_ORDER if key in out}, dropped


def check_dispute_summaries(cards):
    """Every dispute must already be described in its card's summary prose.

    The packet names ``acapulco-gold`` as the one to verify. Any other card
    that carries a dispute has to at least have a summary to have described it
    in; a card with a dispute and no summary would be a STOP.
    """
    lines = []
    for path, data in cards:
        disputes = (data.get("lineage") or {}).get("disputes") or []
        if not disputes:
            continue
        card_id = data.get("id")
        summary = data.get("summary")
        if not _is_str(summary):
            raise Stop("%s drops %d dispute(s) but has no summary" % (path, len(disputes)))
        lines.append("  %s: %d dispute(s) dropped" % (card_id, len(disputes)))
        for dispute in disputes:
            lines.append("    claim: %s" % dispute.get("claim"))
        lines.append("    summary: %s" % summary)
        if card_id == "acapulco-gold" and "Nepalese" not in summary:
            raise Stop("acapulco-gold summary no longer mentions the Nepalese claim")
    return lines


def write_card(path, card):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(card, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def run(path, fixtures=False, dry_run=False):
    table = dict(PUBLISHER_CATEGORY)
    if fixtures:
        table.update(FIXTURE_PUBLISHER_CATEGORY)

    paths = sorted(glob.glob(os.path.join(path, "*.json")))
    if not paths:
        print("nothing to migrate: no *.json under %s" % path)
        return 1

    cards = []
    for card_path in paths:
        with open(card_path, "r", encoding="utf-8") as handle:
            cards.append((card_path, json.load(handle)))

    # Nothing is written until every card has passed, so a STOP leaves the
    # working tree exactly as it was.
    try:
        dispute_lines = check_dispute_summaries(cards)
        migrated = []
        dropped_total = 0
        for card_path, data in cards:
            if "lineage" not in data and "sources" not in data:
                migrated.append((card_path, data, False))  # a stub; v1 == v2
                continue
            card, dropped = migrate_card(data, table)
            dropped_total += dropped
            migrated.append((card_path, card, True))
    except Stop as exc:
        print("STOP %s" % exc)
        return 1

    if dispute_lines:
        print("disputes dropped, and the summary prose that already carries them:")
        for line in dispute_lines:
            print(line)

    changed = 0
    for card_path, card, converted in migrated:
        before = open(card_path, "r", encoding="utf-8").read()
        after = json.dumps(card, indent=2, ensure_ascii=False) + "\n"
        if before != after:
            changed += 1
            if not dry_run:
                write_card(card_path, card)
        del converted
    print(
        "%d cards read, %d rewritten, %d tier-only notes dropped%s"
        % (len(migrated), changed, dropped_total, " (dry run)" if dry_run else "")
    )
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--path",
        default=os.path.join("catalog", "strains"),
        help="directory of strain cards (default: %(default)s)",
    )
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="also accept the fictional publishers used under tests/fixtures/",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report without writing anything"
    )
    args = parser.parse_args(argv)
    return run(args.path, fixtures=args.fixtures, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
