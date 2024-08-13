import pandas as pd

from apollo.calculations.conners_vix_reversal import ConnersVixReversalCalculator
from apollo.settings import (
    LONG_SIGNAL,
    NO_SIGNAL,
    SHORT_SIGNAL,
)


class VIXEnhancedStrategy:
    """
    VIX Enhanced Strategy class.

    Uses VIX index prices to enhance signal
    generation logic of specialized strategies.

    Calculates Conners' VIX Reversals and generates VIX enhanced signal.

    This strategy takes long positions when:

    This strategy takes short positions when:

    NOTE: This strategy class is not a standalone strategy
    and should be used in conjunction with other strategies.

    Yet, the logic of VIX signals proved to be effective
    as a standalone strategy and, therefore, can be found
    in VIX Reversal Strategy class that uses the same signals.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct VIX Reinforced Strategy.

        Initialize PriceDataProvider with VIX index ticker,
        request VIX prices and enrich price dataframe with them.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        # Calculate Conners' VIX Reversals
        cvr_calculator = ConnersVixReversalCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )
        cvr_calculator.calculate_vix_reversals()

        # Mark VIX reinforced signals to the dataframe
        dataframe["vix_signal"] = NO_SIGNAL

        dataframe.loc[
            dataframe["cvr"] == cvr_calculator.UPSIDE_REVERSAL,
            "vix_signal",
        ] = LONG_SIGNAL

        dataframe.loc[
            dataframe["cvr"] == cvr_calculator.DOWNSIDE_REVERSAL,
            "vix_signal",
        ] = SHORT_SIGNAL
