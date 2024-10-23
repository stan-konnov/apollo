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
    """Run screening process."""

    ensure_environment_is_configured()

    ticker_screener = TickerScreener()
    ticker_screener.screen_in_parallel()


if __name__ == "__main__":
    main()
