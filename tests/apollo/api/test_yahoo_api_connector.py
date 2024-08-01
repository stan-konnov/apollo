import pytest

from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.errors.api import EmptyApiResponseError
from apollo.settings import END_DATE, FREQUENCY, MAX_PERIOD, START_DATE, TICKER


@pytest.mark.usefixtures("empty_yahoo_api_response")
def test__request_price_data__with_empty_api_response() -> None:
    """
    Test request_price_data method with empty yahoo API response.

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

    assert str(exception.value) == exception_message
