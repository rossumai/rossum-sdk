from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from rossum_api.types import JsonDict

HookAction = Literal[
    "user_update",  # deprecated in favor of `updated` below
    "created",
    "updated",
    "started",
    "confirm",
    "changed",
    "initialize",
    "export",
    "received",
    "manual",
    "scheduled",
    "integration",
    "interface",
]
HookType = Literal["webhook", "function", "job"]
HookEvent = Literal["annotation_status", "annotation_content", "email", "invocation", "upload"]
HookExtensionSource = Literal["custom", "rossum_store"]


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
    config: JsonDict
    test: JsonDict
    guide: str | None
    read_more_url: str | None
    extension_image_url: str | None
    type: HookType = "webhook"
    metadata: JsonDict = field(default_factory=dict)
    queues: list[str] = field(default_factory=list)
    run_after: list[str] = field(default_factory=list)
    events: list[HookEvent] = field(default_factory=list)
    settings: JsonDict = field(default_factory=dict)
    settings_schema: JsonDict | None = None
    secrets: JsonDict = field(default_factory=dict)
    extension_source: HookExtensionSource = "custom"
    sideload: list[str] = field(default_factory=list)
    token_owner: str | None = None
    token_lifetime_s: int | None = None
    description: str | None = None


@dataclass
class HookRunData:
    """Data class for hook execution logs.

    HookRunData captures detailed execution logs and metadata for webhook/hook runs within the system.
    It provides structured logging for tracking hook lifecycle events, performance metrics, and debugging information.

    Notes
    -----
    The ``timestamp`` field is automatically set to the current UTC time if not provided.

    The ``start`` and ``end`` fields should be used to track execution duration for performance monitoring.

    Attributes
    ----------
    log_level
        The severity level of the log entry: "INFO" for successful execution, "ERROR" for failures,
        or "WARNING" for non-critical issues.
    action
        The specific action being performed by the hook.
    event
        The event type that triggered the hook execution.
    request_id
        Unique identifier for the HTTP request that initiated this hook execution.
    organization_id
        The ID of the organization that owns the hook configuration.
    hook_id
        The unique identifier of the hook configuration being executed.
    hook_type
        The type/category of the hook (e.g., webhook, email, custom integration).
    queue_id
        Reference to the queue where the document/annotation is located.
    annotation_id
        Reference to the specific annotation that triggered or is associated with the hook execution.
    email_id
        Reference to an email record if the hook involves email processing.
    message
        Human-readable description or log message providing additional context about the execution.
    request
        Serialized representation of the outgoing HTTP request body sent by the hook (typically JSON).
    response
        Serialized representation of the HTTP response received from the hook endpoint.
    start
        ISO 8601 timestamp indicating when the hook execution started.
    end
        ISO 8601 timestamp indicating when the hook execution completed.
    settings
        Dictionary containing hook-specific configuration settings and parameters used during execution.
    status
        Text description of the execution status (e.g., "success", "failed", "timeout").
    status_code
        HTTP status code returned from the hook endpoint (e.g., 200, 404, 500).
        If ``None``, no status code is available.
    timestamp
        ISO 8601 timestamp of when the log entry was created.
    uuid
        Unique identifier for this specific hook execution instance, useful for idempotency and deduplication.
    output
        Serialized output or result produced by the hook execution.
        If ``None``, no output is captured.

    Notes
    -----
    The retention policy for the logs is set to 7 days.

    References
    ----------
    https://elis.rossum.ai/api/docs/#hook

    https://elis.rossum.ai/api/docs/#webhook-events
    """

    log_level: Literal["INFO", "ERROR", "WARNING"]
    action: HookAction
    event: HookEvent
    request_id: str
    organization_id: int
    hook_id: int
    hook_type: HookType
    queue_id: int | None = None
    annotation_id: int | None = None
    email_id: int | None = None
    message: str = ""
    request: str | None = None
    response: str | None = None
    start: str | None = None
    end: str | None = None
    settings: JsonDict = field(default_factory=dict)
    status: str | None = None
    status_code: int | None = None
    timestamp: str = ""
    uuid: str | None = None
    output: str | None = None
