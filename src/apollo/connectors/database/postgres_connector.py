import pandas as pd
from prisma import Prisma

from apollo.models.backtesting_results import BacktestingResults


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
        backtesting_results: pd.Series,
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
        :param backtesting_results: Backtesting results Series.
        :param backtesting_end_date: End date of the backtesting period.
        :param backtesting_start_date: Start date of the backtesting period.
        """

        # Connect to the database
        self.database_client.connect()

        # Map incoming inputs to the database model
        backtesting_results_model = BacktestingResults(
            ticker=ticker,
            strategy=strategy,
            frequency=frequency,
            max_period=max_period,
            parameters=parameters,
            backtesting_results=backtesting_results,
            backtesting_end_date=backtesting_end_date,
            backtesting_start_date=backtesting_start_date,
        )

        # Query existing backtesting result;
        # based on whether max period was used or not
        # parameters of start and end date are either None or dates
        existing_backtesting_result = (
            self.database_client.backtesting_results.find_first(
                where={
                    "ticker": backtesting_results_model.ticker,
                    "strategy": backtesting_results_model.strategy,
                    "frequency": backtesting_results_model.frequency,
                    "max_period": backtesting_results_model.max_period,
                    "start_date": backtesting_results_model.start_date,
                    "end_date": backtesting_results_model.end_date,
                },
            )
        )

        # Map the model to a writable representation
        writable_model_representation = backtesting_results_model.model_dump()

        # NOTE: prisma python client and pydantic models
        # are not yet fully compatible between each other
        # due to the fact that pydantic produces dict[str, Any]
        # while prisma client operates solely on TypedDict objects
        # In such, we ignore the type check for the data parameter

        # Create or update the backtesting result
        if not existing_backtesting_result:
            self.database_client.backtesting_results.create(
                data=writable_model_representation,  # type: ignore  # noqa: PGH003
            )
        else:
            self.database_client.backtesting_results.update(
                where={
                    "id": existing_backtesting_result.id,
                },
                data=writable_model_representation,  # type: ignore  # noqa: PGH003
            )

        # Disconnect from the database
        self.database_client.disconnect()
