#!/usr/bin/env python3
"""Compile the catalog into a static site: dist/ plus dist/data/stemma.json.

Stdlib only. Validation runs first; any error aborts the build with exit 1.
The dataset is deterministic apart from ``generated``: strains are sorted by id
and edges by (child, parent). Pages are rendered from the plain HTML templates
in ``site/`` by substituting ``{{placeholder}}`` values, so the runtime only
ever reads ``data/stemma.json``.

Output layout under ``--out`` (the site root):

    index.html            search
    about/index.html      what the catalog is, source categories, labels
    browse/index.html     one list per dimension, with counts
    browse/<dim>/<v>/     one page per value at least one card has
    timeline/index.html   every dated card on a shared year axis
    map/index.html        every located card on a world map, with lineage arcs
    404.html
    s/<id>/index.html     one page per card, rendered at build time
    assets/               style.css, app.js
    data/stemma.json      the Budlogs seam
    _headers              Cloudflare Pages cache rules for assets/ (base / only)
    screenshot.png        copied from site/ when the file exists

Assets are referenced as ``<base>assets/<name>?v=<hash>``, where the hash is the
first ten hex characters of the file's sha256. The URL changes exactly when the
bytes change, so ``_headers`` can hand assets a one-year immutable cache
without a deploy ever pairing new HTML with stale CSS or JS.

``--base`` is where the site is mounted on its host. Cloudflare Pages serves it
at the root (``/``, the default); GitHub Pages serves it as a project site
under ``/stemma/``. Every internal URL the build emits goes through
``tools/urls.py``, so one tree compiles for either host and a root build spells
every URL exactly as it did before the flag existed.
"""

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import browse  # noqa: E402  (sibling module, resolved via the path insert)
import countries  # noqa: E402
import lineage  # noqa: E402
import links  # noqa: E402
import origins  # noqa: E402
import timeline  # noqa: E402
import urls  # noqa: E402
import validate  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

SCHEMA_VERSION = 2
DEFAULT_OUT = "dist"
DATASET_RELPATH = os.path.join("data", "stemma.json")

PLACEHOLDER_RE = re.compile(r"\{\{([a-z_]+)\}\}")

KIND_LABELS = timeline.KIND_LABELS  # one wording, shared with the timeline legend
LABEL_HINT_PATH = "/about/#traditional-labels"

# The one pre-approved front-end library, pinned to an exact version on cdnjs.
# The subresource-integrity digests were verified against the fetched files and
# the cdnjs API on 2026-09-24. Leaflet is pinned by version, not by our ?v=, so
# these URLs stay exactly as cdnjs publishes them.
LEAFLET_VERSION = "1.9.4"
LEAFLET_BASE = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/%s" % LEAFLET_VERSION
LEAFLET_SRI = {
    "leaflet.min.css": (
        "sha512-h9FcoyWjHcOcmEVkxOfTLnmZFWIH0iZhZT1H2TbOq55xssQGEJHEaIm+"
        "PgoUaZbRvQTNTluNOEfb1ZRy6D3BOw=="
    ),
    "leaflet.min.js": (
        "sha512-puJW3E/qXDqYp9IfhAI54BJEaWIfloJ7JWs7OeD5i6ruC9JZL1gERT1wjtwXFlh7"
        "CjE7ZJ+/vcRZRkIYIb6p4g=="
    ),
}
LEAFLET_HEAD = (
    '<link rel="stylesheet" href="%s/leaflet.min.css" integrity="%s" '
    'crossorigin="anonymous" referrerpolicy="no-referrer">\n'
    '<script src="%s/leaflet.min.js" integrity="%s" crossorigin="anonymous" '
    'referrerpolicy="no-referrer"></script>\n'
    % (
        LEAFLET_BASE,
        LEAFLET_SRI["leaflet.min.css"],
        LEAFLET_BASE,
        LEAFLET_SRI["leaflet.min.js"],
    )
)

# Cloudflare Pages reads this from the site root. Only /assets/* gets a rule:
# every reference to those files is versioned, so a year-long immutable cache
# is safe. HTML and data keep the Pages default, which revalidates.
HEADERS_RELPATH = "_headers"
HEADERS_TEXT = "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n"

ASSET_HASH_LEN = 10  # first 10 hex of sha256 — short enough to read in a URL

# Copied verbatim when it exists. The planner adds the image; the build only
# carries it, so a missing file is not an error.
SCREENSHOT = "screenshot.png"


def label_hint():
    """The "what this means" link beside a traditional label."""
    return '<a class="chip__hint" href="%s">what this means</a>' % esc(
        urls.url(LABEL_HINT_PATH)
    )


# -- dataset ---------------------------------------------------------------


def build_edges(cards):
    """One edge per (child, parent) pair, sorted, with duplicates collapsed.

    A card that lists the same parent twice — a backcross written out long —
    still draws one line, so the edge list is a set rather than a transcript.
    """
    pairs = set()
    for card in cards:
        for parent in card.data.get("parents") or []:
            if card.id and isinstance(parent, str) and parent:
                pairs.add((card.id, parent))
    return [{"child": child, "parent": parent} for child, parent in sorted(pairs)]


# -- templating ------------------------------------------------------------


def read_template(name):
    with open(os.path.join(SITE, name), "r", encoding="utf-8") as handle:
        return handle.read()


def render(template, values):
    """Substitute ``{{name}}`` once, left to right. Unknown names are an error."""

    def replace(match):
        key = match.group(1)
        if key not in values:
            raise KeyError("template placeholder '%s' has no value" % key)
        return values[key]

    return PLACEHOLDER_RE.sub(replace, template)


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def asset_hash(path):
    """The first ``ASSET_HASH_LEN`` hex characters of the file's sha256.

    Content-addressed on purpose: the same bytes always give the same hash, so
    a rebuild of an unchanged file emits a byte-identical page.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()[:ASSET_HASH_LEN]


def asset_hrefs(assets_src):
    """``{name: "<base>assets/<name>?v=<hash>"}`` for every file the build copies."""
    hrefs = {}
    for name in sorted(os.listdir(assets_src)):
        path = os.path.join(assets_src, name)
        if os.path.isfile(path):
            hrefs[name] = urls.url("/assets/%s?v=%s" % (name, asset_hash(path)))
    return hrefs


def asset_values(hrefs):
    """The two asset placeholders the page shell in base.html spends."""
    return {"css_href": hrefs["style.css"], "js_href": hrefs["app.js"]}


def write_page(out, relpath, text):
    path = os.path.join(out, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


# -- page fragments --------------------------------------------------------


def strain_href(strain_id):
    return urls.strain(strain_id)


def fact(term, value_html):
    return "<div><dt>%s</dt><dd>%s</dd></div>" % (esc(term), value_html)


def browse_link(dimension, value, text):
    """A field value as a link to its browse page.

    Every value a card carries has a page, because the browse pages are built
    from the cards, so a field link cannot point at nothing.
    """
    return '<a href="%s">%s</a>' % (esc(browse.value_href(dimension, value)), esc(text))


def facts_block(data):
    rows = []

    born = data.get("born") or {}
    if born:
        display = esc(born.get("display") or "Unknown")
        if born.get("unknown") is not True and born.get("year_min") is not None:
            display = "%s <span class=\"result__meta\">%s&ndash;%s</span>" % (
                display,
                esc(born.get("year_min")),
                esc(born.get("year_max")),
            )
        rows.append(fact("Born", display))

    origin = data.get("origin") or {}
    if origin:
        if origin.get("unknown") is True:
            rows.append(fact("Origin", "Unknown"))
        else:
            place = origin.get("place") or "Unknown"
            code = countries.code(origin.get("country"))
            rows.append(
                fact(
                    "Origin",
                    browse_link("country", code, place) if code else esc(place),
                )
            )

    if "breeder" in data:
        breeder = data.get("breeder")
        rows.append(
            fact(
                "Breeder",
                browse_link("breeder", breeder, breeder) if breeder else "Not recorded",
            )
        )

    if not rows:
        return ""
    return '<dl class="facts">%s</dl>' % "".join(rows)


def chemotype_block(data):
    """One plain-text line: the cannabinoid ranges, then the dominant terpenes.

    Deliberately prose. Badges and charts belong to the parked visual-design
    pass; until then a card says its chemotype the way it says everything else.
    Each range prints its ``display`` string, which is what the card wrote for
    a reader — the numbers underneath are for the dataset.
    """
    chemotype = data.get("chemotype")
    if not isinstance(chemotype, dict):
        return ""

    sentences = []
    ranges = []
    for field, label in (("thc", "THC"), ("cbd", "CBD")):
        value = chemotype.get(field)
        if isinstance(value, dict) and value.get("display"):
            ranges.append("%s %s" % (label, esc(value["display"])))
    if ranges:
        sentences.append("%s." % ", ".join(ranges))

    names = [
        esc(entry["name"])
        for entry in chemotype.get("dominant_terpenes") or []
        if isinstance(entry, dict) and entry.get("name")
    ]
    if names:
        sentences.append("Dominant terpenes: %s." % ", ".join(names))

    if not sentences:
        return ""
    return '<p class="chemotype">%s</p>' % " ".join(sentences)


def chips_block(data):
    items = []
    kind = data.get("kind")
    if kind:
        wording = KIND_LABELS.get(kind, kind)
        items.append(
            '<li class="chip">%s</li>'
            % (
                browse_link("kind", kind, wording)
                if kind in KIND_LABELS
                else esc(wording)
            )
        )
    label = data.get("traditional_label")
    if label:
        items.append(
            '<li class="chip">%s %s</li>'
            % (browse_link("label", label, label), label_hint())
        )
    status = data.get("status")
    if status:
        items.append('<li class="chip">%s</li>' % esc(status))
    if not items:
        return ""
    return '<ul class="chips">%s</ul>' % "".join(items)


def relation_item(strain_id, names, extra_html=""):
    name = names.get(strain_id, strain_id)
    return '<li><a href="%s">%s</a>%s</li>' % (
        esc(strain_href(strain_id)),
        esc(name),
        extra_html,
    )


def parents_block(data, names):
    out = ["<h3>Parents</h3>"]
    rows = [
        relation_item(parent, names)
        for parent in data.get("parents") or []
        if isinstance(parent, str) and parent
    ]
    if rows:
        out.append('<ul class="relations">%s</ul>' % "".join(rows))
    else:
        out.append('<p class="empty">No parents recorded.</p>')
    return "".join(out)


def children_block(strain_id, edges, names):
    rows = [
        relation_item(edge["child"], names)
        for edge in edges
        if edge["parent"] == strain_id
    ]
    out = ["<h3>Children</h3>"]
    if rows:
        out.append('<ul class="relations">%s</ul>' % "".join(rows))
    else:
        out.append('<p class="empty">No children in the catalog yet.</p>')
    return "".join(out)


def sources_block(data):
    """A quiet list at the foot of the card: title, publisher, category.

    Unnumbered on purpose. Nothing on the page points at a source any more, so
    a number would only imply a ranking the categories deliberately are not.
    """
    rows = []
    for source in data.get("sources") or []:
        if not isinstance(source, dict):
            continue
        title = esc(source.get("title"))
        url = source.get("url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            title = '<a href="%s" rel="nofollow noopener">%s</a>' % (esc(url), title)
        line = [title]
        if source.get("publisher"):
            line.append('<span class="publisher">%s</span>' % esc(source["publisher"]))
        if source.get("category"):
            line.append(
                '<span class="sources__category">%s</span>' % esc(source["category"])
            )
        rows.append("<li>%s</li>" % " &middot; ".join(line))
    if not rows:
        return ""
    return (
        '<section aria-labelledby="sources-heading">'
        '<h2 id="sources-heading">Sources</h2>'
        '<ul class="sources">%s</ul></section>' % "".join(rows)
    )


def inline_json_block(element_id, payload):
    """Build-time data the page carries, so it needs no fetch on first render."""
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    safe = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return '<script id="%s" type="application/json">%s</script>' % (element_id, safe)


def inline_data_block(data, children):
    """The card data, inlined so the page needs no fetch on first render."""
    return inline_json_block("strain-data", {"strain": data, "children": children})


# -- pages -----------------------------------------------------------------


def page(shell, assets, title, description, page_class, content, inline_data="", head=""):
    """One page. ``head`` is the seam a page uses to pin its own library.

    ``shell`` is base.html; ``assets`` carries the versioned ``css_href`` and
    ``js_href`` it spends. ``content`` is substituted rather than rescanned, so
    a page template that uses ``{{base}}`` renders it before it gets here.
    """
    values = {
        "base": esc(urls.get_base()),
        "title": title,
        "description": description,
        "page_class": page_class,
        "content": content,
        "inline_data": inline_data,
        "head": head,
    }
    values.update(assets)
    return render(shell, values)


def render_content(template, values=None):
    """A page template rendered with the base every template may spend."""
    merged = {"base": esc(urls.get_base())}
    merged.update(values or {})
    return render(template, merged)


def strain_page(shell, assets, template, data, edges, names, cards=None):
    strain_id = data["id"]
    aliases = [alias for alias in data.get("aliases") or [] if alias]
    stub = data.get("status") == "stub"
    children = [edge for edge in edges if edge["parent"] == strain_id]

    values = {
        "id": esc(strain_id),
        "name": esc(data.get("name") or strain_id),
        "aliases": (
            '<p class="aliases">Also known as %s</p>' % esc(", ".join(aliases))
            if aliases
            else ""
        ),
        "chips": chips_block(data),
        "stub_notice": (
            '<p class="stub-notice">Not yet cataloged. This strain appears in another '
            "card's lineage, so it has a page, but we have not researched it yet.</p>"
            if stub
            else ""
        ),
        # The prose links inline: [[...]] becomes an anchor, everything escapes.
        "summary": (
            ""
            if stub or not data.get("summary")
            else "<p>%s</p>" % links.render(data["summary"], names)
        ),
        "facts": "" if stub else facts_block(data),
        "chemotype": "" if stub else chemotype_block(data),
        "parents": parents_block(data, names),
        "children": children_block(strain_id, edges, names),
        "lineage_graph": lineage.graph_html(strain_id, edges, cards or {strain_id: data}),
        "timeline_link": '<a href="%s?family=%s">See on timeline</a>'
        % (esc(urls.url("/timeline/")), esc(strain_id)),
        "map_link": '<a href="%s?family=%s">See on map</a>'
        % (esc(urls.url("/map/")), esc(strain_id)),
        "sources": "" if stub else sources_block(data),
        "updated": esc(data.get("updated")),
    }

    name = data.get("name") or strain_id
    if stub:
        description = "%s is in the Stemma catalog as a stub: lineage links only." % name
    else:
        # The visible text, so a meta description never shows link markup.
        description = (
            data.get("summary_plain")
            or links.plain(data.get("summary") or "", names)
            or ("%s lineage and history." % name)
        )
    return page(
        shell,
        assets,
        title="%s — Stemma" % name,
        description=description,
        page_class="page-strain",
        content=render_content(template, values),
        inline_data=inline_data_block(data, children),
    )


def index_page(shell, assets, template, strains):
    if strains:
        rows = "".join(
            "<li><a href=\"%s\"><strong>%s</strong>%s</a></li>"
            % (
                esc(strain_href(strain["id"])),
                esc(strain.get("name") or strain["id"]),
                (
                    '<span class="result__meta">%s</span>'
                    % esc(", ".join(a for a in strain.get("aliases") or [] if a))
                    if any(strain.get("aliases") or [])
                    else ""
                ),
            )
            for strain in strains
        )
        browse = '<ul class="card-list">%s</ul>' % rows
        heading = "All %d cards" % len(strains)
    else:
        browse = '<p class="empty">No cards yet. The first ones land with the next packet.</p>'
        heading = "The catalog"
    body = render_content(template, {"browse": browse, "browse_heading": esc(heading)})
    return page(
        shell,
        assets,
        title="Stemma — cannabis strain lineage",
        description="Search a cannabis strain name and see where it came from, who bred it, and which sources the catalog is reading.",
        page_class="page-search",
        content=body,
    )


def timeline_page(shell, assets, template, graph, payload):
    return page(
        shell,
        assets,
        title="Timeline — Stemma",
        description="Every dated strain in the Stemma catalog on one year axis, with landraces and undated cards in a strip at the start.",
        page_class="page-timeline",
        content=render_content(
            template,
            {"counts": esc(timeline.counts(graph)), "chart": timeline.render(graph)},
        ),
        inline_data=inline_json_block("timeline-data", payload),
    )


def map_page(shell, assets, template, marker_groups, arc_list, unknown_cards, payload):
    return page(
        shell,
        assets,
        title="Map — Stemma",
        description="Where every strain in the Stemma catalog emerged, at an approximate regional centre, with a line from each parent's origin to its child's.",
        page_class="page-map",
        content=render_content(
            template,
            {
                "counts": esc(origins.counts(marker_groups, arc_list, unknown_cards)),
                "places": origins.places_html(marker_groups),
                "unknown": origins.unknown_html(unknown_cards),
            },
        ),
        inline_data=inline_json_block("map-data", payload),
        head=LEAFLET_HEAD,
    )


def browse_pages(out, shell, assets, strains):
    """Write ``/browse/`` and one page per value. Returns ``(groups, written)``.

    The tree is replaced wholesale, exactly as ``s/`` is: a breeder page whose
    last card changed its breeder has no cards left, so it must stop existing
    rather than linger from the previous build.
    """
    found = browse.groups(strains)
    root = os.path.join(out, browse.ROOT)
    if os.path.isdir(root):
        shutil.rmtree(root)

    template = read_template("browse.html")
    written = 0
    for group in found:
        for entry in group["entries"]:
            label = browse.heading_text(entry, group["label"])
            write_page(
                out,
                os.path.join(*entry["relpath"]),
                page(
                    shell,
                    assets,
                    title="%s — Stemma" % esc(label),
                    description="Every card in the Stemma catalog under %s."
                    % esc(label),
                    page_class="page-browse",
                    content=render_content(
                        template,
                        {
                            "heading": browse.heading(entry, group["label"]),
                            "count": esc(browse.count_text(len(entry["members"]))),
                            "cards": browse.rows_html(entry["members"]),
                        },
                    ),
                ),
            )
            written += 1

    write_page(
        out,
        os.path.join(browse.ROOT, "index.html"),
        page(
            shell,
            assets,
            title="Browse — Stemma",
            description="Browse the Stemma catalog by breeder, kind, origin country, and traditional label.",
            page_class="page-browse page-browse-index",
            content=render_content(
                read_template("browse-index.html"),
                {"groups": browse.index_html(found)},
            ),
        ),
    )
    written += 1
    return found, written


def write_site(out, dataset):
    shell = read_template("base.html")
    assets_src = os.path.join(SITE, "assets")
    hrefs = asset_hrefs(assets_src)
    assets = asset_values(hrefs)
    strains = dataset["strains"]
    edges = dataset["edges"]
    cards = {strain["id"]: strain for strain in strains if strain.get("id")}
    names = {
        strain_id: strain.get("name") or strain_id for strain_id, strain in cards.items()
    }

    write_page(
        out,
        "index.html",
        index_page(shell, assets, read_template("index.html"), strains),
    )
    write_page(
        out,
        os.path.join("about", "index.html"),
        page(
            shell,
            assets,
            title="About — Stemma",
            description="What Stemma is, how sources are categorized, and why indica and sativa are only traditional labels.",
            page_class="page-about",
            content=render_content(read_template("about.html")),
        ),
    )
    chart = timeline.layout(strains, edges)
    path = write_page(
        out,
        os.path.join("timeline", "index.html"),
        timeline_page(
            shell,
            assets,
            read_template("timeline.html"),
            chart,
            timeline.payload(strains, edges),
        ),
    )
    # One bar per dated card, so the two counts are the page's own check.
    print(
        "wrote %s: %d bars, %d dated cards, %d in the roots strip, %d decades"
        % (
            path,
            len(chart["bars"]),
            sum(1 for strain in strains if timeline.is_dated(strain)),
            len(chart["roots"]),
            len(chart["decades"]),
        )
    )
    marker_groups = origins.groups(strains)
    arc_list = origins.arcs(strains, edges)
    unknown_cards = origins.unknown(strains)
    path = write_page(
        out,
        os.path.join("map", "index.html"),
        map_page(
            shell,
            assets,
            read_template("map.html"),
            marker_groups,
            arc_list,
            unknown_cards,
            origins.payload(strains, edges),
        ),
    )
    # Every card is either on the map or in the unknown list, so the three
    # counts are the page's own check.
    print(
        "wrote %s: %d markers, %d arcs, %d origin unknown (%d cards placed)"
        % (
            path,
            len(marker_groups),
            len(arc_list),
            len(unknown_cards),
            sum(len(group["members"]) for group in marker_groups),
        )
    )
    write_page(
        out,
        "404.html",
        page(
            shell,
            assets,
            title="Not found — Stemma",
            description="That page is not in the Stemma catalog.",
            page_class="page-404",
            content=render_content(read_template("404.html")),
        ),
    )

    # Stale pages from a previous build would outlive their cards, so the
    # generated strain tree is replaced wholesale.
    strain_root = os.path.join(out, "s")
    if os.path.isdir(strain_root):
        shutil.rmtree(strain_root)
    template = read_template("strain.html")
    for strain in strains:
        write_page(
            out,
            os.path.join("s", strain["id"], "index.html"),
            strain_page(shell, assets, template, strain, edges, names, cards),
        )

    found, browse_written = browse_pages(out, shell, assets, strains)
    # One page per value plus the index, so the two counts are the page's check.
    print(
        "wrote %s: %d pages (%s)"
        % (
            os.path.join(out, browse.ROOT),
            browse_written,
            ", ".join(
                "%d %s" % (len(group["entries"]), group["dimension"])
                for group in found
            )
            or "no dimensions",
        )
    )

    assets_out = os.path.join(out, "assets")
    os.makedirs(assets_out, exist_ok=True)
    for name in sorted(hrefs):
        shutil.copyfile(
            os.path.join(assets_src, name), os.path.join(assets_out, name)
        )

    # The planner drops the image in when there is one; the build only carries it.
    screenshot_src = os.path.join(SITE, SCREENSHOT)
    if os.path.isfile(screenshot_src):
        shutil.copyfile(screenshot_src, os.path.join(out, SCREENSHOT))
        print("wrote %s" % os.path.join(out, SCREENSHOT))

    # _headers is Cloudflare's, and it is written against the site root. Under a
    # base the rule would name the wrong path, and GitHub Pages ignores the file
    # either way, so the subpath build simply does not write one.
    if urls.is_root():
        path = write_page(out, HEADERS_RELPATH, HEADERS_TEXT)
        print("wrote %s: %s" % (path, ", ".join(hrefs[name] for name in sorted(hrefs))))
    else:
        print(
            "base %s: skipped %s (Cloudflare only); assets %s"
            % (
                urls.get_base(),
                HEADERS_RELPATH,
                ", ".join(hrefs[name] for name in sorted(hrefs)),
            )
        )

    # index, about, timeline, map, 404, one per card, plus the browse tree
    return 5 + len(strains) + browse_written


# -- driver ----------------------------------------------------------------


def build(path, out, base=urls.DEFAULT_BASE):
    # Set before anything renders: every module that emits an href reads it.
    site_base = urls.set_base(base)

    validator = validate.Validator(path)
    code = validator.run()
    if code:
        print("build aborted: validation reported %d errors" % validator.errors)
        return 1

    cards = sorted(
        (card for card in validator.cards if card.id is not None),
        key=lambda card: card.id,
    )

    # ``summary`` stays the raw text with its markup, because that is the source
    # of truth a card is edited as. ``summary_plain`` is the visible text, for
    # anything that cannot render a link: a meta description, a search result,
    # a Budlogs consumer. Additive, so the dataset is still schema_version 2.
    names = {card.id: (card.data.get("name") or card.id) for card in cards}
    for card in cards:
        summary = card.data.get("summary")
        if isinstance(summary, str) and summary:
            card.data["summary_plain"] = links.plain(summary, names)

    dataset = {
        "schema_version": SCHEMA_VERSION,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strains": [card.data for card in cards],
        "edges": build_edges(cards),
    }

    dataset_path = os.path.join(out, DATASET_RELPATH)
    os.makedirs(os.path.dirname(os.path.abspath(dataset_path)), exist_ok=True)
    with open(dataset_path, "w", encoding="utf-8") as handle:
        json.dump(dataset, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(
        "wrote %s: %d strains, %d edges"
        % (dataset_path, len(dataset["strains"]), len(dataset["edges"]))
    )

    pages = write_site(out, dataset)
    print("wrote %s: %d pages, base %s" % (out, pages, site_base))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--path",
        default=validate.DEFAULT_CATALOG,
        help="directory of strain cards (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help="output directory, the site root (default: %(default)s)",
    )
    parser.add_argument(
        "--base",
        default=urls.DEFAULT_BASE,
        help="where the site is mounted on its host, e.g. /stemma/ for a GitHub "
        "Pages project site (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    return build(args.path, args.out, args.base)


if __name__ == "__main__":
    sys.exit(main())
