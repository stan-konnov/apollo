import logging
from unittest.mock import patch

import pytest

from apollo.utils.configuration import Configuration

logger = logging.getLogger(__name__)


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


@patch("apollo.utils.configuration.PARM_DIR", "parameters")
@patch("apollo.utils.configuration.STRATEGY", "NonExistingStrategy")
def test__configuration__with_non_existing_parameter_file(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test configuration construction with non existing parameter file.

    Configuration must log an exception and exit with code 1.
    """

    caplog.set_level(logging.ERROR)

    with pytest.raises(SystemExit) as exception:
        Configuration()

    assert str(
        "Parameter set file not found. "
        "Please create one at parameters/NonExistingStrategy.json",
    ) in caplog.text

    assert exception.value.code == 1
