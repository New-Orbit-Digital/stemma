"""Unit tests for the timeline layout and the family filter (tools/timeline.py).

The layout is computed in Python at build time, so these tests exercise the real
functions the site ships, not a mirror of them. Fixture ids are obviously
fictional.
"""

import os
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import timeline  # noqa: E402


def edge(child, parent, tier="documented", disputed=False):
    return {"child": child, "parent": parent, "best_tier": tier, "disputed": disputed}


def dated(strain_id, year_min, year_max, kind="cultivar", name=None):
    return {
        "id": strain_id,
        "name": name or strain_id.replace("example-", "Example ").title(),
        "kind": kind,
        "status": "draft",
        "born": {
            "year_min": year_min,
            "year_max": year_max,
            "display": "%d to %d" % (year_min, year_max),
        },
    }


def undated(strain_id, kind="landrace", name=None):
    return {
        "id": strain_id,
        "name": name or strain_id.replace("example-", "Example ").title(),
        "kind": kind,
        "status": "draft",
        "born": {"unknown": True, "display": "traditional"},
    }


def stub(strain_id):
    return {
        "id": strain_id,
        "name": strain_id.replace("example-", "Example ").title(),
        "kind": "cultivar",
        "status": "stub",
    }


def ids(rows):
    return sorted(row["id"] for row in rows)


class FamilyFilterTest(unittest.TestCase):
    """A ?family=<id> filter keeps the strain and its ancestors, nothing else."""

    def setUp(self):
        # example-kid <- example-mum <- example-gran; example-dad on the other
        # side; example-grandkid below; example-cousin off to the side.
        self.edges = [
            edge("example-kid", "example-mum"),
            edge("example-kid", "example-dad"),
            edge("example-mum", "example-gran"),
            edge("example-grandkid", "example-kid"),
            edge("example-cousin", "example-dad"),
        ]

    def test_family_is_exactly_the_strain_and_its_ancestors(self):
        self.assertEqual(
            timeline.family("example-kid", self.edges),
            ["example-dad", "example-gran", "example-kid", "example-mum"],
        )

    def test_family_excludes_children_and_siblings(self):
        family = timeline.family("example-kid", self.edges)
        self.assertNotIn("example-grandkid", family)  # a child, not an ancestor
        self.assertNotIn("example-cousin", family)  # shares a parent, not a line

    def test_a_root_is_its_own_family(self):
        self.assertEqual(timeline.family("example-gran", self.edges), ["example-gran"])

    def test_an_unknown_id_has_no_ancestors(self):
        self.assertEqual(timeline.family("example-missing", self.edges), ["example-missing"])

    def test_a_repeated_ancestor_is_listed_once(self):
        """A backcross reaches the same ancestor twice; a family is a set."""
        edges = [
            edge("example-backcross", "example-f1"),
            edge("example-backcross", "example-parent-a"),
            edge("example-f1", "example-parent-a"),
            edge("example-f1", "example-parent-b"),
        ]
        self.assertEqual(
            timeline.family("example-backcross", edges),
            [
                "example-backcross",
                "example-f1",
                "example-parent-a",
                "example-parent-b",
            ],
        )

    def test_the_whole_line_is_kept_past_the_diagram_generation_cap(self):
        """The filter has no row budget, so it does not stop at six generations."""
        chain = ["example-g%d" % n for n in range(12)]
        edges = [edge(chain[n], chain[n + 1]) for n in range(len(chain) - 1)]
        self.assertEqual(timeline.family(chain[0], edges), sorted(chain))

    def test_disputed_parents_stay_out_unless_asked_for(self):
        edges = [
            edge("example-kid", "example-mum"),
            edge("example-kid", "example-rumoured", tier="folklore", disputed=True),
        ]
        self.assertEqual(
            timeline.family("example-kid", edges), ["example-kid", "example-mum"]
        )
        self.assertEqual(
            timeline.family("example-kid", edges, with_disputed=True),
            ["example-kid", "example-mum", "example-rumoured"],
        )

    def test_families_covers_every_card(self):
        strains = [dated("example-kid", 1990, 1995), undated("example-mum")]
        families = timeline.families(strains, self.edges)
        self.assertEqual(sorted(families), ["example-kid", "example-mum"])
        self.assertIn("example-gran", families["example-kid"])


class RootsStripTest(unittest.TestCase):
    """Undated cards have no span to plot, so they go in the strip at the start."""

    def setUp(self):
        self.strains = [
            dated("example-cross", 1975, 1979),
            undated("example-landrace"),
            undated("example-other-landrace"),
            stub("example-stub"),
        ]
        self.graph = timeline.layout(self.strains)

    def test_undated_cards_land_in_the_roots_strip(self):
        self.assertEqual(
            ids(self.graph["roots"]),
            ["example-landrace", "example-other-landrace", "example-stub"],
        )
        self.assertEqual(ids(self.graph["bars"]), ["example-cross"])

    def test_a_stub_with_no_born_at_all_is_undated(self):
        self.assertFalse(timeline.is_dated(stub("example-stub")))
        self.assertFalse(timeline.is_dated(undated("example-landrace")))
        self.assertTrue(timeline.is_dated(dated("example-cross", 1975, 1979)))

    def test_the_strip_sits_before_the_axis(self):
        for row in self.graph["roots"]:
            self.assertEqual(row["x"], timeline.PAD)
            self.assertLessEqual(row["x"] + row["width"], self.graph["plot_x"])
        for bar in self.graph["bars"]:
            self.assertGreaterEqual(bar["x"], self.graph["plot_x"])

    def test_the_strip_is_the_first_group_and_is_labelled(self):
        first = self.graph["groups"][0]
        self.assertEqual(first["key"], "undated")
        self.assertEqual(first["label"], timeline.ROOTS_LABEL)
        self.assertEqual(len(first["rows"]), 3)
        for group in self.graph["groups"][1:]:
            self.assertGreater(group["y"], first["y"])

    def test_every_card_gets_exactly_one_row(self):
        placed = ids(self.graph["roots"] + self.graph["bars"])
        self.assertEqual(placed, sorted(card["id"] for card in self.strains))

    def test_a_catalog_with_no_dates_still_renders_the_strip(self):
        graph = timeline.layout([undated("example-landrace")])
        self.assertEqual(graph["decades"], [])
        self.assertEqual(len(graph["roots"]), 1)
        self.assertIn("Example Landrace", timeline.render(graph))


class LayoutTest(unittest.TestCase):
    def setUp(self):
        self.strains = [
            dated("example-late", 1995, 1999, kind="cut"),
            dated("example-early", 1975, 1979, kind="cultivar"),
            dated("example-middle", 1985, 1989, kind="cultivar"),
            undated("example-landrace"),
        ]
        self.graph = timeline.layout(self.strains)

    def test_one_bar_per_dated_card(self):
        self.assertEqual(len(self.graph["bars"]), 3)

    def test_bars_run_from_year_min_to_year_max(self):
        bar = [b for b in self.graph["bars"] if b["id"] == "example-early"][0]
        per_decade = timeline.DECADE_W
        self.assertEqual(self.graph["start_year"], 1970)
        self.assertEqual(bar["x"], self.graph["plot_x"] + 5 * per_decade // 10)
        self.assertEqual(bar["width"], 4 * per_decade // 10)

    def test_a_single_year_span_still_has_a_clickable_bar(self):
        graph = timeline.layout([dated("example-one-year", 1984, 1984)])
        self.assertEqual(graph["bars"][0]["width"], timeline.MIN_BAR_W)

    def test_the_axis_snaps_out_to_whole_decades(self):
        self.assertEqual(self.graph["start_year"], 1970)
        self.assertEqual(self.graph["end_year"], 2000)
        self.assertEqual(
            [decade["year"] for decade in self.graph["decades"]],
            [1970, 1980, 1990],
        )
        self.assertEqual([d["label"] for d in self.graph["decades"]], ["1970s", "1980s", "1990s"])

    def test_rows_are_grouped_by_decade_in_order(self):
        labels = [group["label"] for group in self.graph["groups"]]
        self.assertEqual(labels, [timeline.ROOTS_LABEL, "1970s", "1980s", "1990s"])
        rows = [group["rows"] for group in self.graph["groups"][1:]]
        self.assertEqual(
            rows, [["example-early"], ["example-middle"], ["example-late"]]
        )

    def test_rows_never_overlap_and_stay_on_the_canvas(self):
        placed = sorted(
            self.graph["roots"] + self.graph["bars"], key=lambda row: row["y"]
        )
        for first, second in zip(placed, placed[1:]):
            self.assertGreaterEqual(second["y"] - first["y"], timeline.BAR_H)
        for row in placed:
            self.assertGreaterEqual(row["x"], timeline.PAD)
            self.assertLessEqual(row["y"] + timeline.BAR_H, self.graph["height"])
            self.assertLessEqual(row["x"] + row["width"], self.graph["width"])

    def test_layout_is_deterministic(self):
        self.assertEqual(timeline.layout(self.strains), timeline.layout(self.strains))

    def test_an_empty_catalog_says_so_instead_of_drawing_an_axis(self):
        graph = timeline.layout([])
        self.assertEqual(graph["bars"], [])
        self.assertEqual(graph["roots"], [])
        self.assertIn("No cards yet", timeline.render(graph))
        self.assertNotIn("<svg", timeline.render(graph))


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.strains = [
            dated("example-cross", 1975, 1979, kind="cultivar"),
            dated("example-cut", 2005, 2008, kind="cut"),
            undated("example-landrace", kind="landrace"),
        ]
        self.graph = timeline.layout(self.strains)
        self.html = timeline.render(self.graph)

    def test_every_row_links_to_its_card_and_carries_its_id(self):
        for strain in self.strains:
            self.assertIn('href="/s/%s/"' % strain["id"], self.html)
            self.assertIn('data-id="%s"' % strain["id"], self.html)

    def test_bars_are_coloured_by_kind(self):
        self.assertIn("timeline-bar--cultivar", self.html)
        self.assertIn("timeline-bar--cut", self.html)
        self.assertIn("timeline-bar--landrace", self.html)

    def test_the_legend_lists_only_the_kinds_on_screen(self):
        self.assertIn("timeline-key__swatch--cultivar", self.html)
        self.assertIn("timeline-key__swatch--cut", self.html)
        graph = timeline.layout([undated("example-landrace")])
        markup = timeline.render(graph)
        self.assertIn("timeline-key__swatch--landrace", markup)
        self.assertNotIn("timeline-key__swatch--cut", markup)

    def test_the_decade_labels_are_on_the_axis(self):
        for label in ("1970s", "1980s", "1990s", "2000s"):
            self.assertIn(">%s<" % label, self.html)

    def test_the_svg_is_well_formed(self):
        deck = [dated("example-cross", 1975, 1979)]
        deck[0]["name"] = 'Ampersands & "quotes" <tags>'
        markup = timeline.render(timeline.layout(deck))
        svg = markup[markup.index("<svg") : markup.index("</svg>") + len("</svg>")]
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))

    def test_names_are_escaped(self):
        deck = [dated("example-cross", 1975, 1979)]
        deck[0]["name"] = 'Ex & <script>"'
        markup = timeline.render(timeline.layout(deck))
        self.assertNotIn("<script>", markup)
        self.assertIn("&amp;", markup)

    def test_long_names_are_clipped_rather_than_overflowing_the_canvas(self):
        deck = [dated("example-cross", 1975, 1979)]
        deck[0]["name"] = "Example Extremely Long Strain Name Indeed"
        markup = timeline.render(timeline.layout(deck))
        drawn = markup.split('class="timeline-row__name"')[1].split("</text>")[0]
        self.assertIn("…", drawn)
        self.assertNotIn("Name Indeed", drawn)
        # The whole name still reaches a screen reader, through the <title>.
        self.assertIn("Example Extremely Long Strain Name Indeed", markup)

    def test_the_counts_line_reports_dated_against_undated(self):
        self.assertEqual(timeline.counts(self.graph), "3 cards: 2 dated, 1 undated.")
        self.assertEqual(timeline.counts(timeline.layout([])), "No cards yet.")

    def test_the_payload_carries_the_families_and_the_picker_index(self):
        edges = [edge("example-cross", "example-landrace")]
        payload = timeline.payload(self.strains, edges)
        self.assertEqual(
            payload["families"]["example-cross"], ["example-cross", "example-landrace"]
        )
        self.assertEqual(
            [entry["id"] for entry in payload["strains"]],
            ["example-cross", "example-cut", "example-landrace"],
        )
        # Only what the picker searches on: no born, no lineage, no sources.
        for entry in payload["strains"]:
            self.assertEqual(sorted(entry), ["id", "kind", "name", "status"])


if __name__ == "__main__":
    unittest.main()
