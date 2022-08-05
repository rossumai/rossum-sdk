from typing import Any, Dict, List, Optional

from pydantic import Field

from rossum_ng.models.base import Base


class Document(Base):
    id: int
    url: str
    s3_name: str
    mime_type: str
    creator: str
    created_at: str
    arrived_at: str
    original_file_name: str
    content: str
    parent: Optional[str] = None
    email: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    annotations: List[str] = Field(default_factory=list)
    attachment_status: Optional[str] = None
