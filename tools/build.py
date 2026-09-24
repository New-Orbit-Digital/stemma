#!/usr/bin/env python3
"""Compile the catalog into a static site: dist/ plus dist/data/stemma.json.

Stdlib only. Validation runs first; any error aborts the build with exit 1.
The dataset is deterministic apart from ``generated``: strains are sorted by id
and edges by (child, parent, disputed). Pages are rendered from the plain HTML
templates in ``site/`` by substituting ``{{placeholder}}`` values, so the
runtime only ever reads ``data/stemma.json``.

Output layout under ``--out`` (the site root):

    index.html            search
    about/index.html      evidence tiers, labels, disputes
    404.html
    s/<id>/index.html     one page per card, rendered at build time
    assets/               style.css, app.js
    data/stemma.json      the Budlogs seam
"""

import argparse
import html
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate  # noqa: E402  (sibling module, resolved via the path insert)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

SCHEMA_VERSION = 1
DEFAULT_OUT = "dist"
DATASET_RELPATH = os.path.join("data", "stemma.json")

PLACEHOLDER_RE = re.compile(r"\{\{([a-z_]+)\}\}")

KIND_LABELS = {
    "landrace": "landrace",
    "cultivar": "cultivar",
    "cut": "clone-only cut",
}
TIER_LABELS = {
    "genetically-tested": "genetically tested",
    "documented": "documented",
    "breeder-claimed": "breeder claimed",
    "folklore": "folklore",
}
LINEAGE_NOTES = {
    "root": "A landrace. The tree stops here.",
    "partial": "One parent is known and the other is not.",
    "unknown": "No credible account of the parents.",
    "disputed": "Competing accounts exist. The best-supported one is shown here.",
}
LABEL_HINT = '<a class="chip__hint" href="/about/#traditional-labels">what this means</a>'


# -- dataset ---------------------------------------------------------------


def build_edges(cards):
    """Edges for main parents (disputed: false) and dispute parents (true).

    ``best_tier`` is the highest-ranked tier among that parent's evidence
    items; where the same (child, parent, disputed) parent is claimed more than
    once, the evidence is pooled and the best tier wins.
    """
    best = {}
    for card in cards:
        lineage = card.data.get("lineage") or {}
        for parent in lineage.get("parents") or []:
            _record(best, card.id, parent.get("id"), False, parent.get("evidence"))
        for dispute in lineage.get("disputes") or []:
            for parent_id in dispute.get("parents") or []:
                _record(best, card.id, parent_id, True, dispute.get("evidence"))
    return [
        {
            "child": child,
            "parent": parent,
            "best_tier": validate.TIER_BY_RANK[rank],
            "disputed": disputed,
        }
        for (child, parent, disputed), rank in sorted(best.items())
    ]


def _record(best, child, parent, disputed, evidence):
    ranks = [
        validate.TIER_RANK[item["tier"]]
        for item in evidence or []
        if isinstance(item, dict) and item.get("tier") in validate.TIER_RANK
    ]
    if not (child and parent and ranks):
        return
    key = (child, parent, disputed)
    best[key] = max(ranks + [best.get(key, 0)])


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


def write_page(out, relpath, text):
    path = os.path.join(out, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


# -- page fragments --------------------------------------------------------


def strain_href(strain_id):
    return "/s/%s/" % strain_id


def badge(tier):
    return '<span class="badge badge--%s">%s</span>' % (
        esc(tier),
        esc(TIER_LABELS.get(tier, tier)),
    )


def evidence_list(items, sources):
    """One badge per evidence item, with the source it rests on."""
    rows = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        parts = [badge(item.get("tier"))]
        source_id = item.get("source")
        source = sources.get(source_id)
        if source is not None:
            parts.append(
                '<a href="#source-%s">%s</a>' % (esc(source_id), esc(source.get("title")))
            )
        elif source_id:
            parts.append("<span>%s</span>" % esc(source_id))
        if item.get("note"):
            parts.append("<span>%s</span>" % esc(item["note"]))
        rows.append("<li>%s</li>" % "".join(parts))
    if not rows:
        return ""
    return '<ul class="evidence">%s</ul>' % "".join(rows)


def fact(term, value_html, evidence_html=""):
    return "<div><dt>%s</dt><dd>%s%s</dd></div>" % (esc(term), value_html, evidence_html)


def facts_block(data, sources):
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
        rows.append(fact("Born", display, evidence_list(born.get("evidence"), sources)))

    origin = data.get("origin") or {}
    if origin:
        if origin.get("unknown") is True:
            rows.append(fact("Origin", "Unknown"))
        else:
            place = esc(origin.get("place") or "Unknown")
            rows.append(
                fact("Origin", place, evidence_list(origin.get("evidence"), sources))
            )

    if "breeder" in data:
        breeder = data.get("breeder")
        if isinstance(breeder, dict):
            rows.append(
                fact(
                    "Breeder",
                    esc(breeder.get("name")),
                    evidence_list(breeder.get("evidence"), sources),
                )
            )
        else:
            rows.append(fact("Breeder", "Not recorded"))

    if not rows:
        return ""
    return '<dl class="facts">%s</dl>' % "".join(rows)


def chips_block(data):
    items = []
    kind = data.get("kind")
    if kind:
        items.append('<li class="chip">%s</li>' % esc(KIND_LABELS.get(kind, kind)))
    label = data.get("traditional_label")
    if label:
        items.append('<li class="chip">%s %s</li>' % (esc(label), LABEL_HINT))
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


def parents_block(data, names, sources):
    lineage = data.get("lineage") or {}
    status = lineage.get("status")
    parents = lineage.get("parents") or []
    note = LINEAGE_NOTES.get(status)
    out = ["<h3>Parents</h3>"]
    if parents:
        rows = [
            relation_item(
                parent.get("id"),
                names,
                evidence_list(parent.get("evidence"), sources),
            )
            for parent in parents
            if isinstance(parent, dict) and parent.get("id")
        ]
        out.append('<ul class="relations">%s</ul>' % "".join(rows))
    else:
        out.append('<p class="empty">No parents recorded.</p>')
    if note:
        out.append('<p class="empty">%s</p>' % esc(note))
    return "".join(out)


def children_block(strain_id, edges, names):
    rows = []
    for edge in edges:
        if edge["parent"] != strain_id:
            continue
        extra = badge(edge["best_tier"])
        if edge["disputed"]:
            extra += '<span class="badge">disputed claim</span>'
        rows.append(relation_item(edge["child"], names, extra))
    out = ["<h3>Children</h3>"]
    if rows:
        out.append('<ul class="relations">%s</ul>' % "".join(rows))
    else:
        out.append('<p class="empty">No children in the catalog yet.</p>')
    return "".join(out)


def disputes_block(data, names, sources):
    disputes = (data.get("lineage") or {}).get("disputes") or []
    if not disputes:
        return ""
    blocks = []
    for dispute in disputes:
        if not isinstance(dispute, dict):
            continue
        parent_links = ", ".join(
            '<a href="%s">%s</a>' % (esc(strain_href(pid)), esc(names.get(pid, pid)))
            for pid in dispute.get("parents") or []
            if isinstance(pid, str)
        )
        parts = ["<p>%s</p>" % esc(dispute.get("claim"))]
        if parent_links:
            parts.append("<p>Parents named: %s</p>" % parent_links)
        parts.append(evidence_list(dispute.get("evidence"), sources))
        blocks.append('<div class="dispute">%s</div>' % "".join(parts))
    return (
        '<section class="disputes" aria-labelledby="disputes-heading">'
        '<h2 id="disputes-heading">Disputed</h2>'
        "<p>Accounts disagree about this lineage. Each claim is listed with its own "
        "evidence. <a href=\"/about/#disputes\">How to read disputes</a></p>"
        "%s</section>" % "".join(blocks)
    )


def sources_block(data):
    sources = data.get("sources") or []
    rows = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        title = esc(source.get("title"))
        url = source.get("url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            title = '<a href="%s" rel="nofollow noopener">%s</a>' % (esc(url), title)
        line = [title]
        if source.get("publisher"):
            line.append('<span class="publisher">%s</span>' % esc(source["publisher"]))
        if source.get("accessed"):
            line.append(
                '<span class="publisher">accessed %s</span>' % esc(source["accessed"])
            )
        rows.append(
            '<li id="source-%s">%s</li>' % (esc(source.get("id")), " &middot; ".join(line))
        )
    if not rows:
        return ""
    return (
        '<section aria-labelledby="sources-heading">'
        '<h2 id="sources-heading">Sources</h2>'
        '<ol class="sources">%s</ol></section>' % "".join(rows)
    )


def inline_data_block(data, children):
    """The card data, inlined so the page needs no fetch on first render."""
    payload = json.dumps(
        {"strain": data, "children": children}, ensure_ascii=False, sort_keys=True
    )
    safe = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return '<script id="strain-data" type="application/json">%s</script>' % safe


# -- pages -----------------------------------------------------------------


def page(base, title, description, page_class, content, inline_data=""):
    return render(
        base,
        {
            "title": title,
            "description": description,
            "page_class": page_class,
            "content": content,
            "inline_data": inline_data,
        },
    )


def strain_page(base, template, data, edges, names):
    strain_id = data["id"]
    sources = {
        source["id"]: source
        for source in data.get("sources") or []
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
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
        "summary": (
            "" if stub or not data.get("summary") else "<p>%s</p>" % esc(data["summary"])
        ),
        "facts": "" if stub else facts_block(data, sources),
        "parents": parents_block(data, names, sources),
        "children": children_block(strain_id, edges, names),
        "disputes": "" if stub else disputes_block(data, names, sources),
        "sources": "" if stub else sources_block(data),
        "updated": esc(data.get("updated")),
    }

    name = data.get("name") or strain_id
    if stub:
        description = "%s is in the Stemma catalog as a stub: lineage links only." % name
    else:
        description = data.get("summary") or ("%s lineage and history." % name)
    return page(
        base,
        title="%s — Stemma" % name,
        description=description,
        page_class="page-strain",
        content=render(template, values),
        inline_data=inline_data_block(data, children),
    )


def index_page(base, template, strains):
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
    content = render(template, {"browse": browse, "browse_heading": esc(heading)})
    return page(
        base,
        title="Stemma — cannabis strain lineage",
        description="Search a cannabis strain name and see where it came from, with a source and an evidence tier for every claim.",
        page_class="page-search",
        content=content,
    )


def write_site(out, dataset):
    base = read_template("base.html")
    strains = dataset["strains"]
    edges = dataset["edges"]
    names = {
        strain["id"]: strain.get("name") or strain["id"]
        for strain in strains
        if strain.get("id")
    }

    write_page(out, "index.html", index_page(base, read_template("index.html"), strains))
    write_page(
        out,
        os.path.join("about", "index.html"),
        page(
            base,
            title="About — Stemma",
            description="What Stemma is, the four evidence tiers, why indica and sativa are traditional labels, and how to read disputes.",
            page_class="page-about",
            content=read_template("about.html"),
        ),
    )
    write_page(
        out,
        "404.html",
        page(
            base,
            title="Not found — Stemma",
            description="That page is not in the Stemma catalog.",
            page_class="page-404",
            content=read_template("404.html"),
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
            strain_page(base, template, strain, edges, names),
        )

    assets_src = os.path.join(SITE, "assets")
    assets_out = os.path.join(out, "assets")
    os.makedirs(assets_out, exist_ok=True)
    for name in sorted(os.listdir(assets_src)):
        source = os.path.join(assets_src, name)
        if os.path.isfile(source):
            shutil.copyfile(source, os.path.join(assets_out, name))

    return 3 + len(strains)


# -- driver ----------------------------------------------------------------


def build(path, out):
    validator = validate.Validator(path)
    code = validator.run()
    if code:
        print("build aborted: validation reported %d errors" % validator.errors)
        return 1

    cards = sorted(
        (card for card in validator.cards if card.id is not None),
        key=lambda card: card.id,
    )
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
    print("wrote %s: %d pages" % (out, pages))
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
    args = parser.parse_args(argv)
    return build(args.path, args.out)


if __name__ == "__main__":
    sys.exit(main())
