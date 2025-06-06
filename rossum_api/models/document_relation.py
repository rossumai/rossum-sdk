from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DocumentRelationType(str, Enum):
    EXPORT = "export"
    EINVOICE = "einvoice"


@dataclass
class DocumentRelation:
    id: int
    type: DocumentRelationType
    annotation: str  # Multiple values may be separated using a comma.
    key: Optional[str]
    documents: List[str]
    url: str
