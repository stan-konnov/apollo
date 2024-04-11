from os import curdir
from pathlib import Path
from unittest.mock import patch

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.settings import END_DATE, START_DATE, TICKER
from tests.fixtures.api_response import yahoo_download_mock


@patch("apollo.api.yahoo_api_connector.download", yahoo_download_mock)
@patch(
    "apollo.api.yahoo_api_connector.DATA_DIR",
    Path(f"{Path(curdir).resolve()}/tests/data"),
)
def test__request_or_read_prices__with_valid_parameters() -> None:
    """
    Test request_or_read_prices method with valid parameters.

    API Connector must be properly constructed.
    API Connector must return a pandas DataFrame with price data.
    API Connector must cast all columns to lowercase.
    API Connector must reindex the dataframe to date column.
    API Connector must save the dataframe to a CSV file.
    """

    api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    api_connector.request_or_read_prices()
