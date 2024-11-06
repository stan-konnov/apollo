import logging
from datetime import datetime
from pathlib import Path

from zoneinfo import ZoneInfo

from apollo.processors.parameter_optimizer import ParameterOptimizer
from apollo.processors.ticker_screener import TickerScreener
from apollo.settings import ParameterOptimizerMode
from apollo.utils.common import ensure_environment_is_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run signal generation process."""

    output_file = "process_time_log.txt"
    start_time = datetime.now(tz=ZoneInfo("UTC"))

    ensure_environment_is_configured()

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

    output = (
        f"Process Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Process End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Time Delta: {hours} hours and {minutes} minutes\n"
    )

    # Write to file
    with Path.open(Path(output_file), "w") as file:
        file.write(output)


if __name__ == "__main__":
    main()
