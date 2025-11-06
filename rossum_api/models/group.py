from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Group:
    """User role is a group of permissions that are assigned to the user.

    Permissions are assigned to individual operations on objects.

    Arguments
    ---------
    id
        Id of the user role (may differ between different organizations).
    name
        Name of the user role.
    url
        URL of the user role.

    References
    ----------
    https://elis.rossum.ai/api/docs/#user-role
    """

    id: int
    name: str
    url: str
