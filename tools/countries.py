#!/usr/bin/env python3
"""ISO 3166-1 alpha-2 codes the catalog may use, with their English names.

Stdlib only, and deliberately not the whole 249-code list. A card's
``origin.country`` has to be a key here (E14), and so does a
``[[country:<CC>|text]]`` link (E13), so the map grows by decision rather than
by typo: adding a country is an edit someone makes on purpose.

The names are the short English forms a reader expects to see in a heading —
"United States", not "United States of America" — because they are what the
browse pages print.
"""

COUNTRIES = {
    "AF": "Afghanistan",
    "AU": "Australia",
    "BR": "Brazil",
    "CA": "Canada",
    "CN": "China",
    "CO": "Colombia",
    "DE": "Germany",
    "ES": "Spain",
    "FR": "France",
    "GB": "United Kingdom",
    "IN": "India",
    "JM": "Jamaica",
    "JP": "Japan",
    "KH": "Cambodia",
    "LA": "Laos",
    "LB": "Lebanon",
    "MA": "Morocco",
    "MX": "Mexico",
    "NL": "Netherlands",
    "NP": "Nepal",
    "PK": "Pakistan",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "US": "United States",
    "VN": "Vietnam",
    "ZA": "South Africa",
}


def code(value):
    """The normalized ISO-2 code for ``value``, or ``None`` when unknown.

    Case and surrounding space are forgiven — cards store ``"MX"`` and a link
    may be written ``[[country:mx|Mexico]]`` — but nothing else is: an
    unrecognized code is unknown, not guessed at.
    """
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized if normalized in COUNTRIES else None


def name(value):
    """The English name for an ISO-2 code, or ``None`` when it isn't in the map."""
    normalized = code(value)
    return COUNTRIES[normalized] if normalized else None


def is_known(value):
    return code(value) is not None
