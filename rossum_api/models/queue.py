from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Queue:
    id: int
    name: str
    url: str
    workspace: str | None
    connector: str | None
    schema: str
    inbox: str | None
    counts: dict[str, int]
    session_timeout: str = "01:00:00"
    webhooks: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)
    users: list[str] = field(default_factory=list)
    rir_url: str | None = None
    rir_params: str | None = None
    automation_enabled: bool = False
    automation_level: str = "never"
    default_score_threshold: float = 0.8
    locale: str = "en_GB"
    metadata: dict[str, Any] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)
    dedicated_engine: str | dict[str, Any] | None = None
    generic_engine: str | dict[str, Any] | None = None
    use_confirmed_state: bool = False
    document_lifetime: str | None = None
    delete_after: str | None = None
    status: str | None = None
    engine: str | None = None
    training_enabled: bool = True
