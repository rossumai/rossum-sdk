from typing import Any, Dict, List, Optional

from pydantic import Field

from rossum_ng.models.base import Base


class AutomationBlockerContent(Base):
    level: str
    type: str
    schema_id: Optional[str] = None
    samples_truncated: Optional[bool] = False
    samples: Dict[str, Any] = Field(default_factory=dict)
    details: Dict[str, Any] = Field(default_factory=dict)


class AutomationBlocker(Base):
    id: int
    url: str
    annotation: str
    content: List[AutomationBlockerContent] = Field(default_factory=list)
