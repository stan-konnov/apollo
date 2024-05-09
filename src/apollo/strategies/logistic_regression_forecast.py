from pandas import DataFrame

from apollo.calculations.models.logistic_regression import (
    LogisticRegressionModelCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class LogisticRegressionForecast(BaseStrategy):
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
        test_size: float,
    ) -> None:
        """
        Construct Logistic Regression Forecast Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param test_size: Size of the test set.
        """

        self._validate_parameters(
            [
                ("test_size", test_size, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.lrm_calculator = LogisticRegressionModelCalculator(
            dataframe=dataframe,
            test_size=test_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.lrm_calculator.forecast_periods()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self.dataframe.loc[self.dataframe["lrf"] > 0, "signal"] = LONG_SIGNAL
        self.dataframe.loc[self.dataframe["lrf"] < 0, "signal"] = SHORT_SIGNAL
