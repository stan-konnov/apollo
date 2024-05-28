import logging

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.calculations.momentum.relative_strength_index import (
    RelativeStrengthIndexCalculator,
)
from apollo.settings import END_DATE, START_DATE, TICKER

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Quickly iterate on new concepts."""

    yahoo_api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    dataframe = yahoo_api_connector.request_or_read_prices()

    macd_calculator = RelativeStrengthIndexCalculator(
        dataframe=dataframe,
        window_size=5,
    )

    macd_calculator.calculate_relative_strength_index()


if __name__ == "__main__":
    main()
