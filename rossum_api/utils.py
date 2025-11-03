from __future__ import annotations

import typing


def to_singular(word: str) -> str:
    """Convert plural form of a word to singular.

    Simple implementation that removes trailing 's' from plural words.
    Used primarily for converting sideload names to their corresponding
    singular resource field names in API responses.

    Examples
    --------
        - 'documents' -> 'document'
        - 'automation_blockers' -> 'automation_blocker'
        - 'modifiers' -> 'modifier'
        - 'queues' -> 'queue'
        - 'content' -> 'content' (already singular, no change)

    See Also
    --------
        rossum_api.types.Sideload for all available sideload values.
    """
    if word.endswith("s"):
        return word[:-1]
    return word


def enforce_domain(url: str, base_url: str) -> str:
    """Make sure the url contains the domain."""
    if not url.startswith("https://") and not url.startswith("http://"):
        return f"{base_url}/{url}"
    return url


class ObjectWithStatus(typing.Protocol):  # noqa: D101
    status: typing.Any
