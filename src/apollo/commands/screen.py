import logging

from apollo.screening.ticker_screener import TickerScreener
from apollo.utils.common import ensure_environment_is_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Run screening process.

    NOTE: Due to the nature of Yahoo Finance API,
    after the market closed, we need to wait roughly 30 minutes
    for the prices to settle before we can run the screening process.

    Otherwise, we might get incorrect results.
    """

    ensure_environment_is_configured()

    ticker_screener = TickerScreener()
    ticker_screener.process_in_parallel()


if __name__ == "__main__":
    main()
