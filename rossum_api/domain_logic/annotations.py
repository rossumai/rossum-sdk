from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from rossum_api.utils import ObjectWithStatus

if TYPE_CHECKING:
    from typing import Sequence


class ExportFileFormats(Enum):
    CSV = "csv"
    XML = "xml"
    XLSX = "xlsx"


def validate_list_annotations_params(
    sideloads: Sequence[str] = (),
    content_schema_ids: Sequence[str] = (),
) -> None:
    """Validate parameters to list_annotations request."""
    if sideloads and "content" in sideloads and not content_schema_ids:
        raise ValueError(
            'When content sideloading is requested, "content_schema_ids" must be provided'
        )


def get_http_method_for_annotation_export(**filters) -> str:
    """to_status filter requires a different HTTP method.

    https://elis.rossum.ai/api/docs/#export-annotations
    """
    if "to_status" in filters:
        return "POST"
    return "GET"


def is_annotation_imported(annotation: ObjectWithStatus) -> bool:
    """Check whether the import of the given annotation has finished."""
    return annotation.status not in ("importing", "created")
