#!/usr/bin/env python3
"""Compile the catalog into dist/data/stemma.json — the Budlogs seam.

Stdlib only. Validation runs first; any error aborts the build with exit 1.
The output is deterministic apart from ``generated``: strains are sorted by id
and edges by (child, parent, disputed).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate  # noqa: E402  (sibling module, resolved via the path insert)

SCHEMA_VERSION = 1
DEFAULT_OUT = os.path.join("dist", "data", "stemma.json")


def build_edges(cards):
    """Edges for main parents (disputed: false) and dispute parents (true).

    ``best_tier`` is the highest-ranked tier among that parent's evidence
    items; where the same (child, parent, disputed) parent is claimed more than
    once, the evidence is pooled and the best tier wins.
    """
    best = {}
    for card in cards:
        lineage = card.data.get("lineage") or {}
        for parent in lineage.get("parents") or []:
            _record(best, card.id, parent.get("id"), False, parent.get("evidence"))
        for dispute in lineage.get("disputes") or []:
            for parent_id in dispute.get("parents") or []:
                _record(best, card.id, parent_id, True, dispute.get("evidence"))
    return [
        {
            "child": child,
            "parent": parent,
            "best_tier": validate.TIER_BY_RANK[rank],
            "disputed": disputed,
        }
        for (child, parent, disputed), rank in sorted(best.items())
    ]


def _record(best, child, parent, disputed, evidence):
    ranks = [
        validate.TIER_RANK[item["tier"]]
        for item in evidence or []
        if isinstance(item, dict) and item.get("tier") in validate.TIER_RANK
    ]
    if not (child and parent and ranks):
        return
    key = (child, parent, disputed)
    best[key] = max(ranks + [best.get(key, 0)])


def build(path, out):
    validator = validate.Validator(path)
    code = validator.run()
    if code:
        print("build aborted: validation reported %d errors" % validator.errors)
        return 1

    cards = sorted(
        (card for card in validator.cards if card.id is not None),
        key=lambda card: card.id,
    )
    dataset = {
        "schema_version": SCHEMA_VERSION,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strains": [card.data for card in cards],
        "edges": build_edges(cards),
    }

    parent_dir = os.path.dirname(os.path.abspath(out))
    os.makedirs(parent_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(dataset, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(
        "wrote %s: %d strains, %d edges"
        % (out, len(dataset["strains"]), len(dataset["edges"]))
    )
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--path",
        default=validate.DEFAULT_CATALOG,
        help="directory of strain cards (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help="dataset output path (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    return build(args.path, args.out)


if __name__ == "__main__":
    sys.exit(main())
