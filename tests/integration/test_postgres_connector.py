from json import dumps, loads

import pandas as pd
import pytest
from prisma import Prisma

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.settings import (
    BACKTESTING_CASH_SIZE,
    END_DATE,
    FREQUENCY,
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
    "dataframe",
    "window_size",
)
def test__write_backtesting_results__for_correctly_writing_results(
    prisma_client: Prisma,
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test write_backtesting_results for correctly writing results to the database.

    PostgresConnector should write backtesting results to the database.
    All of the values written into database should match original backtesting results.
    """

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
