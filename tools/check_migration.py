#!/usr/bin/env python3
"""Prove the v2 migration changed no facts (STM-U7 acceptance).

Stdlib only. Compares every card in the working tree against the same card at a
git revision (default ``main``) and asserts that the fields the packet calls
unchanged really are: ``name``, ``summary``, ``born`` (minus its evidence), and
``origin``'s place and coordinates.

    python3 tools/check_migration.py --ref main
"""

import argparse
import glob
import json
import os
import subprocess
import sys

DEFAULT_CATALOG = os.path.join("catalog", "strains")

# born/origin carried an ``evidence`` list in v1; dropping it is the migration.
BORN_KEYS = ("unknown", "year_min", "year_max", "display")
ORIGIN_KEYS = ("unknown", "place", "country", "lat", "lon")


def _subset(value, keys):
    if not isinstance(value, dict):
        return value
    return {key: value[key] for key in keys if key in value}


def facts(card):
    """The parts of a card the migration was not allowed to touch."""
    return {
        "name": card.get("name"),
        "summary": card.get("summary"),
        "born": _subset(card.get("born"), BORN_KEYS),
        "origin": _subset(card.get("origin"), ORIGIN_KEYS),
    }


def at_ref(ref, path):
    blob = subprocess.run(
        ["git", "show", "%s:%s" % (ref, path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(blob)


def run(ref, path):
    paths = sorted(glob.glob(os.path.join(path, "*.json")))
    failures = 0
    for card_path in paths:
        rel = card_path.replace(os.sep, "/")
        with open(card_path, "r", encoding="utf-8") as handle:
            now = facts(json.load(handle))
        before = facts(at_ref(ref, rel))
        same = now == before
        print("%s %s" % ("same " if same else "CHANGED", rel))
        if not same:
            failures += 1
            for key in sorted(set(now) | set(before)):
                if now.get(key) != before.get(key):
                    print("    %s: %r -> %r" % (key, before.get(key), now.get(key)))
    print(
        "%d cards compared against %s, %d with changed facts"
        % (len(paths), ref, failures)
    )
    return 1 if failures else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", default="main", help="git revision (default: %(default)s)")
    parser.add_argument("--path", default=DEFAULT_CATALOG)
    args = parser.parse_args(argv)
    return run(args.ref, args.path)


if __name__ == "__main__":
    sys.exit(main())
