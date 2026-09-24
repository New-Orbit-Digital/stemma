#!/usr/bin/env python3
"""Validate Stemma strain cards against docs/schema.md (schema v2).

Stdlib only. Reads every ``*.json`` card in a catalog directory (default
``catalog/strains``) and reports every rule break as a line that starts with
its rule id, for example::

    E05 catalog/strains/x.json: parent 'y' not found

The run always ends with ``N cards, E errors, W warnings`` and exits 1 when
there is at least one error. Warnings never fail the run.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import countries  # noqa: E402  (sibling module, resolved via the path insert)
import links  # noqa: E402

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

KINDS = ("landrace", "cultivar", "cut")
STATUSES = ("stub", "draft", "reviewed")
TRADITIONAL_LABELS = ("indica", "sativa", "hybrid", "unknown")
ENVIRONMENTS = ("indoor", "outdoor", "both", "unknown")

# docs/schema.md "Source". Descriptive labels, deliberately not a ranking, so
# nothing here is ordered and nothing compares two of them.
SOURCE_CATEGORIES = ("breeder", "publication", "database", "community")

ALWAYS_REQUIRED = ("id", "name", "kind", "status", "updated")
DRAFT_REQUIRED = ("summary", "sources")
DRAFT_PLUS = ("draft", "reviewed")

DEFAULT_CATALOG = os.path.join("catalog", "strains")
EARLIEST_YEAR = 1900
MAX_SUMMARY = 400


def _enum(values):
    return ", ".join(repr(v) for v in values)


def _is_str(value):
    return isinstance(value, str) and value != ""


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _rel(path):
    try:
        return os.path.relpath(path)
    except ValueError:  # different drive on Windows
        return path


class Card:
    """One parsed strain card."""

    def __init__(self, path, data):
        self.path = path
        self.rel = _rel(path)
        self.data = data
        self.id = None  # set only once the id is well formed and unique


class Validator:
    def __init__(self, path=DEFAULT_CATALOG, current_year=None):
        self.path = path
        self.current_year = current_year or datetime.now(timezone.utc).year
        self.cards = []
        self.messages = []
        self.errors = 0
        self.warnings = 0
        self._known_ids = {}
        self._link_index = None

    # -- reporting ---------------------------------------------------------
    def error(self, rule, where, message):
        self.messages.append("%s %s: %s" % (rule, where, message))
        self.errors += 1

    def warn(self, rule, where, message):
        self.messages.append("%s %s: %s" % (rule, where, message))
        self.warnings += 1

    # -- driver ------------------------------------------------------------
    def run(self):
        """Validate the catalog. Returns the process exit code."""
        if not os.path.isdir(self.path):
            self.messages.append("error: %s is not a directory" % _rel(self.path))
            self.errors += 1
        else:
            for path in sorted(glob.glob(os.path.join(self.path, "*.json"))):
                self._load(path)
            self._check_ids()
            for card in self.cards:
                self._check_card(card)
            self._check_cycles()
            self._check_w1()
        for line in self.messages:
            print(line)
        print(
            "%d cards, %d errors, %d warnings"
            % (len(self.cards), self.errors, self.warnings)
        )
        return 1 if self.errors else 0

    def _load(self, path):
        rel = _rel(path)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            self.error("E01", rel, "JSON parse failure: %s" % exc)
            return
        except OSError as exc:
            self.error("E01", rel, "cannot read file: %s" % exc)
            return
        if not isinstance(data, dict):
            self.error("E01", rel, "top-level value is not a JSON object")
            return
        self.cards.append(Card(path, data))

    # -- E02: id ------------------------------------------------------------
    def _check_ids(self):
        for card in self.cards:
            card_id = card.data.get("id")
            stem = os.path.splitext(os.path.basename(card.path))[0]
            if card_id is None:
                continue  # E03 reports the missing required field
            if not _is_str(card_id) or not ID_RE.match(card_id):
                self.error(
                    "E02",
                    card.rel,
                    "id %r is not kebab-case [a-z0-9]+(-[a-z0-9]+)*" % (card_id,),
                )
                continue
            if card_id != stem:
                self.error(
                    "E02",
                    card.rel,
                    "id '%s' does not match filename stem '%s'" % (card_id, stem),
                )
            first = self._known_ids.get(card_id)
            if first is not None:
                self.error(
                    "E02", card.rel, "id '%s' duplicates %s" % (card_id, first)
                )
                continue
            self._known_ids[card_id] = card.rel
            card.id = card_id

    # -- per-card ----------------------------------------------------------
    def _check_card(self, card):
        data = card.data
        rel = card.rel
        status = data.get("status")

        for field in ALWAYS_REQUIRED:
            if field not in data:
                self.error("E03", rel, "required field '%s' is missing" % field)
        if "name" in data and not _is_str(data["name"]):
            self.error("E03", rel, "'name' must be a non-empty string")
        if "kind" in data and data["kind"] not in KINDS:
            self.error(
                "E03", rel, "'kind' %r is not one of %s" % (data["kind"], _enum(KINDS))
            )
        if "status" in data and status not in STATUSES:
            self.error(
                "E03", rel, "'status' %r is not one of %s" % (status, _enum(STATUSES))
            )
        if "updated" in data and not (
            _is_str(data["updated"]) and DATE_RE.match(data["updated"])
        ):
            self.error("E03", rel, "'updated' must be a YYYY-MM-DD date")

        # A draft or reviewed card is a researched card: it says something, and
        # it says where that came from.
        if status in DRAFT_PLUS:
            for field in DRAFT_REQUIRED:
                if not data.get(field):
                    self.error(
                        "E03",
                        rel,
                        "a '%s' card needs a non-empty '%s'" % (status, field),
                    )

        if "aliases" in data and not (
            isinstance(data["aliases"], list)
            and all(isinstance(a, str) for a in data["aliases"])
        ):
            self.error("E03", rel, "'aliases' must be an array of strings")
        if "traditional_label" in data and data["traditional_label"] not in (
            TRADITIONAL_LABELS
        ):
            self.error(
                "E03",
                rel,
                "'traditional_label' %r is not one of %s"
                % (data["traditional_label"], _enum(TRADITIONAL_LABELS)),
            )
        if "breeder" in data and not (
            data["breeder"] is None or _is_str(data["breeder"])
        ):
            self.error("E03", rel, "'breeder' must be a non-empty string or null")

        self._check_sources(card)
        self._check_summary(card)
        self._check_born(card)
        self._check_origin(card)
        self._check_parents(card)
        self._check_growing(card)

    # -- E04: sources -------------------------------------------------------
    def _check_sources(self, card):
        sources = card.data.get("sources")
        if sources is None:
            return
        if not isinstance(sources, list):
            self.error("E03", card.rel, "'sources' must be an array")
            return
        for index, source in enumerate(sources):
            label = "sources[%d]" % index
            if not isinstance(source, dict):
                self.error("E03", card.rel, "%s is not an object" % label)
                continue
            if not _is_str(source.get("title")):
                self.error(
                    "E04", card.rel, "%s needs a non-empty string 'title'" % label
                )
            category = source.get("category")
            if category not in SOURCE_CATEGORIES:
                self.error(
                    "E04",
                    card.rel,
                    "%s category %r is not one of %s"
                    % (label, category, _enum(SOURCE_CATEGORIES)),
                )

    # -- E11, E12, E13: the summary and its links ---------------------------
    def _check_summary(self, card):
        """The prose, its ``[[...]]`` links, and the length a reader sees.

        The 400-character ceiling counts the visible text: markup reduces to
        its display text first, so linking a name never costs a card prose.
        """
        summary = card.data.get("summary")
        if summary is None:
            return
        if not isinstance(summary, str):
            self.error("E03", card.rel, "'summary' must be a string")
            return

        found, problems = links.parse(summary)
        for problem in problems:
            self.error("E12", card.rel, problem)
        for link in found:
            unresolved = self._unresolved(link)
            if unresolved:
                self.error("E13", card.rel, unresolved)

        visible = links.plain(summary, self._index()["names"])
        if len(visible) > MAX_SUMMARY:
            self.error(
                "E11",
                card.rel,
                "summary is %d visible characters, over the %d limit"
                % (len(visible), MAX_SUMMARY),
            )

    def _index(self):
        """What a summary's links may point at, read once off every card.

        Built lazily rather than in ``__init__`` because it needs every card:
        a breeder or a country resolves when *any* card carries it, not only
        the card doing the linking.
        """
        if self._link_index is None:
            names, breeders, origin_codes = {}, set(), set()
            for other in self.cards:
                data = other.data
                if other.id is not None:
                    name = data.get("name")
                    names[other.id] = name if _is_str(name) else other.id
                breeder = data.get("breeder")
                if _is_str(breeder):
                    breeders.add(breeder)
                origin = data.get("origin")
                if isinstance(origin, dict) and origin.get("unknown") is not True:
                    code = countries.code(origin.get("country"))
                    if code:
                        origin_codes.add(code)
            self._link_index = {
                "names": names,
                "breeders": breeders,
                "countries": origin_codes,
            }
        return self._link_index

    def _unresolved(self, link):
        """The E13 message for a link that points at nothing, else ``None``."""
        index = self._index()
        if link.dimension == links.STRAIN:
            if link.value not in self._known_ids:
                return "%s names no card" % link.raw
            return None
        if link.dimension == "breeder":
            if link.value not in index["breeders"]:
                return "%s matches no card's 'breeder' exactly" % link.raw
            return None
        if link.dimension == "kind":
            if link.value not in KINDS:
                return "%s is not one of %s" % (link.raw, _enum(KINDS))
            return None
        if link.dimension == "label":
            if link.value not in TRADITIONAL_LABELS:
                return "%s is not one of %s" % (link.raw, _enum(TRADITIONAL_LABELS))
            return None
        code = countries.code(link.value)
        if code is None:
            return "%s is not a country in tools/countries.py" % link.raw
        if code not in index["countries"]:
            return "%s matches no card's 'origin.country'" % link.raw
        return None

    def _check_born(self, card):
        born = card.data.get("born")
        if born is None:
            return
        if not isinstance(born, dict):
            self.error("E03", card.rel, "'born' must be an object")
            return
        if not _is_str(born.get("display")):
            self.error("E03", card.rel, "'born.display' must be a non-empty string")
        if born.get("unknown") is True:
            return  # an unknown born needs no years
        for field in ("year_min", "year_max"):
            if field not in born:
                self.error(
                    "E03",
                    card.rel,
                    "required field 'born.%s' is missing (born is not unknown)" % field,
                )
        year_min = born.get("year_min")
        year_max = born.get("year_max")
        for field, value in (("year_min", year_min), ("year_max", year_max)):
            if value is None:
                continue
            if not _is_int(value):
                self.error("E09", card.rel, "born.%s must be an integer year" % field)
            elif not EARLIEST_YEAR <= value <= self.current_year:
                self.error(
                    "E09",
                    card.rel,
                    "born.%s %d is outside %d..%d"
                    % (field, value, EARLIEST_YEAR, self.current_year),
                )
        if _is_int(year_min) and _is_int(year_max) and year_min > year_max:
            self.error(
                "E09",
                card.rel,
                "born.year_min %d is greater than born.year_max %d"
                % (year_min, year_max),
            )

    def _check_origin(self, card):
        origin = card.data.get("origin")
        if origin is None:
            return
        if not isinstance(origin, dict):
            self.error("E03", card.rel, "'origin' must be an object")
            return
        if origin.get("unknown") is True:
            return  # an unknown origin needs no other fields
        for field in ("place", "country"):
            if field not in origin:
                self.error(
                    "E03", card.rel, "required field 'origin.%s' is missing" % field
                )
            elif not _is_str(origin[field]):
                self.error(
                    "E03", card.rel, "'origin.%s' must be a non-empty string" % field
                )
        # E14: the country map is the browse dimension's vocabulary, so an
        # unrecognized code would otherwise become a page nobody can reach.
        country = origin.get("country")
        if _is_str(country) and not countries.is_known(country):
            self.error(
                "E14",
                card.rel,
                "origin.country '%s' is not in tools/countries.py" % country,
            )
        self._check_coord(card, "lat", origin.get("lat"), 90)
        self._check_coord(card, "lon", origin.get("lon"), 180)

    def _check_coord(self, card, field, value, limit):
        if value is None:
            self.error("E03", card.rel, "required field 'origin.%s' is missing" % field)
            return
        if not _is_number(value):
            self.error("E03", card.rel, "'origin.%s' must be a number" % field)
            return
        if not -limit <= value <= limit:
            self.error(
                "E10",
                card.rel,
                "origin.%s %s is outside -%d..%d" % (field, value, limit, limit),
            )
            return
        if abs(round(float(value), 1) - float(value)) > 1e-9:
            self.error(
                "E10",
                card.rel,
                "origin.%s %s has more than 1 decimal place" % (field, value),
            )

    # -- E05: parents -------------------------------------------------------
    def _check_parents(self, card):
        parents = card.data.get("parents")
        if parents is None:
            return
        if not isinstance(parents, list):
            self.error("E03", card.rel, "'parents' must be an array of card ids")
            return
        for index, parent_id in enumerate(parents):
            if not _is_str(parent_id):
                self.error(
                    "E03", card.rel, "parents[%d] must be a card id" % index
                )
                continue
            if card.id is not None and parent_id == card.id:
                self.error("E05", card.rel, "card lists itself as a parent")
            elif parent_id not in self._known_ids:
                self.error("E05", card.rel, "parent '%s' not found" % parent_id)

        # W3: a landrace is a regional population, not something with parents.
        if parents and card.data.get("kind") == "landrace":
            self.warn(
                "W3",
                card.rel,
                "a 'landrace' card lists %d parent(s)" % len(parents),
            )

    def _check_growing(self, card):
        if "growing" not in card.data:
            return
        growing = card.data["growing"]
        if growing is None:
            return
        if not isinstance(growing, dict):
            self.error("E03", card.rel, "'growing' must be an object")
            return
        environment = growing.get("environment")
        if environment is None:
            self.error(
                "E03", card.rel, "required field 'growing.environment' is missing"
            )
        elif environment not in ENVIRONMENTS:
            self.error(
                "E03",
                card.rel,
                "'growing.environment' %r is not one of %s"
                % (environment, _enum(ENVIRONMENTS)),
            )
        weeks = growing.get("flowering_weeks")
        if weeks is None:
            self.error(
                "E03", card.rel, "required field 'growing.flowering_weeks' is missing"
            )
            return
        if not isinstance(weeks, dict):
            self.error("E03", card.rel, "'growing.flowering_weeks' must be an object")
            return
        for field in ("min", "max"):
            if field not in weeks:
                self.error(
                    "E03",
                    card.rel,
                    "required field 'growing.flowering_weeks.%s' is missing" % field,
                )
            elif not _is_number(weeks[field]):
                self.error(
                    "E03",
                    card.rel,
                    "'growing.flowering_weeks.%s' must be a number" % field,
                )

    # -- cross-card --------------------------------------------------------
    def parent_edges(self, card):
        """Parent ids listed by a card, in file order."""
        parents = card.data.get("parents")
        if not isinstance(parents, list):
            return []
        return [parent for parent in parents if _is_str(parent)]

    def _check_cycles(self):
        """E06. docs/schema.md, "Parents": the graph must have no cycles."""
        graph = {}
        rel_by_id = {}
        for card in self.cards:
            if card.id is None:
                continue
            rel_by_id[card.id] = card.rel
            graph[card.id] = sorted(set(self.parent_edges(card)))

        white, grey, black = 0, 1, 2
        color = dict.fromkeys(graph, white)
        reported = set()
        for start in sorted(graph):
            if color[start] != white:
                continue
            color[start] = grey
            path = [start]
            stack = [(start, iter(graph[start]))]
            while stack:
                node, children = stack[-1]
                descended = False
                for child in children:
                    if child not in color:
                        continue  # not a card; E05 already reported it
                    if color[child] == grey:
                        cycle = path[path.index(child):] + [child]
                        key = self._cycle_key(cycle)
                        if key not in reported:
                            reported.add(key)
                            self.error(
                                "E06",
                                rel_by_id[node],
                                "lineage cycle: %s" % " -> ".join(cycle),
                            )
                        continue
                    if color[child] == white:
                        color[child] = grey
                        path.append(child)
                        stack.append((child, iter(graph[child])))
                        descended = True
                        break
                if not descended:
                    color[node] = black
                    stack.pop()
                    path.pop()

    @staticmethod
    def _cycle_key(cycle):
        nodes = cycle[:-1]
        pivot = nodes.index(min(nodes))
        return tuple(nodes[pivot:] + nodes[:pivot])

    def _check_w1(self):
        """W1: a child's year_max is earlier than a parent's year_min."""
        born_by_id = {}
        for card in self.cards:
            if card.id is None:
                continue
            born = card.data.get("born")
            if isinstance(born, dict) and born.get("unknown") is not True:
                born_by_id[card.id] = born
        for card in self.cards:
            if card.id is None:
                continue
            child_born = born_by_id.get(card.id)
            if child_born is None or not _is_int(child_born.get("year_max")):
                continue
            year_max = child_born["year_max"]
            for parent_id in self.parent_edges(card):
                parent_born = born_by_id.get(parent_id)
                if parent_born is None or not _is_int(parent_born.get("year_min")):
                    continue
                if year_max < parent_born["year_min"]:
                    self.warn(
                        "W1",
                        card.rel,
                        "born.year_max %d is earlier than parent '%s' born.year_min %d"
                        % (year_max, parent_id, parent_born["year_min"]),
                    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Stemma strain cards against docs/schema.md."
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_CATALOG,
        help="directory of strain cards (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    return Validator(args.path).run()


if __name__ == "__main__":
    sys.exit(main())
