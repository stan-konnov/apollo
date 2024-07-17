from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestingResult:
    """A data model to represent backtesting result."""

    ticker: str
    strategy: str
    frequency: str
    max_period: bool
    parameters: dict[str, float]

    exposure_time: float
    equity_final: float
    equity_peak: float
    total_return: float
    buy_and_hold_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    average_drawdown: float
    max_drawdown_duration: str
    average_drawdown_duration: str
    number_of_trades: int
    win_rate: float
    best_trade: float
    worst_trade: float
    average_trade: float
    max_trade_duration: str
    average_trade_duration: str
    system_quality_number: float

    def __init__(
        self,
        ticker: str,
        strategy: str,
        frequency: str,
        max_period: bool,
        parameters: dict[str, float],
        backtesting_results: pd.DataFrame,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> None:
        """
        Construct a new Backtesting Result object.

        :param ticker: Instrument ticker symbol.
        :param strategy: Strategy name.
        :param frequency: Frequency of the data.
        :param max_period: Flag indicating if maximum available data was used.
        :param parameters: Best performing strategy parameters.
        :param backtesting_results: Backtesting results.
        :param start_date: Start date of the backtesting period.
        :param end_date: End date of the backtesting period.

        :raises ValueError: If both start_date and end_date provided with max_period.
        """

        if start_date and end_date and max_period:
            raise ValueError(
                "Either start_date and end_date or max_period should be provided.",
            )

        self.ticker = ticker
        self.strategy = strategy
        self.frequency = frequency
        self.max_period = max_period
        self.parameters = parameters

        # Parse the first (and single) row of results
        results_to_parse = backtesting_results.iloc[0]

        # Populate the model with the parsed results
        self.exposure_time = results_to_parse["Exposure Time [%]"]
        self.equity_final = results_to_parse["Equity Final [$]"]
        self.equity_peak = results_to_parse["Equity Peak [$]"]
        self.total_return = results_to_parse["Return [%]"]
        self.buy_and_hold_return = results_to_parse["Buy & Hold Return [%]"]
        self.annualized_return = results_to_parse["Return (Ann.) [%]"]
        self.annualized_volatility = results_to_parse["Volatility (Ann.) [%]"]
        self.sharpe_ratio = results_to_parse["Sharpe Ratio"]
        self.sortino_ratio = results_to_parse["Sortino Ratio"]
        self.calmar_ratio = results_to_parse["Calmar Ratio"]
        self.max_drawdown = results_to_parse["Max. Drawdown [%]"]
        self.average_drawdown = results_to_parse["Avg. Drawdown [%]"]
        self.max_drawdown_duration = results_to_parse["Max. Drawdown Duration"]
        self.average_drawdown_duration = results_to_parse["Avg. Drawdown Duration"]
        self.number_of_trades = results_to_parse["# Trades"]
        self.win_rate = results_to_parse["Win Rate [%]"]
        self.best_trade = results_to_parse["Best Trade [%]"]
        self.worst_trade = results_to_parse["Worst Trade [%]"]
        self.average_trade = results_to_parse["Avg. Trade [%]"]
        self.max_trade_duration = results_to_parse["Max. Trade Duration"]
        self.average_trade_duration = results_to_parse["Avg. Trade Duration"]
        self.system_quality_number = results_to_parse["SQN"]
