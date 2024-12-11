from __future__ import annotations

import inflect


def enforce_domain(url: str, base_url: str) -> str:
    """Make sure the url contains the domain."""
    if not url.startswith("https://") and not url.startswith("http://"):
        return f"{base_url}/{url}"
    return url


def to_singular(word):
    p = inflect.engine()
    singular_form = p.singular_noun(word)
    return singular_form if singular_form else word
