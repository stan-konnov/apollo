from datetime import datetime
from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    END_DATE,
    START_DATE,
    YahooApiFrequencies,
)

API_RESPONSE_DATAFRAME = pd.DataFrame(
    {
        "Date": [
            datetime.strptime(str(START_DATE), DEFAULT_DATE_FORMAT),
            datetime.strptime(str(END_DATE), DEFAULT_DATE_FORMAT),
        ],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [99.0, 100.0],
        "Adj Close": [98.0, 99.0],
        "Volume": [1000, 2000],
    },
)
API_RESPONSE_DATAFRAME.set_index("Date", inplace=True)


@pytest.fixture(name="yahoo_api_response", scope="session")
def _yahoo_api_response() -> Generator[None, None, None]:
    """Simulate raw Yahoo API OHLCV response."""

    def download(
        tickers: str | list[str],  # noqa: ARG001
        start: str,  # noqa: ARG001
        end: str,  # noqa: ARG001
        interval: str = YahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
        return API_RESPONSE_DATAFRAME.copy()

    with patch("apollo.connectors.api.yahoo_api_connector.download", download):
        yield


@pytest.fixture(name="empty_yahoo_api_response", scope="session")
def _empty_yahoo_api_response() -> Generator[None, None, None]:
    """Simulate empty Yahoo API OHLCV response."""

    def download(
        tickers: str | list[str],  # noqa: ARG001
        start: str,  # noqa: ARG001
        end: str,  # noqa: ARG001
        interval: str = YahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
        return pd.DataFrame()

    with patch("apollo.connectors.api.yahoo_api_connector.download", download):
        yield
