from pandas import DataFrame

from apollo.calculations.models.logistic_regression import (
    LogisticRegressionModelCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)

"""
NOTE: currently is not used as optimization takes unreasonably long time.
"""


class LogisticRegressionForecast(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Logistic Regression Forecast.

    This strategy takes long positions when:

    * Underlying logistic regression model forecasts positive change on next period.

    This strategy takes short positions when:

    * Underlying logistic regression model forecasts negative change on next period.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Logistic Regression Forecast Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param train_size: Size of the train set.
        """

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._lrm_calculator = LogisticRegressionModelCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._lrm_calculator.forecast_periods()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self._dataframe.loc[self._dataframe["lrf"] > 0, "signal"] = LONG_SIGNAL
        self._dataframe.loc[self._dataframe["lrf"] < 0, "signal"] = SHORT_SIGNAL
