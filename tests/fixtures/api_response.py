from typing import Generator, Union
from unittest.mock import patch

import pandas as pd
import pytest

from apollo.settings import ValidYahooApiFrequencies


@pytest.fixture(name="yahoo_api_response", scope="session")
def _yahoo_api_response() -> Generator[None, None, None]:
    """Simulate raw Yahoo API OHLCV response."""

    def download(
        tickers: Union[str, list[str]],  # noqa: ARG001
        start: str,
        end: str,
        interval: str = ValidYahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
        raw_yahoo_api_response = pd.DataFrame(
            {
                "Date": [start, end],
                "Open": [100.0, 101.0],
                "High": [105.0, 106.0],
                "Low": [95.0, 96.0],
                "Close": [99.0, 100.0],
                "Volume": [1000, 2000],
            },
        )
        raw_yahoo_api_response.set_index("Date", inplace=True)

        return raw_yahoo_api_response

    with patch("apollo.api.yahoo_api_connector.download", download):
        yield


@pytest.fixture(name="empty_yahoo_api_response", scope="session")
def _empty_yahoo_api_response() -> Generator[None, None, None]:
    """Simulate empty Yahoo API OHLCV response."""

    def download(
        tickers: Union[str, list[str]],  # noqa: ARG001
        start: str,  # noqa: ARG001
        end: str,  # noqa: ARG001
        interval: str = ValidYahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
        return pd.DataFrame()

    with patch("apollo.api.yahoo_api_connector.download", download):
        yield
