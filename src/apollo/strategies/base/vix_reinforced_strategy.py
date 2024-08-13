import pandas as pd

from apollo.calculations.conners_vix_reversal import ConnersVixReversalCalculator
from apollo.settings import (
    LONG_SIGNAL,
    NO_SIGNAL,
    SHORT_SIGNAL,
)


class VixReinforcedStrategy:
    """
    VIX Reinforced Strategy class.

    VIXEnhancedStrategy sounds better

    TODO: this is a fallback strategy (OR condition):
    adapt the docstrings of those strategies where it is used

    TODO: this strategy in itself is also a good strategy
    make a separate strategy class that uses only VIX

    TODO: reoptimize impacted strategies and new strategy

    Just some reading (this is a heavy WIP):

    https://www.investopedia.com/articles/active-trading/032415/strategies-trade-volatility-effectively-vix.asp

    https://www.whselfinvest.com/en-lu/trading-platform/free-trading-strategies/tradingsystem/40-vix-reversal

    https://howtotrade.com/trading-strategies/vix/

    Uses VIX index prices to reinforce signal
    generation logic of specialized strategies.

    Requests VIX index prices from the price data
    provider and enriches the supplied dataframe with them.

    Calculates Conners' VIX Reversals and generates VIX reinforced signal.

    This strategy reinforces long positions when:

    * VIX high at T is greater than the VIX highest high within the window.

    * VIX close at T is lower than VIX open at T.

    * VIX close at T-1 is greater than VIX open at T-1.

    * VIX range at T is greater than the VIX ranges within the window.

    This strategy reinforces short positions when:

    * VIX high at T is lower than the VIX highest high within the window.

    * VIX close at T is greater than VIX open at T.

    * VIX close at T-1 is lower than VIX open at T-1.

    * VIX ranges at T is lower than the VIX ranges within the window.

    Where VIX range is the difference between high and low.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.

    self._dataframe.loc[
        self._dataframe["vix_signal"] == LONG_SIGNAL,
        "signal",
    ] = LONG_SIGNAL

    self._dataframe.loc[
        self._dataframe["vix_signal"] == SHORT_SIGNAL,
        "signal",
    ] = SHORT_SIGNAL
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
