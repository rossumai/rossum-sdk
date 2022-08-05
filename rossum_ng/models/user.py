from typing import List, Optional

from pydantic import Field

from rossum_ng.models.base import Base


class User(Base):
    id: int
    url: str
    first_name: str
    last_name: str
    email: str
    date_joined: str
    username: str
    organization: str
    last_login: str
    is_active: bool = True
    email_verified: Optional[bool] = False
    password: Optional[str] = None
    groups: List[str] = Field(default_factory=list)
    queues: List[str] = Field(default_factory=list)
    ui_settings: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    oidc_id: Optional[str] = None
    auth_type: str = "password"
