from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Hook:
    """Hook is an extension of Rossum that is notified when specific event occurs.

    Hook object is used to configure what endpoint or function is executed and when.
    For an overview of other extension options see `Extensions <https://elis.rossum.ai/api/docs/#extensions>`_.

    Notes
    -----
    Hooks are notified in parallel if ``run_after`` is not specified.

    Arguments
    ---------
    id
        ID of the hook.
    name
        Name of the hook.
    url
        URL of the hook.
    active
        If set to ``True`` the hook is notified.
    config
        Configuration of the hook.
    test
        Input saved for hook testing purposes, see `Test a hook <https://elis.rossum.ai/api/docs/#test-a-hook>`_.
    guide
        Description how to use the extension.
    read_more_url
        URL address leading to more info page.
    extension_image_url
        URL address of extension picture.
    type
        type of the hook.
    metadata
        Client data
    queues
        List of :class:`~rossum_api.models.queue.Queue` objects that use hook object.
    run_after
        List of all hooks that has to be executed before running this hook.
    events
        List of events, when the hook should be notified.
        For the list of events see `Webhook events <https://elis.rossum.ai/api/docs/#webhook-events>`_.
    settings
        Specific settings that will be included in the payload when executing the hook.
        Field is validated with json schema stored in ``settings_schema`` field.
    settings_schema
        [BETA] JSON schema for settings field validation.
    secrets
        JSON schema for ``settings`` field validation.
        This is in **BETA**.
    extension_source
        Import source of the extension.
    sideload
        List of related objects that should be included in hook request.
        For the list of events see `Webhook events <https://elis.rossum.ai/api/docs/#webhook-events>`_.
    token_owner
        URL of a :class:`~rossum_api.models.user.User`.
        If present, an API access token is generated for this user and sent to the hook.
        Users with organization group admin cannot be set as token_owner.
        If ``None``, token is not generated.
    token_lifetime_s
        Lifetime number of seconds for ``rossum_authorization_token`` (min=0, max=7200).
        This setting will ensure the token will be valid after hook response is returned.
        If ``None``, default lifetime of 600 is used.
    description
        Hook description text.

    References
    ----------
    https://elis.rossum.ai/api/docs/#hook

    https://elis.rossum.ai/api/docs/#test-a-hook

    https://elis.rossum.ai/api/docs/#webhook-events
    """

    id: int
    name: str
    url: str
    active: bool
    config: dict[str, Any]
    test: dict[str, Any]
    guide: str | None
    read_more_url: str | None
    extension_image_url: str | None
    type: Literal["webhook", "function", "job"] = "webhook"
    metadata: dict[str, Any] = field(default_factory=dict)
    queues: list[str] = field(default_factory=list)
    run_after: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    settings_schema: dict[str, Any] | None = None
    secrets: dict[str, Any] = field(default_factory=dict)
    extension_source: str = "custom"
    sideload: list[str] = field(default_factory=list)
    token_owner: str | None = None
    token_lifetime_s: int | None = None
    description: str | None = None
