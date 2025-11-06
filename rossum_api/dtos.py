from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Token:  # noqa: D101
    token: str


@dataclass
class UserCredentials:  # noqa: D101
    username: str
    password: str
