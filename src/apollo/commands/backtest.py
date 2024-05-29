import logging
from typing import TYPE_CHECKING

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.settings import END_DATE, START_DATE, TICKER
from apollo.strategies.bollinger_bands_mean_reversion import BollingerBandsMeanReversion

if TYPE_CHECKING:
    import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run backtesting process for individual strategy."""

    yahoo_api_connector = YahooApiConnector(
        ticker=str(TICKER),
        start_date=str(START_DATE),
        end_date=str(END_DATE),
    )

    dataframe = yahoo_api_connector.request_or_read_prices()

    strategy = BollingerBandsMeanReversion(
        dataframe=dataframe,
        window_size=10,
        channel_sd_spread=0.1,
    )

    strategy.model_trading_signals()

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name="BollingerBandsMeanReversion",
        lot_size_cash=1000,
        sl_volatility_multiplier=0.1,
        tp_volatility_multiplier=0.1,
        write_result_plot=True,
    )

    stats = backtesting_runner.run()

    logger.info(stats)

    trades: pd.DataFrame = stats["_trades"]
    trades["ReturnPct"] = trades["ReturnPct"] * 100

    # trades.to_csv("trades.csv")  # noqa: ERA001


if __name__ == "__main__":
    main()
