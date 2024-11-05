import logging
import warnings
from pathlib import Path

from backtesting import Backtest
from pandas import DataFrame, Series

from apollo.core.backtesting.strategy_simulation_agent import StrategySimulationAgent
from apollo.settings import PLOT_DIR, TRDS_DIR

logger = logging.getLogger(__name__)

# NOTE: Ignore warnings related
# to internal arithmetics of the library
# E.g., division by zero during attempts to calculate
# Sortino ratio for a strategy that has no negative returns
warnings.filterwarnings("ignore")


class BacktestingRunner:
    """Backtesting Runner class that facilitates the backtesting process."""

    def __init__(
        self,
        dataframe: DataFrame,
        strategy_name: str,
        lot_size_cash: float,
        sl_volatility_multiplier: float,
        tp_volatility_multiplier: float,
        write_result_plot: bool = False,
        write_result_trades: bool = False,
    ) -> None:
        """
        Construct Backtesting runner.

        Rename dataframe columns to adhere to library signature.

        :param dataframe: Precalculated and marked dataframe to run backtesting on.
        :param strategy_name: Name of the strategy.
        :param lot_size_cash: Initial cash amount to backtest with.
        :param sl_volatility_multiplier: Stop loss volatility multiplier.
        :param tp_volatility_multiplier: Take profit volatility multiplier.
        :param write_result_plot: Flag to write backtesting plot.
        :param write_result_trades: Flag to write backtesting trades.
        """

        dataframe.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            },
            inplace=True,
        )

        self._dataframe = dataframe
        self._strategy_name = strategy_name
        self._lot_size_cash = lot_size_cash
        self._write_result_plot = write_result_plot
        self._write_result_trades = write_result_trades

        self._strategy_sim_agent = StrategySimulationAgent
        self._strategy_sim_agent.sl_volatility_multiplier = sl_volatility_multiplier
        self._strategy_sim_agent.tp_volatility_multiplier = tp_volatility_multiplier

    def run(self) -> Series:
        """
        Run the backtesting process.

        If requested, plot the backtesting results in dedicated directory.
        Log statistics with slight name changes to display proper strategy name.
        """

        backtesting_process = Backtest(
            data=self._dataframe,
            strategy=self._strategy_sim_agent,
            cash=self._lot_size_cash,
            exclusive_orders=True,
            trade_on_close=True,
        )

        stats = backtesting_process.run()

        if self._write_result_plot:
            # Make sure directory for plots exists
            if not Path.is_dir(PLOT_DIR):
                PLOT_DIR.mkdir(parents=True, exist_ok=True)

            backtesting_process.plot(
                plot_return=True,
                plot_equity=False,
                open_browser=False,
                filename=f"{PLOT_DIR}/{self._strategy_name}.html",
            )

        if self._write_result_trades:
            # Make sure directory for trades exists
            if not Path.is_dir(TRDS_DIR):
                TRDS_DIR.mkdir(parents=True, exist_ok=True)

            stats["_trades"].to_csv(f"{TRDS_DIR}/{self._strategy_name}.csv")

        # Rename the strategy name in
        # stats to display proper strategy name
        stats["_strategy"] = self._strategy_name

        return stats
