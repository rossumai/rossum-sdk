from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from rossum_api.domain_logic.urls import (
    parse_annotation_id_from_datapoint_url,
    parse_resource_id_from_url,
)
from rossum_api.utils import to_singular

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Union


def build_sideload_params(sideloads: Sequence[str], content_schema_ids: Sequence[str]) -> dict:
    """Build params used for sideloading.

    Arguments
    ---------
    sideloads
        A sequence of resources to be fetched along with the requested resource,
        e.g. ["content", "automation_blockers"] when fetching `annotations` resource.
    content_schema_ids
        sideloads only particular `content` fields when fetching `annotations` resource,
        has no effect when fetching other resources
    """
    return {
        "sideload": ",".join(sideloads),
        "content.schema_id": ",".join(content_schema_ids),
    }


def embed_sideloads(response_data: dict[str, Any], sideloads: Sequence[str]) -> None:
    """Put sideloads into the response data."""
    sideloads_by_id = _group_sideloads_by_annotation_id(sideloads, response_data)
    for result, sideload in itertools.product(response_data["results"], sideloads):
        sideload_name = to_singular(sideload)
        url = result[sideload_name]
        if url is None:
            continue
        sideload_id = parse_resource_id_from_url(url)

        result[sideload_name] = sideloads_by_id[sideload].get(
            sideload_id, []
        )  # `content` can have 0 datapoints, use [] default value in this case


def _group_sideloads_by_annotation_id(
    sideloads: Sequence[str], response_data: dict[str, Any]
) -> dict[str, dict[int, Union[dict, list]]]:
    sideloads_by_id: dict[str, dict[int, Union[dict, list]]] = {}
    for sideload in sideloads:
        if sideload == "content":
            # Datapoints from all annotations are present in response data, we have to construct
            # content (list of datapoints) for each annotation.
            def get_annotation_id(datapoint: dict[str, Any]) -> int:
                return parse_annotation_id_from_datapoint_url(datapoint["url"])

            sideloads_by_id[sideload] = {
                k: list(v)
                for k, v in itertools.groupby(
                    sorted(response_data[sideload], key=get_annotation_id),
                    key=get_annotation_id,
                )
            }
        else:
            sideloads_by_id[sideload] = {s["id"]: s for s in response_data[sideload]}
    return sideloads_by_id
