import logging

import pandas as pd

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.calculations.absolute_price_oscillator import (
    AbsolutePriceOscillatorCalculator,
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

    apo_calculator = AbsolutePriceOscillatorCalculator(
        dataframe=dataframe,
        window_size=5,
        fast_ema_period=10,
        slow_ema_period=40,
    )

    apo_calculator.calculate_absolute_price_oscillator()

    # pd.options.display.max_rows = 10000
    # print(dataframe)


if __name__ == "__main__":
    main()
