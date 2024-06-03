from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Engine:
    id: int
    url: str
    name: str
    type: str
    learning_enabled: bool
    description: str
    agenda_id: str
