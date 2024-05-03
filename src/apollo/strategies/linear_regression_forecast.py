from pandas import DataFrame

from apollo.calculations.models.linear_regression import LinearRegressionModelCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class LinearRegressionForecast(BaseStrategy):
    """Linear Regression Forecast."""

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        split_ratio: float,
        smoothing_factor: float,
    ) -> None:
        """
        Construct.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param split_ratio: Ratio to split data into train and test.
        """

        self._validate_parameters(
            [
                ("split_ratio", split_ratio, float),
                ("smoothing_factor", smoothing_factor, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.lr_calculator = LinearRegressionModelCalculator(
            dataframe=dataframe,
            window_size=window_size,
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

        self.lr_calculator.forecast_periods()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self.dataframe.loc[self.dataframe["forecast"] > 0, "signal"] = LONG_SIGNAL
        self.dataframe.loc[self.dataframe["forecast"] < 0, "signal"] = SHORT_SIGNAL
