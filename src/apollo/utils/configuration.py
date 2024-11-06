import logging
from json import load
from pathlib import Path
from sys import exit

from apollo.settings import (
    PARM_DIR,
    STRATEGY,
)
from apollo.utils.types import ParameterSet

logger = logging.getLogger(__name__)


class Configuration:
    """
    Configuration class.

    Looks up strategy parameters file and parses it into a typed object.
    """

    def get_parameter_set(self, strategy: str = str(STRATEGY)) -> ParameterSet:
        """
        Look up strategy parameters file and parse it into a typed object.

        Catch potential FileNotFoundError, log exception and exit with code 1.

        :param strategy: Strategy name to look up parameters for.
        :returns: Typed parameter set object.
        """

        parameters_file_path = f"{PARM_DIR}/{strategy}.json"

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
