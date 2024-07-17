import pandas as pd
from prisma import Prisma

from apollo.models.backtesting_result import BacktestingResult


class PostgresConnector:
    """
    Postgres Database connector class.

    Acts as a wrapper around Prisma Python client.
    """

    def __init__(self) -> None:
        """
        Construct Postgres Database Connector.

        Initialize Prisma client.
        """

        self.database_client = Prisma()

    def write_backtesting_results(
        self,
        ticker: str,
        strategy: str,
        frequency: str,
        max_period: bool,
        parameters: str,
        backtesting_results: pd.DataFrame,
        backtesting_end_date: str,
        backtesting_start_date: str,
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

        # Connect to the database
        self.database_client.connect()

        # Map incoming inputs to the database model
        backtesting_result = BacktestingResult(
            ticker=ticker,
            strategy=strategy,
            frequency=frequency,
            max_period=max_period,
            parameters=parameters,
            backtesting_results=backtesting_results,
            backtesting_end_date=backtesting_end_date,
            backtesting_start_date=backtesting_start_date,
        )

        # Query existing backtesting result
        # Based on whether max period was used or not
        # parameters of start and end date are either None or dates
        existing_backtesting_result = (
            self.database_client.backtesting_results.find_first(
                where={
                    "ticker": backtesting_result.ticker,
                    "strategy": backtesting_result.strategy,
                    "frequency": backtesting_result.frequency,
                    "max_period": backtesting_result.max_period,
                    "start_date": backtesting_result.start_date,
                    "end_date": backtesting_result.end_date,
                },
            )
        )

        # Map the model to a dictionary representation
        model_dict_representation = backtesting_result.model_dump()

        # Create or update the backtesting result
        if not existing_backtesting_result:
            self.database_client.backtesting_results.create(
                data=model_dict_representation,
            )

        else:
            self.database_client.backtesting_results.update(
                where={
                    "id": existing_backtesting_result.id,
                },
                data=model_dict_representation,
            )

        # Disconnect from the database
        self.database_client.disconnect()
