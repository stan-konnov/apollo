from unittest.mock import Mock

import pytest

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
