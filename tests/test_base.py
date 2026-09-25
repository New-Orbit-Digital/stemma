"""The build's ``--base``: one tree, two hosts.

Cloudflare Pages serves Stemma at the root of its own host; GitHub Pages serves
it as a project site under ``/stemma/``. These tests hold both ends down:

* ``tools/urls.py`` normalizes whatever the flag is handed.
* The default build is exactly the root-absolute site it has always been.
* The ``/stemma/`` build carries the base on every internal URL it emits, and
  every one of those URLs still reaches a file the build wrote.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "tools", "build.py")
SITE = os.path.join(ROOT, "site")
VALID = os.path.join(ROOT, "tests", "fixtures", "valid")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import build  # noqa: E402
import urls  # noqa: E402

BASE = "/stemma/"

# Every href/src that starts at the host root, and every internal path spelled
# in a string — the two ways a URL reaches a page, markup and JavaScript.
ATTR_RE = re.compile(r'(?:href|src)="(/[^"]*)"')
INTERNAL_RE = re.compile(r'"(/(?:data|s|assets)/[^"]*)"')


def compile_site(out, base=None):
    argv = [sys.executable, BUILD, "--path", VALID, "--out", out]
    if base is not None:
        argv += ["--base", base]
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError("build failed:\n" + result.stdout + result.stderr)
    return result.stdout


def site_files(out, suffixes=(".html", ".js")):
    for dirpath, _dirnames, filenames in os.walk(out):
        for name in sorted(filenames):
            if name.endswith(suffixes):
                yield os.path.join(dirpath, name)


class NormalizeTest(unittest.TestCase):
    """``--base`` is spelled however it is spelled; the build agrees on one form."""

    def test_a_bare_name_becomes_a_rooted_directory(self):
        self.assertEqual(urls.normalize("stemma"), "/stemma/")

    def test_the_slashes_are_idempotent(self):
        for written in ("/stemma/", "/stemma", "stemma/", " stemma ", "stemma"):
            self.assertEqual(urls.normalize(written), "/stemma/", written)

    def test_nothing_means_the_site_root(self):
        for written in (None, "", "   ", "/"):
            self.assertEqual(urls.normalize(written), "/")

    def test_a_nested_base_keeps_its_interior(self):
        self.assertEqual(urls.normalize("a/b"), "/a/b/")


class UrlTest(unittest.TestCase):
    """The helper every module spends, so no module spells a ``/`` of its own."""

    def setUp(self):
        # The base is process state, so a test that moves it puts it back: the
        # rest of the suite renders at the root.
        self.addCleanup(urls.set_base, urls.DEFAULT_BASE)

    def test_the_root_base_leaves_a_path_exactly_as_written(self):
        urls.set_base("/")
        self.assertEqual(urls.url("/data/stemma.json"), "/data/stemma.json")
        self.assertEqual(urls.url("/"), "/")
        self.assertEqual(urls.strain("skunk-1"), "/s/skunk-1/")

    def test_a_subpath_base_prefixes_every_path(self):
        urls.set_base("stemma")
        self.assertEqual(urls.url("/data/stemma.json"), "/stemma/data/stemma.json")
        self.assertEqual(urls.url("/"), "/stemma/")
        self.assertEqual(urls.strain("skunk-1"), "/stemma/s/skunk-1/")

    def test_a_path_is_where_the_file_lives_whatever_the_base_is(self):
        """The file path never carries the base, or the pages would nest twice."""
        urls.set_base(BASE)
        self.assertEqual(urls.strain_path("skunk-1"), "/s/skunk-1/")
        import browse  # noqa: E402  (imported here so the base is already set)

        self.assertEqual(browse.value_path("kind", "landrace"), "/browse/kind/landrace/")
        self.assertEqual(
            browse.value_href("kind", "landrace"), "/stemma/browse/kind/landrace/"
        )


class RootBuildTest(unittest.TestCase):
    """The Cloudflare build: the site it has always been, URL for URL."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = os.path.join(cls.tmp.name, "root")
        compile_site(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, *relpath):
        with open(os.path.join(self.out, *relpath), encoding="utf-8") as handle:
            return handle.read()

    def test_the_default_base_is_the_site_root(self):
        index = self.read("index.html")
        self.assertIn('data-base="/"', index)
        for href in (
            '<a class="masthead__brand" href="/">Stemma</a>',
            '<a href="/browse/">Browse</a>',
            '<a href="/timeline/">Timeline</a>',
            '<a href="/map/">Map</a>',
            '<a href="/about/">About</a>',
        ):
            self.assertIn(href, index)
        self.assertIn('href="/s/fixture-known-cross/"', index)
        self.assertRegex(index, r'href="/assets/style\.css\?v=[0-9a-f]{10}"')

    def test_the_card_page_keeps_its_root_absolute_links(self):
        page = self.read("s", "fixture-known-cross", "index.html")
        for href in (
            'href="/s/fixture-landrace-root/"',
            'href="/browse/breeder/fixture-seeds/"',
            '<a href="/timeline/?family=fixture-known-cross">See on timeline</a>',
            '<a href="/map/?family=fixture-known-cross">See on map</a>',
            'href="/about/#traditional-labels"',
        ):
            self.assertIn(href, page)

    def test_the_root_build_still_writes_the_cloudflare_headers(self):
        self.assertTrue(os.path.isfile(os.path.join(self.out, "_headers")))

    def test_the_root_build_redirects_everything_to_justbost(self):
        """Cloudflare serves only the 301 now: every path, splat preserved."""
        with open(os.path.join(self.out, "_redirects"), encoding="utf-8") as handle:
            self.assertEqual(
                handle.read(), "/*  https://justbost.com/stemma/:splat  301\n"
            )


class SubpathBuildTest(unittest.TestCase):
    """The GitHub Pages build: everything internal moves under ``/stemma/``."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = os.path.join(cls.tmp.name, "sub")
        cls.stdout = compile_site(cls.out, BASE)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, *relpath):
        with open(os.path.join(self.out, *relpath), encoding="utf-8") as handle:
            return handle.read()

    def test_no_internal_url_is_left_at_the_host_root(self):
        """The check the cutover turns on: one stray ``/`` is a 404 on Pages."""
        stray = []
        scanned = 0
        for path in site_files(self.out):
            scanned += 1
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for pattern in (ATTR_RE, INTERNAL_RE):
                for match in pattern.finditer(text):
                    target = match.group(1)
                    if target.startswith("//"):  # protocol-relative: external
                        continue
                    if not target.startswith(BASE):
                        stray.append("%s: %s" % (os.path.relpath(path, self.out), target))
        self.assertGreater(scanned, 0)
        self.assertEqual(stray, [], "root-absolute URLs survived a subpath build")

    def test_the_shell_moves_under_the_base(self):
        index = self.read("index.html")
        self.assertIn('data-base="/stemma/"', index)
        for href in (
            '<a class="masthead__brand" href="/stemma/">Stemma</a>',
            '<a href="/stemma/browse/">Browse</a>',
            '<a href="/stemma/timeline/">Timeline</a>',
            '<a href="/stemma/map/">Map</a>',
            '<a href="/stemma/about/">About</a>',
            '<a href="/stemma/about/">How to read this catalog</a>',
        ):
            self.assertIn(href, index)
        self.assertRegex(index, r'href="/stemma/assets/style\.css\?v=[0-9a-f]{10}"')

    def test_every_module_that_emits_an_href_moves_with_it(self):
        page = self.read("s", "fixture-known-cross", "index.html")
        for href in (
            'href="/stemma/s/fixture-landrace-root/"',  # relations, and the graph
            'href="/stemma/browse/breeder/fixture-seeds/"',  # facts, via links.py
            'href="/stemma/browse/kind/cultivar/"',  # chips
            'href="/stemma/about/#traditional-labels"',  # the label hint
            '<a href="/stemma/timeline/?family=fixture-known-cross">',
            '<a href="/stemma/map/?family=fixture-known-cross">',
        ):
            self.assertIn(href, page)
        # timeline.py and origins.py draw their own rows.
        self.assertIn(
            'href="/stemma/s/fixture-known-cross/"',
            self.read("timeline", "index.html"),
        )
        self.assertIn(
            'href="/stemma/s/fixture-known-cross/"', self.read("map", "index.html")
        )
        # browse.py writes both the rows and the index.
        self.assertIn(
            'href="/stemma/s/fixture-known-cross/"',
            self.read("browse", "kind", "cultivar", "index.html"),
        )
        self.assertIn(
            'href="/stemma/browse/kind/cultivar/"', self.read("browse", "index.html")
        )

    def test_the_pages_still_live_where_the_base_says_they_do(self):
        """The base is a URL prefix, not a directory: ``--out`` is the site root."""
        self.assertFalse(os.path.isdir(os.path.join(self.out, "stemma")))
        for relpath in (
            ("index.html",),
            ("about", "index.html"),
            ("s", "fixture-known-cross", "index.html"),
            ("browse", "index.html"),
            ("data", "stemma.json"),
            ("assets", "app.js"),
        ):
            self.assertTrue(os.path.isfile(os.path.join(self.out, *relpath)), relpath)

    def test_every_internal_url_resolves_to_a_file_once_the_base_is_dropped(self):
        checked = 0
        for path in site_files(self.out, (".html",)):
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for target in ATTR_RE.findall(text):
                if target.startswith("//"):
                    continue
                relpath = target[len(BASE) :].split("#")[0].split("?")[0]
                landing = os.path.join(self.out, relpath)
                if not relpath or relpath.endswith("/"):
                    landing = os.path.join(landing, "index.html")
                self.assertTrue(
                    os.path.isfile(landing),
                    "%s links to %s" % (os.path.relpath(path, self.out), target),
                )
                checked += 1
        self.assertGreater(checked, 0)

    def test_the_subpath_build_writes_no_cloudflare_headers(self):
        """``_headers`` is Cloudflare's, and its /assets/* rule would be wrong."""
        self.assertFalse(os.path.isfile(os.path.join(self.out, "_headers")))
        self.assertIn("skipped _headers", self.stdout)

    def test_the_subpath_build_writes_no_redirects(self):
        """A /* rule on the new host would loop, so only Cloudflare gets one."""
        self.assertFalse(os.path.isfile(os.path.join(self.out, "_redirects")))

    def test_the_dataset_is_the_same_dataset(self):
        """The base is a hosting detail; the Budlogs seam does not know about it."""
        with open(
            os.path.join(self.out, "data", "stemma.json"), encoding="utf-8"
        ) as handle:
            dataset = json.load(handle)
        self.assertEqual(dataset["schema_version"], build.SCHEMA_VERSION)
        self.assertTrue(dataset["strains"])


class ScreenshotTest(unittest.TestCase):
    """``site/screenshot.png`` rides along when the planner has added one."""

    def test_the_build_copies_the_screenshot_when_the_file_exists(self):
        source = os.path.join(SITE, build.SCREENSHOT)
        placed = not os.path.isfile(source)
        if placed:
            # A one-pixel PNG: the build only copies bytes, it never reads them.
            with open(source, "wb") as handle:
                handle.write(
                    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00"
                    b"\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\n"
                    b"IDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00"
                    b"\x00IEND\xaeB`\x82"
                )
            self.addCleanup(os.remove, source)
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "shot")
            compile_site(out)
            copied = os.path.join(out, build.SCREENSHOT)
            self.assertTrue(os.path.isfile(copied))
            with open(source, "rb") as handle:
                original = handle.read()
            with open(copied, "rb") as handle:
                self.assertEqual(handle.read(), original)

    def test_a_missing_screenshot_is_not_an_error(self):
        source = os.path.join(SITE, build.SCREENSHOT)
        if os.path.isfile(source):
            self.skipTest("site/%s exists, so the build copies it" % build.SCREENSHOT)
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "none")
            compile_site(out)  # raises if the build exits nonzero
            self.assertFalse(os.path.isfile(os.path.join(out, build.SCREENSHOT)))


if __name__ == "__main__":
    unittest.main()
