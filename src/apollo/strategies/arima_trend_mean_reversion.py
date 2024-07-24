from pandas import DataFrame

from apollo.calculations.models.arima_regression import ARIMARegressionModelCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class ARIMATrendMeanReversion(BaseStrategy):
    """
    ARIMA Trend Mean Reversion.

    This strategy takes long positions when:

    * Adjusted close crosses below the forecasted trend,
    indicating that instrument entered oversold zone.

    This strategy takes short positions when:

    * Adjusted close crosses above the forecasted trend,
    indicating that instrument entered overbought zone.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct ARIMA Regression Forecast Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        super().__init__(dataframe, window_size)

        self._arm_calculator = ARIMARegressionModelCalculator(
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

        self._arm_calculator.forecast_trend_periods()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self._dataframe.loc[
            self._dataframe["adj close"] < self._dataframe["artf"],
            "signal",
        ] = LONG_SIGNAL

        self._dataframe.loc[
            self._dataframe["adj close"] > self._dataframe["artf"],
            "signal",
        ] = SHORT_SIGNAL
