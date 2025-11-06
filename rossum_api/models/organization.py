from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Organization:
    """Organization is a basic unit that contains all objects that are required to fully use Rossum platform.

    .. warning::
        Please note that Organization is an internal API and can be changed without notice.

    Arguments
    ---------
    id
        ID of the organization.
    name
        Name of the organization.
    url
        URL of the organization.
    workspaces
        List of :class:`~rossum_api.models.workspace.Workspace` objects in the organization.
    users
        List of :class:`~rossum_api.models.user.User` in the organization.
    organization_group
        URL to organization group the organization belongs to.
    is_trial
        Property indicates whether this license is a trial license.
    created_at
        Timestamp for when the organization was created.
    trial_expires_at
        Timestamp for when the trial period ended (ISO 8601).
    expires_at
        Timestamp for when the organization is to be expired.
    oidc_provider
        (Deprecated) OpenID Connect provider name.
    ui_settings
        Organization-wide frontend UI settings (e.g. locales). Rossum internal.
    metadata
        Client data.

    References
    ----------
    https://elis.rossum.ai/api/docs/#organization
    """

    id: int
    name: str
    url: str
    workspaces: list[str]
    users: list[str]
    organization_group: str
    is_trial: bool
    created_at: str
    trial_expires_at: str | None = None
    expires_at: str | None = None
    oidc_provider: str | None = None
    ui_settings: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
