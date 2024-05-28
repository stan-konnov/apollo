import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class RelativeStrengthIndexCalculator(BaseCalculator):
    """
    Relative Strength Index (RSI) Calculator.

    Momentum oscillator that measures
    the speed and change of price movements.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Wilder, New Concepts in Technical Trading Systems, 1978.
    """

    def calculate_relative_strength_index(self) -> None:
        """Calculate RSI using deltas and EMA."""

        # Calculate positive and negative deltas
        pos_delta, neg_delta = (
            self.dataframe["adj close"]
            .rolling(self.window_size)
            .apply(self.__calc_deltas)
        )

        # Calculate EMA for both deltas
        self.dataframe["pos_delta_ma"] = self.__calc_ema(pos_delta)
        self.dataframe["neg_delta_ma"] = self.__calc_ema(neg_delta)

        # Calculate RSI
        self.dataframe["rsi"] = (
            self.dataframe["adj close"]
            .rolling(self.window_size)
            .apply(
                self.__calc_rsi,
                args=(self.dataframe,),
            )
        )

        # Drop unnecessary columns
        self.dataframe.drop(
            columns=["pos_delta_ma", "neg_delta_ma"],
            inplace=True,
        )

    def __calc_deltas(self, series: pd.Series) -> tuple[pd.Series, pd.Series]:
        """
        Calculate deltas between adjusted close prices.

        :param series: Series to calculate deltas for.
        :returns: Tuple of positive and negative deltas.
        """

        # Identify differences between adjusted close prices
        close_delta = series.diff()

        # Calculate positive and negative deltas
        pos_delta = close_delta.clip(lower=0)
        neg_delta = close_delta.clip(upper=0) * -1

        # Return latest entry from processed window
        return (pos_delta, neg_delta)

    def __calc_ema(self, series: pd.Series) -> pd.Series:
        """
        Calculate EMA using J. Welles Wilder's EMA (The creator of RSI).

        :param series: Series to calculate EMA for.
        :returns: EMA of provided series.
        """

        return series.ewm(
            alpha=1 / self.window_size,
            min_periods=self.window_size,
            adjust=False,
        ).mean()

    def __calc_rsi(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Calculate RSI for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Calculate Relative Strength
        rel_str = rolling_df["pos_delta_ma"] / rolling_df["neg_delta_ma"]

        # Calculate Relative Strength Index
        rsi = 100 - (100 / (1 + rel_str))

        # Return latest entry from processed window
        return rsi.iloc[-1]
