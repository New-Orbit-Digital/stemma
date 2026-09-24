#!/usr/bin/env python3
"""The browse pages: one static page per value the catalog actually records.

Stdlib only, no new data fields. Every dimension is read off the compiled
dataset's ``strains``, so the pages are a view of the same cards the search and
the map read, and a value with no cards has no page.

Four dimensions, the four things a summary can link to that isn't a strain:

===========  ==================================  ==================
Dimension    URL                                 Heading
===========  ==================================  ==================
``breeder``  ``/browse/breeder/<slug>/``         Breeder · Sensi Seeds
``kind``     ``/browse/kind/<kind>/``            Kind · Landrace
``country``  ``/browse/country/<cc>/``           Origin · Mexico
``label``    ``/browse/label/<label>/``          Label · Sativa
===========  ==================================  ==================

The URL segment is ``links.slug`` of the value, called rather than copied, so a
``[[breeder:Sensi Seeds]]`` link in a summary and the page it lands on cannot
drift apart. Two different values that slug the same way would quietly share a
page, so that raises instead.

Rows reuse the search results list style: the name as a link, the kind, and the
born display.
"""

import html

import countries
import links
import timeline

KIND_LABELS = timeline.KIND_LABELS  # one wording, shared with the timeline legend

# In reading order, which is also the order the /browse/ index lists them.
DIMENSIONS = (
    ("breeder", "Breeder"),
    ("kind", "Kind"),
    ("country", "Origin"),
    ("label", "Label"),
)

ROOT = "browse"


def _esc(value):
    return html.escape("" if value is None else str(value), quote=True)


# -- reading the cards -----------------------------------------------------


def card_value(dimension, card):
    """The card's value on one dimension, or ``None`` when it has none.

    A stub has a ``kind`` and nothing else, an unknown origin has no country,
    and ``breeder: null`` is "not recorded" — all of which mean the card simply
    does not appear on that dimension's pages.
    """
    if dimension == "breeder":
        breeder = card.get("breeder")
        return breeder if isinstance(breeder, str) and breeder.strip() else None
    if dimension == "kind":
        kind = card.get("kind")
        return kind if kind in KIND_LABELS else None
    if dimension == "label":
        label = card.get("traditional_label")
        return label if isinstance(label, str) and label else None
    if dimension == "country":
        origin = card.get("origin") or {}
        if origin.get("unknown") is True:
            return None
        return countries.code(origin.get("country"))
    raise ValueError("unknown browse dimension %r" % (dimension,))


def value_title(dimension, value):
    """The value as a heading reads it: ``Sensi Seeds``, ``Landrace``, ``Mexico``."""
    if dimension == "kind":
        wording = KIND_LABELS.get(value, value)
        return wording[:1].upper() + wording[1:]
    if dimension == "country":
        return countries.name(value) or value
    if dimension == "label":
        return value[:1].upper() + value[1:]
    return value


def value_href(dimension, value):
    """The page's URL — the same one ``links.Link.href`` builds for a summary."""
    return links.Link(dimension, value, None, "").href


def _sort_key(card):
    name = card.get("name") or card.get("id") or ""
    return (name.lower(), card.get("id") or "")


def entries(strains, dimension):
    """One entry per value at least one card has, sorted by title."""
    members = {}
    for card in strains:
        value = card_value(dimension, card)
        if value is None:
            continue
        members.setdefault(value, []).append(card)

    by_slug = {}
    found = []
    for value in sorted(members):
        href = value_href(dimension, value)
        clash = by_slug.get(href)
        if clash is not None:
            raise ValueError(
                "browse %s: %r and %r both map to %s" % (dimension, clash, value, href)
            )
        by_slug[href] = value
        found.append(
            {
                "dimension": dimension,
                "value": value,
                "title": value_title(dimension, value),
                "href": href,
                "relpath": href.strip("/").split("/") + ["index.html"],
                "members": sorted(members[value], key=_sort_key),
            }
        )
    found.sort(key=lambda entry: (entry["title"].lower(), entry["value"]))
    return found


def groups(strains):
    """Every dimension with at least one value, in reading order."""
    out = []
    for dimension, label in DIMENSIONS:
        found = entries(strains, dimension)
        if found:
            out.append({"dimension": dimension, "label": label, "entries": found})
    return out


def page_count(found_groups):
    """Pages the build writes: one per value, plus the ``/browse/`` index."""
    return 1 + sum(len(group["entries"]) for group in found_groups)


# -- markup ----------------------------------------------------------------


def count_text(total):
    return "1 card" if total == 1 else "%d cards" % total


def row(card):
    """One results-list row: the name as a link, the kind, the born display."""
    kind = KIND_LABELS.get(card.get("kind"), card.get("kind") or "")
    born = (card.get("born") or {}).get("display") or "Born unknown"
    meta = " &middot; ".join(part for part in (_esc(kind), _esc(born)) if part)
    return (
        '<li data-id="%s"><a href="/s/%s/"><strong>%s</strong>'
        '<span class="result__meta">%s</span></a></li>'
        % (
            _esc(card.get("id")),
            _esc(card.get("id")),
            _esc(card.get("name") or card.get("id")),
            meta,
        )
    )


def rows_html(cards):
    if not cards:
        return '<p class="empty">No cards here yet.</p>'
    return '<ul class="card-list">%s</ul>' % "".join(row(card) for card in cards)


def heading(entry, label):
    """``Breeder &middot; Sensi Seeds``."""
    return "%s &middot; %s" % (_esc(label), _esc(entry["title"]))


def heading_text(entry, label):
    """The same heading as plain text, for ``<title>`` and the description."""
    return "%s · %s" % (label, entry["title"])


def index_html(found_groups):
    """The ``/browse/`` index: one short list per dimension, with counts."""
    sections = []
    for group in found_groups:
        rows = "".join(
            '<li><a href="%s">%s</a> <span class="result__meta">%s</span></li>'
            % (
                _esc(entry["href"]),
                _esc(entry["title"]),
                _esc(count_text(len(entry["members"]))),
            )
            for entry in group["entries"]
        )
        sections.append(
            '<section class="browse-group" aria-labelledby="browse-%s">'
            '<h2 id="browse-%s">%s</h2>'
            '<ul class="browse-values">%s</ul></section>'
            % (
                _esc(group["dimension"]),
                _esc(group["dimension"]),
                _esc(group["label"]),
                rows,
            )
        )
    if not sections:
        return '<p class="empty">No cards yet, so there is nothing to browse.</p>'
    return "".join(sections)
