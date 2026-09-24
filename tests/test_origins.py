"""Unit tests for the origin map (tools/origins.py).

The markers, the arcs and the unknown list are computed in Python at build time,
so these tests exercise the real functions the site ships, not a mirror of them.
Fixture ids are obviously fictional.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import origins  # noqa: E402


def edge(child, parent, tier="documented", disputed=False):
    return {"child": child, "parent": parent, "best_tier": tier, "disputed": disputed}


def card(strain_id, lat=None, lon=None, name=None, kind="cultivar", place=None):
    """A located card when lat/lon are given, an unplaceable one when not."""
    data = {
        "id": strain_id,
        "name": name or strain_id.replace("example-", "Example ").title(),
        "kind": kind,
        "status": "draft",
    }
    if lat is None or lon is None:
        data["origin"] = {"unknown": True}
    else:
        data["origin"] = {
            "place": place or ("%s, Testland" % strain_id),
            "country": "TL",
            "lat": lat,
            "lon": lon,
            "evidence": [{"tier": "documented", "source": "s1"}],
        }
    return data


def stub(strain_id):
    """A stub has no origin key at all."""
    return {
        "id": strain_id,
        "name": strain_id.replace("example-", "Example ").title(),
        "kind": "cultivar",
        "status": "stub",
    }


def ids(rows):
    return sorted(row["id"] for row in rows)


def pairs(arcs):
    return sorted((arc["child"], arc["parent"]) for arc in arcs)


class LocatedTest(unittest.TestCase):
    """What can be plotted, and what has to be listed instead."""

    def test_a_card_with_a_centroid_is_located(self):
        self.assertTrue(origins.is_located(card("example-a", 34.5, 69.2)))
        self.assertEqual(
            origins.coordinates(card("example-a", 34.5, 69.2)), (34.5, 69.2)
        )

    def test_an_unknown_origin_is_not_located(self):
        self.assertFalse(origins.is_located(card("example-a")))
        self.assertIsNone(origins.coordinates(card("example-a")))

    def test_a_stub_with_no_origin_at_all_is_not_located(self):
        self.assertFalse(origins.is_located(stub("example-stub")))

    def test_a_place_with_no_coordinates_is_not_located(self):
        partial = {"id": "example-p", "origin": {"place": "Somewhere, Testland"}}
        self.assertFalse(origins.is_located(partial))

    def test_coordinates_off_the_globe_are_not_located(self):
        for lat, lon in ((91.0, 0.0), (0.0, 181.0), (-90.5, 0.0)):
            self.assertFalse(origins.is_located(card("example-a", lat, lon)))

    def test_a_boolean_is_not_a_coordinate(self):
        self.assertIsNone(origins.coordinates({"id": "x", "origin": {"lat": True, "lon": 0}}))

    def test_unknown_lists_every_card_the_map_cannot_place(self):
        strains = [
            card("example-placed", 10.0, 20.0),
            card("example-unknown"),
            stub("example-stub"),
        ]
        self.assertEqual(
            ids(origins.unknown(strains)), ["example-stub", "example-unknown"]
        )
        self.assertEqual(ids(origins.located(strains)), ["example-placed"])

    def test_every_card_is_either_placed_or_unknown(self):
        strains = [
            card("example-a", 10.0, 20.0),
            card("example-b"),
            stub("example-c"),
            card("example-d", -12.3, 45.0),
        ]
        placed = ids(origins.located(strains))
        listed = ids(origins.unknown(strains))
        self.assertEqual(sorted(placed + listed), ids(strains))
        self.assertEqual(set(placed) & set(listed), set())


class GroupingTest(unittest.TestCase):
    """Cards that share a centroid share one marker: the hand-rolled cluster."""

    def setUp(self):
        self.strains = [
            card("example-one", 34.5, 69.2, place="Fixture Valley, Testland"),
            card("example-two", 34.5, 69.2, place="Fixture Valley, Testland"),
            card("example-three", 34.5, 69.2, place="Fixture Valley, Testland"),
            card("example-far", -12.3, 45.0, place="Fixture Delta, Testland"),
            card("example-unplaced"),
        ]
        self.groups = origins.groups(self.strains)

    def test_a_shared_centroid_is_one_marker(self):
        self.assertEqual(len(self.groups), 2)
        shared = [g for g in self.groups if g["key"] == "34.5,69.2"][0]
        self.assertEqual(
            ids(shared["members"]), ["example-one", "example-three", "example-two"]
        )
        self.assertEqual((shared["lat"], shared["lon"]), (34.5, 69.2))

    def test_a_lone_card_still_gets_its_own_marker(self):
        alone = [g for g in self.groups if g["key"] == "-12.3,45.0"][0]
        self.assertEqual(ids(alone["members"]), ["example-far"])

    def test_every_located_card_lands_in_exactly_one_group(self):
        placed = []
        for group in self.groups:
            placed.extend(member["id"] for member in group["members"])
        self.assertEqual(sorted(placed), ids(origins.located(self.strains)))
        self.assertEqual(len(placed), len(set(placed)))

    def test_unplaceable_cards_are_in_no_group(self):
        for group in self.groups:
            self.assertNotIn("example-unplaced", [m["id"] for m in group["members"]])

    def test_near_neighbours_are_not_merged(self):
        """Grouping is the centroid the schema records, not screen distance."""
        groups = origins.groups(
            [card("example-a", 34.5, 69.2), card("example-b", 34.6, 69.2)]
        )
        self.assertEqual(len(groups), 2)

    def test_coordinates_are_rounded_to_the_schema_centroid_before_grouping(self):
        groups = origins.groups(
            [card("example-a", 34.5, 69.2), card("example-b", 34.50, 69.20)]
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]["members"]), 2)

    def test_a_shared_place_name_labels_the_marker(self):
        shared = [g for g in self.groups if g["key"] == "34.5,69.2"][0]
        self.assertEqual(shared["place"], "Fixture Valley, Testland")

    def test_two_wordings_at_one_centroid_fall_back_to_a_count(self):
        groups = origins.groups(
            [
                card("example-a", 1.0, 2.0, place="North Testland"),
                card("example-b", 1.0, 2.0, place="Northern Testland"),
            ]
        )
        self.assertEqual(groups[0]["place"], "2 strains at one centroid")

    def test_grouping_is_deterministic(self):
        self.assertEqual(origins.groups(self.strains), origins.groups(self.strains))

    def test_groups_read_north_to_south(self):
        latitudes = [group["lat"] for group in self.groups]
        self.assertEqual(latitudes, sorted(latitudes, reverse=True))


class ArcTest(unittest.TestCase):
    """An arc needs both ends on the map."""

    def setUp(self):
        # example-child <- example-mum (located) and <- example-nowhere (not).
        self.strains = [
            card("example-child", 52.4, 4.9),
            card("example-mum", 34.5, 69.2),
            card("example-nowhere"),
            card("example-gran", 10.8, -73.7),
        ]
        self.edges = [
            edge("example-child", "example-mum"),
            edge("example-child", "example-nowhere"),
            edge("example-mum", "example-gran"),
            edge("example-nowhere", "example-gran"),
        ]

    def test_only_edges_with_both_endpoints_located_are_drawn(self):
        self.assertEqual(
            pairs(origins.arcs(self.strains, self.edges)),
            [("example-child", "example-mum"), ("example-mum", "example-gran")],
        )

    def test_an_arc_runs_from_the_parent_to_the_child(self):
        arc = origins.arcs(self.strains, self.edges)[0]
        self.assertEqual(arc["from"], [34.5, 69.2])  # the parent
        self.assertEqual(arc["to"], [52.4, 4.9])  # the child
        self.assertEqual(arc["points"][0], [34.5, 69.2])
        self.assertEqual(arc["points"][-1], [52.4, 4.9])

    def test_disputed_edges_stay_off_the_map_unless_asked_for(self):
        edges = [
            edge("example-child", "example-mum"),
            edge("example-child", "example-gran", tier="folklore", disputed=True),
        ]
        self.assertEqual(
            pairs(origins.arcs(self.strains, edges)),
            [("example-child", "example-mum")],
        )
        self.assertEqual(
            pairs(origins.arcs(self.strains, edges, with_disputed=True)),
            [("example-child", "example-gran"), ("example-child", "example-mum")],
        )

    def test_an_arc_carries_its_best_tier_for_the_line_style(self):
        edges = [edge("example-child", "example-mum", tier="folklore")]
        self.assertEqual(origins.arcs(self.strains, edges)[0]["best_tier"], "folklore")

    def test_an_arc_is_a_curve_not_a_straight_line(self):
        arc = origins.arcs(self.strains, self.edges)[0]
        self.assertEqual(len(arc["points"]), origins.ARC_STEPS + 1)
        middle = arc["points"][len(arc["points"]) // 2]
        straight = [(34.5 + 52.4) / 2, (69.2 + 4.9) / 2]
        self.assertNotEqual(middle, straight)

    def test_the_curve_stays_inside_the_world(self):
        points = origins.curve((-80.0, -179.0), (80.0, 179.0))
        for lat, lon in points:
            self.assertLessEqual(abs(lat), origins.LAT_LIMIT)
            self.assertLessEqual(abs(lon), 360.0)

    def test_a_long_chord_bends_no_further_than_the_cap(self):
        points = origins.curve((0.0, -175.0), (0.0, 175.0))
        self.assertLessEqual(max(abs(lat) for lat, _lon in points), origins.MAX_BULGE)

    def test_two_cards_at_one_centroid_make_a_degenerate_arc_not_a_crash(self):
        strains = [card("example-a", 1.0, 2.0), card("example-b", 1.0, 2.0)]
        arc = origins.arcs(strains, [edge("example-a", "example-b")])[0]
        self.assertEqual(arc["points"], [[1.0, 2.0], [1.0, 2.0]])

    def test_arcs_are_deterministic(self):
        self.assertEqual(
            origins.arcs(self.strains, self.edges),
            origins.arcs(self.strains, self.edges),
        )


class FamilyArcTest(unittest.TestCase):
    """The packet's contract: a family's arcs are its ancestor edges, located."""

    def setUp(self):
        # example-kid <- example-mum <- example-gran, and example-kid <-
        # example-dad. example-dad has no origin. example-cousin and
        # example-grandkid are outside the family.
        self.strains = [
            card("example-kid", 52.4, 4.9),
            card("example-mum", 37.0, -122.0),
            card("example-gran", 34.5, 69.2),
            card("example-dad"),  # in the family, but not on the map
            card("example-cousin", 16.9, -99.9),
            card("example-grandkid", 10.8, -73.7),
        ]
        self.edges = [
            edge("example-kid", "example-mum"),
            edge("example-kid", "example-dad"),
            edge("example-mum", "example-gran"),
            edge("example-grandkid", "example-kid"),
            edge("example-cousin", "example-gran"),
        ]

    def test_the_family_arc_set_is_the_located_ancestor_edges(self):
        # Ancestor edges of example-kid, by hand: kid<-mum, kid<-dad,
        # mum<-gran. Only the two with both ends located can be drawn.
        self.assertEqual(
            pairs(origins.family_arcs("example-kid", self.strains, self.edges)),
            [("example-kid", "example-mum"), ("example-mum", "example-gran")],
        )

    def test_the_filter_leaves_out_children_and_siblings(self):
        drawn = pairs(origins.family_arcs("example-kid", self.strains, self.edges))
        self.assertNotIn(("example-grandkid", "example-kid"), drawn)
        self.assertNotIn(("example-cousin", "example-gran"), drawn)

    def test_the_rule_holds_for_every_card_in_the_catalog(self):
        """Stated as the packet states it, checked against every family."""
        located = {c["id"] for c in origins.located(self.strains)}
        for strain in self.strains:
            family = set(origins.family(strain["id"], self.edges))
            expected = sorted(
                (e["child"], e["parent"])
                for e in self.edges
                if not e["disputed"]
                and e["child"] in family
                and e["parent"] in family
                and e["child"] in located
                and e["parent"] in located
            )
            self.assertEqual(
                pairs(origins.family_arcs(strain["id"], self.strains, self.edges)),
                expected,
                "family arcs for %s" % strain["id"],
            )

    def test_disputed_parents_are_out_of_a_family_by_default(self):
        strains = [
            card("example-kid", 52.4, 4.9),
            card("example-mum", 37.0, -122.0),
            card("example-rumoured", 34.5, 69.2),
        ]
        edges = [
            edge("example-kid", "example-mum"),
            edge("example-kid", "example-rumoured", tier="folklore", disputed=True),
        ]
        self.assertEqual(
            pairs(origins.family_arcs("example-kid", strains, edges)),
            [("example-kid", "example-mum")],
        )
        self.assertEqual(
            pairs(origins.family_arcs("example-kid", strains, edges, with_disputed=True)),
            [("example-kid", "example-mum"), ("example-kid", "example-rumoured")],
        )

    def test_a_family_keeps_only_its_own_markers(self):
        groups = origins.family_groups("example-kid", self.strains, self.edges)
        placed = []
        for group in groups:
            placed.extend(member["id"] for member in group["members"])
        self.assertEqual(sorted(placed), ["example-gran", "example-kid", "example-mum"])

    def test_a_marker_keeps_only_the_family_members_that_share_it(self):
        strains = [
            card("example-kid", 34.5, 69.2),
            card("example-mum", 34.5, 69.2),
            card("example-stranger", 34.5, 69.2),
        ]
        edges = [edge("example-kid", "example-mum")]
        groups = origins.family_groups("example-kid", strains, edges)
        self.assertEqual(len(groups), 1)
        self.assertEqual(ids(groups[0]["members"]), ["example-kid", "example-mum"])

    def test_an_unknown_id_filters_to_itself(self):
        self.assertEqual(
            origins.family_arcs("example-missing", self.strains, self.edges), []
        )

    def test_the_family_is_the_shared_ancestor_walk(self):
        """Same walk as the diagram and the timeline: not a second copy."""
        self.assertEqual(
            origins.family("example-kid", self.edges),
            ["example-dad", "example-gran", "example-kid", "example-mum"],
        )
        self.assertEqual(
            sorted(origins.families(self.strains, self.edges)), ids(self.strains)
        )


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.strains = [
            card("example-kid", 52.4, 4.9, place="Amsterdam, Testland"),
            card("example-mum", 34.5, 69.2, place="Fixture Valley, Testland"),
            card("example-nowhere"),
            stub("example-stub"),
        ]
        self.edges = [edge("example-kid", "example-mum")]
        self.groups = origins.groups(self.strains)
        self.arcs = origins.arcs(self.strains, self.edges)
        self.unknown = origins.unknown(self.strains)

    def test_every_marker_is_listed_in_text_under_the_map(self):
        markup = origins.places_html(self.groups)
        for strain_id in ("example-kid", "example-mum"):
            self.assertIn('data-id="%s"' % strain_id, markup)
            self.assertIn('href="/s/%s/"' % strain_id, markup)
        self.assertIn("Amsterdam, Testland", markup)
        self.assertNotIn("example-nowhere", markup)

    def test_the_unknown_list_names_the_cards_the_map_cannot_place(self):
        markup = origins.unknown_html(self.unknown)
        self.assertIn("Origin unknown", markup)
        self.assertIn('data-id="example-nowhere"', markup)
        self.assertIn('data-id="example-stub"', markup)
        self.assertIn("not yet cataloged", markup)  # the stub's reason
        self.assertNotIn("example-kid", markup)

    def test_an_empty_unknown_list_says_so(self):
        markup = origins.unknown_html([])
        self.assertIn("Origin unknown", markup)
        self.assertIn("Every card in the catalog has an origin", markup)

    def test_an_empty_map_says_so_instead_of_an_empty_list(self):
        self.assertIn("No card has an origin", origins.places_html([]))

    def test_names_are_escaped(self):
        deck = [card("example-kid", 1.0, 2.0, name='Ex & <script>"')]
        markup = origins.places_html(origins.groups(deck))
        self.assertNotIn("<script>", markup)
        self.assertIn("&amp;", markup)
        markup = origins.unknown_html([card("example-a", name='Ex & <script>"')])
        self.assertNotIn("<script>", markup)

    def test_places_are_escaped(self):
        deck = [card("example-kid", 1.0, 2.0, place='Nowhere & <b>bold</b>')]
        markup = origins.places_html(origins.groups(deck))
        self.assertNotIn("<b>", markup)

    def test_the_counts_line_reports_markers_arcs_and_unknowns(self):
        self.assertEqual(
            origins.counts(self.groups, self.arcs, self.unknown),
            "2 cards at 2 places, 1 line. 2 with an unknown origin.",
        )
        self.assertEqual(origins.counts([], [], []), "No cards yet.")
        self.assertEqual(
            origins.counts(self.groups, [], []),
            "2 cards at 2 places, 0 lines. Every card has an origin.",
        )


class PayloadTest(unittest.TestCase):
    def setUp(self):
        self.strains = [
            card("example-kid", 52.4, 4.9),
            card("example-mum", 34.5, 69.2),
            card("example-nowhere"),
        ]
        self.edges = [edge("example-kid", "example-mum")]
        self.payload = origins.payload(self.strains, self.edges)

    def test_the_payload_carries_what_the_page_draws(self):
        self.assertEqual(len(self.payload["groups"]), 2)
        self.assertEqual(len(self.payload["arcs"]), 1)
        self.assertEqual(self.payload["unknown"], ["example-nowhere"])
        self.assertEqual(
            self.payload["families"]["example-kid"], ["example-kid", "example-mum"]
        )

    def test_the_payload_carries_only_the_pickers_fields(self):
        for entry in self.payload["strains"]:
            self.assertEqual(sorted(entry), ["id", "kind", "name", "status"])

    def test_the_payload_is_json_serialisable_and_deterministic(self):
        import json

        first = json.dumps(self.payload, sort_keys=True)
        second = json.dumps(origins.payload(self.strains, self.edges), sort_keys=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
