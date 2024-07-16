from datetime import datetime
from unittest.mock import Mock

import pandas as pd
import pytest
from freezegun import freeze_time
from zoneinfo import ZoneInfo

from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.connectors.database.influxdb_connector import InfluxDbConnector
from apollo.errors.api import (
    ApiResponseDatetimeIndexError,
    ApiResponseEmptyDataframeError,
)
from apollo.settings import (
    DEFAULT_DATE_FORMAT,
)
from tests.fixtures.api_response import API_RESPONSE_DATAFRAME
from tests.fixtures.env_and_constants import END_DATE, START_DATE, TICKER
from tests.fixtures.window_size_and_dataframe import SameDataframe


@pytest.mark.usefixtures("empty_yahoo_api_response")
def test__request_or_read_prices__with_empty_api_response() -> None:
    """
    Test request_or_read_prices method with empty yahoo API response.

    API Connector must call InfluxDB connector to get last record date.
    API Connector must raise ApiResponseEmptyDataframeError when API response is empty.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.get_last_record_date.return_value = None

    exception_message = "API response returned empty dataframe."

    with pytest.raises(
        ApiResponseEmptyDataframeError,
        match=exception_message,
    ) as exception:
        api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("non_date_index_yahoo_api_response")
def test__request_or_read_prices__with_non_date_index_api_response() -> None:
    """
    Test request_or_read_prices method with yahoo API response.

    Returned dataframe is not indexed by datetime.

    API Connector must call InfluxDB connector to get last record date.
    API Connector must raise ApiResponseEmptyDataframeError when API response is empty.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.get_last_record_date.return_value = None

    exception_message = "Dataframe received from API is not indexed by datetime."

    with pytest.raises(
        ApiResponseDatetimeIndexError,
        match=exception_message,
    ) as exception:
        api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("yahoo_api_response")
def test__request_or_read_prices__with_valid_parameters_and_no_data_present() -> None:
    """
    Test request_or_read_prices method with valid parameters.

    And no data present in the database.

    API Connector must call InfluxDB connector to get last record date.
    API Connector must call InfluxDB connector to write price data.

    API Connector must reindex the dataframe to date column.
    API Connector must insert ticker column at first position.
    API Connector must cast all columns to lowercase.
    API Connector must return a pandas Dataframe with price data.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.get_last_record_date.return_value = None

    expected_dataframe_to_write = API_RESPONSE_DATAFRAME.copy()

    expected_dataframe_to_write.reset_index(inplace=True)
    expected_dataframe_to_write.drop(columns="index", inplace=True)
    expected_dataframe_to_write.columns = (
        expected_dataframe_to_write.columns.str.lower()
    )

    expected_dataframe_to_write.set_index("date", inplace=True)
    expected_dataframe_to_write.insert(0, "ticker", TICKER)

    price_dataframe = api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()
    api_connector.database_connector.write_price_data.assert_called_once_with(
        frequency=api_connector.frequency,
        # Please see tests/fixtures/window_size_and_dataframe.py
        # for explanation on SameDataframe class
        dataframe=SameDataframe(expected_dataframe_to_write),
    )

    assert price_dataframe.index.name == "date"
    assert price_dataframe.columns[0] == "ticker"
    assert all(column.islower() for column in price_dataframe.columns)

    pd.testing.assert_frame_equal(price_dataframe, expected_dataframe_to_write)


@pytest.mark.usefixtures("yahoo_api_response", "dataframe")
def test__request_or_read_prices__with_valid_parameters_and_data_present_no_refresh(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test request_or_read_prices method with valid parameters.

    And data present in the database and needs no refresh.

    API Connector must call InfluxDB connector to get last record date.
    API Connector must call InfluxDB connector to read price data.
    API Connector must return a pandas Dataframe with price data.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.read_price_data.return_value = dataframe
    api_connector.database_connector.get_last_record_date.return_value = datetime.now(
        tz=ZoneInfo("UTC"),
    ).date()

    price_dataframe = api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()
    api_connector.database_connector.read_price_data.assert_called_once()

    pd.testing.assert_frame_equal(dataframe, price_dataframe)


@pytest.mark.usefixtures("yahoo_api_response")
def test__request_or_read_prices__with_valid_parameters_and_data_present_to_refresh() -> (  # noqa: E501
    None
):
    """
    Test request_or_read_prices method with valid parameters.

    And data present in the database and needs refresh.

    API Connector must call InfluxDB connector to get last record date.
    API Connector must call InfluxDB connector to write price data.
    API Connector must return a pandas Dataframe with price data.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    expected_dataframe_to_write = API_RESPONSE_DATAFRAME.copy()

    expected_dataframe_to_write.reset_index(inplace=True)
    expected_dataframe_to_write.drop(columns="index", inplace=True)
    expected_dataframe_to_write.columns = (
        expected_dataframe_to_write.columns.str.lower()
    )

    expected_dataframe_to_write.set_index("date", inplace=True)
    expected_dataframe_to_write.insert(0, "ticker", TICKER)

    last_queried_datetime: datetime = expected_dataframe_to_write.index[-1]
    last_queried_date = last_queried_datetime.date()

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.get_last_record_date.return_value = (
        last_queried_date
    )

    price_dataframe = api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()
    api_connector.database_connector.write_price_data.assert_called_once_with(
        frequency=api_connector.frequency,
        # Please see tests/fixtures/window_size_and_dataframe.py
        # for explanation on SameDataframe class
        dataframe=SameDataframe(expected_dataframe_to_write),
    )

    pd.testing.assert_frame_equal(price_dataframe, expected_dataframe_to_write)


@pytest.mark.usefixtures("yahoo_api_response")
def test__request_or_read_prices__with_max_period() -> None:
    """
    Test request_or_read_prices method with max_period.

    API Connector must construct request arguments with period=max.
    API Connector must call InfluxDB connector to get last record date.
    API Connector must call InfluxDB connector without start and end date.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
        max_period=True,
    )

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.get_last_record_date.return_value = datetime.now(
        tz=ZoneInfo("UTC"),
    ).date()

    api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()
    api_connector.database_connector.read_price_data.assert_called_once_with(
        ticker=TICKER,
        frequency=api_connector.frequency,
    )

    assert api_connector.request_arguments["period"] == "max"


@pytest.mark.usefixtures("yahoo_api_response")
def test__request_or_read_prices__with_start_and_end_date() -> None:
    """
    Test request_or_read_prices method with start and end date.

    API Connector must call InfluxDB connector to get last record date.
    API Connector must call InfluxDB connector with start and end date.
    API Connector must construct request arguments with start and end date.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
        max_period=False,
    )

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.get_last_record_date.return_value = datetime.now(
        tz=ZoneInfo("UTC"),
    ).date()

    api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()
    api_connector.database_connector.read_price_data.assert_called_once_with(
        ticker=TICKER,
        frequency=api_connector.frequency,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    assert api_connector.request_arguments["start"] == START_DATE
    assert api_connector.request_arguments["end"] == END_DATE


@freeze_time(f"{END_DATE} 17:00:00")
@pytest.mark.usefixtures("yahoo_api_response")
def test__request_or_read_prices__with_valid_parameters_and_intraday_data() -> None:
    """
    Test request_or_read_prices method with valid parameters.

    And requested data is intraday.

    API Connector must parse last queried date.

    API Connector must call InfluxDB connector to get last record date.
    API Connector must call InfluxDB connector to write price data without intraday.
    API Connector must return a pandas Dataframe with price data.
    """

    api_connector = YahooApiConnector(
        ticker=TICKER,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    api_connector.database_connector = Mock(InfluxDbConnector)
    api_connector.database_connector.get_last_record_date.return_value = None

    expected_dataframe_to_write = API_RESPONSE_DATAFRAME.copy()

    expected_dataframe_to_write.reset_index(inplace=True)
    expected_dataframe_to_write.drop(columns="index", inplace=True)
    expected_dataframe_to_write.columns = (
        expected_dataframe_to_write.columns.str.lower()
    )

    expected_dataframe_to_write.set_index("date", inplace=True)
    expected_dataframe_to_write.insert(0, "ticker", TICKER)

    expected_dataframe_to_write.drop(
        index=expected_dataframe_to_write.index[-1],
        inplace=True,
    )

    price_dataframe = api_connector.request_or_read_prices()

    api_connector.database_connector.get_last_record_date.assert_called_once()
    api_connector.database_connector.write_price_data.assert_called_once_with(
        frequency=api_connector.frequency,
        # Please see tests/fixtures/window_size_and_dataframe.py
        # for explanation on SameDataframe class
        dataframe=SameDataframe(expected_dataframe_to_write),
    )

    pd.testing.assert_frame_equal(price_dataframe, expected_dataframe_to_write)


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
            ticker=TICKER,
            start_date=START_DATE,
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
            ticker=TICKER,
            start_date="3333-01-01",
            end_date=END_DATE,
        )

    assert str(exception.value) == "Start date must be before end date."
