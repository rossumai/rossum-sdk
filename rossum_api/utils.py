from __future__ import annotations

import typing

import inflect


def to_singular(word: str) -> str:
    """Convert plural form of a word to singular."""
    engine = inflect.engine()
    singular_form = engine.singular_noun(word)
    return singular_form or word


def enforce_domain(url: str, base_url: str) -> str:
    """Make sure the url contains the domain."""
    if not url.startswith("https://") and not url.startswith("http://"):
        return f"{base_url}/{url}"
    return url


class ObjectWithStatus(typing.Protocol):
    status: typing.Any
