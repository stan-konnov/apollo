from typing import Generator
from unittest.mock import patch

import pytest


@pytest.fixture(name="multiprocessing_pool")
def multiprocessing_pool(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """
    Simulate Multiprocessing Pool object by patching dynamic path.

    Usage example:

    @pytest.mark.parametrize(
        "multiprocessing_pool",
        ["path.to.patch.get"],
        indirect=True
    )
    """

    with patch(request.param) as mocked_pool:
        # Assign the instance of the pool to a variable
        # so we can access it later and make assertions against it
        mock_pool_instance = mocked_pool.return_value.__enter__.return_value

        yield mock_pool_instance
