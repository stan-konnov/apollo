from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(name="trading_client")
def trading_client(request: pytest.FixtureRequest) -> Generator[Mock, None, None]:
    """
    Simulate call(s) to Trading API by patching dynamic path.

    Usage example:

    @pytest.mark.parametrize(
        "trading_client",
        ["path.to.patch.trading_client"],
        indirect=True
    )
    """

    with patch(request.param) as mock_trading_client:
        yield mock_trading_client
