from datetime import datetime

from apollo.settings import DEFAULT_DATE_FORMAT


class PriceDataProvider:
    """
    Class to provide price data for a given instrument.

    Makes use of API and Database connectors to either fetch or retrieve data.
    """

    def __init__(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        frequency: str,
    ) -> None:
        """
        Construct Price Data Provider.

        :param ticker: Ticker to provide prices for.
        :param start_date: Start point to provide prices from (inclusive).
        :param end_date: End point until which to provide prices (exclusive).
        :param frequency: Frequency of provided prices.

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
