from datetime import datetime
from unittest.mock import Mock

import pandas as pd
import pytest
from zoneinfo import ZoneInfo

from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.errors.api import EmptyApiResponseError
from apollo.settings import END_DATE, FREQUENCY, MAX_PERIOD, START_DATE, TICKER


@pytest.mark.usefixtures("yahoo_api_call")
def test__request_price_data__with_empty_api_response(yahoo_api_call: Mock) -> None:
    """
    Test request_price_data method with empty yahoo API response.

    API Connector must call Yahoo API to request price data.
    API Connector must raise EmptyApiResponseError when API response is empty.
    """

    api_connector = YahooApiConnector()

    exception_message = "API response returned empty dataframe."

    with pytest.raises(
        EmptyApiResponseError,
        match=exception_message,
    ) as exception:
        api_connector.request_price_data(
            ticker=str(TICKER),
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

    yahoo_api_call.assert_called_once()

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("yahoo_api_call", "api_response_dataframe")
def test__request_price_data__with_max_period_requested(
    yahoo_api_call: Mock,
    api_response_dataframe: pd.DataFrame,
) -> None:
    """
    Test request_price_data method with max period requested.

    API Connector must call Yahoo API to request price data with correct arguments.
    API Connector must return price data dataframe.
    """

    yahoo_api_call.return_value = api_response_dataframe

    api_connector = YahooApiConnector()

    price_dataframe = api_connector.request_price_data(
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=True,
    )

    yahoo_api_call.assert_called_once_with(
        tickers=str(TICKER),
        interval=str(FREQUENCY),
        period="max",
    )

    assert not price_dataframe.empty


@pytest.mark.usefixtures("yahoo_api_call", "api_response_dataframe")
def test__request_price_data__with_start_and_end_date_requested(
    yahoo_api_call: Mock,
    api_response_dataframe: pd.DataFrame,
) -> None:
    """
    Test request_price_data method with max period requested.

    API Connector must call Yahoo API to request price data with correct arguments.
    API Connector must return price data dataframe.
    """

    yahoo_api_call.return_value = api_response_dataframe

    api_connector = YahooApiConnector()

    price_dataframe = api_connector.request_price_data(
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=False,
    )

    yahoo_api_call.assert_called_once_with(
        tickers=str(TICKER),
        interval=str(FREQUENCY),
        start=str(START_DATE),
        end=str(END_DATE),
    )

    assert not price_dataframe.empty


@pytest.mark.usefixtures("yahoo_ticker_object")
def test__request_upcoming_earnings_date__for_returning_upcoming_earnings_date(
    yahoo_ticker_object: Mock,
) -> None:
    """
    Test request_upcoming_earnings_date method for returning upcoming earnings date.

    API Connector must return upcoming earnings date if it is available.
    """

    control_earnings_date = datetime.now(tz=ZoneInfo("UTC")).date()

    yahoo_ticker_object.calendar.__getitem__.return_value = [
        control_earnings_date,
    ]

    api_connector = YahooApiConnector()

    earnings_date = api_connector.request_upcoming_earnings_date(str(TICKER))

    assert earnings_date == control_earnings_date
