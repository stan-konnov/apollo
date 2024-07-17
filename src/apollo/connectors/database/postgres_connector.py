from typing import TYPE_CHECKING

import pandas as pd
from prisma import Prisma

from apollo.models.backtesting_result import BacktestingResult

if TYPE_CHECKING:
    from datetime import datetime


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
        backtesting_end_date: str | None,
        backtesting_start_date: str | None,
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

        # Map to dictionary acceptable by the client
        model_dump = backtesting_result.model_dump()

        # Create default lookup arguments for the query
        lookup_arguments: dict[str, str | bool | datetime | None] = {
            "ticker": backtesting_result.ticker,
            "strategy": backtesting_result.strategy,
            "frequency": backtesting_result.frequency,
        }

        # Lookup either by max period or by start and end date
        if backtesting_result.max_period:
            lookup_arguments["max_period"] = backtesting_result.max_period

        else:
            lookup_arguments["end_date"] = backtesting_result.end_date
            lookup_arguments["start_date"] = backtesting_result.start_date

        # Query existing backtesting result
        existing_backtesting_result = (
            self.database_client.backtesting_results.find_first(
                where=lookup_arguments,
            )
        )

        # Create or update the backtesting result
        if not existing_backtesting_result:
            self.database_client.backtesting_results.create(
                data=model_dump,
            )

        else:
            self.database_client.backtesting_results.update(
                where={
                    "id": existing_backtesting_result.id,
                },
                data=model_dump,
            )

        # Disconnect from the database
        self.database_client.disconnect()
