"""Smoke tests for the static site that tools/build.py compiles into --out."""

import html
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "tools", "build.py")
VALID = os.path.join(ROOT, "tests", "fixtures", "valid")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import timeline  # noqa: E402  (the site's own dated/undated rule, not a copy)

LINK_RE = re.compile(r'(?:href|src)="([^"]*)"')
EXTERNAL = ("http://", "https://", "//", "mailto:", "tel:", "data:")


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
            os.path.join("assets", "style.css"),
            os.path.join("assets", "app.js"),
            os.path.join("data", "stemma.json"),
        ):
            self.assertTrue(
                os.path.isfile(os.path.join(self.out, relpath)), "missing %s" % relpath
            )

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
        self.assertIn('class="badge badge--documented"', page)  # evidence tier
        self.assertIn("Fixture magazine feature", page)  # sources list
        self.assertIn("https://example.invalid/fixture", page)  # source link
        self.assertIn('id="strain-data"', page)  # card data inlined

    def test_every_claim_on_a_card_carries_a_tier_badge(self):
        page = self.read(os.path.join("s", "fixture-cut", "index.html"))
        for section in ("Born", "Origin", "Breeder", "Parents"):
            self.assertIn(section, page)
        self.assertIn('class="badge badge--breeder-claimed"', page)
        self.assertIn('class="badge badge--genetically-tested"', page)

    def test_disputes_are_listed_as_claims(self):
        page = self.read(os.path.join("s", "fixture-disputed", "index.html"))
        self.assertIn("Disputed", page)
        self.assertIn("Some growers name a landrace as the second parent", page)
        self.assertIn('class="badge badge--folklore"', page)

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
        self.assertIn('class="lineage-key"', graph)  # the legend
        self.assertIn("lineage-edge--documented", graph)
        self.assertIn("lineage-edge--breeder-claimed", graph)

    def test_disputed_edges_ship_hidden_behind_an_unchecked_toggle(self):
        page = self.read(os.path.join("s", "fixture-cut", "index.html"))
        graph = page.split('id="lineage-graph"')[1].split("</section>")[0]
        self.assertIn('type="checkbox"', graph)
        self.assertNotIn("checked", graph)
        self.assertIn("lineage-edge--disputed", graph)
        self.assertIn("lineage-layer--disputed", graph)
        css = self.read(os.path.join("assets", "style.css"))
        self.assertIn(".lineage-layer--disputed { display: none; }", css)
        self.assertIn(".lineage-graph__toggle:checked ~ .lineage-graph__scroll", css)

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
                "fixture-disputed",
                "fixture-known-cross",
                "fixture-landrace-root",
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

    def test_about_page_covers_the_contract(self):
        page = self.read(os.path.join("about", "index.html"))
        for needle in (
            "genetically tested",
            "documented",
            "breeder claimed",
            "folklore",
            "verifies the",  # the genetic-testing caveat
            'id="traditional-labels"',
            'id="disputes"',
            "Not medical advice",
        ):
            self.assertIn(needle, page)

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
