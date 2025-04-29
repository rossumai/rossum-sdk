from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
    last_login: Optional[str] = None
    is_active: bool = True
    email_verified: Optional[bool] = False
    password: Optional[str] = None
    groups: List[str] = field(default_factory=list)
    queues: List[str] = field(default_factory=list)
    ui_settings: Dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    oidc_id: Optional[str] = None
    auth_type: str = "password"
    deleted: bool = False
