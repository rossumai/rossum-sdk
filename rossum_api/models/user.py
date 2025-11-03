from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class User:
    """User represents individual user of Rossum.

    Every user is assigned to an organization and can have access to multiple
    queues and user groups for document processing workflows.

    Arguments
    ---------
    id
        Id of the user.
    url
        URL of the user.
    first_name
        First name of the user.
    last_name
        Last name of the user.
    email
        Email of the user.
    date_joined
        Date of user join.
    username
        Username of a user.
    organization
        Related organization.
    last_login
        Date of last login.
    is_active
        Whether user is enabled or disabled.
    email_verified
        Whether the user's email is verified.
    password
        Password (not shown on API).
    groups
        List of user role (permission groups).
    queues
        List of queues user is assigned to.
    ui_settings
        User-related frontend UI settings (e.g. locales). Rossum internal.
    metadata
        Client data.
    oidc_id
        OIDC provider id used to match Rossum user (displayed only to admin user).
    auth_type
        Authorization method, can be sso or password. This field can be edited only by admin.
    deleted
        Whether a user is deleted.

    References
    ----------
    https://elis.rossum.ai/api/docs/#user
    """

    id: int
    url: str
    first_name: str
    last_name: str
    email: str
    date_joined: str
    username: str
    organization: str
    last_login: str | None = None
    is_active: bool = True
    email_verified: bool | None = False
    password: str | None = None
    groups: list[str] = field(default_factory=list)
    queues: list[str] = field(default_factory=list)
    ui_settings: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    oidc_id: str | None = None
    auth_type: str = "password"
    deleted: bool = False
