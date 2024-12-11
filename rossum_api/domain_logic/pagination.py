from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

DEFAULT_PAGE_SIZE = 100


def build_pagination_params(ordering: Sequence[str], page_size: int = DEFAULT_PAGE_SIZE) -> dict:
    """Build params used for fetching paginated resources."""
    return {
        "page_size": page_size,
        "ordering": ",".join(ordering),
    }
