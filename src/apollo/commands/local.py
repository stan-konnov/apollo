import logging

# from apollo.backtesting.parameter_optimizer import ParameterOptimizer
from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.settings import END_DATE, START_DATE, TICKER
from apollo.strategies.swing_events_mean_reversion import SwingEventsMeanReversion
from apollo.strategies.skew_kurt_vol_trend_following import SkewnessKurtosisVolatilityTrendFollowing

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run local scripts to quickly iterate on code."""

    # parameter_optimizer = ParameterOptimizer()
    # parameter_optimizer.process()

    yahoo_api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    dataframe = yahoo_api_connector.request_or_read_prices()

    strategy = SwingEventsMeanReversion(
        dataframe=dataframe,
        window_size=15,
        swing_filter=0.03,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name="SwingEventsMeanReversion",
        lot_size_cash=1000,
        volatility_multiplier=1.0,
        write_result_plot=True,
    )

    stats = backtesting_runner.run()

    print(stats)


if __name__ == "__main__":
    main()
