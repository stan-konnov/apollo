import pandas as pd
from prisma import Prisma

from apollo.models.backtesting_result import BacktestingResult


class PostgresConnector:
    """
    Postgres Database connector class.

    Acts as a wrapper around Prisma Python client.
    """

    database_client: Prisma

    def __init__(self) -> None:
        """
        Construct Postgres Database Connector.

        Initialize Prisma client.
        """

        if not self.database_client:
            self.database_client = Prisma()

    def write_backtesting_results(
        self,
        ticker: str,
        strategy: str,
        frequency: str,
        max_period: bool,
        parameters: dict[str, float],
        backtesting_results: pd.DataFrame,
        backtesting_end_date: str | None = None,
        backtesting_start_date: str | None = None,
    ) -> None:
        """
        Write backtesting results to the database.

        :param ticker: Ticker symbol.
        :param strategy: Strategy name.
        :param frequency: Frequency of the data.
        :param max_period: If all available data was used.
        :param parameters: Best performing strategy parameters.
        :param backtesting_results: Backtesting results Dataframe.
        :param backtesting_end_date: End date of the backtesting period.
        :param backtesting_start_date: Start date of the backtesting period.
        """

        self.database_client.connect()

        BacktestingResult(
            ticker=ticker,
            strategy=strategy,
            frequency=frequency,
            max_period=max_period,
            parameters=parameters,
            end_date=backtesting_end_date,
            start_date=backtesting_start_date,
            backtesting_results=backtesting_results,
        )

        self.database_client.disconnect()
