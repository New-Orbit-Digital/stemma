"""Tests for tools/links.py — the [[...]] markup a summary carries.

The validator and the build both read a summary through this module, so what
it says a summary means is what a card means.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import countries  # noqa: E402
import links  # noqa: E402

NAMES = {
    "skunk-1": "Skunk #1",
    "acapulco-gold": "Acapulco Gold",
}


class SlugTest(unittest.TestCase):
    def test_a_name_lowercases_and_joins_on_non_alphanumerics(self):
        self.assertEqual(links.slug("Sensi Seeds"), "sensi-seeds")
        self.assertEqual(
            links.slug("Sacred Seeds (David Watson, aka Sam the Skunkman)"),
            "sacred-seeds-david-watson-aka-sam-the-skunkman",
        )

    def test_runs_collapse_and_the_edges_are_stripped(self):
        self.assertEqual(links.slug("  Green -- House!!  "), "green-house")
        self.assertEqual(links.slug("#1 Cut"), "1-cut")


class FormTest(unittest.TestCase):
    """Every row of the packet's markup table, rendered."""

    def render(self, text):
        return links.render(text, NAMES)

    def test_a_bare_id_links_to_the_card_using_its_name(self):
        self.assertEqual(
            self.render("A cross of [[skunk-1]]."),
            'A cross of <a href="/s/skunk-1/">Skunk #1</a>.',
        )

    def test_an_id_with_text_links_to_the_card_using_that_text(self):
        self.assertEqual(
            self.render("[[skunk-1|the Skunk line]] came first."),
            '<a href="/s/skunk-1/">the Skunk line</a> came first.',
        )

    def test_a_breeder_links_to_its_browse_page(self):
        self.assertEqual(
            self.render("Bred by [[breeder:Sensi Seeds]]."),
            'Bred by <a href="/browse/breeder/sensi-seeds/">Sensi Seeds</a>.',
        )
        self.assertEqual(
            self.render("Bred by [[breeder:Sensi Seeds|the Dutch house]]."),
            'Bred by <a href="/browse/breeder/sensi-seeds/">the Dutch house</a>.',
        )

    def test_a_kind_links_to_its_browse_page(self):
        self.assertEqual(
            self.render("A [[kind:landrace|landrace]]."),
            'A <a href="/browse/kind/landrace/">landrace</a>.',
        )

    def test_a_country_links_to_the_lowercase_code(self):
        self.assertEqual(
            self.render("From [[country:MX|Mexico]]."),
            'From <a href="/browse/country/mx/">Mexico</a>.',
        )

    def test_a_country_is_read_case_insensitively_and_names_itself(self):
        self.assertEqual(
            self.render("From [[country:mx]]."),
            'From <a href="/browse/country/mx/">Mexico</a>.',
        )

    def test_a_label_links_to_its_browse_page(self):
        self.assertEqual(
            self.render("The [[label:sativa|sativa]] label."),
            'The <a href="/browse/label/sativa/">sativa</a> label.',
        )

    def test_several_links_in_one_sentence_all_render(self):
        rendered = self.render(
            "[[skunk-1]] crossed with [[acapulco-gold|Acapulco]] by "
            "[[breeder:Sacred Seeds]] in [[country:US|California]]."
        )
        self.assertEqual(rendered.count("<a href="), 4)
        self.assertIn('href="/browse/breeder/sacred-seeds/"', rendered)
        self.assertIn('href="/browse/country/us/"', rendered)


class EscapingTest(unittest.TestCase):
    def test_prose_is_escaped(self):
        self.assertEqual(
            links.render("Sold as <b>gold</b> & seed.", NAMES),
            "Sold as &lt;b&gt;gold&lt;/b&gt; &amp; seed.",
        )

    def test_link_text_and_href_are_escaped(self):
        rendered = links.render('[[breeder:Ben & Co "Seeds"]]', NAMES)
        self.assertNotIn("<b", rendered)
        self.assertIn("Ben &amp; Co &quot;Seeds&quot;", rendered)
        self.assertIn('href="/browse/breeder/ben-co-seeds/"', rendered)

    def test_markup_cannot_smuggle_a_tag_through_the_text(self):
        rendered = links.render("[[skunk-1|<script>alert(1)</script>]]", NAMES)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)


class PlainTextTest(unittest.TestCase):
    def test_the_visible_text_is_the_prose_with_the_markup_reduced(self):
        self.assertEqual(
            links.plain(
                "A [[kind:cultivar|hybrid]] from [[breeder:Sensi Seeds]], "
                "out of [[skunk-1]].",
                NAMES,
            ),
            "A hybrid from Sensi Seeds, out of Skunk #1.",
        )

    def test_markup_does_not_count_against_the_visible_length(self):
        text = "Out of [[acapulco-gold|Acapulco Gold]] and [[skunk-1|Skunk #1]]."
        self.assertEqual(
            links.plain(text, NAMES), "Out of Acapulco Gold and Skunk #1."
        )
        self.assertLess(links.visible_length(text, NAMES), len(text))
        self.assertEqual(links.visible_length(text, NAMES), 34)

    def test_a_summary_without_markup_is_its_own_visible_text(self):
        self.assertEqual(links.plain("Plain prose.", NAMES), "Plain prose.")
        self.assertEqual(links.plain("", NAMES), "")

    def test_an_unknown_id_still_reads_as_the_id(self):
        # The validator reports it (E13); the text stays legible meanwhile.
        self.assertEqual(links.plain("From [[mystery]].", NAMES), "From mystery.")


class MalformedTest(unittest.TestCase):
    def problems(self, text):
        return links.parse(text)[1]

    def test_an_unclosed_link_is_reported(self):
        problems = self.problems("Out of [[skunk-1 and nothing else.")
        self.assertEqual(len(problems), 1)
        self.assertIn("unbalanced '[['", problems[0])

    def test_a_stray_close_is_reported(self):
        problems = self.problems("Out of skunk-1]] and nothing else.")
        self.assertEqual(len(problems), 1)
        self.assertIn("unbalanced ']]'", problems[0])

    def test_an_empty_target_is_reported(self):
        self.assertIn("empty link target", self.problems("Out of [[]].")[0])
        self.assertIn("empty link target", self.problems("Out of [[|text]].")[0])
        self.assertIn("empty link target", self.problems("Out of [[breeder:]].")[0])

    def test_an_empty_link_text_is_reported(self):
        self.assertIn("empty link text", self.problems("Out of [[skunk-1|]].")[0])

    def test_an_unknown_prefix_is_reported(self):
        problems = self.problems("A [[strain:skunk-1|Skunk]] link.")
        self.assertEqual(len(problems), 1)
        self.assertIn("unknown link prefix 'strain:'", problems[0])

    def test_a_malformed_token_is_reported_once(self):
        # It must not also be counted as a stray bracket run.
        self.assertEqual(len(self.problems("[[nope:x|y]]")), 1)

    def test_ordinary_brackets_are_not_markup(self):
        self.assertEqual(self.problems("A note [in brackets] and [one more]."), [])
        self.assertEqual(links.plain("A note [in brackets].", NAMES), "A note [in brackets].")

    def test_well_formed_markup_reports_nothing(self):
        self.assertEqual(self.problems("[[skunk-1]] and [[country:MX|Mexico]]."), [])


class ParseTest(unittest.TestCase):
    def test_parse_returns_the_links_in_order(self):
        found, problems = links.parse(
            "[[skunk-1]] from [[breeder:Sensi Seeds]] in [[country:NL|the Netherlands]]"
        )
        self.assertEqual(problems, [])
        self.assertEqual(
            [(link.dimension, link.value, link.text) for link in found],
            [
                (links.STRAIN, "skunk-1", None),
                ("breeder", "Sensi Seeds", None),
                ("country", "NL", "the Netherlands"),
            ],
        )

    def test_every_dimension_has_a_browse_url(self):
        for dimension in links.DIMENSIONS:
            href = links.Link(dimension, "NL" if dimension == "country" else "x", None, "").href
            self.assertTrue(href.startswith("/browse/%s/" % dimension), href)
            self.assertTrue(href.endswith("/"), href)


class CountryMapTest(unittest.TestCase):
    def test_the_packet_s_countries_are_all_in_the_map(self):
        required = (
            "AF CO MX US NL IN TH JM NP PK JP CA ES GB FR DE LB MA BR ZA VN LA KH CN AU"
        ).split()
        for code in required:
            self.assertIsNotNone(countries.name(code), code)

    def test_codes_are_two_upper_case_letters_with_a_name(self):
        for code, name in countries.COUNTRIES.items():
            self.assertRegex(code, r"^[A-Z]{2}$")
            self.assertTrue(name and name[0].isupper(), code)

    def test_an_unknown_code_is_unknown(self):
        self.assertIsNone(countries.code("ZZ"))
        self.assertIsNone(countries.name("ZZ"))
        self.assertFalse(countries.is_known(None))
        self.assertEqual(countries.code(" mx "), "MX")


if __name__ == "__main__":
    unittest.main()
