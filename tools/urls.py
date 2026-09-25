#!/usr/bin/env python3
"""The one place a site URL is spelled, so the site can live under a subpath.

Stdlib only. Stemma is built twice from one tree: Cloudflare Pages serves it at
the root of its own host, GitHub Pages serves it as a project site under
``/stemma/``. Every internal URL therefore has to be written as *base plus a
site-relative path* rather than as a root-absolute literal.

The base is a property of the build run — one process compiles one site — so it
is set once by ``tools/build.py`` and read from here by every module that emits
an href. The alternative, threading a ``base`` argument through the dozen
rendering functions in ``browse``, ``lineage``, ``links``, ``origins``, and
``timeline``, would put the same value in every signature to no end: nothing in
a build ever wants two bases at once.

Two spellings, kept apart on purpose:

``path``
    Site-relative, always starting with ``/``: ``/s/skunk-1/``. This is what the
    build uses for *files* — ``browse`` turns a path into ``browse/kind/…/
    index.html`` under ``--out`` — and it never carries the base.
``url``
    What a page links to: ``base`` + the path without its leading slash. With
    the default base ``/`` the two are identical, which is exactly why the
    Cloudflare build is byte-for-byte what it was before the base existed.
"""

DEFAULT_BASE = "/"

_base = DEFAULT_BASE


def normalize(base):
    """A base path that starts and ends with ``/``: ``stemma`` → ``/stemma/``.

    Empty, ``None``, and ``/`` all mean the site root. Interior slashes are left
    alone, so a nested base like ``/a/b`` normalizes to ``/a/b/``.
    """
    if base is None:
        return DEFAULT_BASE
    text = str(base).strip()
    if not text:
        return DEFAULT_BASE
    if not text.startswith("/"):
        text = "/" + text
    if not text.endswith("/"):
        text += "/"
    return text


def set_base(base):
    """Set the base for this build. Returns the normalized value."""
    global _base
    _base = normalize(base)
    return _base


def get_base():
    return _base


def is_root():
    """True when the site is served from the root of its host."""
    return _base == DEFAULT_BASE


def url(path):
    """``base`` + a site-relative ``path``, whose own leading ``/`` is dropped.

    ``url("/")`` is the base itself, which is the home page.
    """
    return _base + str(path).lstrip("/")


def strain(strain_id):
    """The URL of a card's page. The ``/s/<id>/`` shape lives here only."""
    return url(strain_path(strain_id))


def strain_path(strain_id):
    """The site-relative path of a card's page."""
    return "/s/%s/" % strain_id
