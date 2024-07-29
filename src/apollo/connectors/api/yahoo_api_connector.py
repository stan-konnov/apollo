import pandas as pd
from yfinance import download

from apollo.errors.api import EmptyApiResponseError


class YahooApiConnector:
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

        :param ticker: Ticker to request prices for.
        :param start_date: Start point to request prices from (inclusive).
        :param end_date: End point until which to request prices (exclusive).
        :param max_period: Flag to request the maximum available period.
        :param frequency: Frequency of requested prices.
        :returns: Dataframe with price data.

        :raises EmptyApiResponseError: If API response is empty.
        """

        price_data: pd.DataFrame

        if max_period:
            # Request prices without start and end date
            price_data = download(
                tickers=ticker,
                interval=frequency,
                period="max",
            )
        else:
            # Otherwise, request prices with bounds
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
