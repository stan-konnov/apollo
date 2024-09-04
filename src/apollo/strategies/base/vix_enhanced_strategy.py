import pandas as pd

from apollo.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.settings import (
    LONG_SIGNAL,
    NO_SIGNAL,
    SHORT_SIGNAL,
)


class VIXEnhancedStrategy:
    """
    VIX Enhanced Strategy class.

    WIP DOCS.

    Uses VIX index prices to enhance signal
    generation logic of specialized strategies.

    Calculates Conners' VIX Expansion and
    Contraction and generates VIX enhanced signal.

    This strategy takes long positions when:

    * Current VIX open is lower than the previous VIX open.

    * Current VIX close is higher than the previous VIX close.

    * Current VIX close is higher than the current VIX open.

    Combination of these factors point to an upside
    range expansion in implied volatility and a sharp decline
    in the underlying asset price with the potential for a reversal.

    This strategy takes short positions when:

    * Current VIX open is higher than the previous VIX open.

    * Current VIX close is lower than the previous VIX close.

    * Current VIX close is lower than the current VIX open.

    Combination of these factors point to a downside
    range contraction in implied volatility and a steady rise
    in the underlying asset price with the potential for a reversal.

    "This capitalizes on the concept that non-professional traders liquidate
    when volatility increases, and buy when volatility decreases,
    commonly termed 'risk on' and 'risk off'".

    Kaufman, Trading Systems and Methods, 2020, 6th ed., p 863.

    The strategy, therefore, aims to reverse this logic
    and capture the reversal points in the underlying asset price.

    NOTE: This strategy class is not a standalone strategy
    and should be used in conjunction with other strategies.

    Yet, the logic of VIX signals proved to be effective
    enough and, therefore, is applied in isolation in
    VIX Expansion Contraction Mean Reversion class.

    NOTE: This is an adapted version of Conners' VIX Reversals
    and does not follow the original logic to the letter.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct VIX Enhanced Strategy.

        Initialize PriceDataProvider with VIX index ticker,
        request VIX prices and enrich price dataframe with them.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        # Calculate Engulfing VIX Pattern
        evp_calculator = EngulfingVIXPatternCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )
        evp_calculator.calculate_engulfing_vix_pattern()

        # Mark VIX enhanced signals to the dataframe
        dataframe["vix_signal"] = NO_SIGNAL

        dataframe.loc[
            dataframe["vixep"] == evp_calculator.BULLISH_ENGULFING,
            "vix_signal",
        ] = LONG_SIGNAL

        dataframe.loc[
            dataframe["vixep"] == evp_calculator.BEARISH_ENGULFING,
            "vix_signal",
        ] = SHORT_SIGNAL
