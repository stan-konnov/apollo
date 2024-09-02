import pandas as pd

from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL

"""
TODO:

1. Every enhanced strategy or strategy that relies on enhanced data
   should validate if the data is present in the dataframe before using it.

2. Go through every strategy top to bottom and figure out if they
   can be enhanced with VIX Futures signals.

3. Use futures high and low for enhancing instead of VIX Futures Conv Divergence.
"""


class VIXFuturesEnhancedStrategy:
    """
    VIX Futures Enhanced Strategy class.

    Massive work in progress.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Construct VIX Futures Enhanced Strategy.

        :param dataframe: Dataframe with price data.
        """

        # Mark VIX Futures enhanced signals to the dataframe
        dataframe["vix_spf_signal"] = NO_SIGNAL

        dataframe["spf_prev_open"] = dataframe["spf open"].shift(1)
        dataframe["spf_prev_close"] = dataframe["spf close"].shift(1)

        long = (dataframe["spf open"] > dataframe["spf_prev_open"]) & (
            dataframe["spf close"] > dataframe["prev_spf_close"]
        )

        dataframe.loc[long, "vix_spf_signal"] = LONG_SIGNAL

        short = (dataframe["spf open"] < dataframe["spf_prev_open"]) & (
            dataframe["spf close"] < dataframe["spf_prev_close"]
        )

        dataframe.loc[short, "vix_spf_signal"] = SHORT_SIGNAL
