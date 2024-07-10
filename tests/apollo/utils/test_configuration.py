import logging
from json import load
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from apollo.utils.configuration import Configuration
from tests.fixtures.env_and_constants import STRATEGY
from tests.fixtures.files_and_directories import PARM_DIR, PARM_FILE_PATH

if TYPE_CHECKING:
    from apollo.utils.types import ParameterSet

logger = logging.getLogger(__name__)


@patch("apollo.utils.configuration.PARM_DIR", PARM_DIR)
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

    assert (
        str(
            "Parameter set file not found. "
            f"Please create one at {PARM_DIR}/NonExistingStrategy.json",
        )
        in caplog.text
    )

    assert exception.value.code == 1


@patch("apollo.utils.configuration.PARM_DIR", PARM_DIR)
@patch("apollo.utils.configuration.STRATEGY", STRATEGY)
def test__configuration__with_existing_parameter_set_file() -> None:
    """
    Test Configuration construction with existing parameter set file.

    Configuration must parse the parameter set file into a typed object.
    """

    configuration = Configuration()

    parameter_set: ParameterSet

    with Path.open(Path(PARM_FILE_PATH)) as file:
        parameter_set = load(file)

    assert configuration.parameter_set == parameter_set
    assert type(configuration.parameter_set) is type(parameter_set)
