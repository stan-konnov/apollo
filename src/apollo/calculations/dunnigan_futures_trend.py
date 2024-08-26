import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class DunniganFuturesTrendCalculator(BaseCalculator):
    """
    Dunnigan Futures Trend Calculator.

    Is based on the Ruggiero's adaptation of Dunnigan's trend system,
    that revolves around identifying higher highs / higher lows and
    lower highs / lower lows to determine the trend of a security.

    Is applied to futures prices to produce enhancing trading signals.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Dunnigan, Selected Studies in Speculation, 1954.
    Ruggiero, "Dunnigan's Way", Futures, 1998.
    """

    # A constant to represent up trend
    UP_TREND: float = 1.0

    # A constant to represent down trend
    DOWN_TREND: float = -1.0

    # A constant to represent current trend
    CURRENT_TREND: float = 0.0

    # A constant to represent long-term trend
    LONG_TERM_TREND: float = 1.0

    # A constant to represent short-term trend
    SHORT_TERM_TREND: float = -1.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct Dunnigan Futures Trend Calculator."""

        super().__init__(dataframe, window_size)

    def calculate_dunnigan_futures_trend(self) -> None:
        """Calculate Dunnigan Futures Trend."""
