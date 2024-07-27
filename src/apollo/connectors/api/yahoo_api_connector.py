from logging import getLogger
from typing import TYPE_CHECKING

import pandas as pd
from yfinance import download

from apollo.connectors.api.base_api_connector import BaseApiConnector
from apollo.connectors.database.influxdb_connector import InfluxDbConnector
from apollo.errors.api import EmptyApiResponseError
from apollo.settings import YahooApiFrequencies
from apollo.utils.data_availability_helper import DataAvailabilityHelper

if TYPE_CHECKING:
    from datetime import datetime

logger = getLogger(__name__)


class YahooApiConnector(BaseApiConnector):
    """
    API connector for Yahoo Finance.

    Connects to Yahoo Finance API to request price data.
    """

    def __init__(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        max_period: bool = False,
        frequency: str = YahooApiFrequencies.ONE_DAY.value,
    ) -> None:
        """
        Construct Yahoo API connector.

        :param ticker: Ticker to request prices for.
        :param start_date: Start point to request prices from (inclusive).
        :param end_date: End point until which to request prices (exclusive).
        :param max_period: Flag to request the maximum available period of prices.
        :param frequency: Frequency of requested prices.
        """

        super().__init__(
            ticker,
            start_date,
            end_date,
            frequency,
        )

        self._request_arguments = {}
        self._querydb_arguments = {
            "ticker": self._ticker,
            "frequency": self._frequency,
        }

        if max_period:
            self._request_arguments["period"] = "max"

        else:
            self._request_arguments["end"] = self._end_date
            self._request_arguments["start"] = self._start_date

            self._querydb_arguments["end_date"] = self._end_date
            self._querydb_arguments["start_date"] = self._start_date

        self._database_connector = InfluxDbConnector()

    def request_or_read_prices(self) -> pd.DataFrame:
        """
        Request prices from Yahoo Finance or read them from storage.

        If prices are missing, prepare dataframe for consistency and save to storage.

        :returns: Dataframe with price data.
        """

        price_data: pd.DataFrame

        last_record_date = self._database_connector.get_last_record_date(
            ticker=self._ticker,
            frequency=self._frequency,
        )

        # Re-query prices
        # if no records are available
        # or last record date is before previous business day
        # or last record date is previous business day and data available from exchange
        price_data_needs_update = last_record_date is None or (
            DataAvailabilityHelper.check_if_price_data_needs_update(last_record_date)
        )

        if price_data_needs_update:
            price_data = download(
                tickers=self._ticker,
                interval=self._frequency,
                **self._request_arguments,
            )

            # Make sure we have data to work with
            if price_data.empty:
                raise EmptyApiResponseError(
                    "API response returned empty dataframe.",
                )

            # At this point in time,
            # if prices were requested intraday
            # Yahoo Finance API sporadically returns an intraday close
            # which is undesirable, since it leads to data inconsistency.
            # If it is the case, we remove the last record from the dataframe.
            last_queried_datetime: datetime = price_data.index[-1]
            last_queried_date = last_queried_datetime.date()

            price_data_includes_intraday = (
                DataAvailabilityHelper.check_if_price_data_includes_intraday(
                    last_queried_date,
                )
            )

            if price_data_includes_intraday:
                price_data.drop(index=last_queried_date, inplace=True)

            self._prep_dataframe(price_data)
            self._save_dataframe(price_data)

            logger.info("Requested price data from Yahoo Finance API.")

        # Otherwise, read from disk
        else:
            price_data = self._database_connector.read_price_data(
                **self._querydb_arguments,
            )

            logger.info("Price data read from storage.")

        return price_data

    def _prep_dataframe(self, dataframe: pd.DataFrame) -> None:
        """
        Prepare Dataframe for consistency.

        Reset indices,
        Cast columns to lowercase.
        Reset indices back to date column.
        Add ticker column.

        :param dataframe: Requested Dataframe.
        """

        # Adjusted Open = Open * Adjusted Close / Unadjusted Close

        # Adjusted High = High * Adjusted Close / Close

        # Adjusted Low = Low * Adjusted Close / Close

        # Adjusted volume = Volume / (Adjusted Close / Close)

        dataframe.reset_index(inplace=True)
        dataframe.columns = dataframe.columns.str.lower()

        dataframe.set_index("date", inplace=True)
        dataframe.insert(0, "ticker", self._ticker)

        dataframe["adj open"] = (
            dataframe["open"] * dataframe["adj close"] / dataframe["close"]
        )
        dataframe["adj high"] = (
            dataframe["high"] * dataframe["adj close"] / dataframe["close"]
        )
        dataframe["adj low"] = (
            dataframe["low"] * dataframe["adj close"] / dataframe["close"]
        )
        dataframe["adj volume"] = dataframe["volume"] / (
            dataframe["adj close"] / dataframe["close"]
        )

    def _save_dataframe(self, dataframe: pd.DataFrame) -> None:
        """
        Save dataframe as CSV to storage.

        :param dataframe: Requested Dataframe.
        """

        self._database_connector.write_price_data(
            frequency=self._frequency,
            dataframe=dataframe,
        )
