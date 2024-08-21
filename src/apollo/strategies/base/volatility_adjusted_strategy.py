from pandas import DataFrame

from apollo.calculations.average_true_range import AverageTrueRangeCalculator


class VolatilityAdjustedStrategy:
    """
    Volatility Adjusted Strategy class.

    All strategies are designed to be trailing strategies
    that apply dynamic limit, stop loss and take profit orders.

    The limit, stop loss and take profit levels are calculated based on:

    * Average True Range (ATR), which is a measure of volatility.
    * Volatility multiplier, which is a user-defined parameter.
    * Current closing price of the analyzed instrument.

    The job of calculating these levels is delegated to backtesting module,
    yet, the strategy is responsible for providing necessary inputs.
    Therefore, this class calculates volatility for all strategies.
    """

    def __init__(self, dataframe: DataFrame, window_size: int) -> None:
        """
        Construct Volatility Adjusted Strategy.

        Calculate volatility for the strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        self._atr_calculator = AverageTrueRangeCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )
        self._atr_calculator.calculate_average_true_range()
