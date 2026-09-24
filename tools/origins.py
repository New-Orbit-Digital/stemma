#!/usr/bin/env python3
"""The origin and migration map: markers at region centroids, arcs along lineage.

Stdlib only, no new data fields: markers come from ``origin.lat``/``origin.lon``
on the compiled dataset's ``strains``, and arcs come from its ``edges``. The
family filter is the ancestor walk in ``tools/lineage.py``, called rather than
copied, so the map, the timeline and the diagram all mean the same thing by
"family".

A slippy map draws itself in the browser, so unlike the timeline this module
does not emit the plotted geometry as markup. What it does is compute every
value the page needs — the marker groups, the arc polylines, the unknown list —
at build time, as pure functions the tests exercise, and ship them inline with
the page. The runtime only hands them to Leaflet.

Shape of the page:

* **Markers.** One marker per centroid, not per card: cards that share a
  rounded centroid group into a single marker whose popup lists them. Grouping
  is hand-rolled, so the page needs no clustering plugin.
* **Arcs.** One curved polyline per lineage edge whose *both* endpoints are
  located, sampled here as a quadratic Bézier so the browser only draws points.
  An arc is the link between a parent's origin and its child's, not the route
  anyone travelled, so it is interpolated straight across the projection and
  never wrapped around the dateline.
* **Unknown origins.** Cards with ``origin.unknown``, with no coordinates, or
  with no ``origin`` at all (a stub) cannot be placed, so they are listed under
  the map instead of being dropped.
* **Filter.** ``?family=<id>`` keeps a strain and all of its ancestors, exactly
  as the timeline does.
"""

import html
import math

import lineage

# Curve geometry, in degrees on the lat/lon plane the map projects.
ARC_STEPS = 24  # sampled points per arc = ARC_STEPS + 1
ARC_BULGE = 0.18  # sideways offset as a fraction of the chord
MAX_BULGE = 18.0  # a long chord still bends gently, not out of the world
COORD_PLACES = 3  # rounding for the sampled points, to keep the payload small
LAT_LIMIT = 85.0  # Web Mercator stops here

# Cards are grouped on the centroid the schema records: 1 decimal place.
CENTROID_PLACES = 1

UNKNOWN_LABEL = "Origin unknown"


# -- cards -----------------------------------------------------------------


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def coordinates(card):
    """The card's centroid as ``(lat, lon)``, or ``None`` when it has none.

    ``origin.unknown`` is the schema's other shape, a stub has no ``origin`` at
    all, and a card whose coordinates were never filled in is just as unplaceable
    as either; all three land in the unknown list.
    """
    origin = (card or {}).get("origin") or {}
    if origin.get("unknown") is True:
        return None
    lat, lon = origin.get("lat"), origin.get("lon")
    if not (_is_number(lat) and _is_number(lon)):
        return None
    if not (-90.0 <= float(lat) <= 90.0 and -180.0 <= float(lon) <= 180.0):
        return None
    return round(float(lat), CENTROID_PLACES), round(float(lon), CENTROID_PLACES)


def is_located(card):
    """True when the card has a centroid to plot."""
    return coordinates(card) is not None


def _name(card):
    return card.get("name") or card["id"]


def _place(card):
    origin = card.get("origin") or {}
    return origin.get("place") or ""


def _cards(strains):
    return [card for card in strains or [] if isinstance(card, dict) and card.get("id")]


def _member(card):
    return {
        "id": card["id"],
        "name": _name(card),
        "kind": card.get("kind") or "",
        "place": _place(card),
    }


def located(strains):
    """Every card that can be placed, sorted by name then id."""
    cards = [card for card in _cards(strains) if is_located(card)]
    return sorted(cards, key=lambda card: (_name(card), card["id"]))


def unknown(strains):
    """Every card that cannot be placed: the "Origin unknown" list."""
    cards = [card for card in _cards(strains) if not is_located(card)]
    return sorted(cards, key=lambda card: (_name(card), card["id"]))


# -- markers ---------------------------------------------------------------


def centroid_key(lat, lon):
    """The key two cards must share to become one marker."""
    return "%.1f,%.1f" % (round(lat, CENTROID_PLACES), round(lon, CENTROID_PLACES))


def groups(strains):
    """Marker groups: cards that share a centroid collapse into one marker.

    Hand-rolled rather than clustered by a plugin, and by exact centroid rather
    than by screen distance, so the grouping is the same at every zoom level and
    is decided here, at build time. Groups are sorted north to south, then west
    to east, so the order is stable and reads top-left to bottom-right.
    """
    by_key = {}
    for card in located(strains):
        lat, lon = coordinates(card)
        key = centroid_key(lat, lon)
        group = by_key.get(key)
        if group is None:
            group = {"key": key, "lat": lat, "lon": lon, "members": []}
            by_key[key] = group
        group["members"].append(_member(card))
    out = sorted(by_key.values(), key=lambda g: (-g["lat"], g["lon"], g["key"]))
    for group in out:
        # One shared place name reads better in the popup than a repeated one;
        # a genuinely shared centroid with two wordings falls back to a count.
        places = {member["place"] for member in group["members"] if member["place"]}
        if len(places) == 1:
            group["place"] = places.pop()
        elif len(group["members"]) == 1:
            group["place"] = group["members"][0]["place"]
        else:
            group["place"] = "%d strains at one centroid" % len(group["members"])
    return out


# -- arcs ------------------------------------------------------------------


def curve(start, end, steps=ARC_STEPS):
    """A quadratic Bézier from ``start`` to ``end``, sampled into lat/lon points.

    The control point sits beside the midpoint, square to the chord, so every
    arc bends the same way and two arcs between the same pair never overlap
    their whole length. The offset grows with the chord but is capped, so a
    Kabul-to-California line still bends gently instead of leaving the world.
    """
    lat1, lon1 = float(start[0]), float(start[1])
    lat2, lon2 = float(end[0]), float(end[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    length = math.hypot(dlat, dlon)
    if length == 0:
        return [[round(lat1, COORD_PLACES), round(lon1, COORD_PLACES)]] * 2
    offset = min(ARC_BULGE * length, MAX_BULGE)
    control = (
        (lat1 + lat2) / 2.0 + offset * (dlon / length),
        (lon1 + lon2) / 2.0 - offset * (dlat / length),
    )
    points = []
    for step in range(steps + 1):
        t = step / float(steps)
        inv = 1.0 - t
        lat = inv * inv * lat1 + 2 * inv * t * control[0] + t * t * lat2
        lon = inv * inv * lon1 + 2 * inv * t * control[1] + t * t * lon2
        points.append(
            [
                round(max(-LAT_LIMIT, min(LAT_LIMIT, lat)), COORD_PLACES),
                round(lon, COORD_PLACES),
            ]
        )
    return points


def arcs(strains, edges):
    """One arc per lineage edge whose parent and child are both located.

    An edge to or from a card with no centroid has nothing to draw between, so
    it is left to the card's own page; the "Origin unknown" list under the map
    is where those cards stay visible.
    """
    points = {
        card["id"]: coordinates(card)
        for card in _cards(strains)
        if is_located(card)
    }
    out = []
    for edge in edges or []:
        child, parent = edge.get("child"), edge.get("parent")
        if child not in points or parent not in points:
            continue
        out.append(
            {
                "child": child,
                "parent": parent,
                "from": list(points[parent]),
                "to": list(points[child]),
                "points": curve(points[parent], points[child]),
            }
        )
    out.sort(key=lambda arc: (arc["child"], arc["parent"]))
    return out


def family(strain_id, edges):
    """The ids ``?family=<strain_id>`` keeps: the strain and all its ancestors.

    Delegated to ``lineage.family`` rather than walked again here, so the map
    and the timeline can never drift apart on what a family is.
    """
    return lineage.family(strain_id, edges)


def families(strains, edges):
    """Every card's family, the lookup the runtime filter reads."""
    return {card["id"]: family(card["id"], edges) for card in _cards(strains)}


def family_arcs(strain_id, strains, edges):
    """The arcs ``?family=<strain_id>`` leaves on the map.

    Exactly the ancestor edges with both endpoints located: the filter is a set
    intersection against ``family()``, which is the same intersection the page
    does at runtime, so what the browser draws is what this returns.
    """
    keep = set(family(strain_id, edges))
    return [
        arc
        for arc in arcs(strains, edges)
        if arc["child"] in keep and arc["parent"] in keep
    ]


def family_groups(strain_id, strains, edges):
    """The marker groups ``?family=<strain_id>`` leaves, members filtered."""
    keep = set(family(strain_id, edges))
    out = []
    for group in groups(strains):
        members = [member for member in group["members"] if member["id"] in keep]
        if members:
            kept = dict(group)
            kept["members"] = members
            out.append(kept)
    return out


# -- rendering -------------------------------------------------------------


def _esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def _strain_href(strain_id):
    return "/s/%s/" % strain_id


def _member_row(member):
    meta = member["kind"]
    return (
        '<li class="map-place__strain" data-id="%s"><a href="%s">%s</a>%s</li>'
        % (
            _esc(member["id"]),
            _esc(_strain_href(member["id"])),
            _esc(member["name"]),
            (
                '<span class="result__meta">%s</span>' % _esc(meta)
                if meta
                else ""
            ),
        )
    )


def places_html(marker_groups):
    """The text of the map: every marker group, as a list the page ships.

    The markers themselves are drawn by the browser, so without this a crawler
    — or a reader with JavaScript off — would see an empty box. The rows carry
    ``data-id``, which is all the family filter needs to hide them.
    """
    if not marker_groups:
        return '<p class="empty">No card has an origin we can place yet.</p>'
    rows = []
    for group in marker_groups:
        rows.append(
            '<li class="map-place" data-group="%s"><h3 class="map-place__name">%s</h3>'
            '<ul class="map-place__strains">%s</ul></li>'
            % (
                _esc(group["key"]),
                _esc(group["place"] or group["key"]),
                "".join(_member_row(member) for member in group["members"]),
            )
        )
    return '<ul class="map-places">%s</ul>' % "".join(rows)


def unknown_html(cards):
    """The "Origin unknown" list: the cards the map cannot place."""
    heading = (
        '<h2 id="map-unknown-heading">%s</h2>' % _esc(UNKNOWN_LABEL)
    )
    if not cards:
        body = '<p class="empty">Every card in the catalog has an origin on the map.</p>'
    else:
        rows = "".join(
            '<li data-id="%s"><a href="%s"><strong>%s</strong>%s</a></li>'
            % (
                _esc(card["id"]),
                _esc(_strain_href(card["id"])),
                _esc(_name(card)),
                (
                    '<span class="result__meta">%s</span>'
                    % _esc(
                        "not yet cataloged"
                        if card.get("status") == "stub"
                        else "origin not established"
                    )
                ),
            )
            for card in cards
        )
        body = (
            "<p>No source places these cards, so they are listed here rather than "
            'guessed at on the map.</p><ul class="card-list" id="map-unknown-list">%s</ul>'
            % rows
        )
    return (
        '<section class="map-unknown" aria-labelledby="map-unknown-heading">%s%s</section>'
        % (heading, body)
    )


def counts(marker_groups, arc_list, unknown_cards):
    """The status line the page ships, and the text the filter restores."""
    placed = sum(len(group["members"]) for group in marker_groups)
    if not placed and not unknown_cards:
        return "No cards yet."
    parts = [
        "%d %s at %d %s"
        % (
            placed,
            "card" if placed == 1 else "cards",
            len(marker_groups),
            "place" if len(marker_groups) == 1 else "places",
        ),
        "%d %s" % (len(arc_list), "line" if len(arc_list) == 1 else "lines"),
    ]
    if unknown_cards:
        tail = "%d with an unknown origin." % len(unknown_cards)
    else:
        tail = "Every card has an origin."
    return "%s. %s" % (", ".join(parts), tail)


# -- the runtime payload ---------------------------------------------------

# What the picker needs to search a name or alias, and nothing more.
PICKER_FIELDS = ("id", "name", "aliases", "kind", "traditional_label", "status")


def payload(strains, edges):
    """The inline JSON the page ships: markers, arcs, families, picker index.

    It rides along in the page rather than being fetched so that a shared
    ``?family=`` URL renders filtered, without a round trip that would draw the
    whole map first. The values are the compiled dataset's, not the catalog's:
    the runtime still never reads ``catalog/``.
    """
    cards = _cards(strains)
    return {
        "groups": groups(cards),
        "arcs": arcs(cards, edges),
        "unknown": [card["id"] for card in unknown(cards)],
        "families": families(cards, edges),
        "strains": [
            {key: card[key] for key in PICKER_FIELDS if key in card} for card in cards
        ],
    }
