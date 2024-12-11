from __future__ import annotations

import re
from typing import TYPE_CHECKING

from rossum_api.api_client import Resource

if TYPE_CHECKING:
    from rossum_api.models import Resource

DEFAULT_BASE_URL = "https://elis.rossum.ai/api/v1"


def parse_resource_id_from_url(url: str) -> int:
    # Annotation content resource is special, we need to strip /content suffix
    return int(url.replace("/content", "").split("/")[-1])


def parse_annotation_id_from_datapoint_url(url: str) -> int:
    # URL format: .../annotation/<annotation ID>/content/<datapoint ID>
    # Remove the /content/<datapoint ID> from the URL and then pass it to the generic function.
    return parse_resource_id_from_url(re.sub(r"/content/.*", "", url))


def build_url(resource: Resource, id_: int) -> str:
    return f"{resource.value}/{id_}"


def build_export_url(resource: Resource, id_: int) -> str:
    return f"{build_url(resource, id_)}/export"


def build_upload_url(resource: Resource, id_: int) -> str:
    return f"{build_url(resource, id_)}/upload"


def build_full_login_url(base_url: str) -> str:
    return f"{base_url}/auth/login"
