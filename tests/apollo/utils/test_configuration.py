from unittest.mock import patch

import pytest

from apollo.utils.configuration import Configuration


@patch("apollo.utils.configuration.TICKER", None)
def test__configuration__with_missing_environment_variables() -> None:
    """
    Test configuration construction with missing environment variables.

    Configuration must raise a ValueError when environment variables are missing.
    """

    with pytest.raises(
        ValueError,
        match="TICKER, STRATEGY, START_DATE, END_DATE variables must be set.",
    ) as exception:

        Configuration()

    assert str(exception.value) == (
        "TICKER, STRATEGY, START_DATE, END_DATE variables must be set."
    )
