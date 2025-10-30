from __future__ import annotations

import pytest

from rossum_api.utils import to_singular


class TestToSingular:
    @pytest.mark.parametrize(
        "plural,singular",
        [
            # All defined sideload values from rossum_api.types.Sideload
            # See: https://elis.rossum.ai/api/docs/#webhook-events
            ("content", "content"),  # Already singular
            ("automation_blockers", "automation_blocker"),
            ("documents", "document"),
            ("modifiers", "modifier"),
            ("queues", "queue"),
            # Other resource names used in the codebase
            ("users", "user"),
            ("annotations", "annotation"),
            # Edge cases
            ("document", "document"),  # Already singular
        ],
    )
    def test_to_singular(self, plural: str, singular: str) -> None:
        """Test conversion from plural to singular."""
        assert to_singular(plural) == singular
