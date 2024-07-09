from datetime import datetime
from logging import getLogger

import pandas as pd
from yfinance import download
from zoneinfo import ZoneInfo

from apollo.connectors.api.base_api_connector import BaseApiConnector
from apollo.connectors.database.influxdb_connector import InfluxDbConnector
from apollo.errors.api import EmptyApiResponseError
from apollo.settings import YahooApiFrequencies
from apollo.utils.data_availability_helper import DataAvailabilityHelper

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

        self.request_arguments = {}

        if max_period:
            self.request_arguments["period"] = "max"

        else:
            self.request_arguments["end"] = self.end_date
            self.request_arguments["start"] = self.start_date

        self.database_connector = InfluxDbConnector()

    def request_or_read_prices(self) -> pd.DataFrame:
        """
        Request prices from Yahoo Finance or read them from storage.

        If prices are missing, prepare dataframe for consistency and save to storage.

        :returns: Dataframe with price data.
        """

        price_data: pd.DataFrame

        last_record_date = self.database_connector.get_last_record_date()

        # Re-query prices
        # if no records are available
        # or last record date is before previous business day
        # or last record date is previous business day and data available from exchange
        price_data_needs_update = last_record_date is None or (
            DataAvailabilityHelper.check_if_price_data_needs_update(last_record_date)
        )

        if price_data_needs_update:
            price_data = download(
                tickers=self.ticker,
                interval=self.frequency,
                **self.request_arguments,
            )

            # NOTE: this might not work over weekend, check!
            # At this point in time, if prices were requested
            # intraday, yahoo finance API will return intraday close
            # which is undesirable as it can lead to data inconsistency
            # Therefore, we can check if data should be available and drop last row
            if not DataAvailabilityHelper.check_if_data_available_from_exchange(
                datetime.now(ZoneInfo("UTC")),
            ):
                price_data = price_data.iloc[: price_data.shape[0] - 2]

            # Make sure we have data to work with
            if price_data.empty:
                raise EmptyApiResponseError(
                    "API response returned empty dataframe.",
                ) from None

            self._prep_dataframe(price_data)
            self._save_dataframe(price_data)

            logger.info("Requested price data from Yahoo Finance API.")

        # Otherwise, read from disk
        else:
            price_data = pd.DataFrame()

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

        dataframe.reset_index(inplace=True)
        dataframe.columns = dataframe.columns.str.lower()

        dataframe.set_index("date", inplace=True)
        dataframe.insert(0, "ticker", self.ticker)

    def _save_dataframe(self, dataframe: pd.DataFrame) -> None:
        """
        Save dataframe as CSV to storage.

        Use "Ticker-Frequency-Start-End" format for filename.
        In the current state of things, local file system
        serves well as storage, move to S3 or database with time.

        :param dataframe: Requested Dataframe.
        """

        self.database_connector.write_price_data(self.frequency, dataframe)
