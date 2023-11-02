from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Group:
    id: int
    name: str
    url: str
