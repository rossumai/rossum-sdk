from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

EngineFieldType = Literal["string", "number", "date", "enum"]
MultilineType = Literal["true", "false", ""]  # Preparation for "auto" option


@dataclass
class Engine:
    id: int
    url: str
    name: str
    type: str
    learning_enabled: bool
    description: str
    agenda_id: str


@dataclass
class EngineField:
    id: int
    url: str
    engine: str
    name: str
    tabular: bool
    label: str
    type: EngineFieldType
    subtype: Optional[str]
    pre_trained_field_id: Optional[str]
    multiline: MultilineType
