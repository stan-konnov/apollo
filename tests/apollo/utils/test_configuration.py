import logging
from json import load
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from apollo.settings import END_DATE, START_DATE, TICKER
from apollo.utils.configuration import Configuration

if TYPE_CHECKING:
    from apollo.utils.types import ParameterSet

logger = logging.getLogger(__name__)

PARM_DIR = "tests/test_data"
STRATEGY = "test_strategy"
PARM_FILE_PATH = f"{PARM_DIR}/{STRATEGY}.json"


@patch("apollo.utils.configuration.TICKER", None)
def test__configuration__with_missing_environment_variables() -> None:
    """
    Test Configuration construction with missing environment variables.

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
def test__configuration__with_non_existing_parameter_set_file(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test Configuration construction with non existing parameter set file.

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


@patch("apollo.utils.configuration.PARM_DIR", PARM_DIR)
@patch("apollo.utils.configuration.STRATEGY", STRATEGY)
def test__configuration__with_existing_parameter_set_file() -> None:
    """
    Test Configuration construction with existing parameter set file.

    Configuration must properly consume environment variables.
    Configuration must parse the parameter set file into a typed object.
    """

    configuration = Configuration()

    parameter_set: ParameterSet

    with Path.open(Path(PARM_FILE_PATH)) as file:
        parameter_set = load(file)

    assert configuration.ticker == TICKER
    assert configuration.strategy == "test_strategy"
    assert configuration.start_date == START_DATE
    assert configuration.end_date == END_DATE

    assert configuration.parameter_set == parameter_set
    assert type(configuration.parameter_set) == type(parameter_set)
