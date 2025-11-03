from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from rossum_api.types import HttpMethod, Sideload
    from rossum_api.utils import ObjectWithStatus


class ExportFileFormats(Enum):  # noqa: D101
    CSV = "csv"
    XML = "xml"
    XLSX = "xlsx"


def validate_list_annotations_params(
    sideloads: Sequence[Sideload] = (), content_schema_ids: Sequence[str] = ()
) -> None:
    """Validate parameters to list_annotations request."""
    if sideloads and "content" in sideloads and not content_schema_ids:
        raise ValueError(
            'When content sideloading is requested, "content_schema_ids" must be provided'
        )


def get_http_method_for_annotation_export(**filters: Any) -> HttpMethod:
    """to_status filter requires a different HTTP method.

    https://elis.rossum.ai/api/docs/#export-annotations
    """
    return "POST" if "to_status" in filters else "GET"


def is_annotation_imported(annotation: ObjectWithStatus) -> bool:
    """Check whether the import of the given annotation has finished."""
    return annotation.status not in ("importing", "created")


def build_export_query_params(  # noqa: D103
    export_format: str, columns: Sequence[str] = (), **filters: Any
) -> dict[str, Any]:
    query_params = {"format": export_format}
    filters = filters or {}
    if filters:
        query_params = {**query_params, **filters}
    if columns:
        query_params["columns"] = ",".join(columns)
    return query_params
