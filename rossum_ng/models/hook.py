from typing import Any, Dict, List, Optional

from pydantic import Field

from rossum_ng.models.base import Base


class Hook(Base):
    id: int
    name: str
    url: str
    active: bool
    config: Dict[str, Any]
    test: Dict[str, Any]
    guide: str
    read_more_url: str
    extension_image_url: str
    type: str = "webhook"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    queues: List[str] = Field(default_factory=list)
    run_after: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    settings_schema: Optional[Dict[str, Any]] = None
    secrets: Dict[str, Any] = Field(default_factory=dict)
    extension_source: str = "custom"
    sideload: List[str] = Field(default_factory=list)
    token_owner: Optional[str] = None
    description: Optional[str] = None
