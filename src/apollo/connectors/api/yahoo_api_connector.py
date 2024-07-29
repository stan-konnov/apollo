import pandas as pd
from yfinance import download

from apollo.connectors.api.base_api_connector import BaseApiConnector
from apollo.errors.api import EmptyApiResponseError


class YahooApiConnector(BaseApiConnector):
    """
    API connector for Yahoo Finance.

    Acts as a wrapper around Yahoo Finance API to request price data.
    """

    def request_price_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        max_period: bool,
        frequency: str,
    ) -> pd.DataFrame:
        """
        Request price data from Yahoo Finance.

        Deduce the request arguments
        based on the provided max period flag.

        :param ticker: Ticker to request prices data for.
        :param start_date: Start point to request price data from (inclusive).
        :param end_date: End point until which to request prices data (exclusive).
        :param max_period: Flag to request the maximum available period of price data.
        :param frequency: Frequency of requested price data.
        :returns: Dataframe with price data.

        :raises EmptyApiResponseError: If API response is empty.
        """

        price_data: pd.DataFrame

        # If max period is requested
        # request prices without start and end date
        if max_period:
            price_data = download(
                tickers=ticker,
                interval=frequency,
                period="max",
            )
        # Otherwise, request prices with bounds
        else:
            price_data = download(
                tickers=ticker,
                interval=frequency,
                start=start_date,
                end=end_date,
            )

        # Make sure we have data to work with
        if price_data.empty:
            raise EmptyApiResponseError(
                "API response returned empty dataframe.",
            )

        return price_data
