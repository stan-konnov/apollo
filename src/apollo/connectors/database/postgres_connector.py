import pandas as pd
from prisma import Prisma

from apollo.models.backtesting_results import BacktestingResults
from apollo.models.position import Position, PositionStatus
from apollo.models.strategy_parameters import StrategyParameters


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

        self._database_client = Prisma()

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

        self._database_client.connect()

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
            self._database_client.backtesting_results.find_first(
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
        writable_model_representation = backtesting_results_model.model_dump(
            exclude_defaults=True,
        )

        # NOTE: prisma python client and pydantic models
        # are not yet fully compatible between each other
        # due to the fact that pydantic produces dict[str, Any]
        # while prisma client operates solely on TypedDict objects
        # In such, we ignore the type check for the data parameter

        # Create or update the backtesting result
        if not existing_backtesting_result:
            self._database_client.backtesting_results.create(
                data=writable_model_representation,  # type: ignore  # noqa: PGH003
            )
        else:
            self._database_client.backtesting_results.update(
                where={
                    "id": existing_backtesting_result.id,
                },
                data=writable_model_representation,  # type: ignore  # noqa: PGH003
            )

        self._database_client.disconnect()

    def get_existing_active_position(self, ticker: str) -> Position | None:
        """
        Get existing active position for a ticker.

        Used to validate system invariant of having
        single active position for a ticker at a time.

        NOTE: We consider a position to be active if it
        falls under any of the following statuses:
        screened, optimized, dispatched, open.

        :param ticker: Ticker to check for active position.
        :returns: Active position if exists.
        """

        self._database_client.connect()

        # Check if we have active position
        existing_active_position = self._database_client.positions.find_first(
            where={
                "ticker": ticker,
                "status": {
                    "in": [
                        PositionStatus.SCREENED.value,
                        PositionStatus.OPTIMIZED.value,
                        PositionStatus.DISPATCHED.value,
                        PositionStatus.OPEN.value,
                    ],
                },
            },
        )

        self._database_client.disconnect()

        # And return the position if exists
        return (
            Position(
                id=existing_active_position.id,
                ticker=existing_active_position.ticker,
                status=PositionStatus(existing_active_position.status),
            )
            if existing_active_position
            else None
        )

    def create_position_on_screening(self, ticker: str) -> None:
        """
        Create a position entity after screening.

        :param ticker: Ticker to create a position for.
        """

        self._database_client.connect()

        # Create a model and write it to the database
        self._database_client.positions.create(
            data=Position(
                ticker=ticker,
                status=PositionStatus.SCREENED,
            ).model_dump(exclude_defaults=True),  # type: ignore  # noqa: PGH003
        )

        self._database_client.disconnect()

    def get_existing_position_by_status(
        self,
        position_status: PositionStatus,
    ) -> Position | None:
        """
        Get existing position by status.

        :param position_status: Position status to query.
        :returns: Position if exists.
        """

        self._database_client.connect()

        # Check if we have a position by status
        position = self._database_client.positions.find_first(
            where={
                "status": position_status.value,
            },
        )

        self._database_client.disconnect()

        # And return the position if exists
        return (
            Position(
                id=position.id,
                ticker=position.ticker,
                status=PositionStatus(position.status),
            )
            if position
            else None
        )

    def update_existing_position_by_status(
        self,
        position_id: str,
        position_status: PositionStatus,
    ) -> None:
        """
        Update existing position by status.

        :param position_id: Position id to update.
        :param position_status: Position status to update.
        """

        self._database_client.connect()

        # Update the position status
        self._database_client.positions.update(
            where={
                "id": position_id,
            },
            data={
                "status": position_status.value,
            },
        )

        self._database_client.disconnect()

    def update_position_upon_dispatching(
        self,
        position_id: str,
        strategy: str,
        direction: int,
        stop_loss: float,
        take_profit: float,
        target_entry_price: float,
    ) -> None:
        """
        Update position upon dispatching.

        :param position_id: Position id to update.
        :param strategy: Strategy name.
        :param direction: Signal direction.
        :param stop_loss: Stop loss price.
        :param take_profit: Take profit price.
        :param target_entry_price: Target entry price.
        """

        self._database_client.connect()

        # Update the position with dispatching details
        self._database_client.positions.update(
            where={
                "id": position_id,
            },
            data={
                "strategy": strategy,
                "direction": direction,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "target_entry_price": target_entry_price,
            },
        )

        self._database_client.disconnect()

    def get_optimized_parameters(self, ticker: str) -> list[StrategyParameters]:
        """
        Get optimized strategy parameters for a ticker sorted by sharpe ratio.

        :param ticker: Ticker to get optimized parameters for.
        :returns: List of optimized strategy parameters.
        """

        self._database_client.connect()

        # Query backtesting results for a given ticker
        backtesting_results = self._database_client.backtesting_results.find_many(
            where={
                "ticker": ticker,
            },
            order={
                "sharpe_ratio": "desc",
            },
        )

        self._database_client.disconnect()

        # And return the parameters
        return [
            StrategyParameters(
                strategy=backtesting_result.strategy,
                # NOTE: Prisma is packing the JSON
                # into a dict for us under the hood
                parameters=backtesting_result.parameters,  # type: ignore  # noqa: PGH003
            )
            for backtesting_result in backtesting_results
        ]
