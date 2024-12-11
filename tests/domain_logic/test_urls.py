from __future__ import annotations

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.domain_logic.urls import (
    build_export_url,
    build_full_login_url,
    build_upload_url,
    build_url,
    parse_annotation_id_from_datapoint_url,
    parse_resource_id_from_url,
)


@pytest.mark.parametrize(
    "url, expected_id",
    [
        ("https://elis.rossum.ai/api/v1/queues/8199", 8199),
        ("https://elis.rossum.ai/api/v1/annotations/314521/content", 314521),
    ],
)
def test_parse_resource_id_from_url(url, expected_id):
    assert parse_resource_id_from_url(url) == expected_id


def test_parse_annotation_id_from_datapoint_url():
    assert (
        parse_annotation_id_from_datapoint_url(
            "https://elis.rossum.ai/api/v1/annotations/314521/content/1123123"
        )
        == 314521
    )


def test_build_url():
    assert build_url(Resource.Queue, 123) == "queues/123"


def test_build_full_login_url():
    assert (
        build_full_login_url("https://elis.rossum.ai/api/v1")
        == "https://elis.rossum.ai/api/v1/auth/login"
    )


def test_build_upload_url():
    assert build_upload_url(Resource.Queue, 123) == "queues/123/upload"


def test_build_export_url():
    assert build_export_url(Resource.Queue, 123) == "queues/123/export"
