from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuleAction:
    """Rule action object defines actions to be executed when trigger condition is met.

    Arguments
    ---------
    id
        Rule action ID. Needs to be unique within the Rule's actions.
    enabled
        If False the action is disabled (default: True).
    type
        Type of action. See `Rule actions <https://elis.rossum.ai/api/docs/#rule-actions>`_
        for the list of possible actions.
    payload
        Action payload. Structure depends on the action type.
        See `Rule actions <https://elis.rossum.ai/api/docs/#rule-actions>`_ for details.
    event
        Actions are configured to be executed on a specific event.
        See `Trigger events <https://elis.rossum.ai/api/docs/#trigger-events>`_.

    References
    ----------
    https://elis.rossum.ai/api/docs/#rule-actions
    """

    id: str
    type: str
    payload: dict[str, Any]
    event: str
    enabled: bool = True


@dataclass
class Rule:
    """Rule object represents arbitrary business rules added to schema objects.

    Rules allow you to define custom business logic that is evaluated when specific
    conditions are met. Each rule consists of a trigger condition (TxScript formula)
    and a list of actions to execute when the condition evaluates to True.

    .. warning::
        Rules are currently in beta version and the API may change.
        Talk with a Rossum representative about enabling this feature.

    Notes
    -----
    The trigger condition is a TxScript formula which controls the execution of actions.
    There are two evaluation modes:

    - **Simple mode**: when the condition does not reference any datapoint, or only
      references header fields. Example: ``len(field.document_id) < 10``.
    - **Line-item mode**: when the condition references a line item datapoint (a column
      of a multivalue table). Example: ``field.item_amount > 100.0``.

    In line item mode, the condition is evaluated once for each row of the table.

    Arguments
    ---------
    id
        Rule object ID.
    url
        Rule object URL.
    name
        Name of the rule.
    enabled
        If False the rule is disabled (default: True).
    organization
        URL of the :class:`~rossum_api.models.organization.Organization` the rule belongs to.
    schema
        URL of the :class:`~rossum_api.models.schema.Schema` the rule belongs to.
    trigger_condition
        A condition for triggering the rule's actions.
        This is a formula evaluated by `Rossum TxScript <https://elis.rossum.ai/api/docs/#rossum-transaction-scripts>`_.
        Note that trigger condition must evaluate strictly to ``"True"``,
        truthy values are not enough to trigger the execution of actions.
        Wrap your condition with ``bool(your_condition)`` if necessary.
    created_by
        URL of the :class:`~rossum_api.models.user.User` who created the rule.
    created_at
        Timestamp of the rule creation.
    modified_by
        URL of the :class:`~rossum_api.models.user.User` who was the last to modify the rule.
    modified_at
        Timestamp of the latest modification.
    rule_template
        URL of the rule template the rule was created from.
    synchronized_from_template
        Signals whether the rule is automatically updated from the linked template.
    actions
        List of :class:`~rossum_api.models.rule.RuleAction` objects.
        See `Rule actions <https://elis.rossum.ai/api/docs/#rule-actions>`_.

    References
    ----------
    https://elis.rossum.ai/api/docs/#rule
    """

    id: int
    name: str
    enabled: bool
    organization: str
    schema: str
    trigger_condition: str = "True"
    url: str | None = None
    created_by: str | None = None
    created_at: str | None = None
    modified_by: str | None = None
    modified_at: str | None = None
    rule_template: str | None = None
    synchronized_from_template: bool = False
    actions: list[RuleAction] = field(default_factory=list)
