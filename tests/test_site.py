"""Smoke tests for the static site that tools/build.py compiles into --out."""

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "tools", "build.py")
VALID = os.path.join(ROOT, "tests", "fixtures", "valid")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import build  # noqa: E402  (the build's own hash rule, not a copy)
import origins  # noqa: E402  (the site's own located/unknown rule, not a copy)
import timeline  # noqa: E402  (the site's own dated/undated rule, not a copy)

LINK_RE = re.compile(r'(?:href|src)="([^"]*)"')
EXTERNAL = ("http://", "https://", "//", "mailto:", "tel:", "data:")
ASSET_REF_RE = re.compile(r'(?:href|src)="(/assets/[^"]*)"')


def html_files(out):
    for dirpath, _dirnames, filenames in os.walk(out):
        for name in sorted(filenames):
            if name.endswith(".html"):
                yield os.path.join(dirpath, name)


def resolve(out, page, target):
    """Map one internal href/src to the file on disk it should reach."""
    target = html.unescape(target).split("#")[0].split("?")[0]
    if not target:
        return None
    if target.startswith("/"):
        path = os.path.join(out, target.lstrip("/"))
    else:
        path = os.path.join(os.path.dirname(page), target)
    if target.endswith("/") or os.path.isdir(path):
        path = os.path.join(path, "index.html")
    return os.path.normpath(path)


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = os.path.join(cls.tmp.name, "dist")
        result = subprocess.run(
            [sys.executable, BUILD, "--path", VALID, "--out", cls.out],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            cls.tmp.cleanup()
            raise AssertionError("build failed:\n" + result.stdout + result.stderr)
        with open(os.path.join(cls.out, "data", "stemma.json"), encoding="utf-8") as fh:
            cls.dataset = json.load(fh)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, relpath):
        with open(os.path.join(self.out, relpath), encoding="utf-8") as handle:
            return handle.read()

    # -- the three checks the packet names --------------------------------

    def test_every_strain_has_a_page(self):
        for strain in self.dataset["strains"]:
            page = os.path.join(self.out, "s", strain["id"], "index.html")
            self.assertTrue(os.path.isfile(page), "missing page for %s" % strain["id"])

    def test_every_internal_link_resolves_to_a_file(self):
        checked = 0
        for page in html_files(self.out):
            for target in LINK_RE.findall(self.read(os.path.relpath(page, self.out))):
                if target.startswith(EXTERNAL) or target.startswith("#") or not target:
                    continue
                path = resolve(self.out, page, target)
                checked += 1
                self.assertTrue(
                    os.path.isfile(path),
                    "%s links to %s, which is not a file"
                    % (os.path.relpath(page, self.out), target),
                )
        self.assertGreater(checked, 0)

    def test_no_page_references_the_catalog(self):
        for page in html_files(self.out):
            text = self.read(os.path.relpath(page, self.out))
            self.assertNotIn("catalog/", text, "%s references catalog/" % page)
        for asset in ("assets/app.js", "assets/style.css"):
            self.assertNotIn("catalog/", self.read(asset))

    # -- the rest of the scaffold ----------------------------------------

    def test_core_files_exist(self):
        for relpath in (
            "index.html",
            "404.html",
            os.path.join("about", "index.html"),
            os.path.join("timeline", "index.html"),
            os.path.join("map", "index.html"),
            os.path.join("assets", "style.css"),
            os.path.join("assets", "app.js"),
            os.path.join("data", "stemma.json"),
        ):
            self.assertTrue(
                os.path.isfile(os.path.join(self.out, relpath)), "missing %s" % relpath
            )

    # -- asset cache-busting ----------------------------------------------

    def test_every_asset_reference_carries_the_built_file_s_hash(self):
        pages = list(html_files(self.out))
        checked = 0
        for page in pages:
            relpath = os.path.relpath(page, self.out)
            for ref in ASSET_REF_RE.findall(self.read(relpath)):
                name, _, query = ref[len("/assets/") :].partition("?")
                built = os.path.join(self.out, "assets", name)
                self.assertTrue(os.path.isfile(built), "%s: no such asset" % ref)
                with open(built, "rb") as handle:
                    digest = hashlib.sha256(handle.read()).hexdigest()
                self.assertEqual(
                    query,
                    "v=%s" % digest[:10],
                    "%s references %s, not the built file's hash" % (relpath, ref),
                )
                checked += 1
        # Every page loads exactly the two shell assets, both versioned.
        self.assertEqual(checked, 2 * len(pages))

    def test_an_asset_s_hash_follows_its_bytes(self):
        source = os.path.join(ROOT, "site", "assets", "app.js")
        before = build.asset_hash(source)
        self.assertEqual(len(before), 10)
        copy = os.path.join(self.tmp.name, "app.js")
        shutil.copyfile(source, copy)
        self.assertEqual(build.asset_hash(copy), before)  # same bytes, same hash
        with open(copy, "ab") as handle:
            handle.write(b"\n")  # one byte is enough
        self.assertNotEqual(build.asset_hash(copy), before)

    def test_the_headers_file_gives_assets_an_immutable_cache(self):
        path = os.path.join(self.out, "_headers")
        self.assertTrue(os.path.isfile(path), "missing _headers")
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("/assets/*", text)
        self.assertIn("Cache-Control: public, max-age=31536000, immutable", text)
        # HTML and the dataset keep the Pages default, which revalidates.
        self.assertNotIn("/data/", text)
        self.assertNotIn(".html", text)

    def test_a_rebuild_of_unchanged_assets_keeps_the_same_version(self):
        out = os.path.join(self.tmp.name, "rebuild")
        result = subprocess.run(
            [sys.executable, BUILD, "--path", VALID, "--out", out],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(os.path.join(out, "index.html"), encoding="utf-8") as handle:
            rebuilt = handle.read()
        self.assertEqual(
            ASSET_REF_RE.findall(rebuilt),
            ASSET_REF_RE.findall(self.read("index.html")),
        )

    # -- the rest of the scaffold, continued ------------------------------

    def test_every_page_is_noindex_and_carries_the_age_notice(self):
        pages = list(html_files(self.out))
        self.assertGreaterEqual(len(pages), 9)  # index, about, 404, 6 fixture cards
        for page in pages:
            text = self.read(os.path.relpath(page, self.out))
            self.assertIn('<meta name="robots" content="noindex">', text)
            self.assertIn('id="age-gate"', text)

    def test_age_notice_overlays_rather_than_replacing_the_page(self):
        index = self.read("index.html")
        self.assertIn("age-gate", index)
        # The page content ships in the HTML, so a crawler reads it regardless.
        self.assertIn("search-input", index)
        app = self.read("assets/app.js")
        self.assertIn("stemma_age_ok", app)
        self.assertIn("localStorage", app)

    def test_search_reads_only_the_dataset(self):
        app = self.read("assets/app.js")
        self.assertIn("/data/stemma.json", app)
        self.assertIn("Not in the catalog yet.", app)

    def test_strain_page_shows_the_card(self):
        page = self.read(os.path.join("s", "fixture-known-cross", "index.html"))
        self.assertIn("Fixture Known Cross", page)
        self.assertIn("Fictional two-parent cross fixture", page)  # summary
        self.assertIn("late 1970s", page)  # born display
        self.assertIn("Fixture Coast, Testland", page)  # origin place
        self.assertIn("Fixture Seeds", page)  # breeder
        self.assertIn('href="/s/fixture-landrace-root/"', page)  # parent link
        self.assertIn('href="/s/fixture-partial/"', page)  # child link, from edges
        self.assertIn('id="lineage-graph"', page)  # the U3 graph lands here
        self.assertIn("/about/#traditional-labels", page)  # "what this means"
        self.assertIn("Fixture magazine feature", page)  # sources list
        self.assertIn("https://example.invalid/fixture", page)  # source link
        self.assertIn('id="strain-data"', page)  # card data inlined

    def test_a_card_shows_its_facts_and_its_relations(self):
        page = self.read(os.path.join("s", "fixture-cut", "index.html"))
        for section in ("Born", "Origin", "Breeder", "Parents", "Children"):
            self.assertIn(section, page)

    def test_sources_are_a_quiet_unnumbered_list_with_a_category(self):
        page = self.read(os.path.join("s", "fixture-reviewed", "index.html"))
        block = page.split('id="sources-heading"')[1].split("</section>")[0]
        self.assertIn('<ul class="sources">', block)
        self.assertNotIn("<ol", block)
        self.assertNotIn("badge", block)
        for category in ("breeder", "publication", "database", "community"):
            self.assertIn(
                '<span class="sources__category">%s</span>' % category, block
            )

    def test_no_tier_or_dispute_language_survives_on_a_rendered_page(self):
        """Card prose may say "differ"; the chrome may not carry the old model."""
        for name in ("fixture-reviewed", "fixture-cut", "fixture-known-cross"):
            page = self.read(os.path.join("s", name, "index.html"))
            for gone in (
                "tier",
                "documented",
                "breeder-claimed",
                "folklore",
                "disputed",
                "badge",
            ):
                self.assertNotIn(gone, page, "%s still mentions %r" % (name, gone))

    def test_stub_pages_show_lineage_only(self):
        page = self.read(os.path.join("s", "fixture-stub-parent", "index.html"))
        self.assertIn("Not yet cataloged", page)
        self.assertIn("Children", page)
        self.assertIn('href="/s/fixture-known-cross/"', page)
        self.assertNotIn("Sources", page)

    # -- the lineage graph -------------------------------------------------

    def test_strain_pages_ship_a_rendered_lineage_graph(self):
        page = self.read(os.path.join("s", "fixture-known-cross", "index.html"))
        graph = page.split('id="lineage-graph"')[1].split("</section>")[0]
        self.assertIn('<svg class="lineage-svg"', graph)
        self.assertIn('class="lineage-node lineage-node--current"', graph)
        self.assertIn('href="/s/fixture-landrace-root/"', graph)  # parent node
        self.assertIn('href="/s/fixture-partial/"', graph)  # child node
        self.assertIn("lineage-node--stub", graph)  # stubs are muted
        self.assertIn('class="lineage-edge"', graph)

    def test_the_graph_draws_one_edge_style_and_carries_no_legend(self):
        page = self.read(os.path.join("s", "fixture-cut", "index.html"))
        graph = page.split('id="lineage-graph"')[1].split("</section>")[0]
        self.assertNotIn('type="checkbox"', graph)
        self.assertNotIn("lineage-edge--", graph)
        self.assertNotIn("lineage-key", graph)
        css = self.read(os.path.join("assets", "style.css"))
        self.assertNotIn("lineage-layer--disputed", css)
        self.assertNotIn("lineage-key", css)

    def test_the_graph_scrolls_inside_its_own_box(self):
        css = self.read(os.path.join("assets", "style.css"))
        scroll = css.split(".lineage-graph__scroll {")[1].split("}")[0]
        self.assertIn("overflow-x: auto;", scroll)
        self.assertIn("max-width: 100%;", scroll)

    def test_every_rendered_graph_is_well_formed_svg(self):
        drawn = 0
        for strain in self.dataset["strains"]:
            page = self.read(os.path.join("s", strain["id"], "index.html"))
            if "<svg" not in page:
                continue
            svg = page[page.index("<svg") : page.index("</svg>") + len("</svg>")]
            ET.fromstring(svg)  # raises on malformed markup
            drawn += 1
        self.assertGreater(drawn, 0)

    def test_a_root_with_no_children_still_renders_something(self):
        page = self.read(os.path.join("s", "fixture-landrace-root", "index.html"))
        graph = page.split('id="lineage-graph"')[1].split("</section>")[0]
        self.assertTrue("<svg" in graph or "No lineage links" in graph)

    # -- the timeline ------------------------------------------------------

    def dated_ids(self):
        return [
            strain["id"]
            for strain in self.dataset["strains"]
            if timeline.is_dated(strain)
        ]

    def timeline_page(self):
        return self.read(os.path.join("timeline", "index.html"))

    def test_the_timeline_draws_one_bar_per_dated_strain(self):
        page = self.timeline_page()
        self.assertEqual(page.count('class="timeline-bar'), len(self.dataset["strains"]))
        bars = page.count('class="timeline-row timeline-row--bar"')
        self.assertEqual(bars, len(self.dated_ids()))
        for strain_id in self.dated_ids():
            self.assertIn('data-id="%s"' % strain_id, page)

    def test_undated_strains_are_in_the_roots_strip(self):
        page = self.timeline_page()
        self.assertIn("Roots and undated", page)
        roots = page.count('class="timeline-row timeline-row--root"')
        self.assertEqual(
            roots, len(self.dataset["strains"]) - len(self.dated_ids())
        )
        self.assertIn('data-id="fixture-landrace-root"', page)  # born unknown
        self.assertIn('data-id="fixture-stub-parent"', page)  # no born at all

    def test_the_timeline_ships_its_families_for_the_filter(self):
        page = self.timeline_page()
        self.assertIn('id="timeline-data"', page)
        payload = json.loads(
            page.split('id="timeline-data" type="application/json">')[1]
            .split("</script>")[0]
            .replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\u0026", "&")
        )
        self.assertEqual(
            sorted(payload["families"]),
            sorted(strain["id"] for strain in self.dataset["strains"]),
        )
        self.assertEqual(
            payload["families"]["fixture-cut"],
            [
                "fixture-cut",
                "fixture-known-cross",
                "fixture-landrace-root",
                "fixture-reviewed",
                "fixture-stub-parent",
            ],
        )
        app = self.read(os.path.join("assets", "app.js"))
        self.assertIn('queryParam("family")', app)
        self.assertIn("is-filtered", app)
        css = self.read(os.path.join("assets", "style.css"))
        self.assertIn(".timeline-row.is-filtered { display: none; }", css)

    def test_every_strain_page_links_to_its_family_on_the_timeline(self):
        for strain in self.dataset["strains"]:
            page = self.read(os.path.join("s", strain["id"], "index.html"))
            self.assertIn(
                '<a href="/timeline/?family=%s">See on timeline</a>' % strain["id"],
                page,
            )

    def test_the_timeline_axis_scrolls_inside_its_own_box(self):
        css = self.read(os.path.join("assets", "style.css"))
        scroll = css.split(".timeline__scroll {")[1].split("}")[0]
        self.assertIn("overflow-x: auto;", scroll)
        self.assertIn("max-width: 100%;", scroll)

    def test_the_timeline_svg_is_well_formed(self):
        page = self.timeline_page()
        svg = page[page.index("<svg") : page.index("</svg>") + len("</svg>")]
        ET.fromstring(svg)  # raises on malformed markup

    # -- the origin map ----------------------------------------------------

    def map_page(self):
        return self.read(os.path.join("map", "index.html"))

    def located_ids(self):
        return [
            strain["id"]
            for strain in self.dataset["strains"]
            if origins.is_located(strain)
        ]

    def map_payload(self):
        page = self.map_page()
        return json.loads(
            page.split('id="map-data" type="application/json">')[1]
            .split("</script>")[0]
            .replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\u0026", "&")
        )

    def test_the_map_pins_leaflet_to_the_approved_version(self):
        page = self.map_page()
        base = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/"
        self.assertIn('<script src="%sleaflet.min.js"' % base, page)
        self.assertIn('<link rel="stylesheet" href="%sleaflet.min.css"' % base, page)
        # Pinned by version, so the URLs carry no ?v= of ours.
        self.assertNotIn("leaflet.min.js?v=", page)
        self.assertNotIn("leaflet.min.css?v=", page)
        # Subresource integrity: the exact digests the planner verified against
        # the fetched files and the cdnjs API on 2026-09-24.
        self.assertIn(
            'integrity="sha512-puJW3E/qXDqYp9IfhAI54BJEaWIfloJ7JWs7OeD5i6ruC9JZ'
            'L1gERT1wjtwXFlh7CjE7ZJ+/vcRZRkIYIb6p4g=="',
            page,
        )
        self.assertIn(
            'integrity="sha512-h9FcoyWjHcOcmEVkxOfTLnmZFWIH0iZhZT1H2TbOq55xssQG'
            'EJHEaIm+PgoUaZbRvQTNTluNOEfb1ZRy6D3BOw=="',
            page,
        )
        self.assertEqual(page.count('crossorigin="anonymous"'), 2)
        # Pinned exactly: no range, no "latest", and no second library. Checked
        # against the URLs the page loads, not its text: a content hash or a
        # base64 digest can spell "d3" by chance.
        self.assertNotIn("leaflet/latest", page)
        urls = [ref for ref in LINK_RE.findall(page) if ref.startswith(EXTERNAL)]
        self.assertEqual(len(urls), 2)
        for other in ("d3", "mapbox", "jquery", "leaflet.markercluster"):
            for url in urls:
                self.assertNotIn(other, url, "%s loads %s" % (url, other))

    def test_only_the_map_page_loads_leaflet(self):
        for page in html_files(self.out):
            text = self.read(os.path.relpath(page, self.out))
            if page.endswith(os.path.join("map", "index.html")):
                continue
            self.assertNotIn("leaflet", text, "%s loads Leaflet" % page)

    def test_the_map_keeps_the_openstreetmap_attribution(self):
        app = self.read(os.path.join("assets", "app.js"))
        self.assertIn("tile.openstreetmap.org", app)
        self.assertIn("openstreetmap.org/copyright", app)
        self.assertIn("OpenStreetMap", app)

    def test_every_located_strain_is_on_the_map_in_text_too(self):
        page = self.map_page()
        for strain_id in self.located_ids():
            self.assertIn('data-id="%s"' % strain_id, page)
            self.assertIn('href="/s/%s/"' % strain_id, page)
        self.assertIn("Fixture Valley, Testland", page)  # an origin place name

    def test_unknown_origins_are_listed_under_the_map(self):
        page = self.map_page()
        block = page.split('class="map-unknown"')[1]
        self.assertIn("Origin unknown", block)
        for strain in self.dataset["strains"]:
            if origins.is_located(strain):
                continue
            self.assertIn('data-id="%s"' % strain["id"], block)
        self.assertIn('data-id="fixture-partial"', block)  # origin.unknown
        self.assertIn('data-id="fixture-stub-parent"', block)  # no origin at all

    def test_the_map_ships_its_markers_arcs_and_families_inline(self):
        payload = self.map_payload()
        placed = []
        for group in payload["groups"]:
            placed.extend(member["id"] for member in group["members"])
        self.assertEqual(sorted(placed), sorted(self.located_ids()))
        self.assertEqual(
            sorted(payload["families"]),
            sorted(strain["id"] for strain in self.dataset["strains"]),
        )
        # The arcs are the located edges: no arc leaves the map hanging.
        drawn = sorted((arc["child"], arc["parent"]) for arc in payload["arcs"])
        self.assertEqual(
            drawn,
            sorted(
                (edge["child"], edge["parent"])
                for edge in self.dataset["edges"]
                if edge["child"] in self.located_ids()
                and edge["parent"] in self.located_ids()
            ),
        )
        for arc in payload["arcs"]:
            self.assertGreaterEqual(len(arc["points"]), 2)

    def test_the_map_filter_is_the_same_family_the_timeline_uses(self):
        payload = self.map_payload()
        self.assertEqual(
            payload["families"]["fixture-cut"],
            timeline.family("fixture-cut", self.dataset["edges"]),
        )
        app = self.read(os.path.join("assets", "app.js"))
        self.assertIn('inlineJSON("map-data")', app)
        self.assertIn("map-family-input", app)
        css = self.read(os.path.join("assets", "style.css"))
        self.assertIn(".map-place__strain.is-filtered", css)

    def test_every_strain_page_links_to_its_family_on_the_map(self):
        for strain in self.dataset["strains"]:
            page = self.read(os.path.join("s", strain["id"], "index.html"))
            self.assertIn(
                '<a href="/map/?family=%s">See on map</a>' % strain["id"], page
            )

    def test_the_map_works_without_javascript_as_a_list(self):
        page = self.map_page()
        self.assertIn("<noscript>", page)
        self.assertIn('class="map-places"', page)

    def test_about_page_covers_the_contract(self):
        page = self.read(os.path.join("about", "index.html"))
        for needle in (
            "community-maintained catalog",
            "breeder",
            "publication",
            "database",
            "community",
            "not a ranking",  # the categories are descriptive
            "the card says so",  # where accounts differ
            'id="traditional-labels"',
            "Not medical advice",
        ):
            self.assertIn(needle, page)

    def test_about_page_carries_no_tier_or_dispute_model(self):
        page = self.read(os.path.join("about", "index.html"))
        for gone in ("tier", "genetically tested", "breeder claimed", "folklore"):
            self.assertNotIn(gone, page)

    def test_index_lists_the_catalog_for_crawlers(self):
        index = self.read("index.html")
        for strain in self.dataset["strains"]:
            self.assertIn('href="/s/%s/"' % strain["id"], index)

    def test_build_replaces_stale_strain_pages(self):
        stale = os.path.join(self.out, "s", "gone-from-catalog", "index.html")
        os.makedirs(os.path.dirname(stale), exist_ok=True)
        with open(stale, "w", encoding="utf-8") as handle:
            handle.write("stale")
        result = subprocess.run(
            [sys.executable, BUILD, "--path", VALID, "--out", self.out],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(os.path.exists(stale))


if __name__ == "__main__":
    unittest.main()
