from datetime import datetime
from json import dumps, loads

import pandas as pd
import pytest
from prisma import Prisma
from pytz import timezone

from apollo.backtesters.backtesting_runner import BacktestingRunner
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.models.backtesting_results import BacktestingResults
from apollo.models.position import Position, PositionStatus
from apollo.settings import (
    BACKTESTING_CASH_SIZE,
    DEFAULT_DATE_FORMAT,
    END_DATE,
    FREQUENCY,
    LONG_SIGNAL,
    START_DATE,
    STRATEGY,
    TICKER,
)
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
    "enhanced_dataframe",
    "window_size",
)
def test__write_backtesting_results__for_correctly_writing_results(
    prisma_client: Prisma,
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test write_backtesting_results for correctly writing results to the database.

    PostgresConnector should write backtesting results to the database.
    All of the values used for identification of backtesting results should be match.
    All of the values produced by the backtesting library should be match.
    """

    dataframe = enhanced_dataframe.copy()

    strategy = SkewnessKurtosisVolatilityTrendFollowing(
        dataframe=dataframe,
        window_size=window_size,
        kurtosis_threshold=0.0,
        volatility_multiplier=0.5,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=str(STRATEGY),
        lot_size_cash=BACKTESTING_CASH_SIZE,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.3,
    )

    stats = backtesting_runner.run()

    backtesting_results = pd.DataFrame(stats).transpose()
    backtesting_results = backtesting_results.iloc[0]

    parameters = dumps(
        {
            "window_size": window_size,
            "kurtosis_threshold": 0.0,
            "volatility_multiplier": 0.5,
            "sl_volatility_multiplier": 0.1,
            "tp_volatility_multiplier": 0.3,
        },
    )

    postgres_connector = PostgresConnector()

    postgres_connector.write_backtesting_results(
        ticker=str(TICKER),
        strategy=str(STRATEGY),
        frequency=str(FREQUENCY),
        max_period=True,
        parameters=parameters,
        backtesting_results=backtesting_results,
        backtesting_end_date=str(START_DATE),
        backtesting_start_date=str(END_DATE),
    )

    backtesting_results_from_db = prisma_client.backtesting_results.find_first(
        where={
            "ticker": str(TICKER),
            "strategy": str(STRATEGY),
            "frequency": str(FREQUENCY),
            "max_period": True,
            "start_date": None,
            "end_date": None,
        },
    )

    assert backtesting_results_from_db is not None
    assert backtesting_results_from_db.ticker == str(TICKER)
    assert backtesting_results_from_db.strategy == str(STRATEGY)
    assert backtesting_results_from_db.frequency == str(FREQUENCY)
    assert backtesting_results_from_db.max_period is True
    assert backtesting_results_from_db.parameters == loads(parameters)
    assert backtesting_results_from_db.start_date is None
    assert backtesting_results_from_db.end_date is None

    # NOTE: we round incoming and outgoing values
    # to 2 decimal places to avoid float precision issues
    round_factor = 2

    assert round(backtesting_results_from_db.exposure_time, round_factor) == round(
        backtesting_results["Exposure Time [%]"],
        round_factor,
    )
    assert round(backtesting_results_from_db.total_return, round_factor) == round(
        backtesting_results["Return [%]"],
        round_factor,
    )
    assert round(
        backtesting_results_from_db.buy_and_hold_return,
        round_factor,
    ) == round(
        backtesting_results["Buy & Hold Return [%]"],
        round_factor,
    )
    assert round(
        backtesting_results_from_db.annualized_return,
        round_factor,
    ) == round(
        backtesting_results["Return (Ann.) [%]"],
        round_factor,
    )
    assert round(backtesting_results_from_db.sharpe_ratio, round_factor) == round(
        backtesting_results["Sharpe Ratio"],
        round_factor,
    )
    assert round(
        backtesting_results_from_db.annualized_volatility,
        round_factor,
    ) == round(
        backtesting_results["Volatility (Ann.) [%]"],
        round_factor,
    )
    assert round(backtesting_results_from_db.sortino_ratio, round_factor) == round(
        backtesting_results["Sortino Ratio"],
        round_factor,
    )
    assert round(backtesting_results_from_db.calmar_ratio, round_factor) == round(
        backtesting_results["Calmar Ratio"],
        round_factor,
    )
    assert round(backtesting_results_from_db.max_drawdown, round_factor) == round(
        backtesting_results["Max. Drawdown [%]"],
        round_factor,
    )
    assert round(backtesting_results_from_db.average_drawdown, round_factor) == round(
        backtesting_results["Avg. Drawdown [%]"],
        round_factor,
    )
    assert backtesting_results_from_db.max_drawdown_duration == str(
        backtesting_results["Max. Drawdown Duration"],
    )
    assert backtesting_results_from_db.average_drawdown_duration == str(
        backtesting_results["Avg. Drawdown Duration"],
    )
    assert (
        backtesting_results_from_db.number_of_trades == backtesting_results["# Trades"]
    )
    assert round(backtesting_results_from_db.win_rate, round_factor) == round(
        backtesting_results["Win Rate [%]"],
        round_factor,
    )
    assert round(backtesting_results_from_db.best_trade, round_factor) == round(
        backtesting_results["Best Trade [%]"],
        round_factor,
    )
    assert round(backtesting_results_from_db.worst_trade, round_factor) == round(
        backtesting_results["Worst Trade [%]"],
        round_factor,
    )
    assert round(backtesting_results_from_db.average_trade, round_factor) == round(
        backtesting_results["Avg. Trade [%]"],
        round_factor,
    )
    assert backtesting_results_from_db.max_trade_duration == str(
        backtesting_results["Max. Trade Duration"],
    )
    assert backtesting_results_from_db.average_trade_duration == str(
        backtesting_results["Avg. Trade Duration"],
    )
    assert round(
        backtesting_results_from_db.system_quality_number,
        round_factor,
    ) == round(backtesting_results["SQN"], round_factor)


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
    "enhanced_dataframe",
    "window_size",
)
def test__write_backtesting_results__for_writing_results_with_defined_time_period(
    prisma_client: Prisma,
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test write_backtesting_results for writing results with defined time period.

    PostgresConnector should write backtesting results to the database.
    Written backtesting results should have correct start and end dates.
    """

    dataframe = enhanced_dataframe.copy()

    strategy = SkewnessKurtosisVolatilityTrendFollowing(
        dataframe=dataframe,
        window_size=window_size,
        kurtosis_threshold=0.0,
        volatility_multiplier=0.5,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=str(STRATEGY),
        lot_size_cash=BACKTESTING_CASH_SIZE,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.3,
    )

    stats = backtesting_runner.run()

    backtesting_results = pd.DataFrame(stats).transpose()
    backtesting_results = backtesting_results.iloc[0]

    parameters = dumps(
        {
            "window_size": window_size,
            "kurtosis_threshold": 0.0,
            "volatility_multiplier": 0.5,
            "sl_volatility_multiplier": 0.1,
            "tp_volatility_multiplier": 0.3,
        },
    )

    postgres_connector = PostgresConnector()

    postgres_connector.write_backtesting_results(
        ticker=str(TICKER),
        strategy=str(STRATEGY),
        frequency=str(FREQUENCY),
        max_period=False,
        parameters=parameters,
        backtesting_results=backtesting_results,
        backtesting_end_date=str(START_DATE),
        backtesting_start_date=str(END_DATE),
    )

    start_date = datetime.strptime(
        str(END_DATE),
        DEFAULT_DATE_FORMAT,
    )
    end_date = datetime.strptime(
        str(START_DATE),
        DEFAULT_DATE_FORMAT,
    )

    backtesting_results_from_db = prisma_client.backtesting_results.find_first(
        where={
            "ticker": str(TICKER),
            "strategy": str(STRATEGY),
            "frequency": str(FREQUENCY),
            "max_period": False,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    assert backtesting_results_from_db is not None
    assert backtesting_results_from_db.max_period is False
    assert backtesting_results_from_db.start_date == start_date.astimezone().replace(
        tzinfo=timezone("UTC"),
    )
    assert backtesting_results_from_db.end_date == end_date.astimezone().replace(
        tzinfo=timezone("UTC"),
    )


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
    "enhanced_dataframe",
    "window_size",
)
def test__write_backtesting_results__for_updating_already_existing_entity(
    prisma_client: Prisma,
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test write_backtesting_results for updating already existing entity.

    PostgresConnector should update backtesting results already present in the database.
    """

    dataframe = enhanced_dataframe.copy()

    strategy = SkewnessKurtosisVolatilityTrendFollowing(
        dataframe=dataframe,
        window_size=window_size,
        kurtosis_threshold=0.0,
        volatility_multiplier=0.5,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=str(STRATEGY),
        lot_size_cash=BACKTESTING_CASH_SIZE,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.3,
    )

    stats = backtesting_runner.run()

    backtesting_results = pd.DataFrame(stats).transpose()
    backtesting_results = backtesting_results.iloc[0]

    parameters = dumps(
        {
            "window_size": window_size,
            "kurtosis_threshold": 0.0,
            "volatility_multiplier": 0.5,
            "sl_volatility_multiplier": 0.1,
            "tp_volatility_multiplier": 0.3,
        },
    )

    backtesting_results_model = BacktestingResults(
        ticker=str(TICKER),
        strategy=str(STRATEGY),
        frequency=str(FREQUENCY),
        max_period=True,
        parameters=parameters,
        backtesting_results=backtesting_results,
        backtesting_end_date=str(START_DATE),
        backtesting_start_date=str(END_DATE),
    )

    writable_model_representation = backtesting_results_model.model_dump()

    already_present_backtesting_results = prisma_client.backtesting_results.create(
        data=writable_model_representation,  # type: ignore  # noqa: PGH003
    )

    postgres_connector = PostgresConnector()

    postgres_connector.write_backtesting_results(
        ticker=str(TICKER),
        strategy=str(STRATEGY),
        frequency=str(FREQUENCY),
        max_period=True,
        parameters=parameters,
        backtesting_results=backtesting_results,
        backtesting_end_date=str(START_DATE),
        backtesting_start_date=str(END_DATE),
    )

    backtesting_results_from_db = prisma_client.backtesting_results.find_first(
        where={
            "ticker": str(TICKER),
            "strategy": str(STRATEGY),
            "frequency": str(FREQUENCY),
            "max_period": True,
            "start_date": None,
            "end_date": None,
        },
    )

    assert backtesting_results_from_db is not None
    assert backtesting_results_from_db.id == already_present_backtesting_results.id


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
)
@pytest.mark.parametrize(
    "position_status",
    [
        PositionStatus.OPEN,
        PositionStatus.SCREENED,
        PositionStatus.OPTIMIZED,
        PositionStatus.DISPATCHED,
    ],
)
def test__get_existing_active_position__for_returning_existing_active_position(
    prisma_client: Prisma,
    position_status: PositionStatus,
) -> None:
    """
    Test get_existing_active_position for returning active position.

    PostgresConnector should return active position for a ticker if it exists.
    """

    postgres_connector = PostgresConnector()

    control_active_position = Position(
        ticker=str(TICKER),
        status=position_status,
    )

    control_inactive_position = Position(
        ticker=str(TICKER),
        status=PositionStatus.CLOSED,
    )

    prisma_client.positions.create(
        data=control_active_position.model_dump(
            exclude_defaults=True,
        ),  # type: ignore  # noqa: PGH003
    )

    prisma_client.positions.create(
        data=control_inactive_position.model_dump(
            exclude_defaults=True,
        ),  # type: ignore  # noqa: PGH003
    )

    position = postgres_connector.get_existing_active_position(ticker=str(TICKER))

    assert position is not None
    assert position.ticker == control_active_position.ticker
    assert position.status == control_active_position.status.value


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
)
def test__get_existing_active_position__for_returning_none_if_no_active_position(
    prisma_client: Prisma,
) -> None:
    """
    Test get_existing_active_position for returning None.

    PostgresConnector should return None if no active position for a ticker exists.
    """

    postgres_connector = PostgresConnector()

    control_inactive_position = Position(
        ticker=str(TICKER),
        status=PositionStatus.CLOSED,
    )

    prisma_client.positions.create(
        data=control_inactive_position.model_dump(),  # type: ignore  # noqa: PGH003
    )

    position = postgres_connector.get_existing_active_position(ticker=str(TICKER))

    assert position is None


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
)
def test__create_position_on_screening__for_creating_position(
    prisma_client: Prisma,
) -> None:
    """
    Test create_position_on_screening for creating position.

    PostgresConnector should create a position entity with status set to screened.
    """

    postgres_connector = PostgresConnector()

    postgres_connector.create_position_on_screening(ticker=str(TICKER))

    position = prisma_client.positions.find_first(
        where={
            "ticker": str(TICKER),
            "status": PositionStatus.SCREENED.value,
        },
    )

    assert position is not None
    assert position.ticker == str(TICKER)
    assert position.status == PositionStatus.SCREENED.value


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
)
@pytest.mark.parametrize(
    "position_status",
    [
        PositionStatus.OPEN,
        PositionStatus.CLOSED,
        PositionStatus.SCREENED,
        PositionStatus.OPTIMIZED,
        PositionStatus.CANCELLED,
        PositionStatus.DISPATCHED,
    ],
)
def test__get_existing_position_by_status__for_returning_position_by_status(
    prisma_client: Prisma,
    position_status: PositionStatus,
) -> None:
    """
    Test get_existing_position_by_status for returning position by status.

    PostgresConnector should return position by status if it exists.
    """

    postgres_connector = PostgresConnector()

    control_position = Position(
        ticker=str(TICKER),
        status=position_status,
    )

    prisma_client.positions.create(
        data=control_position.model_dump(
            exclude_defaults=True,
        ),  # type: ignore  # noqa: PGH003
    )

    position = postgres_connector.get_existing_position_by_status(
        position_status=position_status,
    )

    assert position is not None
    assert position.ticker == control_position.ticker
    assert position.status == control_position.status.value


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
)
@pytest.mark.parametrize(
    "position_status",
    [
        PositionStatus.OPEN,
        PositionStatus.CLOSED,
        PositionStatus.OPTIMIZED,
        PositionStatus.CANCELLED,
        PositionStatus.DISPATCHED,
    ],
)
def test__update_existing_position_by_status__for_updating_position(
    prisma_client: Prisma,
    position_status: PositionStatus,
) -> None:
    """
    Test update_existing_position_by_status for updating position.

    PostgresConnector should update position by status.
    """

    postgres_connector = PostgresConnector()

    control_position = Position(
        ticker=str(TICKER),
        status=PositionStatus.SCREENED,
    )

    control_position = prisma_client.positions.create(
        data=control_position.model_dump(
            exclude_defaults=True,
        ),  # type: ignore  # noqa: PGH003
    )

    postgres_connector.update_existing_position_by_status(
        position_id=control_position.id,
        position_status=position_status,
    )

    position = prisma_client.positions.find_first(
        where={
            "id": control_position.id,
        },
    )

    assert position is not None
    assert position.status == position_status.value


@pytest.mark.usefixtures(
    "prisma_client",
    "flush_postgres_database",
)
def test__update_position_upon_dispatching__for_updating_position(
    prisma_client: Prisma,
) -> None:
    """
    Test update_position_upon_dispatching for updating position.

    PostgresConnector should update position upon dispatching.
    """

    postgres_connector = PostgresConnector()

    control_position = Position(
        ticker=str(TICKER),
        status=PositionStatus.SCREENED,
    )

    control_position = prisma_client.positions.create(
        data=control_position.model_dump(
            exclude_defaults=True,
        ),  # type: ignore  # noqa: PGH003
    )

    stop_loss = 90.0
    take_profit = 110.0
    target_entry_price = 100.0

    postgres_connector.update_position_upon_dispatching(
        position_id=control_position.id,
        strategy=str(STRATEGY),
        direction=LONG_SIGNAL,
        stop_loss=stop_loss,
        take_profit=take_profit,
        target_entry_price=target_entry_price,
    )

    position = prisma_client.positions.find_first(
        where={
            "id": control_position.id,
        },
    )

    assert position is not None
    assert position.strategy == str(STRATEGY)
    assert position.direction == LONG_SIGNAL
    assert position.stop_loss == stop_loss
    assert position.take_profit == take_profit
    assert position.target_entry_price == target_entry_price


@pytest.mark.usefixtures(
    "flush_postgres_database",
    "enhanced_dataframe",
    "window_size",
)
def test__get_optimized_parameters__for_returning_optimized_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test get_optimized_parameters for returning optimized parameters.

    PostgresConnector should return optimized parameters for a ticker if they exist.
    """

    dataframe = enhanced_dataframe.copy()

    strategy = SkewnessKurtosisVolatilityTrendFollowing(
        dataframe=dataframe,
        window_size=window_size,
        kurtosis_threshold=0.0,
        volatility_multiplier=0.5,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=str(STRATEGY),
        lot_size_cash=BACKTESTING_CASH_SIZE,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.3,
    )

    stats = backtesting_runner.run()

    backtesting_results = pd.DataFrame(stats).transpose()
    backtesting_results = backtesting_results.iloc[0]

    parameters = dumps(
        {
            "window_size": window_size,
            "kurtosis_threshold": 0.0,
            "volatility_multiplier": 0.5,
            "sl_volatility_multiplier": 0.1,
            "tp_volatility_multiplier": 0.3,
        },
    )

    postgres_connector = PostgresConnector()

    postgres_connector.write_backtesting_results(
        ticker=str(TICKER),
        strategy=str(STRATEGY),
        frequency=str(FREQUENCY),
        max_period=True,
        parameters=parameters,
        backtesting_results=backtesting_results,
        backtesting_end_date=str(START_DATE),
        backtesting_start_date=str(END_DATE),
    )

    optimized_parameters = postgres_connector.get_optimized_parameters(
        ticker=str(TICKER),
    )[0]

    assert optimized_parameters is not None
    assert optimized_parameters.strategy == str(STRATEGY)
    assert optimized_parameters.parameters == loads(parameters)
