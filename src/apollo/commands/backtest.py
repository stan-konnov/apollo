import logging

from apollo.calculations.wilders_swing_index import WildersSwingIndexCalculator
from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.settings import (
    END_DATE,
    MAX_PERIOD,
    START_DATE,
    TICKER,
)
from apollo.utils.common import ensure_environment_is_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run backtesting process for individual strategy."""

    ensure_environment_is_configured()

    yahoo_api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=bool(MAX_PERIOD),
    )

    dataframe = yahoo_api_connector.request_or_read_prices()

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=5,
    )

    wsi_calculator.calculate_swing_index()


if __name__ == "__main__":
    main()
