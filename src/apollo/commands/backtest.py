import logging

import pandas as pd

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.settings import (
    END_DATE,
    MAX_PERIOD,
    START_DATE,
    TICKER,
)
from apollo.strategies.wilders_swing_index_trend_following import (
    WildersSwingIndexTrendFollowing,
)
from apollo.utils.common import ensure_environment_is_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run backtesting process for individual strategy."""

    ensure_environment_is_configured()

    yahoo_api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=bool(MAX_PERIOD),
    )

    dataframe = yahoo_api_connector.request_or_read_prices()

    strategy = WildersSwingIndexTrendFollowing(
        dataframe=dataframe,
        window_size=5,
    )

    strategy.model_trading_signals()

    pd.options.display.max_rows = 100
    print(dataframe.head(100))  # noqa: T201

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name="WildersSwingIndexTrendFollowing",
        lot_size_cash=1000,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.3,
        write_result_plot=True,
    )

    stats = backtesting_runner.run()

    logger.info(stats)


if __name__ == "__main__":
    main()
