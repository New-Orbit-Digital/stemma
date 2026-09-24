#!/usr/bin/env python3
"""Validate Stemma strain cards against docs/schema.md.

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

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

KINDS = ("landrace", "cultivar", "cut")
STATUSES = ("stub", "draft", "reviewed")
LINEAGE_STATUSES = ("root", "known", "partial", "unknown", "disputed")
TRADITIONAL_LABELS = ("indica", "sativa", "hybrid", "unknown")
ENVIRONMENTS = ("indoor", "outdoor", "both", "unknown")

# docs/schema.md "Evidence item": tier name -> rank.
TIER_RANK = {
    "genetically-tested": 4,
    "documented": 3,
    "breeder-claimed": 2,
    "folklore": 1,
}
TIER_BY_RANK = {rank: tier for tier, rank in TIER_RANK.items()}

ALWAYS_REQUIRED = ("id", "name", "kind", "status", "updated")
DRAFT_REQUIRED = (
    "aliases",
    "summary",
    "born",
    "origin",
    "lineage",
    "traditional_label",
    "sources",
)
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
        self.tier_ranks = []


class Validator:
    def __init__(self, path=DEFAULT_CATALOG, current_year=None):
        self.path = path
        self.current_year = current_year or datetime.now(timezone.utc).year
        self.cards = []
        self.messages = []
        self.errors = 0
        self.warnings = 0
        self._known_ids = {}

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

        draft_plus = status in DRAFT_PLUS
        if draft_plus:
            for field in DRAFT_REQUIRED:
                if field not in data:
                    self.error("E03", rel, "required field '%s' is missing" % field)

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

        source_ids = self._check_sources(card)
        self._check_summary(card)
        self._check_born(card, source_ids)
        self._check_origin(card, source_ids)
        self._check_breeder(card, source_ids)
        self._check_lineage(card, source_ids)
        self._check_growing(card)

        # W2: a draft or reviewed card with nothing stronger than folklore.
        if draft_plus and max(card.tier_ranks, default=0) < TIER_RANK["breeder-claimed"]:
            self.warn("W2", rel, "no evidence stronger than 'folklore'")

    def _check_sources(self, card):
        """Returns the set of source ids declared on the card."""
        sources = card.data.get("sources")
        if sources is None:
            return set()
        if not isinstance(sources, list):
            self.error("E03", card.rel, "'sources' must be an array")
            return set()
        ids = set()
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                self.error("E03", card.rel, "sources[%d] is not an object" % index)
                continue
            source_id = source.get("id")
            if not _is_str(source_id):
                self.error(
                    "E03", card.rel, "sources[%d] needs a non-empty string 'id'" % index
                )
                continue
            if source_id in ids:
                self.error(
                    "E04", card.rel, "source id '%s' is duplicated" % source_id
                )
            ids.add(source_id)
            if not _is_str(source.get("title")):
                self.error(
                    "E03",
                    card.rel,
                    "sources[%d] ('%s') needs a non-empty string 'title'"
                    % (index, source_id),
                )
        return ids

    def _check_summary(self, card):
        summary = card.data.get("summary")
        if summary is None:
            return
        if not isinstance(summary, str):
            self.error("E03", card.rel, "'summary' must be a string")
            return
        if len(summary) > MAX_SUMMARY:
            self.error(
                "E11",
                card.rel,
                "summary is %d characters, over the %d limit"
                % (len(summary), MAX_SUMMARY),
            )

    def _check_evidence(self, card, where, items, source_ids, required=True):
        """Checks one claim's evidence list (E03/E04/E08)."""
        if items is None:
            if required:
                self.error("E08", card.rel, "%s has no evidence" % where)
            return
        if not isinstance(items, list):
            self.error("E03", card.rel, "%s.evidence must be an array" % where)
            return
        if required and not items:
            self.error("E08", card.rel, "%s has no evidence" % where)
        for index, item in enumerate(items):
            label = "%s.evidence[%d]" % (where, index)
            if not isinstance(item, dict):
                self.error("E03", card.rel, "%s is not an object" % label)
                continue
            tier = item.get("tier")
            if tier is None:
                self.error("E03", card.rel, "%s is missing 'tier'" % label)
            elif tier not in TIER_RANK:
                self.error(
                    "E03",
                    card.rel,
                    "%s tier %r is not one of %s" % (label, tier, _enum(TIER_RANK)),
                )
            else:
                card.tier_ranks.append(TIER_RANK[tier])
            source = item.get("source")
            if not _is_str(source):
                self.error(
                    "E03", card.rel, "%s needs a non-empty string 'source'" % label
                )
            elif source not in source_ids:
                self.error(
                    "E04",
                    card.rel,
                    "%s source '%s' does not resolve to 'sources'" % (label, source),
                )

    def _check_born(self, card, source_ids):
        born = card.data.get("born")
        if born is None:
            return
        if not isinstance(born, dict):
            self.error("E03", card.rel, "'born' must be an object")
            return
        if not _is_str(born.get("display")):
            self.error("E03", card.rel, "'born.display' must be a non-empty string")
        if born.get("unknown") is True:
            return  # an unknown born needs no years and no evidence
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
        self._check_evidence(card, "born", born.get("evidence"), source_ids)

    def _check_origin(self, card, source_ids):
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
        self._check_coord(card, "lat", origin.get("lat"), 90)
        self._check_coord(card, "lon", origin.get("lon"), 180)
        self._check_evidence(card, "origin", origin.get("evidence"), source_ids)

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

    def _check_breeder(self, card, source_ids):
        if "breeder" not in card.data:
            return
        breeder = card.data["breeder"]
        if breeder is None:
            return
        if not isinstance(breeder, dict):
            self.error("E03", card.rel, "'breeder' must be an object or null")
            return
        if not _is_str(breeder.get("name")):
            self.error("E03", card.rel, "'breeder.name' must be a non-empty string")
        self._check_evidence(card, "breeder", breeder.get("evidence"), source_ids)

    def _check_lineage(self, card, source_ids):
        lineage = card.data.get("lineage")
        if lineage is None:
            return
        if not isinstance(lineage, dict):
            self.error("E03", card.rel, "'lineage' must be an object")
            return

        status = lineage.get("status")
        if status is None:
            self.error("E03", card.rel, "required field 'lineage.status' is missing")
        elif status not in LINEAGE_STATUSES:
            self.error(
                "E03",
                card.rel,
                "'lineage.status' %r is not one of %s"
                % (status, _enum(LINEAGE_STATUSES)),
            )

        parents = lineage.get("parents", [])
        if not isinstance(parents, list):
            self.error("E03", card.rel, "'lineage.parents' must be an array")
            parents = []
        disputes = lineage.get("disputes", [])
        if not isinstance(disputes, list):
            self.error("E03", card.rel, "'lineage.disputes' must be an array")
            disputes = []

        for index, parent in enumerate(parents):
            label = "parents[%d]" % index
            if not isinstance(parent, dict):
                self.error("E03", card.rel, "%s is not an object" % label)
                continue
            parent_id = parent.get("id")
            if not _is_str(parent_id):
                self.error(
                    "E03", card.rel, "%s needs a non-empty string 'id'" % label
                )
            else:
                self._check_reference(card, "parent", parent_id)
            self._check_evidence(card, label, parent.get("evidence"), source_ids)

        for index, dispute in enumerate(disputes):
            label = "disputes[%d]" % index
            if not isinstance(dispute, dict):
                self.error("E03", card.rel, "%s is not an object" % label)
                continue
            if not _is_str(dispute.get("claim")):
                self.error(
                    "E03", card.rel, "%s needs a non-empty string 'claim'" % label
                )
            dispute_parents = dispute.get("parents", [])
            if not isinstance(dispute_parents, list):
                self.error("E03", card.rel, "%s.parents must be an array" % label)
                dispute_parents = []
            for parent_id in dispute_parents:
                if not _is_str(parent_id):
                    self.error(
                        "E03", card.rel, "%s.parents must hold card ids" % label
                    )
                    continue
                self._check_reference(card, "dispute parent", parent_id)
            self._check_evidence(card, label, dispute.get("evidence"), source_ids)

        # E07: the lineage status/parents table in docs/schema.md.
        if status == "root":
            if card.data.get("kind") != "landrace":
                self.error(
                    "E07", card.rel, "lineage status 'root' requires kind 'landrace'"
                )
            if parents:
                self.error(
                    "E07", card.rel, "lineage status 'root' requires empty 'parents'"
                )
        elif status == "known":
            if len(parents) < 1:
                self.error(
                    "E07",
                    card.rel,
                    "lineage status 'known' requires at least 1 parent",
                )
        elif status == "partial":
            if len(parents) != 1:
                self.error(
                    "E07",
                    card.rel,
                    "lineage status 'partial' requires exactly 1 parent, found %d"
                    % len(parents),
                )
        elif status == "unknown":
            if parents:
                self.error(
                    "E07", card.rel, "lineage status 'unknown' requires empty 'parents'"
                )
        elif status == "disputed":
            if not disputes:
                self.error(
                    "E07",
                    card.rel,
                    "lineage status 'disputed' requires a non-empty 'disputes'",
                )

    def _check_reference(self, card, label, parent_id):
        if card.id is not None and parent_id == card.id:
            self.error("E05", card.rel, "card lists itself as a %s" % label)
        elif parent_id not in self._known_ids:
            self.error("E05", card.rel, "%s '%s' not found" % (label, parent_id))

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
        """Main-parent ids listed by a card, in file order."""
        lineage = card.data.get("lineage")
        if not isinstance(lineage, dict):
            return []
        parents = lineage.get("parents")
        if not isinstance(parents, list):
            return []
        out = []
        for parent in parents:
            if isinstance(parent, dict) and _is_str(parent.get("id")):
                out.append(parent["id"])
        return out

    def _check_cycles(self):
        """E06. The lineage graph is the main-parent graph (docs/schema.md,
        "Parent": "The lineage graph must have no cycles")."""
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
