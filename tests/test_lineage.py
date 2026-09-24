"""Unit tests for the lineage graph layout (tools/lineage.py).

The layout is precomputed in Python at build time, so these tests exercise the
real function the site ships, not a mirror of it. Fixture ids are obviously
fictional.
"""

import os
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import lineage  # noqa: E402


def edge(child, parent):
    return {"child": child, "parent": parent}


def card(strain_id, name=None, status="draft", born="1990s"):
    return {
        "id": strain_id,
        "name": name or strain_id.replace("example-", "Example ").title(),
        "status": status,
        "born": {"display": born},
    }


def cards(*ids):
    return {strain_id: card(strain_id) for strain_id in ids}


def by_id(graph):
    return {node["id"]: node for node in graph["nodes"]}


def crossings(graph):
    """Pairs of same-row-span edges whose endpoints are ordered the other way."""
    nodes = by_id(graph)
    total = 0
    drawn = graph["edges"]
    for i, one in enumerate(drawn):
        for other in drawn[i + 1 :]:
            top_a, bottom_a = nodes[one["parent"]], nodes[one["child"]]
            top_b, bottom_b = nodes[other["parent"]], nodes[other["child"]]
            if top_a["row"] != top_b["row"] or bottom_a["row"] != bottom_b["row"]:
                continue
            if (top_a["x"] - top_b["x"]) * (bottom_a["x"] - bottom_b["x"]) < 0:
                total += 1
    return total


class LayoutTest(unittest.TestCase):
    # -- a simple cross ---------------------------------------------------

    def setUp(self):
        self.cross_edges = [
            edge("example-cross", "example-mother"),
            edge("example-cross", "example-father"),
        ]

    def test_simple_cross_puts_parents_on_the_row_above(self):
        graph = lineage.layout(
            "example-cross",
            self.cross_edges,
            cards("example-cross", "example-mother", "example-father"),
        )
        nodes = by_id(graph)
        self.assertEqual(sorted(nodes), ["example-cross", "example-father", "example-mother"])
        self.assertEqual(graph["rows"], 2)
        self.assertEqual(nodes["example-cross"]["row"], 1)
        self.assertEqual(nodes["example-mother"]["row"], 0)
        self.assertEqual(nodes["example-father"]["row"], 0)
        self.assertTrue(nodes["example-cross"]["current"])
        self.assertFalse(nodes["example-mother"]["current"])
        self.assertEqual(len(graph["edges"]), 2)
        self.assertFalse(graph["truncated"])

    def test_roots_are_at_the_top_and_every_edge_points_upward(self):
        edges = self.cross_edges + [
            edge("example-mother", "example-landrace"),
            edge("example-child", "example-cross"),
        ]
        graph = lineage.layout("example-cross", edges, cards(*(
            "example-cross example-mother example-father "
            "example-landrace example-child"
        ).split()))
        nodes = by_id(graph)
        self.assertEqual(nodes["example-landrace"]["row"], 0)  # the root, on top
        self.assertEqual(nodes["example-child"]["row"], graph["rows"] - 1)
        self.assertEqual(nodes["example-child"]["depth"], -1)
        for drawn in graph["edges"]:
            self.assertLess(
                nodes[drawn["parent"]]["row"],
                nodes[drawn["child"]]["row"],
                "%s -> %s does not point upward" % (drawn["child"], drawn["parent"]),
            )

    def test_the_current_strain_is_the_only_node_without_a_link(self):
        html = lineage.graph_html(
            "example-cross",
            self.cross_edges,
            cards("example-cross", "example-mother", "example-father"),
        )
        self.assertIn('href="/s/example-mother/"', html)
        self.assertIn('href="/s/example-father/"', html)
        self.assertNotIn('href="/s/example-cross/"', html)
        self.assertIn("lineage-node--current", html)

    def test_tap_targets_clear_forty_pixels(self):
        self.assertGreaterEqual(lineage.NODE_H, 40)

    # -- a backcross ------------------------------------------------------

    def backcross(self):
        """F1 = A x B, then F1 crossed back to A. A is reached twice."""
        return [
            edge("example-backcross", "example-f1"),
            edge("example-backcross", "example-parent-a"),
            edge("example-f1", "example-parent-a"),
            edge("example-f1", "example-parent-b"),
        ]

    def test_backcross_renders_the_repeated_ancestor_once(self):
        graph = lineage.layout(
            "example-backcross",
            self.backcross(),
            cards(*(
                "example-backcross example-f1 example-parent-a example-parent-b"
            ).split()),
        )
        ids = [node["id"] for node in graph["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sorted(ids), [
            "example-backcross",
            "example-f1",
            "example-parent-a",
            "example-parent-b",
        ])
        nodes = by_id(graph)
        # Longest path wins: A is a parent (depth 1) and a grandparent (depth 2).
        self.assertEqual(nodes["example-parent-a"]["depth"], 2)
        self.assertEqual(nodes["example-f1"]["depth"], 1)
        self.assertEqual(nodes["example-parent-b"]["depth"], 2)
        # Both claims on A are still drawn, and both still point upward.
        to_a = [e for e in graph["edges"] if e["parent"] == "example-parent-a"]
        self.assertEqual(
            sorted(e["child"] for e in to_a), ["example-backcross", "example-f1"]
        )
        for drawn in graph["edges"]:
            self.assertLess(nodes[drawn["parent"]]["row"], nodes[drawn["child"]]["row"])

    def test_backcross_svg_draws_one_box_per_strain(self):
        html = lineage.graph_html(
            "example-backcross",
            self.backcross(),
            cards(*(
                "example-backcross example-f1 example-parent-a example-parent-b"
            ).split()),
        )
        self.assertEqual(html.count('href="/s/example-parent-a/"'), 1)
        self.assertEqual(html.count("<rect"), 4)
        self.assertEqual(html.count("<path"), 4)

    # -- one edge style ---------------------------------------------------

    def test_every_edge_is_drawn_the_same_way(self):
        html = lineage.graph_html(
            "example-cross",
            self.cross_edges,
            cards("example-cross", "example-mother", "example-father"),
        )
        self.assertEqual(html.count('class="lineage-edge"'), 2)
        for gone in ("lineage-edge--", "lineage-layer--disputed", "lineage-key"):
            self.assertNotIn(gone, html)

    def test_the_graph_carries_no_toggle_and_no_legend(self):
        html = lineage.graph_html(
            "example-cross",
            self.cross_edges,
            cards("example-cross", "example-mother", "example-father"),
        )
        self.assertNotIn('type="checkbox"', html)
        self.assertNotIn("Show disputed", html)

    def test_every_parent_edge_is_laid_out_and_drawn(self):
        """Nothing is hidden now, so every edge in the data reaches the SVG."""
        edges = [
            edge("example-kid", "example-agreed"),
            edge("example-kid", "example-second"),
        ]
        graph = lineage.layout(
            "example-kid",
            edges,
            cards("example-kid", "example-agreed", "example-second"),
        )
        self.assertEqual(len(graph["edges"]), 2)
        self.assertEqual(len(graph["nodes"]), 3)
        for drawn in graph["edges"]:
            self.assertEqual(sorted(drawn), ["child", "from", "parent", "to"])
        placed = {node["id"]: (node["x"], node["y"]) for node in graph["nodes"]}
        self.assertEqual(
            placed["example-agreed"][1], placed["example-second"][1]
        )  # same row

    # -- generations, ordering, determinism -------------------------------

    def test_ancestors_stop_at_six_generations(self):
        chain = ["example-g%d" % n for n in range(10)]
        edges = [edge(chain[n], chain[n + 1]) for n in range(len(chain) - 1)]
        graph = lineage.layout(chain[0], edges, cards(*chain))
        depths = {node["id"]: node["depth"] for node in graph["nodes"]}
        self.assertEqual(max(depths.values()), lineage.MAX_GENERATIONS)
        self.assertEqual(len(graph["nodes"]), lineage.MAX_GENERATIONS + 1)
        self.assertNotIn("example-g7", depths)
        self.assertTrue(graph["truncated"])
        html = lineage.graph_html(chain[0], edges, cards(*chain))
        self.assertIn("6 generations back", html)

    def test_the_barycenter_sweep_uncrosses_a_crossed_pair(self):
        rows = [["a", "b"], ["p", "q"]]
        lineage._sweep(rows, {"a": {"q"}, "b": {"p"}, "p": {"b"}, "q": {"a"}}, True)
        self.assertEqual(rows, [["a", "b"], ["q", "p"]])

    def test_layout_leaves_no_crossings_in_a_two_family_graph(self):
        edges = [
            edge("example-kid", "example-mum"),
            edge("example-kid", "example-dad"),
            edge("example-mum", "example-gran-a"),
            edge("example-dad", "example-gran-b"),
        ]
        graph = lineage.layout("example-kid", edges, cards(*(
            "example-kid example-mum example-dad example-gran-a example-gran-b"
        ).split()))
        self.assertEqual(crossings(graph), 0)

    def test_layout_is_deterministic(self):
        args = (
            "example-backcross",
            self.backcross(),
            cards(*(
                "example-backcross example-f1 example-parent-a example-parent-b"
            ).split()),
        )
        self.assertEqual(lineage.layout(*args), lineage.layout(*args))

    def test_rows_are_centred_and_the_canvas_holds_the_widest_one(self):
        graph = lineage.layout(
            "example-cross",
            self.cross_edges,
            cards("example-cross", "example-mother", "example-father"),
        )
        widest = 2 * lineage.NODE_W + lineage.COL_GAP
        self.assertEqual(graph["width"], widest + 2 * lineage.PAD)
        self.assertEqual(
            graph["height"], 2 * lineage.NODE_H + lineage.ROW_GAP + 2 * lineage.PAD
        )
        current = by_id(graph)["example-cross"]
        self.assertEqual(current["x"], lineage.PAD + (widest - lineage.NODE_W) // 2)
        for node in graph["nodes"]:
            self.assertGreaterEqual(node["x"], lineage.PAD)
            self.assertLessEqual(node["x"] + lineage.NODE_W, graph["width"] - lineage.PAD)

    # -- node content -----------------------------------------------------

    def test_nodes_show_name_born_and_mute_stubs(self):
        deck = cards("example-cross", "example-mother")
        deck["example-father"] = {
            "id": "example-father",
            "name": "Example Father",
            "status": "stub",
        }
        deck["example-mother"]["born"] = {"display": "late 1970s"}
        graph = lineage.layout("example-cross", self.cross_edges, deck)
        nodes = by_id(graph)
        self.assertEqual(nodes["example-mother"]["meta"], "late 1970s")
        self.assertTrue(nodes["example-father"]["stub"])
        self.assertEqual(nodes["example-father"]["meta"], "not yet cataloged")
        html = lineage.graph_html("example-cross", self.cross_edges, deck)
        self.assertIn("lineage-node--stub", html)
        self.assertIn("late 1970s", html)

    def test_long_names_are_clipped_rather_than_overflowing_the_box(self):
        deck = cards("example-cross", "example-mother", "example-father")
        deck["example-mother"]["name"] = "Example Extremely Long Strain Name Indeed"
        html = lineage.graph_html("example-cross", self.cross_edges, deck)
        self.assertIn("…", html)
        self.assertNotIn("Strain Name Indeed", html)

    def test_names_are_escaped(self):
        deck = cards("example-cross", "example-mother", "example-father")
        deck["example-mother"]["name"] = 'Ex & <script>"'
        html = lineage.graph_html("example-cross", self.cross_edges, deck)
        self.assertNotIn("<script>", html)
        self.assertIn("&amp;", html)

    def test_a_lone_strain_says_so_instead_of_drawing_an_empty_box(self):
        html = lineage.graph_html("example-lonely", [], cards("example-lonely"))
        self.assertIn("No lineage links", html)
        self.assertNotIn("<svg", html)

    def test_the_svg_is_well_formed(self):
        deck = cards("example-cross", "example-mother", "example-father")
        deck["example-mother"]["name"] = 'Ampersands & "quotes" <tags>'
        markup = lineage.graph_html("example-cross", self.cross_edges, deck)
        svg = markup[markup.index("<svg") : markup.index("</svg>") + len("</svg>")]
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))


if __name__ == "__main__":
    unittest.main()
