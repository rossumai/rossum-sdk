from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Token:
    token: str


@dataclasses.dataclass
class UserCredentials:
    username: str
    password: str
