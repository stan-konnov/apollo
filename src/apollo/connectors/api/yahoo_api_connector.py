import pandas as pd
from yfinance import download

from apollo.errors.api import EmptyApiResponseError


class YahooApiConnector:
    """
    API connector for Yahoo Finance.

    Acts as a wrapper around Yahoo Finance API to request price data.
    """

    def request_prices(
        self,
        ticker: str,
        frequency: str,
        request_arguments: dict,
    ) -> pd.DataFrame:
        """
        Request prices from Yahoo Finance.

        :param ticker: Instrument symbol.
        :param frequency: Frequency of the data.
        :param request_arguments: Additional arguments for the request.
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
