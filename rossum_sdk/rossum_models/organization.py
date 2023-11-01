from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Organization:
    id: int
    name: str
    url: str
    workspaces: List[str]
    users: List[str]
    organization_group: str
    is_trial: bool
    created_at: str
    trial_expires_at: Optional[str] = None
    expires_at: Optional[str] = None
    oidc_provider: Optional[str] = None
    ui_settings: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
