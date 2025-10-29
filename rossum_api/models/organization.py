from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Organization:
    id: int
    name: str
    url: str
    workspaces: list[str]
    users: list[str]
    organization_group: str
    is_trial: bool
    created_at: str
    trial_expires_at: str | None = None
    expires_at: str | None = None
    oidc_provider: str | None = None
    ui_settings: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
