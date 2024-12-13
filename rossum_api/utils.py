from __future__ import annotations

import inflect


def to_singular(word: str) -> str:
    """Convert plural form of a word to singular."""
    engine = inflect.engine()
    singular_form = engine.singular_noun(word)
    return singular_form or word
