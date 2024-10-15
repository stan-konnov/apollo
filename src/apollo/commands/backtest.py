import logging

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
from apollo.strategies.combinatory_elliot_waves import CombinatoryElliotWaves
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

    strategy = CombinatoryElliotWaves(
        dataframe=dataframe,
        window_size=5,
        fast_oscillator_period=5.0,
        slow_oscillator_period=25.0,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name="CombinatoryElliotWaves",
        lot_size_cash=1000,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.4,
        write_result_plot=True,
    )

    stats = backtesting_runner.run()

    logger.info(stats)


if __name__ == "__main__":
    main()
