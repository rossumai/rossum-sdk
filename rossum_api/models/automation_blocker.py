from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

AutomationBlockerTypes = Literal[
    "automation_disabled",
    "is_duplicate",
    "suggested_edit_present",
    "low_score",
    "failed_checks",
    "no_validation_sources",
    "error_message",
    "delete_recommendation_filename",
    "delete_recommendation_page_count",
    "delete_recommendation_field",
    "extension",
]


@dataclass
class AutomationBlockerContent:
    """Description of a single reason why `Annotation` was not automated.

    Arguments
    ---------
    level
        Whether automation blocker relates to specific datapoint or to the whole
        :class:`~rossum_api.models.annotation.Annotation`.
    type
        The type of automation blocker.
    schema_id
        The schema ID associated with this blocker.
        Only for datapoint level objects.
    samples_truncated
        Indicates if the samples list has been truncated.
    samples
        Whether number samples were truncated to 10, or contains all of them.
    details
        Only for ``level``: annotation with ``type``: ``error_message``.
        Contains message_content with list of error messages.

    References
    ----------
    https://elis.rossum.ai/api/docs/#automation-blocker.
    """

    level: str
    type: AutomationBlockerTypes
    schema_id: str | None = None
    samples_truncated: bool | None = False
    samples: list[dict[str, Any]] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AutomationBlocker:
    """Automation blocker stores reason why `Annotation` was not automated.

    Arguments
    ---------
    id
        Automation blocker object ID.
    url
        Automation blocker object URL.
    annotation
        URL of related :class:`~rossum_api.models.annotation.Annotation`.
    content
        List of reasons why automation is blocked.

    References
    ----------
    https://elis.rossum.ai/api/docs/#automation-blocker.
    """

    id: int
    url: str
    annotation: str
    content: list[AutomationBlockerContent] = field(default_factory=list)
