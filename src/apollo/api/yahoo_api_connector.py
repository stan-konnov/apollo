from logging import getLogger
from pathlib import Path

import pandas as pd
from yfinance import download

from apollo.api.base_api_connector import BaseApiConnector
from apollo.errors.api import EmptyApiResponseError
from apollo.settings import DATA_DIR, ValidYahooApiFrequencies

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
        frequency: str = ValidYahooApiFrequencies.ONE_DAY.value,
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

        self.max_period = max_period

        # Name of the file to store the data
        period = "max" if max_period else f"{start_date}-{end_date}"
        self.data_file: str = f"{DATA_DIR}/{self.ticker}-{self.frequency}-{period}.csv"

    def request_or_read_prices(self) -> pd.DataFrame:
        """
        Request prices from Yahoo Finance or read them from storage.

        If prices are missing, prepare dataframe for consistency and save to storage.

        :returns: Dataframe with price data.
        """

        price_data: pd.DataFrame

        try:
            price_data = pd.read_csv(self.data_file, index_col=0)

            # We always index by date,
            # therefore, we cast indices to datetime.
            price_data.index = pd.to_datetime(price_data.index)

            logger.info("Price data read from storage.")

        except FileNotFoundError:
            period_arguments = {}

            if self.max_period:
                period_arguments["period"] = "max"

            else:
                period_arguments["end"] = self.end_date
                period_arguments["start"] = self.start_date

            price_data = download(
                tickers=self.ticker,
                interval=self.frequency,
                **period_arguments,
            )

            # Make sure we have data to work with
            if price_data.empty:
                raise EmptyApiResponseError(
                    "API response returned empty dataframe.",
                ) from None

            self._prep_dataframe(price_data)
            self._save_dataframe(price_data)

            logger.info("Requested price data from Yahoo Finance API.")

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

        if not Path.is_dir(DATA_DIR):
            DATA_DIR.mkdir(parents=True, exist_ok=True)

        dataframe.to_csv(self.data_file)
