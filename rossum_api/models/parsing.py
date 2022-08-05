from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict


def dict_to_dataclass(klass, data: Dict[str, Any]) -> Any:
    """Creates new instance of a dataclass from a given dict.

    Throws away any fields not defined in the respective dataclass to prevent frequent crashes
    caused adding new fields to API endpoints. Decreases the maintanance burden.
    """
    fields = [field.name for field in dataclasses.fields(klass)]
    filtered_data = {k: v for k, v in data.items() if k in fields}
    return klass(**filtered_data)
