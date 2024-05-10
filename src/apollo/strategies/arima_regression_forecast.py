from pandas import DataFrame

from apollo.calculations.models.arima_regression import ARIMARegressionModelCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class ARIMARegressionForecast(BaseStrategy):
    """
    ARIMA Regression Forecast.

    WIP.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct ARIMA Regression Forecast Strategy.

        WIP.
        """

        super().__init__(dataframe, window_size)

        self.arf_calculator = ARIMARegressionModelCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.arf_calculator.forecast_periods()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self.dataframe.loc[
            self.dataframe["close"] < self.dataframe["arf"],
            "signal",
        ] = LONG_SIGNAL
        self.dataframe.loc[
            self.dataframe["close"] > self.dataframe["arf"],
            "signal",
        ] = SHORT_SIGNAL
