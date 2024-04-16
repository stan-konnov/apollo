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


@patch("apollo.utils.configuration.PARM_DIR", None)
def test__configuration__with_non_existing_parameter_file() -> None:
    """
    Test configuration construction with non existing parameter file.

    Configuration must log an exception and exit with code 1.
    """

    with pytest.raises(SystemExit) as exception:

        Configuration()

    assert exception.value.code == 1
