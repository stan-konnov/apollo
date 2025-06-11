from typing import Generator
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(name="requests_get_call")
def requests_get_call(request: pytest.FixtureRequest) -> Generator[Mock, None, None]:
    """
    Simulate call to requests.get by patching dynamic path.

    Usage example:

    @pytest.mark.parametrize(
        "requests_get_call",
        ["path.to.patch.get"],
        indirect=True
    )
    """

    with patch(request.param) as mock_requests_get:
        yield mock_requests_get


@pytest.fixture(name="requests_post_call")
def requests_post_call(request: pytest.FixtureRequest) -> Generator[Mock, None, None]:
    """
    Simulate call to requests.post by patching dynamic path.

    Usage example:

    @pytest.mark.parametrize(
        "requests_post_call",
        ["path.to.patch.post"],
        indirect=True
    )
    """

    with patch(request.param) as mock_requests_get:
        yield mock_requests_get
