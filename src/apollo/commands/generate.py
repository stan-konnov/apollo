import logging
from datetime import datetime
from pathlib import Path

from zoneinfo import ZoneInfo

from apollo.processors.parameter_optimizer import ParameterOptimizer
from apollo.processors.ticker_screener import TickerScreener
from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_TIME_FORMAT,
    ParameterOptimizerMode,
)
from apollo.utils.common import (
    ensure_environment_is_configured,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run signal generation process."""

    ensure_environment_is_configured()

    start_time = datetime.now(tz=ZoneInfo("UTC"))

    ticker_screener = TickerScreener()
    ticker_screener.process_in_parallel()

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.MULTIPLE_STRATEGIES,
    )
    parameter_optimizer.process_in_parallel()

    end_time = datetime.now(tz=ZoneInfo("UTC"))

    time_delta = end_time - start_time

    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes = remainder // 60

    time_format = f"{DEFAULT_DATE_FORMAT} {DEFAULT_TIME_FORMAT}"

    with Path.open(Path("process_time.log"), "w") as file:
        file.write(
            f"Process Start: {start_time.strftime(time_format)}\n"
            f"Process End: {end_time.strftime(time_format)}\n"
            f"Duration: {hours} hours and {minutes} minutes\n",
        )


if __name__ == "__main__":
    main()
