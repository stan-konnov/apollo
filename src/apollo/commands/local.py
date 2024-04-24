import logging

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.backtesting.parameter_optimizer import ParameterOptimizer
from apollo.settings import END_DATE, START_DATE, TICKER
from apollo.strategies.key_reversals_trend_following import KeyReversalsTrendFollowing

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

    api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    dataframe = api_connector.request_or_read_prices()

    strategy = KeyReversalsTrendFollowing(
        dataframe=dataframe,
        window_size=15,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name="KeyReversalsTrendFollowing",
        lot_size_cash=1000,
        stop_loss_level=0.005,
        take_profit_level=0.1,
        write_result_plot=True,
    )

    stats = backtesting_runner.run()

    print(stats)


if __name__ == "__main__":
    main()
