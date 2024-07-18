import logging
from json import dumps, load
from pathlib import Path
from sys import exit

from apollo.settings import (
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    PARM_DIR,
    START_DATE,
    STRATEGY,
    TICKER,
)
from apollo.utils.types import ParameterSet

logger = logging.getLogger(__name__)


class Configuration:
    """
    Configuration class.

    Takes in environment variables to supply to parameter optimizer.
    Looks up strategy parameters file and parses it into a typed object.
    """

    def __init__(self) -> None:
        """
        Construct Configuration.

        Look up strategy parameters file and parse it into a typed object.
        """

        self.parameter_set = self._get_parameter_set()

        period = "Maximum available" if MAX_PERIOD else f"{START_DATE} - {END_DATE}"

        logger.info(
            f"Running {STRATEGY} for {TICKER}\n\n"
            f"Period: {period}\n\n"
            f"Frequency: {FREQUENCY}\n\n"
            "Parameters:\n\n"
            f"{dumps(self.parameter_set, indent=4)}",
        )

    def _get_parameter_set(self) -> ParameterSet:
        """
        Parse parameters file from file system into typed object.

        Catch potential FileNotFoundError, log exception and exit with code 1.
        """

        parameters_file_path = f"{PARM_DIR}/{STRATEGY}.json"

        try:
            with Path.open(Path(parameters_file_path)) as file:
                parameter_set: ParameterSet = load(file)

        except FileNotFoundError:
            logger.exception(
                f"Parameter set file not found. "
                f"Please create one at {parameters_file_path}",
            )

            # At this point, we should exit
            # as parameters are required to proceed
            exit(1)

        return parameter_set
