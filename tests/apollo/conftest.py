from os import curdir
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from apollo.settings import ValidYahooApiFrequencies

WINDOW_SIZE = 5


@pytest.fixture(name="dataframe", scope="session")
def get_price_dataframe() -> pd.DataFrame:
    """Fixture to get test dataframe from file system."""

    test_dataframe = pd.read_csv(
        Path(f"{Path(curdir).resolve()}/tests/data/test.csv"),
        index_col=0,
    )

    test_dataframe.index = pd.to_datetime(test_dataframe.index)

    return test_dataframe


@pytest.fixture(name="window_size", scope="session")
def get_window_size() -> int:
    """Fixture to define window size for calculations."""

    return WINDOW_SIZE


@pytest.fixture(name="yahoo_api_response", scope="session")
def _yahoo_api_response() -> Generator[None, None, None]:
    """
    Simulate raw Yahoo API OHLCV response.

    :param tickers: Ticker to request prices for.
    :param start: Start point to request prices from (inclusive).
    :param end: End point until which to request prices (exclusive).
    :param interval: Frequency of requested prices.
    :returns: Dataframe with OHLCV data.
    """

    def download(
        tickers: str | list[str],  # noqa: ARG001
        start: str,
        end: str,
        interval: str = ValidYahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
        raw_yahoo_api_response = pd.DataFrame(
            {
                "Date": [start, end], "Open": [100.0, 101.0], "High": [105.0, 106.0],
                "Low":  [95.0, 96.0], "Close": [99.0, 100.0], "Volume": [1000, 2000],
            },
        )
        raw_yahoo_api_response.set_index("Date", inplace=True)

        return raw_yahoo_api_response

    with patch("apollo.api.yahoo_api_connector.download", download):
        yield


@pytest.fixture(name="empty_yahoo_api_response", scope="session")
def _empty_yahoo_api_response() -> Generator[None, None, None]:
    """
    Simulate empty Yahoo API OHLCV response.

    :param tickers: Ticker to request prices for.
    :param start: Start point to request prices from (inclusive).
    :param end: End point until which to request prices (exclusive).
    :param interval: Frequency of requested prices.
    :returns: Empty dataframe.
    """

    def download(
        tickers: str | list[str],  # noqa: ARG001
        start: str,
        end: str,
        interval: str = ValidYahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
        return pd.DataFrame()

    with patch("apollo.api.yahoo_api_connector.download", download):
        yield
