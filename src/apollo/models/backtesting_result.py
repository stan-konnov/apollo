from datetime import datetime

import pandas as pd
from pydantic import BaseModel

from apollo.settings import DEFAULT_DATE_FORMAT

"""
TODO: please install pydantic as we go with it now


Do we need equity final and peak?
Not really, clean it
"""


class BacktestingResult(BaseModel):
    """A data model to represent backtesting result."""

    ticker: str
    strategy: str
    frequency: str
    parameters: str
    max_period: bool

    end_date: datetime | None
    start_date: datetime | None

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
        parameters: str,
        backtesting_results: pd.Series,
        backtesting_end_date: str,
        backtesting_start_date: str,
    ) -> None:
        """
        Construct a new Backtesting Result object.

        :param ticker: Ticker symbol.
        :param strategy: Strategy name.
        :param frequency: Frequency of the data.
        :param max_period: If all available data was used.
        :param parameters: Best performing strategy parameters.
        :param backtesting_results: Backtesting results Series.
        :param backtesting_end_date: End date of the backtesting period.
        :param backtesting_start_date: Start date of the backtesting period.
        """

        # Set the start and end date
        # if maximum available data was not used
        if max_period:
            end_date = None
            start_date = None
        else:
            end_date = datetime.strptime(
                backtesting_end_date,
                DEFAULT_DATE_FORMAT,
            )
            start_date = datetime.strptime(
                backtesting_start_date,
                DEFAULT_DATE_FORMAT,
            )

        super().__init__(
            ticker=ticker,
            strategy=strategy,
            frequency=frequency,
            max_period=max_period,
            parameters=parameters,
            end_date=end_date,
            start_date=start_date,
            exposure_time=backtesting_results["Exposure Time [%]"],
            equity_final=backtesting_results["Equity Final [$]"],
            equity_peak=backtesting_results["Equity Peak [$]"],
            total_return=backtesting_results["Return [%]"],
            buy_and_hold_return=backtesting_results["Buy & Hold Return [%]"],
            annualized_return=backtesting_results["Return (Ann.) [%]"],
            annualized_volatility=backtesting_results["Volatility (Ann.) [%]"],
            sharpe_ratio=backtesting_results["Sharpe Ratio"],
            sortino_ratio=backtesting_results["Sortino Ratio"],
            calmar_ratio=backtesting_results["Calmar Ratio"],
            max_drawdown=backtesting_results["Max. Drawdown [%]"],
            average_drawdown=backtesting_results["Avg. Drawdown [%]"],
            max_drawdown_duration=str(backtesting_results["Max. Drawdown Duration"]),
            average_drawdown_duration=str(
                backtesting_results["Avg. Drawdown Duration"],
            ),
            number_of_trades=backtesting_results["# Trades"],
            win_rate=backtesting_results["Win Rate [%]"],
            best_trade=backtesting_results["Best Trade [%]"],
            worst_trade=backtesting_results["Worst Trade [%]"],
            average_trade=backtesting_results["Avg. Trade [%]"],
            max_trade_duration=str(backtesting_results["Max. Trade Duration"]),
            average_trade_duration=str(backtesting_results["Avg. Trade Duration"]),
            system_quality_number=backtesting_results["SQN"],
        )
