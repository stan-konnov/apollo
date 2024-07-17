import pandas as pd
from pydantic import BaseModel


class BacktestingResult(BaseModel):
    """A data model to represent backtesting result."""

    def __init__(
        self,
        ticker: str,
        strategy: str,
        frequency: str,
        max_period: bool,
        parameters: dict[str, float],
        backtesting_results: pd.Series,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> None:
        """
        Construct a new Backtesting Result object.

        :param ticker: Instrument ticker symbol.
        :param strategy: Strategy name.
        :param frequency: Frequency of the data.
        :param max_period: Flag indicating if maximum available data was used.
        :param parameters: Best performing strategy parameters.
        :param backtesting_results: Backtesting results.
        :param start_date: Start date of the backtesting period.
        :param end_date: End date of the backtesting period.

        :raises ValueError: If both start_date and end_date provided with max_period.
        """

        if start_date and end_date and max_period:
            raise ValueError(
                "Either start_date and end_date or max_period should be provided.",
            )

        self.ticker = ticker
        self.strategy = strategy
        self.frequency = frequency
        self.max_period = max_period

        self.parameters = parameters
        self.backtesting_results = backtesting_results
