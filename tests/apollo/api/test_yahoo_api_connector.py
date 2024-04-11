from os import curdir
from pathlib import Path
from shutil import rmtree
from typing import Generator
from unittest.mock import patch

import pytest

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.settings import END_DATE, START_DATE, TICKER, ValidYahooApiFrequencies
from tests.mocks.api_response import yahoo_api_response

TEST_DATA_DIR = Path(f"{Path(curdir).resolve()}/tests/data")


@pytest.fixture(scope="session", autouse=True)
def _clean_test_data() -> Generator[None, None, None]:
    """Clean test data directory after tests."""
    yield
    rmtree(TEST_DATA_DIR)


@patch("apollo.api.yahoo_api_connector.download", yahoo_api_response)
@patch("apollo.api.yahoo_api_connector.DATA_DIR", TEST_DATA_DIR)
def test__request_or_read_prices__with_valid_parameters() -> None:
    """
    Test request_or_read_prices method with valid parameters.

    API Connector must return a pandas Dataframe with price data.
    API Connector must reindex the dataframe to date column.
    API Connector must cast all columns to lowercase.
    API Connector must save the dataframe to file.
    """

    api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    price_dataframe = api_connector.request_or_read_prices()

    assert price_dataframe is not None
    assert price_dataframe.index.name == "date"
    assert all(column.islower() for column in price_dataframe.columns)
    assert Path.exists(
        Path(
            f"{TEST_DATA_DIR}/{TICKER}-"
            f"{ValidYahooApiFrequencies.ONE_DAY.value}-"
            f"{START_DATE}-{END_DATE}.csv",
        ),
    )


@patch("apollo.api.yahoo_api_connector.DATA_DIR", TEST_DATA_DIR)
def test__request_or_read_prices__when_prices_already_requested_before() -> None:
    """
    Test request_or_read_prices when prices have already been requested before.

    API Connector must return a pandas Dataframe with price data read from file.
    API Connector must reindex the dataframe to date column.
    The type of index column must be datetime.
    """

    api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    price_dataframe = api_connector.request_or_read_prices()

    assert price_dataframe is not None
    assert price_dataframe.index.name == "date"
    assert price_dataframe.index.dtype == "datetime64[ns]"
