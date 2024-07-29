from abc import ABC, abstractmethod

from pandas import DataFrame


class BaseApiConnector(ABC):
    """
    Base class for all API connectors.

    Defines interface to implement by child connectors.
    """

    @abstractmethod
    def request_price_data(
        self,
        ticker: str,
        frequency: str,
        start_date: str,
        end_date: str,
        max_period: bool,
    ) -> DataFrame:
        """
        Request OHLCV from the API and return them as a dataframe.

        :param ticker: Ticker to request prices data for.
        :param frequency: Frequency of requested price data.
        :param start_date: Start point to request price data from (inclusive).
        :param end_date: End point until which to request prices data (exclusive).
        :param max_period: Flag to request the maximum available period of price data.
        :returns: Dataframe with price data.

        :raises EmptyApiResponseError: If API response is empty.
        """
