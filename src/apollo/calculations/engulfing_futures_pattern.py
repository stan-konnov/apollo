import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator
from apollo.settings import MISSING_DATA_PLACEHOLDER


class EngulfingFuturesPatternCalculator(BaseCalculator):
    """
    Engulfing Futures Pattern Calculator.

    Calculates bullish and bearish engulfing pattern for S&P 500 Futures.

    NOTE: This calculator is identical to Engulfing VIX Pattern Calculator,
    yet, is kept separate to maintain possibility of extending one
    or the other with additional functionality in the future.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    # Constant to
    # represent no pattern
    NO_PATTERN: float = 0.0

    # Constant to represent
    # bullish engulfing pattern
    BULLISH_ENGULFING: float = 1.0

    # Constant to represent
    # bearish engulfing pattern
    BEARISH_ENGULFING: float = -1.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Engulfing Futures Pattern Calculator.

        :param dataframe: Dataframe to calculate Engulfing Pattern for.
        :param window_size: Size of the window for Engulfing Pattern calculation.

        TODO: calculate midpoint for stars:
        midpoint_t_2 = (df['open_t_2'] + df['close_t_2']) / 2

        NOTE: even though we accept window_size parameter,
        calculator does not perform any rolling calculations.
        """

        super().__init__(dataframe, window_size)

    def calculate_engulfing_futures_pattern(self) -> None:
        """Calculate Engulfing Futures Pattern."""

        # We consider a doji
        # between 0.5% and 1%
        # NOTE: this should be a parameter
        doji_threshold = 0.007

        # Shadow on body ratio
        shadow_body_ratio = 2.0

        # Since we are working with multiple
        # data sources, there is no guarantee that
        # the data is present for all the rows in the dataframe
        # We, therefore, can calculate only over present data points,
        # otherwise, the strategy using the results will drop missing rows

        # Mark engulfing patterns to the dataframe
        self._dataframe["spfep"] = self.NO_PATTERN

        # Initialize necessary columns with 0
        self._dataframe["spf_low_tm1"] = 0.0
        self._dataframe["spf_high_tm1"] = 0.0

        self._dataframe["spf_open_tm1"] = 0.0
        self._dataframe["spf_open_tm2"] = 0.0

        self._dataframe["spf_close_tm1"] = 0.0
        self._dataframe["spf_close_tm2"] = 0.0

        # Shift open and close to t-1 and t-2
        self._dataframe.loc[
            self._dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
            "spf_open_tm1",
        ] = self._dataframe["spf open"].shift(1)

        self._dataframe.loc[
            self._dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
            "spf_open_tm2",
        ] = self._dataframe["spf open"].shift(2)

        self._dataframe.loc[
            self._dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
            "spf_close_tm1",
        ] = self._dataframe["spf close"].shift(1)

        self._dataframe.loc[
            self._dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
            "spf_close_tm2",
        ] = self._dataframe["spf close"].shift(2)

        # Shift low and high to t-1
        self._dataframe.loc[
            self._dataframe["spf low"] != MISSING_DATA_PLACEHOLDER,
            "spf_low_tm1",
        ] = self._dataframe["spf low"].shift(1)

        self._dataframe.loc[
            self._dataframe["spf high"] != MISSING_DATA_PLACEHOLDER,
            "spf_high_tm1",
        ] = self._dataframe["spf high"].shift(1)

        # Calculate the real body, upper shadow, and lower shadow
        real_body = abs(self._dataframe["spf close"] - self._dataframe["spf open"])

        upper_shadow = self._dataframe["spf high"] - self._dataframe[
            ["spf open", "spf close"]
        ].max(axis=1)

        lower_shadow = (
            self._dataframe[["spf open", "spf close"]].min(axis=1)
            - self._dataframe["spf low"]
        )

        bullish_engulfing = (
            (self._dataframe["spf open"] < self._dataframe["spf_open_tm1"])
            & (self._dataframe["spf close"] > self._dataframe["spf_close_tm1"])
            & (self._dataframe["spf close"] > self._dataframe["spf open"])
        )

        bearish_engulfing = (
            (self._dataframe["spf open"] > self._dataframe["spf_open_tm1"])
            & (self._dataframe["spf close"] < self._dataframe["spf_close_tm1"])
            & (self._dataframe["spf close"] < self._dataframe["spf open"])
        )

        bullish_morning_star = (
            # Candle 1: Long Bearish Candle (t-2)
            (self._dataframe["spf_close_tm2"] < self._dataframe["spf_open_tm2"])
            &
            # Candle 2: Small Candle (t-1), open and close are close together (Doji)
            (
                abs(self._dataframe["spf_close_tm1"] - self._dataframe["spf_open_tm1"])
                / self._dataframe["spf_open_tm1"]
                < doji_threshold
            )
            &
            # Candle 3: Long Bullish Candle (t)
            (self._dataframe["spf close"] > self._dataframe["spf open"])
            &
            # Close of t is above the midpoint of t-2
            (
                self._dataframe["spf close"]
                > (self._dataframe["spf_open_tm2"] + self._dataframe["spf_close_tm2"])
                / 2
            )
        )

        bearish_evening_star = (
            # Candle 1: Long Bullish Candle (t-2)
            (self._dataframe["spf_close_tm2"] > self._dataframe["spf_open_tm2"])
            &
            # Candle 2: Small Candle (t-1), open and close are close together (Doji)
            (
                abs(self._dataframe["spf_close_tm1"] - self._dataframe["spf_open_tm1"])
                / self._dataframe["spf_open_tm1"]
                < doji_threshold
            )
            &
            # Candle 3: Long Bearish Candle (t)
            (self._dataframe["spf close"] < self._dataframe["spf open"])
            &
            # Close of t is below the midpoint of t-2
            (
                self._dataframe["spf close"]
                < (self._dataframe["spf_open_tm2"] + self._dataframe["spf_close_tm2"])
                / 2
            )
        )

        bullish_hammer = (
            # Small real body
            (
                real_body
                < (self._dataframe["spf high"] - self._dataframe["spf low"]) * 0.3
            )
            &
            # Long lower shadow (at least twice the real body)
            (lower_shadow >= shadow_body_ratio * real_body)
            &
            # Little to no upper shadow
            (upper_shadow < real_body * 0.3)
        )

        bearish_shooting_star = (
            # Small real body
            (
                real_body
                < (self._dataframe["spf high"] - self._dataframe["spf low"]) * 0.3
            )
            &
            # Long upper shadow (at least twice the real body)
            (upper_shadow >= shadow_body_ratio * real_body)
            &
            # Little to no lower shadow
            (lower_shadow < real_body * 0.3)
        )

        self._dataframe.loc[
            (bullish_engulfing | bearish_evening_star | bullish_hammer),
            "spfep",
        ] = self.BULLISH_ENGULFING

        self._dataframe.loc[
            (bearish_engulfing | bullish_morning_star | bearish_shooting_star),
            "spfep",
        ] = self.BEARISH_ENGULFING

        # Drop unnecessary columns
        self._dataframe.drop(
            columns=["spf_open_tm1", "spf_close_tm1"],
            inplace=True,
        )
