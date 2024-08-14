import pandas as pd

from apollo.calculations.conners_vix_reversal import (
    ConnersVixExpansionContractionCalculator,
)
from apollo.settings import (
    LONG_SIGNAL,
    NO_SIGNAL,
    SHORT_SIGNAL,
)


class VIXEnhancedStrategy:
    """
    VIX Enhanced Strategy class.

    NOTE: THIS IS WIP, this needs to be properly explained and documented.

    Uses VIX index prices to enhance signal
    generation logic of specialized strategies.

    Calculates Conners' VIX Reversals and generates VIX enhanced signal.

    This strategy takes long positions when:

    * Current VIX open is lower than the previous VIX open,
    indicating a decrease in implied volatility.

    * Current VIX close is higher than the previous VIX close,
    indicating an upside reversal in implied volatility.

    This strategy takes short positions when:

    * Current VIX open is higher than the previous VIX open,
    indicating an increase in implied volatility.

    * Current VIX close is lower than the previous VIX close,
    indicating a downside reversal in implied volatility.

    NOTE: This strategy class is not a standalone strategy
    and should be used in conjunction with other strategies.

    Yet, the logic of VIX signals proved to be effective
    as a standalone strategy and, therefore, can be found
    in VIX Reversal Strategy class that uses the same signals.

    NOTE: This is an adapted version of Conners' VIX Reversals
    and does not follow the original logic to the letter.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.

    NOTE: "This capitalizes on the concept that non-professional traders
    liquidate when volatility increases, and buy when volatility decreases,
    commonly termed 'risk on' and 'risk off'" WE REVERT THIS!
    Kaufman, p 863.

    We are looking for VIX expansion to the upside
    (increased implied vol when underlying is falling)

    And VIX contraction to the downside
    (decreased implied vol when underlying is rising)
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct VIX Reinforced Strategy.

        Initialize PriceDataProvider with VIX index ticker,
        request VIX prices and enrich price dataframe with them.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        # Calculate Conners' VIX Expansion and Contraction
        cvec_calculator = ConnersVixExpansionContractionCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )
        cvec_calculator.calculate_vix_expansion_contraction()

        # Mark VIX reinforced signals to the dataframe
        dataframe["vix_signal"] = NO_SIGNAL

        dataframe.loc[
            dataframe["cvec"] == cvec_calculator.UPSIDE_EXPANSION,
            "vix_signal",
        ] = LONG_SIGNAL

        dataframe.loc[
            dataframe["cvec"] == cvec_calculator.DOWNSIDE_CONTRACTION,
            "vix_signal",
        ] = SHORT_SIGNAL
