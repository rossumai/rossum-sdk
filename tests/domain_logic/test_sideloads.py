from __future__ import annotations

import copy

from rossum_api.domain_logic.sideloads import build_sideload_params, embed_sideloads
from tests.conftest import ANNOTATIONS, AUTOMATION_BLOCKERS, CONTENT

RESPONSE_DATA = {
    "pagination": {"total": 3, "total_pages": 1, "next": None, "previous": None},
    "results": ANNOTATIONS,
    "content": CONTENT,
    "automation_blockers": AUTOMATION_BLOCKERS,
}


def test_build_sideload_params():
    assert build_sideload_params(
        ["content", "automation_blockers"], ["sender_id", "vat_detail"]
    ) == {
        "sideload": "content,automation_blockers",
        "content.schema_id": "sender_id,vat_detail",
    }


def test_embed_sideloads():
    """Automation blockers and datapoints from content are correctly inserted into results."""
    response_data = copy.deepcopy(RESPONSE_DATA)
    embed_sideloads(response_data, ["content", "automation_blockers"])

    expected_annotations = copy.deepcopy(ANNOTATIONS)
    expected_annotations[0]["content"] = [CONTENT[1]]
    expected_annotations[0]["automation_blocker"] = AUTOMATION_BLOCKERS[0]
    expected_annotations[1]["content"] = [CONTENT[0], CONTENT[2]]
    expected_annotations[1]["automation_blocker"] = AUTOMATION_BLOCKERS[0]
    expected_annotations[2]["content"] = []

    assert response_data["results"] == expected_annotations
