# ruff: noqa

# WIP

from datetime import datetime
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.connectors.database.influxdb_connector import InfluxDbConnector
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    START_DATE,
    TICKER,
)
from tests.fixtures.api_response import API_RESPONSE_DATAFRAME
from tests.fixtures.window_size_and_dataframe import SameDataframe


def test__get_price_data__with_valid_parameters_and_no_data_present() -> None:
    """
    Test get_price_data method with valid parameters.

    And no data present in the database.

    Data Provider must call InfluxDB connector to get last record date.
    Data Provider must call API connector to request price data.
    Data Provider must call InfluxDB connector to write price data.

    Data Provider must reindex the dataframe to date column.
    Data Provider must insert ticker column at first position.
    Data Provider must cast all columns to lowercase.
    Data Provider must adjust prices according to adjusted close.
    Data Provider must return a pandas Dataframe with price data.
    """

    price_data_provider = PriceDataProvider(
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=bool(MAX_PERIOD),
    )

    price_data_provider._api_connector = Mock(YahooApiConnector)  # noqa: SLF001
    price_data_provider._api_connector.request_price_data.return_value = (  # noqa: SLF001
        API_RESPONSE_DATAFRAME
    )

    price_data_provider._database_connector = Mock(InfluxDbConnector)  # noqa: SLF001
    price_data_provider._database_connector.get_last_record_date.return_value = None  # noqa: SLF001

    expected_dataframe_to_write = API_RESPONSE_DATAFRAME.copy()

    expected_dataframe_to_write.reset_index(inplace=True)
    expected_dataframe_to_write.columns = (
        expected_dataframe_to_write.columns.str.lower()
    )
    expected_dataframe_to_write.set_index("date", inplace=True)
    expected_dataframe_to_write.insert(0, "ticker", TICKER)

    adjustment_factor = (
        expected_dataframe_to_write["adj close"] / expected_dataframe_to_write["close"]
    )

    for column in ["open", "high", "low", "volume"]:
        expected_dataframe_to_write[f"adj {column}"] = (
            expected_dataframe_to_write[column] * adjustment_factor
        )

    price_dataframe = price_data_provider.get_price_data()

    price_data_provider._database_connector.get_last_record_date.assert_called_once_with(  # noqa: SLF001
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
    )

    price_data_provider._api_connector.request_price_data.assert_called_once_with(
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=bool(MAX_PERIOD),
    )

    price_data_provider._database_connector.write_price_data.assert_called_once_with(  # noqa: SLF001
        frequency=str(FREQUENCY),
        # Please see tests/fixtures/window_size_and_dataframe.py
        # for explanation on SameDataframe class
        dataframe=SameDataframe(expected_dataframe_to_write),
    )

    assert price_dataframe.index.name == "date"
    assert price_dataframe.columns[0] == "ticker"
    assert all(column.islower() for column in price_dataframe.columns)

    pd.testing.assert_frame_equal(price_dataframe, expected_dataframe_to_write)


def test__get_price_data__with_valid_parameters_and_data_present_no_refresh(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test get_price_data method with valid parameters.

    And data present in the database and needs no refresh.

    Data Provider must call InfluxDB connector to get last record date.
    Data Provider must not call API connector to request price data.
    Data Provider must call InfluxDB connector to read price data.
    Data Provider must return a pandas Dataframe with price data.
    """

    price_data_provider = PriceDataProvider(
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=bool(MAX_PERIOD),
    )

    price_data_provider._api_connector = Mock(YahooApiConnector)

    price_data_provider._database_connector = Mock(InfluxDbConnector)
    price_data_provider._database_connector.read_price_data.return_value = dataframe
    price_data_provider._database_connector.get_last_record_date.return_value = (
        datetime.now(
            tz=ZoneInfo("UTC"),
        ).date()
    )

    price_dataframe = price_data_provider.get_price_data()

    price_data_provider._database_connector.get_last_record_date.assert_called_once_with(  # noqa: SLF001
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
    )

    price_data_provider._api_connector.request_price_data.assert_not_called()

    price_data_provider._database_connector.read_price_data.assert_called_once_with(
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=bool(MAX_PERIOD),
    )

    pd.testing.assert_frame_equal(dataframe, price_dataframe)


# def test__get_price_data__with_valid_parameters_and_data_present_to_refresh() -> (  # noqa: E501
#     None
# ):
#     """
#     Test get_price_data method with valid parameters.

#     And data present in the database and needs refresh.

#     API Connector must call InfluxDB connector to get last record date.
#     API Connector must call InfluxDB connector to write price data.
#     API Connector must return a pandas Dataframe with price data.
#     """

#     price_data_provider = PriceDataProvider(
#         ticker=str(TICKER),
#         frequency=str(FREQUENCY),
#         start_date=str(START_DATE),
#         end_date=str(END_DATE),
#         max_period=bool(MAX_PERIOD),
#     )

#     expected_dataframe_to_write = API_RESPONSE_DATAFRAME.copy()

#     expected_dataframe_to_write.reset_index(inplace=True)
#     expected_dataframe_to_write.drop(columns="index", inplace=True)
#     expected_dataframe_to_write.columns = (
#         expected_dataframe_to_write.columns.str.lower()
#     )

#     expected_dataframe_to_write.set_index("date", inplace=True)
#     expected_dataframe_to_write.insert(0, "ticker", TICKER)

#     last_queried_datetime: datetime = expected_dataframe_to_write.index[-1]
#     last_queried_date = last_queried_datetime.date()

#     api_connector._database_connector = Mock(InfluxDbConnector)
#     api_connector._database_connector.get_last_record_date.return_value = (
#         last_queried_date
#     )

#     price_dataframe = api_connector.request_or_read_prices()

#     api_connector._database_connector.get_last_record_date.assert_called_once()
#     api_connector._database_connector.write_price_data.assert_called_once_with(
#         frequency=api_connector._frequency,
#         # Please see tests/fixtures/window_size_and_dataframe.py
#         # for explanation on SameDataframe class
#         dataframe=SameDataframe(expected_dataframe_to_write),
#     )

#     pd.testing.assert_frame_equal(price_dataframe, expected_dataframe_to_write)


# @pytest.mark.usefixtures("yahoo_api_response")
# def test__request_or_read_prices__with_max_period() -> None:
#     """
#     Test request_or_read_prices method with max_period.

#     API Connector must construct request arguments with period=max.
#     API Connector must call InfluxDB connector to get last record date.
#     API Connector must call InfluxDB connector without start and end date.
#     """

#     api_connector = YahooApiConnector(
#         ticker=str(TICKER),
#         start_date=str(START_DATE),
#         end_date=str(END_DATE),
#         max_period=True,
#     )

#     api_connector._database_connector = Mock(InfluxDbConnector)
#     api_connector._database_connector.get_last_record_date.return_value = datetime.now(
#         tz=ZoneInfo("UTC"),
#     ).date()

#     api_connector.request_or_read_prices()

#     api_connector._database_connector.get_last_record_date.assert_called_once()
#     api_connector._database_connector.read_price_data.assert_called_once_with(
#         ticker=TICKER,
#         frequency=api_connector._frequency,
#     )

#     assert api_connector._request_arguments["period"] == "max"


# @pytest.mark.usefixtures("yahoo_api_response")
# def test__request_or_read_prices__with_start_and_end_date() -> None:
#     """
#     Test request_or_read_prices method with start and end date.

#     API Connector must call InfluxDB connector to get last record date.
#     API Connector must call InfluxDB connector with start and end date.
#     API Connector must construct request arguments with start and end date.
#     """

#     api_connector = YahooApiConnector(
#         ticker=str(TICKER),
#         start_date=str(START_DATE),
#         end_date=str(END_DATE),
#         max_period=False,
#     )

#     api_connector._database_connector = Mock(InfluxDbConnector)
#     api_connector._database_connector.get_last_record_date.return_value = datetime.now(
#         tz=ZoneInfo("UTC"),
#     ).date()

#     api_connector.request_or_read_prices()

#     api_connector._database_connector.get_last_record_date.assert_called_once()
#     api_connector._database_connector.read_price_data.assert_called_once_with(
#         ticker=TICKER,
#         frequency=api_connector._frequency,
#         start_date=START_DATE,
#         end_date=END_DATE,
#     )

#     assert api_connector._request_arguments["start"] == START_DATE
#     assert api_connector._request_arguments["end"] == END_DATE


# @freeze_time(f"{END_DATE} 17:00:00")
# @pytest.mark.usefixtures("yahoo_api_response")
# def test__request_or_read_prices__with_valid_parameters_and_intraday_data() -> None:
#     """
#     Test request_or_read_prices method with valid parameters.

#     And requested data is intraday.

#     API Connector must parse last queried date.

#     API Connector must call InfluxDB connector to get last record date.
#     API Connector must call InfluxDB connector to write price data without intraday.
#     API Connector must return a pandas Dataframe with price data.
#     """

#     api_connector = YahooApiConnector(
#         ticker=str(TICKER),
#         start_date=str(START_DATE),
#         end_date=str(END_DATE),
#     )

#     api_connector._database_connector = Mock(InfluxDbConnector)
#     api_connector._database_connector.get_last_record_date.return_value = None

#     expected_dataframe_to_write = API_RESPONSE_DATAFRAME.copy()

#     expected_dataframe_to_write.reset_index(inplace=True)
#     expected_dataframe_to_write.drop(columns="index", inplace=True)
#     expected_dataframe_to_write.columns = (
#         expected_dataframe_to_write.columns.str.lower()
#     )

#     expected_dataframe_to_write.set_index("date", inplace=True)
#     expected_dataframe_to_write.insert(0, "ticker", TICKER)

#     expected_dataframe_to_write.drop(
#         index=expected_dataframe_to_write.index[-1],
#         inplace=True,
#     )

#     price_dataframe = api_connector.request_or_read_prices()

#     api_connector._database_connector.get_last_record_date.assert_called_once()
#     api_connector._database_connector.write_price_data.assert_called_once_with(
#         frequency=api_connector._frequency,
#         # Please see tests/fixtures/window_size_and_dataframe.py
#         # for explanation on SameDataframe class
#         dataframe=SameDataframe(expected_dataframe_to_write),
#     )

#     pd.testing.assert_frame_equal(price_dataframe, expected_dataframe_to_write)


def test__price_data_provider__with_invalid_date_format() -> None:
    """
    Test Price Data Provider method with invalid date format.

    Data Provider must raise a ValueError when dates are not in the correct format.
    """

    exception_message = f"Start and end date format must be {DEFAULT_DATE_FORMAT}."

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        PriceDataProvider(
            ticker=str(TICKER),
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date="01-01-2020",
            max_period=bool(MAX_PERIOD),
        )

    assert str(exception.value) == exception_message


def test__price_data_provider__with_invalid_dates() -> None:
    """
    Test Price Data Provider method with invalid dates.

    Data Provider must raise a ValueError when start_date is greater than end_date.
    """

    exception_message = "Start date must be before end date."

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        PriceDataProvider(
            ticker=str(TICKER),
            frequency=str(FREQUENCY),
            start_date="3333-01-01",
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

    assert str(exception.value) == exception_message
