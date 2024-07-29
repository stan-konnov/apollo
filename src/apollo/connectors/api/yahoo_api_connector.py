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
        frequency: str,
        request_arguments: dict,
    ) -> pd.DataFrame:
        """
        Request price data from Yahoo Finance.

        :param ticker: Ticker to request prices for.
        :param start_date: Start point to request prices from (inclusive).
        :param end_date: End point until which to request prices (exclusive).
        :param frequency: Frequency of requested prices.
        :returns: Dataframe with price data.

        :raises EmptyApiResponseError: If API response is empty.
        """

        price_data: pd.DataFrame = download(
            tickers=ticker,
            interval=frequency,
            **request_arguments,
        )

        # Make sure we have data to work with
        if price_data.empty:
            raise EmptyApiResponseError(
                "API response returned empty dataframe.",
            )

        return price_data
