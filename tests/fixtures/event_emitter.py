from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(name="event_emitter")
def event_emitter(request: pytest.FixtureRequest) -> Generator[Mock, None, None]:
    """
    Simulate call to event_emitter by patching dynamic path.

    Usage example:

    @pytest.mark.parametrize(
        "event_emitter",
        ["path.to.patch.event_emitter"],
        indirect=True
    )
    """

    with patch(request.param) as mock_event_emitter:
        yield mock_event_emitter
