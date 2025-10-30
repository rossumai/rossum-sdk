from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class User:
    id: int
    url: str
    first_name: str
    last_name: str
    email: str
    date_joined: str
    username: str
    organization: str
    last_login: str | None = None
    is_active: bool = True
    email_verified: bool | None = False
    password: str | None = None
    groups: list[str] = field(default_factory=list)
    queues: list[str] = field(default_factory=list)
    ui_settings: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    oidc_id: str | None = None
    auth_type: str = "password"
    deleted: bool = False
