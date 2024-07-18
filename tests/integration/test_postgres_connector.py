from json import dumps

import pandas as pd
import pytest

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.settings import TICKER
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__write_backtesting_results__for_correctly_writing_results(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test write_backtesting_results for correctly writing results to the database.

    PostgresConnector should write backtesting results to the database.
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
        strategy_name="SkewnessKurtosisVolatilityTrendFollowing",
        lot_size_cash=1000,
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
        strategy="SkewnessKurtosisVolatilityTrendFollowing",
        frequency="1d",
        max_period=True,
        parameters=parameters,
        backtesting_results=backtesting_results,
        backtesting_end_date="2021-01-01",
        backtesting_start_date="2020-01-01",
    )
