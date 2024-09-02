import logging

import pandas as pd

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.providers.price_data_enhancer import PriceDataEnhancer
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    START_DATE,
    TICKER,
)
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
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

    price_data_provider = PriceDataProvider()
    price_data_enhancer = PriceDataEnhancer()

    dataframe = price_data_provider.get_price_data(
        ticker=str(TICKER),
        frequency=str(FREQUENCY),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
        max_period=bool(MAX_PERIOD),
    )

    dataframe = price_data_enhancer.enhance_price_data(
        price_dataframe=dataframe,
        additional_data_enhancers=["VIX", "SP500 Futures"],
    )

    strategy = SkewnessKurtosisVolatilityTrendFollowing(
        dataframe=dataframe,
        window_size=5,
        kurtosis_threshold=1.5,
        volatility_multiplier=1.0,
    )

    strategy.model_trading_signals()

    pd.options.display.max_rows = 100000
    print(  # noqa: T201
        dataframe[
            ["open", "high", "low", "close", "signal", "vix_signal", "vix_spf_signal"]
        ],
    )

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name="SkewnessKurtosisVolatilityTrendFollowing",
        lot_size_cash=1000,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.4,
        write_result_plot=True,
    )

    stats = backtesting_runner.run()

    logger.info(stats)


if __name__ == "__main__":
    main()
