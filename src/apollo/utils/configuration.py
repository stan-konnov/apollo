import logging
from json import dumps, load
from pathlib import Path
from sys import exit

from apollo.settings import END_DATE, PARM_DIR, START_DATE, STRATEGY, TICKER
from apollo.utils.types import ParameterSet

logger = logging.getLogger(__name__)


class Configuration:
    """
    Configuration class.

    Takes in environment variables to supply them to other components.
    Looks up strategy parameters file and parses it into a typed object.
    """

    def __init__(self) -> None:
        """
        Construct Configuration.

        Check if all required variables are set and preserve them.
        Look up strategy parameters file and parse it into a typed object.

        TODO: adapt me to factor in max period of prices

        Question: how to know that we need to query again?
        Something to think about when rebuilding storage.
        """

        if None in (TICKER, STRATEGY, START_DATE, END_DATE):
            raise ValueError(
                "TICKER, STRATEGY, START_DATE, END_DATE variables must be set.",
            )

        self.ticker = str(TICKER)
        self.strategy = str(STRATEGY)
        self.start_date = str(START_DATE)
        self.end_date = str(END_DATE)

        self.parameter_set = self._get_parameter_set()

        logger.info(
            f"Running {self.strategy} for {self.ticker}\n\n"
            f"Dates: {self.start_date} - {self.end_date}\n\n"
            "Parameters:\n\n"
            f"{dumps(self.parameter_set, indent=4)}",
        )

    def _get_parameter_set(self) -> ParameterSet:
        """
        Parse parameters file from file system into typed object.

        Catch potential FileNotFoundError, log exception and exit with code 1.
        """

        parameters_file_path = f"{PARM_DIR}/{self.strategy}.json"

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
