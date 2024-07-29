from datetime import datetime
from logging import getLogger

import pandas as pd

from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.connectors.database.influxdb_connector import InfluxDbConnector
from apollo.settings import DEFAULT_DATE_FORMAT
from apollo.utils.price_data_availability_helper import PriceDataAvailabilityHelper

logger = getLogger(__name__)


class PriceDataProvider:
    """
    Price Data Provider class.

    Provides historical price data for a given
    ticker within a specified time frame and frequency.

    Makes use of API and Database connectors to
    either fetch data from remote source or retrieve data from disk.
    """

    def __init__(
        self,
        ticker: str,
        frequency: str,
        start_date: str,
        end_date: str,
        max_period: bool,
    ) -> None:
        """
        Construct Price Data Provider.

        :param ticker: Ticker to provide prices data for.
        :param frequency: Frequency of provided price data.
        :param start_date: Start point to provide price data from (inclusive).
        :param end_date: End point until which to provide prices data (exclusive).
        :param max_period: Flag to provide the maximum available period of price data.
        :returns: Dataframe with price data.

        :raises ValueError: If start_date or end_date are not in the correct format.
        :raises ValueError: If start_date is greater than end_date.
        """

        try:
            datetime.strptime(end_date, DEFAULT_DATE_FORMAT)
            datetime.strptime(start_date, DEFAULT_DATE_FORMAT)

        except ValueError as error:
            raise ValueError(
                f"Start and end date format must be {DEFAULT_DATE_FORMAT}.",
            ) from error

        # In our case a simple string compare is enough
        # since at this point we adhere to YYYY-MM-DD format
        if start_date > end_date:
            raise ValueError("Start date must be before end date.")

        self._ticker = ticker
        self._start_date = start_date
        self._end_date = end_date
        self._frequency = frequency
        self._max_period = max_period

        self._api_connector = YahooApiConnector()
        self._database_connector = InfluxDbConnector()

    def get_price_data(self) -> pd.DataFrame:
        """
        Request price data from API or read it from storage.

        If price data is missing from storage, prepare dataframe
        for consistency, adjust price values and save to storage.

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
            PriceDataAvailabilityHelper.check_if_price_data_needs_update(
                last_record_date,
            )
        )

        if price_data_needs_update:
            price_data = self._api_connector.request_price_data(
                ticker=self._ticker,
                start_date=self._start_date,
                end_date=self._end_date,
                max_period=self._max_period,
                frequency=self._frequency,
            )

            # At this point in time,
            # if prices were requested intraday
            # Yahoo Finance API sporadically returns an intraday close
            # which is undesirable, since it leads to data inconsistency.
            # If it is the case, we remove the last record from the dataframe.
            last_queried_datetime: datetime = price_data.index[-1]
            last_queried_date = last_queried_datetime.date()

            price_data_includes_intraday = (
                PriceDataAvailabilityHelper.check_if_price_data_includes_intraday(
                    last_queried_date,
                )
            )

            if price_data_includes_intraday:
                price_data.drop(index=last_queried_date, inplace=True)

            price_data = self._prepare_price_data(
                dataframe=price_data,
            )

            self._database_connector.write_price_data(
                frequency=self._frequency,
                dataframe=price_data,
            )

            logger.info("Requested price data from Yahoo Finance API.")

        # Otherwise, read from disk
        else:
            price_data = self._database_connector.read_price_data(
                ticker=self._ticker,
                start_date=self._start_date,
                end_date=self._end_date,
                max_period=self._max_period,
                frequency=self._frequency,
            )

            logger.info("Price data read from storage.")

        return price_data

    def _prepare_price_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare price data for consistency and storage.

        Reset indices, cast all columns to lowercase.
        Reindex the dataframe back by date column.
        Add ticker column at first position.

        Adjust OHLV values based on adjusted close to
        avoid inconsistencies around stock splits and dividends.

        :param dataframe: Dataframe with price data to prepare.
        :returns: Dataframe prepared for consistency and storage.
        """

        dataframe.reset_index(inplace=True)
        dataframe.columns = dataframe.columns.str.lower()
        dataframe.set_index("date", inplace=True)
        dataframe.insert(0, "ticker", self._ticker)

        # Determine adjustment factor based on adjusted close
        adjustment_factor = dataframe["adj close"] / dataframe["close"]

        # Adjust open, high, low and volume
        for column in ["open", "high", "low", "volume"]:
            dataframe[f"adj {column}"] = dataframe[column] * adjustment_factor

        return dataframe
