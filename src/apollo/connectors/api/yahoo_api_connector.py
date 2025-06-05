from datetime import date

import pandas as pd
from yfinance import Ticker, download

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
        frequency: str,
        start_date: str,
        end_date: str,
        max_period: bool,
    ) -> pd.DataFrame:
        """
        Request price data from Yahoo Finance.

        :param ticker: Ticker to request prices data for.
        :param frequency: Frequency of requested price data.
        :param start_date: Start point to request price data from (inclusive).
        :param end_date: End point until which to request prices data (exclusive).
        :param max_period: Flag to request the maximum available period of price data.
        :returns: Dataframe with price data.

        :raises EmptyApiResponseError: If API response is empty.
        """

        price_data: pd.DataFrame | None

        # If max period is requested
        # request prices without start and end date
        if max_period:
            price_data = download(
                tickers=ticker,
                interval=frequency,
                period="max",
                # NOTE: we do not auto-adjust prices
                # since we make use of both adjusted and unadjusted prices
                auto_adjust=False,
            )
        # Otherwise, request prices with bounds
        else:
            price_data = download(
                tickers=ticker,
                interval=frequency,
                start=start_date,
                end=end_date,
                auto_adjust=False,
            )

        # Make sure we have data to work with
        if price_data is None or price_data.empty:
            raise EmptyApiResponseError(
                "API response returned empty dataframe.",
            )

        return price_data

    def request_upcoming_earnings_date(self, ticker: str) -> date | None:
        """Request upcoming earnings date for the provided ticker."""

        # Instantiate ticker object
        ticker_object = Ticker(ticker)

        # Get the closest earnings date if available
        return (
            ticker_object.calendar["Earnings Date"][0]
            if ticker_object.calendar["Earnings Date"]
            else None
        )
