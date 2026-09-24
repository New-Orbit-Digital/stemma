#!/usr/bin/env python3
"""The lineage graph: a layered layout and hand-rolled SVG for one strain page.

Stdlib only, no rendering library, and no new data fields: the graph is built
from the ``edges`` of the compiled dataset (the Budlogs seam) plus the card
name, born display and status already in ``strains``.

The layout is precomputed at build time rather than in the browser, so the
markup that ships is the markup that renders. ``layout()`` is the pure function
the tests exercise; ``render()`` turns its result into SVG.

Shape of the layout:

* **Rank.** Ancestors are ranked by the *longest* path from the current strain,
  so an ancestor reached twice (a backcross) is drawn once, on the deepest row
  it belongs to, and every edge points from a lower row to a higher one.
  Ancestors stop at ``MAX_GENERATIONS``. Direct children sit one row below the
  current strain; roots end up on top.
* **Order.** Rows are seeded in breadth-first discovery order, then swept with
  a barycenter heuristic to reduce crossings. Ties keep the previous order, so
  the output is deterministic.
* **Disputed.** Disputed edges, and any node only reachable through one, are
  emitted into a group that CSS hides until the "show disputed" toggle is on.
  They are laid out either way, so toggling never moves the rest of the graph.
"""

import html

MAX_GENERATIONS = 6

# Geometry, in SVG user units (1 unit = 1 CSS px at the rendered size).
NODE_W = 152
NODE_H = 46  # >= 40px tap target
COL_GAP = 20
ROW_GAP = 46
PAD = 12
ROW_STEP = NODE_H + ROW_GAP
SWEEPS = 4

# Roughly how many characters fit on a line at each font size.
NAME_CHARS = 19
META_CHARS = 23

TIER_STYLES = [
    ("genetically-tested", "genetically tested", "solid"),
    ("documented", "documented", "solid"),
    ("breeder-claimed", "breeder claimed", "dashed"),
    ("folklore", "folklore", "dotted"),
]
TIER_ORDER = [tier for tier, _label, _style in TIER_STYLES]


# -- layout ----------------------------------------------------------------


def _parents_by_child(edges, with_disputed):
    out = {}
    for edge in edges:
        if edge.get("disputed") and not with_disputed:
            continue
        out.setdefault(edge["child"], []).append(edge)
    return out


def _ancestor_depths(root, parents_by_child, max_generations):
    """Longest-path depth for every ancestor within ``max_generations``.

    Relaxation rather than a single pass: a node found at depth 2 by one route
    and depth 4 by another settles at 4, and its own ancestors are pushed down
    with it. Depths only ever increase and are capped, so this terminates; the
    catalog is acyclic, and ``root`` is never re-entered in any case.
    """
    depth = {root: 0}
    frontier = [root]
    truncated = False
    while frontier:
        nxt = []
        for node in frontier:
            below = depth[node] + 1
            for edge in parents_by_child.get(node, ()):
                parent = edge["parent"]
                if parent == root:
                    continue
                if below > max_generations:
                    truncated = True
                    continue
                if depth.get(parent, -1) < below:
                    depth[parent] = below
                    nxt.append(parent)
        frontier = nxt
    del depth[root]
    return depth, truncated


def _child_ids(root, edges, with_disputed):
    out = []
    for edge in edges:
        if edge["parent"] != root:
            continue
        if edge.get("disputed") and not with_disputed:
            continue
        if edge["child"] != root and edge["child"] not in out:
            out.append(edge["child"])
    return out


def _reachable(root, edges, max_generations):
    """The node ids the graph would hold if disputed edges did not exist."""
    depth, _truncated = _ancestor_depths(
        root, _parents_by_child(edges, False), max_generations
    )
    seen = set(depth)
    seen.add(root)
    seen.update(_child_ids(root, edges, False))
    return seen


def _discovery_order(root, parents_by_child, children, nodes):
    """Breadth-first seed order: stable, and it clusters relatives together."""
    order = {root: 0}
    queue = [root]
    while queue:
        node = queue.pop(0)
        for edge in parents_by_child.get(node, ()):
            parent = edge["parent"]
            if parent in nodes and parent not in order:
                order[parent] = len(order)
                queue.append(parent)
    for child in children:
        if child not in order:
            order[child] = len(order)
    return order


def _sweep(rows, adjacency, downward):
    """One barycenter pass. Rows with no neighbours above/below hold still."""
    span = range(1, len(rows)) if downward else range(len(rows) - 2, -1, -1)
    for index in span:
        reference = rows[index - 1] if downward else rows[index + 1]
        at = {node: slot for slot, node in enumerate(reference)}
        keyed = []
        for slot, node in enumerate(rows[index]):
            neighbours = [at[other] for other in adjacency.get(node, ()) if other in at]
            bary = sum(neighbours) / float(len(neighbours)) if neighbours else float(slot)
            keyed.append((bary, slot, node))
        keyed.sort()
        rows[index] = [node for _bary, _slot, node in keyed]


def _meta_line(card):
    if not card:
        return ""
    if card.get("status") == "stub":
        return "not yet cataloged"
    born = card.get("born") or {}
    return born.get("display") or "born unknown"


def layout(strain_id, edges, cards=None, max_generations=MAX_GENERATIONS):
    """Lay out ``strain_id``'s ancestors and direct children.

    ``edges`` is the dataset's edge list; ``cards`` maps id to the card, for the
    name, born display and stub status. Returns a dict of ``nodes``, ``edges``,
    the canvas ``width``/``height``, ``rows``, whether any ancestors were
    ``truncated`` by the generation cap, and whether anything is ``disputed``.
    """
    cards = cards or {}
    edges = list(edges or [])

    parents_by_child = _parents_by_child(edges, True)
    depths, truncated = _ancestor_depths(strain_id, parents_by_child, max_generations)
    children = _child_ids(strain_id, edges, True)

    depth_of = dict(depths)
    depth_of[strain_id] = 0
    for child in children:
        depth_of.setdefault(child, -1)
    plain = _reachable(strain_id, edges, max_generations)

    drawn = []
    for edge in edges:
        child, parent = edge["child"], edge["parent"]
        if child not in depth_of or parent not in depth_of:
            continue
        # A layered diagram can only draw an edge that climbs a row: one
        # between two children, or one the generation cap has flattened, is
        # left to the Parents and Children lists rather than drawn sideways.
        if depth_of[parent] <= depth_of[child]:
            continue
        disputed = bool(edge.get("disputed"))
        drawn.append(
            {
                "child": child,
                "parent": parent,
                "best_tier": edge.get("best_tier"),
                "disputed": disputed,
                "hidden": disputed or child not in plain or parent not in plain,
            }
        )

    adjacency = {}
    for edge in drawn:
        adjacency.setdefault(edge["child"], set()).add(edge["parent"])
        adjacency.setdefault(edge["parent"], set()).add(edge["child"])

    ranks = sorted(set(depth_of.values()), reverse=True)
    row_of = {depth: index for index, depth in enumerate(ranks)}
    seed = _discovery_order(strain_id, parents_by_child, children, set(depth_of))
    rows = [[] for _ in ranks]
    for node in sorted(depth_of, key=lambda node: (seed.get(node, len(seed)), node)):
        rows[row_of[depth_of[node]]].append(node)

    for index in range(SWEEPS):
        _sweep(rows, adjacency, downward=index % 2 == 0)

    widths = [len(row) * NODE_W + max(len(row) - 1, 0) * COL_GAP for row in rows]
    canvas = max(widths) if widths else NODE_W
    placed = {}
    nodes = []
    for row_index, row in enumerate(rows):
        left = PAD + (canvas - widths[row_index]) // 2
        for column, node in enumerate(row):
            card = cards.get(node) or {}
            x = left + column * (NODE_W + COL_GAP)
            y = PAD + row_index * ROW_STEP
            placed[node] = (x, y)
            nodes.append(
                {
                    "id": node,
                    "name": card.get("name") or node,
                    "meta": _meta_line(card),
                    "depth": depth_of[node],
                    "row": row_index,
                    "column": column,
                    "x": x,
                    "y": y,
                    "current": node == strain_id,
                    "stub": card.get("status") == "stub",
                    "hidden": node not in plain,
                }
            )

    for edge in drawn:
        edge["from"] = placed[edge["parent"]]
        edge["to"] = placed[edge["child"]]
    drawn.sort(key=lambda edge: (edge["hidden"], edge["parent"], edge["child"]))

    return {
        "id": strain_id,
        "nodes": nodes,
        "edges": drawn,
        "rows": len(rows),
        "width": canvas + 2 * PAD,
        "height": len(rows) * NODE_H + max(len(rows) - 1, 0) * ROW_GAP + 2 * PAD,
        "truncated": truncated,
        "disputed": any(edge["disputed"] for edge in drawn),
        "max_generations": max_generations,
    }


# -- rendering -------------------------------------------------------------


def _esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def _clip(text, limit):
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _path(edge):
    px, py = edge["from"]
    cx, cy = edge["to"]
    x1 = px + NODE_W // 2
    y1 = py + NODE_H
    x2 = cx + NODE_W // 2
    y2 = cy
    bend = max(16, (y2 - y1) // 2)
    return "M%d %d C%d %d %d %d %d %d" % (x1, y1, x1, y1 + bend, x2, y2 - bend, x2, y2)


def _edge_svg(edge):
    classes = ["lineage-edge", "lineage-edge--%s" % (edge["best_tier"] or "folklore")]
    if edge["disputed"]:
        classes.append("lineage-edge--disputed")
    return '<path class="%s" d="%s"></path>' % (" ".join(classes), _path(edge))


def _node_svg(node):
    classes = ["lineage-node"]
    if node["current"]:
        classes.append("lineage-node--current")
    if node["stub"]:
        classes.append("lineage-node--stub")
    middle = node["x"] + NODE_W // 2
    body = (
        '<rect class="lineage-node__box" x="%d" y="%d" width="%d" height="%d" rx="9"></rect>'
        '<text class="lineage-node__name" x="%d" y="%d" text-anchor="middle">%s</text>'
        % (
            node["x"],
            node["y"],
            NODE_W,
            NODE_H,
            middle,
            node["y"] + 20,
            _esc(_clip(node["name"], NAME_CHARS)),
        )
    )
    if node["meta"]:
        body += '<text class="lineage-node__meta" x="%d" y="%d" text-anchor="middle">%s</text>' % (
            middle,
            node["y"] + 36,
            _esc(_clip(node["meta"], META_CHARS)),
        )
    attrs = ' class="%s"' % " ".join(classes)
    if node["current"]:
        return "<g%s>%s</g>" % (attrs, body)
    return '<a%s href="/s/%s/">%s</a>' % (attrs, _esc(node["id"]), body)


def _group(class_name, parts):
    if not parts:
        return ""
    return '<g class="%s">%s</g>' % (class_name, "".join(parts))


def _svg(graph, name):
    edges = graph["edges"]
    nodes = graph["nodes"]
    return (
        '<svg class="lineage-svg" xmlns="http://www.w3.org/2000/svg" '
        'width="%d" height="%d" viewBox="0 0 %d %d">'
        "<title>Lineage graph for %s: ancestors above, children below.</title>"
        "%s%s%s%s</svg>"
        % (
            graph["width"],
            graph["height"],
            graph["width"],
            graph["height"],
            _esc(name),
            _group("lineage-layer", [_edge_svg(e) for e in edges if not e["hidden"]]),
            _group(
                "lineage-layer lineage-layer--disputed",
                [_edge_svg(e) for e in edges if e["hidden"]],
            ),
            _group("lineage-layer", [_node_svg(n) for n in nodes if not n["hidden"]]),
            _group(
                "lineage-layer lineage-layer--disputed",
                [_node_svg(n) for n in nodes if n["hidden"]],
            ),
        )
    )


def _legend(graph):
    tiers = {edge["best_tier"] for edge in graph["edges"] if not edge["hidden"]}
    items = [
        '<li class="lineage-key__item"><span class="lineage-key__line '
        'lineage-key__line--%s"></span>%s</li>' % (style, _esc(label))
        for tier, label, style in TIER_STYLES
        if tier in tiers
    ]
    if graph["disputed"]:
        items.append(
            '<li class="lineage-key__item"><span class="lineage-key__line '
            'lineage-key__line--disputed"></span>disputed claim</li>'
        )
    if not items:
        return ""
    return '<ul class="lineage-key">%s</ul>' % "".join(items)


def render(graph, name=None):
    """The contents of ``#lineage-graph``: toggle, scroller, SVG, legend.

    The "show disputed" toggle is a checkbox the stylesheet reads, so nothing
    here depends on JavaScript and no script patches styles at runtime.
    """
    name = name or graph["id"]
    if len(graph["nodes"]) < 2:
        return '<p class="empty">No lineage links in the catalog yet.</p>'

    head = ""
    if graph["disputed"]:
        head = (
            '<input class="lineage-graph__toggle visually-hidden" type="checkbox" '
            'id="lineage-disputed">'
            '<p class="lineage-graph__bar"><label class="lineage-graph__switch" '
            'for="lineage-disputed">Show disputed links</label></p>'
        )
    note = ""
    if graph["truncated"]:
        note = (
            '<p class="lineage-graph__note">Ancestors are shown %d generations back. '
            "Older ones are on their own pages.</p>" % graph["max_generations"]
        )
    # tabindex keeps the scroller reachable from the keyboard on a narrow
    # screen, where the diagram is wider than the page.
    return (
        '%s<div class="lineage-graph__scroll" tabindex="0" role="group" '
        'aria-label="Lineage diagram for %s">%s</div>%s%s'
    ) % (
        head,
        _esc(name),
        _svg(graph, name),
        _legend(graph),
        note,
    )


def graph_html(strain_id, edges, cards=None, max_generations=MAX_GENERATIONS):
    """Layout plus render, the one call tools/build.py makes."""
    cards = cards or {}
    graph = layout(strain_id, edges, cards, max_generations)
    card = cards.get(strain_id) or {}
    return render(graph, card.get("name") or strain_id)
