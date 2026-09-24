#!/usr/bin/env python3
"""The timeline page: every dated strain as a bar on a shared year axis.

Stdlib only, hand-rolled SVG, and no new data fields. Bars come from ``born``
and ``kind`` on the compiled dataset's ``strains``; the family filter comes from
its ``edges``, through the ancestor walk in ``tools/lineage.py`` rather than a
second copy of it.

Like the lineage graph, the layout is computed at build time, so the markup that
ships is the markup that renders and ``layout()`` is the pure function the tests
exercise. The only runtime work is hiding the rows a ``?family=`` filter leaves
out.

Shape of the page:

* **Rows.** One row per card, never shared, so no bar is ever hidden behind
  another and a row is a stable click target.
* **Groups.** "Roots and undated" first, drawn in a strip to the left of the
  axis: ``born.unknown`` cards and stubs, which have no span to plot. Then one
  group per decade, keyed on ``year_min``, so the rows read as decades and not
  just as a slope.
* **Axis.** Fixed-width decade columns, so a decade is the same distance
  everywhere, with the decade an alternating band behind the bars. Bars run
  from ``year_min`` to ``year_max``, the fuzziness the schema records.
* **Filter.** ``family()`` is the ancestor walk the diagram uses. Every card's
  family ships inline, so a shared ``?family=`` URL filters on first render
  with no fetch, and rows only ever hide: the axis never moves under the
  filter, the way the disputed toggle never moves the diagram.
"""

import html

import lineage

DECADE = 10
ROOTS_LABEL = "Roots and undated"

# Geometry, in SVG user units (1 unit = 1 CSS px at the rendered size).
PAD = 12
STRIP_W = 136  # the roots strip, left of the axis
GUTTER = 16
DECADE_W = 120  # one year is 12 units
AXIS_H = 30
CAPTION_H = 26
ROW_H = 34
BAR_H = 20  # inside a 34px row: >= 40px tap target with the row padding
MIN_BAR_W = 12  # a one-year span still needs something to click
LABEL_W = 152  # room for the name to the right of a bar

# Roughly how many characters fit at the label font size.
NAME_CHARS = 20
STRIP_CHARS = 17

KIND_LABELS = {
    "landrace": "landrace",
    "cultivar": "cultivar",
    "cut": "clone-only cut",
}
KIND_ORDER = ["landrace", "cultivar", "cut"]


# -- cards -----------------------------------------------------------------


def _is_year(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_dated(card):
    """True when ``born`` carries a span to plot.

    ``born.unknown`` is the schema's other shape, and a stub has no ``born`` at
    all; both belong in the roots strip.
    """
    born = card.get("born") or {}
    if born.get("unknown") is True:
        return False
    return _is_year(born.get("year_min")) and _is_year(born.get("year_max"))


def _name(card):
    return card.get("name") or card["id"]


def _meta(card):
    if card.get("status") == "stub":
        return "not yet cataloged"
    born = card.get("born") or {}
    return born.get("display") or "born unknown"


def _dated_key(card):
    born = card["born"]
    return (born["year_min"], born["year_max"], _name(card), card["id"])


def _undated_key(card):
    return (_name(card), card["id"])


def family(strain_id, edges, with_disputed=False):
    """The ids ``?family=<strain_id>`` keeps: the strain and its ancestors.

    Disputed parents are left out by default, matching the rest of the site:
    the timeline shows the best-supported account unless asked otherwise.
    """
    return lineage.family(strain_id, edges, with_disputed)


def families(strains, edges, with_disputed=False):
    """Every card's family, the lookup the runtime filter reads."""
    return {
        card["id"]: family(card["id"], edges, with_disputed)
        for card in strains or []
        if isinstance(card, dict) and card.get("id")
    }


# -- layout ----------------------------------------------------------------


def _span(dated):
    """The decade-snapped year range the axis covers."""
    if not dated:
        return None, None
    first = min(card["born"]["year_min"] for card in dated)
    last = max(card["born"]["year_max"] for card in dated)
    return (first // DECADE) * DECADE, (last // DECADE) * DECADE + DECADE


def _offset(year, start):
    return (year - start) * DECADE_W // DECADE


def _decade_groups(dated):
    """The dated cards, in order, grouped by the decade of ``year_min``."""
    groups = []
    for card in dated:
        decade = (card["born"]["year_min"] // DECADE) * DECADE
        if not groups or groups[-1][0] != decade:
            groups.append((decade, []))
        groups[-1][1].append(card)
    return groups


def layout(strains, edges=None):
    """Place every card on the timeline. Pure: no markup, no I/O.

    Returns the ``bars`` (dated cards, in the plot area), the ``roots`` (undated
    cards, in the strip), the row ``groups`` they sit in, the ``decades`` of the
    axis, the canvas ``width``/``height``, and the ``kinds`` present.
    """
    cards = [
        card for card in strains or [] if isinstance(card, dict) and card.get("id")
    ]
    dated = sorted((card for card in cards if is_dated(card)), key=_dated_key)
    undated = sorted((card for card in cards if not is_dated(card)), key=_undated_key)

    start, end = _span(dated)
    plot_x = PAD + STRIP_W + GUTTER
    decades = []
    for index, year in enumerate(range(start or 0, end or 0, DECADE)):
        decades.append(
            {
                "year": year,
                "label": "%ds" % year,
                "x": plot_x + _offset(year, start),
                "width": DECADE_W,
                "band": index % 2 == 1,
            }
        )
    plot_w = len(decades) * DECADE_W
    axis_h = AXIS_H if decades else 0
    width = (
        plot_x + plot_w + LABEL_W + PAD if decades else PAD + STRIP_W + PAD
    )

    groups = []
    roots = []
    bars = []
    y = PAD + axis_h

    def open_group(key, label):
        group = {"key": key, "label": label, "y": y, "rows": [], "first": not groups}
        groups.append(group)
        return group

    def close_group(group):
        group["height"] = y - group["y"]

    if undated:
        group = open_group("undated", ROOTS_LABEL)
        y += CAPTION_H
        for card in undated:
            roots.append(
                {
                    "id": card["id"],
                    "name": _name(card),
                    "kind": card.get("kind") or "",
                    "meta": _meta(card),
                    "group": "undated",
                    "dated": False,
                    "x": PAD,
                    "y": y + (ROW_H - BAR_H) // 2,
                    "width": STRIP_W,
                }
            )
            group["rows"].append(card["id"])
            y += ROW_H
        close_group(group)

    for decade, members in _decade_groups(dated):
        group = open_group("%d" % decade, "%ds" % decade)
        y += CAPTION_H
        for card in members:
            born = card["born"]
            left = _offset(born["year_min"], start)
            right = _offset(born["year_max"], start)
            bars.append(
                {
                    "id": card["id"],
                    "name": _name(card),
                    "kind": card.get("kind") or "",
                    "meta": _meta(card),
                    "group": group["key"],
                    "dated": True,
                    "year_min": born["year_min"],
                    "year_max": born["year_max"],
                    "x": plot_x + left,
                    "y": y + (ROW_H - BAR_H) // 2,
                    "width": max(right - left, MIN_BAR_W),
                }
            )
            group["rows"].append(card["id"])
            y += ROW_H
        close_group(group)

    present = {row["kind"] for row in roots + bars if row["kind"]}
    return {
        "bars": bars,
        "roots": roots,
        "groups": groups,
        "decades": decades,
        "start_year": start,
        "end_year": end,
        "plot_x": plot_x,
        "plot_w": plot_w,
        "strip_w": STRIP_W,
        "axis_h": axis_h,
        "width": width,
        "height": y + PAD,
        "kinds": [kind for kind in KIND_ORDER if kind in present]
        + sorted(present.difference(KIND_ORDER)),
    }


# -- rendering -------------------------------------------------------------


def _esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def _clip(text, limit):
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _axis_svg(graph):
    if not graph["decades"]:
        return ""
    parts = []
    for decade in graph["decades"]:
        if decade["band"]:
            parts.append(
                '<rect class="timeline-band" x="%d" y="%d" width="%d" height="%d"></rect>'
                % (decade["x"], PAD, decade["width"], graph["height"] - 2 * PAD)
            )
        parts.append(
            '<line class="timeline-grid" x1="%d" y1="%d" x2="%d" y2="%d"></line>'
            % (decade["x"], PAD, decade["x"], graph["height"] - PAD)
        )
        parts.append(
            '<text class="timeline-axis__label" x="%d" y="%d">%s</text>'
            % (decade["x"] + 6, PAD + 16, _esc(decade["label"]))
        )
    edge = graph["plot_x"] + graph["plot_w"]
    parts.append(
        '<line class="timeline-grid" x1="%d" y1="%d" x2="%d" y2="%d"></line>'
        % (edge, PAD, edge, graph["height"] - PAD)
    )
    return '<g class="timeline-axis">%s</g>' % "".join(parts)


def _groups_svg(graph):
    parts = []
    for group in graph["groups"]:
        if not group["first"]:
            parts.append(
                '<line class="timeline-rule" x1="%d" y1="%d" x2="%d" y2="%d"></line>'
                % (PAD, group["y"] + 2, graph["width"] - PAD, group["y"] + 2)
            )
        parts.append(
            '<text class="timeline-caption" x="%d" y="%d">%s</text>'
            % (PAD, group["y"] + CAPTION_H - 8, _esc(group["label"]))
        )
    return '<g class="timeline-groups">%s</g>' % "".join(parts)


def _row_svg(row):
    """One card: a link wrapping its bar and its name.

    ``data-id`` is what the runtime filter matches on, so the filter never needs
    to know the geometry.
    """
    classes = ["timeline-row", "timeline-row--%s" % ("bar" if row["dated"] else "root")]
    kind = row["kind"] if row["kind"] in KIND_LABELS else "unknown"
    bar = (
        '<rect class="timeline-bar timeline-bar--%s" x="%d" y="%d" width="%d" '
        'height="%d" rx="5"></rect>'
        % (_esc(kind), row["x"], row["y"], row["width"], BAR_H)
    )
    if row["dated"]:
        label = (
            '<text class="timeline-row__name" x="%d" y="%d">%s</text>'
            % (
                row["x"] + row["width"] + 8,
                row["y"] + BAR_H - 6,
                _esc(_clip(row["name"], NAME_CHARS)),
            )
        )
        title = "%s, %s (%s)" % (
            row["name"],
            row["meta"] or "%d to %d" % (row["year_min"], row["year_max"]),
            KIND_LABELS.get(row["kind"], "kind unknown"),
        )
    else:
        label = (
            '<text class="timeline-row__name timeline-row__name--inside" x="%d" '
            'y="%d">%s</text>'
            % (
                row["x"] + 10,
                row["y"] + BAR_H - 6,
                _esc(_clip(row["name"], STRIP_CHARS)),
            )
        )
        title = "%s, %s (%s)" % (
            row["name"],
            row["meta"],
            KIND_LABELS.get(row["kind"], "kind unknown"),
        )
    return '<a class="%s" data-id="%s" href="/s/%s/"><title>%s</title>%s%s</a>' % (
        " ".join(classes),
        _esc(row["id"]),
        _esc(row["id"]),
        _esc(title),
        bar,
        label,
    )


def _svg(graph):
    rows = "".join(_row_svg(row) for row in graph["roots"] + graph["bars"])
    return (
        '<svg class="timeline-svg" xmlns="http://www.w3.org/2000/svg" '
        'width="%d" height="%d" viewBox="0 0 %d %d">'
        "<title>Strain timeline: undated cards in the strip at the start, then one "
        "bar per dated card from its earliest to its latest year.</title>"
        "%s%s%s</svg>"
        % (
            graph["width"],
            graph["height"],
            graph["width"],
            graph["height"],
            _axis_svg(graph),
            _groups_svg(graph),
            rows,
        )
    )


def legend(graph):
    items = [
        '<li class="timeline-key__item"><span class="timeline-key__swatch '
        'timeline-key__swatch--%s"></span>%s</li>'
        % (_esc(kind), _esc(KIND_LABELS.get(kind, kind)))
        for kind in graph["kinds"]
    ]
    if not items:
        return ""
    return '<ul class="timeline-key">%s</ul>' % "".join(items)


def counts(graph):
    """The status line the page ships, and the text the filter restores."""
    dated = len(graph["bars"])
    undated = len(graph["roots"])
    if not dated and not undated:
        return "No cards yet."
    return "%d %s: %d dated, %d undated." % (
        dated + undated,
        "card" if dated + undated == 1 else "cards",
        dated,
        undated,
    )


def render(graph):
    """The contents of ``#timeline``: the scroller, the SVG, the legend.

    tabindex keeps the scroller reachable from the keyboard on a narrow screen,
    where the axis is wider than the page.
    """
    if not graph["bars"] and not graph["roots"]:
        return '<p class="empty">No cards yet. The timeline fills in as cards land.</p>'
    return (
        '<div class="timeline__scroll" tabindex="0" role="group" '
        'aria-label="Strain timeline">%s</div>%s' % (_svg(graph), legend(graph))
    )


# -- the runtime payload ---------------------------------------------------

# What the picker needs to search a name or alias, and nothing more.
PICKER_FIELDS = ("id", "name", "aliases", "kind", "traditional_label", "status")


def payload(strains, edges, with_disputed=False):
    """The inline JSON the page ships: every family, plus the picker's index.

    It rides along in the page rather than being fetched so that a shared
    ``?family=`` URL renders filtered, without a round trip that would show the
    whole timeline first. The values are the compiled dataset's, not the
    catalog's: the runtime still never reads ``catalog/``.
    """
    cards = [
        card for card in strains or [] if isinstance(card, dict) and card.get("id")
    ]
    return {
        "families": families(cards, edges, with_disputed),
        "strains": [
            {key: card[key] for key in PICKER_FIELDS if key in card} for card in cards
        ],
    }
