#!/usr/bin/env python3
"""The ``[[...]]`` link markup a card's ``summary`` carries.

Stdlib only. One module, because three callers have to agree on exactly what a
summary says:

* ``tools/validate.py`` reports malformed markup (E12), a target that resolves
  to nothing (E13), and the 400-character ceiling against the *visible* text.
* ``tools/build.py`` renders the markup into anchors on the strain page and
  writes the visible text into the dataset as ``summary_plain``.
* ``tools/browse.py`` slugs the same values into the browse URLs the links
  point at, using :func:`slug` from here.

The forms, as docs/voice.md writes them::

    [[skunk-1]]                  the card's page, with the card's name as text
    [[skunk-1|Skunk #1]]         the card's page, with that text
    [[breeder:Sensi Seeds]]      /browse/breeder/sensi-seeds/
    [[kind:landrace|landrace]]   /browse/kind/landrace/
    [[country:MX|Mexico]]        /browse/country/mx/
    [[label:sativa|sativa]]      /browse/label/sativa/

Everything that is not a strain id points at a browse page, so every link in a
summary lands on something Stemma actually catalogs. Whether a target *exists*
is not a question this module answers — resolution lives in the validator,
which is the one place that has every card in hand.

The markup applies only inside ``summary``. Nothing else on a card is parsed.
"""

import html
import re

import countries

# A well-formed token holds no brackets of its own, so a stray ``[[`` cannot be
# swallowed by the next ``]]`` several sentences later: it is left behind in the
# plain text, where :func:`_scan` sees it and reports it.
TOKEN_RE = re.compile(r"\[\[([^\[\]]*)\]\]")

SLUG_RE = re.compile(r"[^a-z0-9]+")

STRAIN = "strain"
DIMENSIONS = ("breeder", "kind", "country", "label")

EXCERPT = 40  # characters of context in a malformed-markup message


def slug(value):
    """The name, lowercased, with runs of non-alphanumerics turned into ``-``.

    ASCII on purpose: the output is a URL path segment, so a letter that is
    alphanumeric to Python but not to a reader's keyboard collapses to ``-``.
    """
    return SLUG_RE.sub("-", str(value).lower()).strip("-")


class Link:
    """One parsed link: where it points and what it reads as."""

    __slots__ = ("dimension", "value", "text", "raw")

    def __init__(self, dimension, value, text, raw):
        self.dimension = dimension  # STRAIN, or one of DIMENSIONS
        self.value = value  # the target as written, minus the prefix
        self.text = text  # the explicit ``|text``, or None
        self.raw = raw  # the whole ``[[...]]`` span, for messages

    def __repr__(self):  # pragma: no cover - debugging aid
        return "Link(%r, %r, %r)" % (self.dimension, self.value, self.text)

    @property
    def href(self):
        if self.dimension == STRAIN:
            return "/s/%s/" % self.value
        if self.dimension == "country":
            return "/browse/country/%s/" % (countries.code(self.value) or "").lower()
        return "/browse/%s/%s/" % (self.dimension, slug(self.value))

    def display(self, names=None):
        """The visible text: the explicit ``|text``, or the target's own name.

        A bare ``[[<id>]]`` reads as the card's ``name``, which is why rendering
        takes a ``{id: name}`` map. A bare ``[[country:MX]]`` reads as the
        country's English name. The other dimensions read as the value itself.
        """
        if self.text:
            return self.text
        if self.dimension == STRAIN:
            return (names or {}).get(self.value, self.value)
        if self.dimension == "country":
            return countries.name(self.value) or self.value
        return self.value


def _parse_token(raw, body):
    """``(Link, None)`` for a well-formed token, ``(None, message)`` otherwise."""
    target, bar, text = body.partition("|")
    target = target.strip()
    text = text.strip()
    if not target:
        return None, "empty link target in %s" % _excerpt(raw)
    if bar and not text:
        return None, "empty link text in %s" % _excerpt(raw)
    prefix, colon, value = target.partition(":")
    if not colon:
        return Link(STRAIN, target, text or None, raw), None
    prefix = prefix.strip().lower()
    value = value.strip()
    if prefix not in DIMENSIONS:
        return None, "unknown link prefix '%s:' in %s" % (prefix, _excerpt(raw))
    if not value:
        return None, "empty link target in %s" % _excerpt(raw)
    return Link(prefix, value, text or None, raw), None


def _excerpt(text):
    """A short quoted fragment, so a message points at the span it means."""
    text = str(text)
    if len(text) > EXCERPT:
        text = text[:EXCERPT] + "..."
    return "'%s'" % text


def _around(text, marker):
    index = text.find(marker)
    start = max(0, index - EXCERPT // 2)
    return _excerpt(text[start : index + EXCERPT // 2])


def _scan(text):
    """``(spans, problems)``: ``str`` and :class:`Link` spans, in order.

    A malformed token stays in the spans as literal text rather than vanishing,
    so a page built from an unvalidated card still shows the prose. The build
    never sees one: validation runs first and a malformed token is an error.
    """
    spans, problems, outside = [], [], []
    position = 0
    for match in TOKEN_RE.finditer(text):
        if match.start() > position:
            chunk = text[position : match.start()]
            spans.append(chunk)
            outside.append(chunk)
        position = match.end()
        link, problem = _parse_token(match.group(0), match.group(1))
        if link is None:
            problems.append(problem)
            spans.append(match.group(0))
        else:
            spans.append(link)
    if position < len(text):
        spans.append(text[position:])
        outside.append(text[position:])

    # Only the prose between the tokens is scanned for stray markers: a token
    # this scan already read and rejected is reported once, on its own terms.
    stray = "".join(outside)
    for marker in ("[[", "]]"):
        if marker in stray:
            problems.append("unbalanced '%s' in %s" % (marker, _around(stray, marker)))
    return spans, problems


def parse(text):
    """``(links, problems)`` for one summary. ``problems`` is E12's message list."""
    if not isinstance(text, str) or not text:
        return [], []
    spans, problems = _scan(text)
    return [span for span in spans if isinstance(span, Link)], problems


def plain(text, names=None):
    """The visible text: every link reduced to what a reader sees.

    This is what the 400-character ceiling counts and what the dataset carries
    as ``summary_plain``.
    """
    if not isinstance(text, str) or not text:
        return "" if text is None else text
    spans, _problems = _scan(text)
    return "".join(
        span if isinstance(span, str) else span.display(names) for span in spans
    )


def visible_length(text, names=None):
    return len(plain(text, names))


def render(text, names=None):
    """The summary as HTML: links become anchors, everything is escaped.

    Escaping happens here, after the markup is parsed, so a summary can hold
    ``&`` or ``<`` in its prose and in its link text without either being read
    as markup or reaching the page unescaped.
    """
    if not isinstance(text, str) or not text:
        return ""
    spans, _problems = _scan(text)
    out = []
    for span in spans:
        if isinstance(span, str):
            out.append(html.escape(span, quote=True))
        else:
            out.append(
                '<a href="%s">%s</a>'
                % (
                    html.escape(span.href, quote=True),
                    html.escape(span.display(names), quote=True),
                )
            )
    return "".join(out)
