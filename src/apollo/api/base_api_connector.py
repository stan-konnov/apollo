from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseApiConnector(ABC):
    """
    Base class for all API connectors.

    Defines interface to implement by child connectors.
    Contains the common attributes necessary for requesting price data.
    """

    def __init__(
            self,
            ticker: str,
            start_date: str,
            end_date: str,
            frequency: str,
        ) -> None:
        """
        Construct Base API connector.

        :param ticker: Ticker to request prices for.
        :param start_date: Start point to request prices from (inclusive).
        :param end_date: End point until which to request prices (exclusive).
        :param frequency: Frequency of requested prices.
        """

        # In our case a simple string compare is enough
        # since we are using the same YYYY-MM-DD format everywhere
        if start_date > end_date:
            raise ValueError("Start date must be before end date.")

        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency


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
