import logging
import warnings
from pathlib import Path

from backtesting import Backtest
from pandas import DataFrame, Series

from apollo.backtesting.strategy_simulation_agent import StrategySimulationAgent
from apollo.settings import PLOT_DIR

logger = logging.getLogger(__name__)

# NOTE: Ignore warnings related
# to internals arithmetics of the library
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
            stop_loss_level: float,
            take_profit_level: float,
            write_result_plot: bool = False,
        ) -> None:
        """
        Construct Backtesting runner.

        Rename dataframe columns to adhere to library signature.

        :param dataframe: Precalculated and marked dataframe to run backtesting on.
        :param stop_loss_level: Stop loss level to use for exits.
        :param take_profit_level: Take profit level to use for exits.
        :param write_result_plot: Flag to plot backtesting results.
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

        self.dataframe = dataframe
        self.strategy_name = strategy_name
        self.lot_size_cash = lot_size_cash
        self.write_result_plot = write_result_plot

        self.strategy_sim_agent = StrategySimulationAgent
        self.strategy_sim_agent.stop_loss_level = stop_loss_level
        self.strategy_sim_agent.take_profit_level = take_profit_level


    def run(self) -> Series:
        """
        Run the backtesting process.

        If requested, plot the backtesting results in dedicated directory.
        Log statistics with slight name changes to display proper strategy name.
        """

        backtesting_process = Backtest(
            self.dataframe,
            self.strategy_sim_agent,
            cash=self.lot_size_cash,
            trade_on_close=True,
        )

        # Make sure directory for plots exists
        if not Path.is_dir(PLOT_DIR):
            PLOT_DIR.mkdir(parents=True, exist_ok=True)

        stats = backtesting_process.run()

        if self.write_result_plot:
            backtesting_process.plot(
                plot_return=True,
                plot_equity=False,
                open_browser=False,
                filename=f"{PLOT_DIR}/{self.strategy_name}.html",
            )

        # Rename the strategy name in stats
        # to display proper strategy name
        stats["_strategy"] = self.strategy_name

        return stats
