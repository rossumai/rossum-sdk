from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Hook:
    id: int
    name: str
    url: str
    active: bool
    config: dict[str, Any]
    test: dict[str, Any]
    guide: str | None
    read_more_url: str | None
    extension_image_url: str | None
    type: str = "webhook"
    metadata: dict[str, Any] = field(default_factory=dict)
    queues: list[str] = field(default_factory=list)
    run_after: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    settings_schema: dict[str, Any] | None = None
    secrets: dict[str, Any] = field(default_factory=dict)
    extension_source: str = "custom"
    sideload: list[str] = field(default_factory=list)
    token_owner: str | None = None
    token_lifetime_s: int | None = None
    description: str | None = None
