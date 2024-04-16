from pathlib import Path

import pandas as pd
import pytest

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.errors.api import EmptyApiResponseError
from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    END_DATE,
    START_DATE,
    TICKER,
)


@pytest.mark.usefixtures("temp_test_data_dir")
@pytest.mark.usefixtures("empty_yahoo_api_response")
def test__request_or_read_prices__with_empty_api_response() -> None:
    """
    Test request_or_read_prices method with empty yahoo API response.

    API Connector must raise am EmptyApiResponseError when API response is empty.
    """

    api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    with pytest.raises(
        EmptyApiResponseError,
        match="API response returned empty dataframe.",
    ) as exception:

        api_connector.request_or_read_prices()

    assert str(exception.value) == "API response returned empty dataframe."


@pytest.mark.usefixtures("temp_test_data_dir")
@pytest.mark.usefixtures("temp_test_data_file")
@pytest.mark.usefixtures("yahoo_api_response")
def test__request_or_read_prices__with_valid_parameters(
    temp_test_data_file: Path,
) -> None:
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
    assert Path.exists(temp_test_data_file)


@pytest.mark.usefixtures("temp_test_data_dir")
@pytest.mark.usefixtures("temp_test_data_file")
def test__request_or_read_prices__when_prices_already_requested_before(
    temp_test_data_file: Path,
) -> None:
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

    price_data_file = pd.read_csv(temp_test_data_file, index_col=0)
    price_data_file.index = pd.to_datetime(price_data_file.index)

    pd.testing.assert_frame_equal(price_data_file, price_dataframe)
    assert price_dataframe.index.name == price_data_file.index.name
    assert price_dataframe.index.dtype == price_data_file.index.dtype


def test__request_or_read_prices__with_invalid_date_format() -> None:
    """
    Test request_or_read_prices method with invalid date format.

    API Connector must raise a ValueError when dates are not in the correct format.
    """

    with pytest.raises(
        ValueError,
        match=f"Start and end date format must be {DEFAULT_DATE_FORMAT}.",
    ) as exception:

        YahooApiConnector(
            ticker=str(TICKER),
            start_date=str(START_DATE),
            end_date="01-01-2020",
        )

    assert str(exception.value) == (
        f"Start and end date format must be {DEFAULT_DATE_FORMAT}."
    )


def test__request_or_read_prices__with_invalid_dates() -> None:
    """
    Test request_or_read_prices method with invalid dates.

    API Connector must raise a ValueError when start_date is greater than end_date.
    """

    with pytest.raises(
        ValueError,
        match="Start date must be before end date.",
    ) as exception:

        YahooApiConnector(
            ticker=str(TICKER),
            start_date="3333-01-01",
            end_date=str(END_DATE),
        )

    assert str(exception.value) == "Start date must be before end date."
