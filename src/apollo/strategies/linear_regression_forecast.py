from pandas import DataFrame

from apollo.calculations.models.logistic_regression import (
    LogisticRegressionModelCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class LinearRegressionForecast(BaseStrategy):
    """
    Linear Regression Forecast.

    This strategy takes long positions when:

    * Underlying linear regression model forecasts positive change on next period.

    This strategy takes short positions when:

    * Underlying linear regression model forecasts negative change on next period.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        split_ratio: float,
        smoothing_factor: float,
    ) -> None:
        """
        Construct Linear Regression Forecast Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param split_ratio: Ratio to split data into train and test set.
        :param smoothing_factor: Smoothing factor for the linear regression model.
        """

        self._validate_parameters(
            [
                ("split_ratio", split_ratio, float),
                ("smoothing_factor", smoothing_factor, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.lrm_calculator = LogisticRegressionModelCalculator(
            dataframe=dataframe,
            split_ratio=split_ratio,
            smoothing_factor=smoothing_factor,
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
