from abc import ABC, abstractmethod
from datetime import datetime

from pandas import DataFrame

from apollo.settings import DEFAULT_DATE_FORMAT


class BaseApiConnector(ABC):
    """
    Base class for all API connectors.

    Defines interface to implement by child connectors.
    Contains the common attributes necessary for requesting price data.
    """

    def __init__(
        self,
        ticker: str,
        frequency: str,
        start_date: str | None = None,
        end_date: str | None = None,
        max_period: bool = False,
    ) -> None:
        """
        Construct Base API connector.

        :param ticker: Ticker to request prices for.
        :param frequency: Frequency of requested prices.
        :param start_date: Start point to request prices from (inclusive).
        :param end_date: End point until which to request prices (exclusive).
        :param max_period: Flag to request the maximum available period of prices.

        :raises ValueError: If neither max_period nor start_date and end_date are set.
        :raises ValueError: If both max_period and start_date and end_date are set.
        :raises ValueError: If start_date or end_date are not in the correct format.
        :raises ValueError: If start_date is greater than end_date.
        """

        self.ticker = ticker
        self.frequency = frequency

        if not max_period and not start_date and not end_date:
            raise ValueError(
                "Either start_date and end_date or max_period must be set.",
            )

        if max_period and (start_date or end_date):
            raise ValueError(
                "Either start_date and end_date or max_period must be set, not both.",
            )

        # If max period is provided,
        # then no start and end date are given
        # and we can set the flag to request the maximum period
        if max_period:
            self.max_period = max_period

        # Otherwise, start and end date are given
        # which we further validate and set if correct
        else:
            end_date = str(end_date)
            start_date = str(start_date)

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

            self.end_date = end_date
            self.start_date = start_date

    @abstractmethod
    def request_or_read_prices(self) -> DataFrame:
        """
        Request OHLCV from the API and return them as a dataframe.

        :returns: Dataframe with price data.
        """

    @abstractmethod
    def _prep_dataframe(self, dataframe: DataFrame) -> None:
        """
        Prepare dataframe based on specifics of the child connector.

        :param dataframe: Raw data from the API.
        """

    @abstractmethod
    def _save_dataframe(self, dataframe: DataFrame) -> None:
        """
        Save dataframe to disk based on specifics of the child connector.

        Can be file or remote storage.

        :param dataframe: Prepped dataframe for saving.
        """
