from datetime import datetime
from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from apollo.settings import DEFAULT_DATE_FORMAT, YahooApiFrequencies


@pytest.fixture(name="yahoo_api_response", scope="session")
def _yahoo_api_response() -> Generator[None, None, None]:
    """Simulate raw Yahoo API OHLCV response."""

    def download(
        tickers: str | list[str],  # noqa: ARG001
        start: str,
        end: str,
        interval: str = YahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
        raw_yahoo_api_response = pd.DataFrame(
            {
                "Date": [
                    datetime.strptime(start, DEFAULT_DATE_FORMAT),
                    datetime.strptime(end, DEFAULT_DATE_FORMAT),
                ],
                "Open": [100.0, 101.0],
                "High": [105.0, 106.0],
                "Low": [95.0, 96.0],
                "Close": [99.0, 100.0],
                "Volume": [1000, 2000],
            },
        )
        raw_yahoo_api_response.set_index("Date", inplace=True)

        return raw_yahoo_api_response

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
