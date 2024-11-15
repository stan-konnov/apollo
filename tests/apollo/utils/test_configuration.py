import logging
from json import load
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from apollo.settings import STRATEGY
from apollo.utils.configuration import Configuration
from tests.fixtures.files_and_directories import TEST_DIR

if TYPE_CHECKING:
    from apollo.utils.types import ParameterSet

logger = logging.getLogger(__name__)


@patch("apollo.utils.configuration.PARM_DIR", TEST_DIR)
def test__configuration__with_non_existing_parameter_set_file(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test Configuration construction with non existing parameter set file.

    Configuration must log an exception and exit with code 1.
    """

    caplog.set_level(logging.ERROR)

    configuration = Configuration()

    with pytest.raises(SystemExit) as exception:
        configuration.get_parameter_set("NonExistingStrategy")

    assert (
        str(
            "Parameter set file not found. "
            f"Please create one at {TEST_DIR}/NonExistingStrategy.json",
        )
        in caplog.text
    )

    assert exception.value.code == 1


@patch("apollo.utils.configuration.PARM_DIR", TEST_DIR)
def test__configuration__with_existing_parameter_set_file() -> None:
    """
    Test Configuration construction with existing parameter set file.

    Configuration must parse the parameter set file into a typed object.
    """

    configuration = Configuration()

    control_parameter_set: ParameterSet

    with Path.open(Path(f"{TEST_DIR}/{STRATEGY}.json")) as file:
        control_parameter_set = load(file)

    parameter_set = configuration.get_parameter_set()

    assert parameter_set == control_parameter_set
    assert type(parameter_set) is type(control_parameter_set)
