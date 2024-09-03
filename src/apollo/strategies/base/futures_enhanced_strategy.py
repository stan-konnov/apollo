import pandas as pd

from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL

"""
TODO:

1. Reoptimize SkewKurtVol.
   Sharpe 2.095821210696717

2. Backtest new strategy and Futures enhancing on full period.

3. Make sure VIX enhanced strategy does not drop rows either.
"""


class FuturesEnhancedStrategy:
    """
    Futures Enhanced Strategy class.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Construct VIX Futures Enhanced Strategy.

        :param dataframe: Dataframe with price data.
        """

        # Since we are working with multiple
        # data sources, there is no guarantee that
        # the data is present for all the rows in the dataframe
        # We, therefore, need to check for the presence of the data
        # to avoid excluding rows that will result in NaNs during calculations

        # Mark futures enhanced signals to the dataframe
        dataframe["spf_signal"] = NO_SIGNAL

        # Initialize necessary columns with 0s
        dataframe["spf_prev_open"] = 0
        dataframe["spf_prev_close"] = 0

        # Shift open and close prices only if the data is present
        dataframe.loc[dataframe["spf open"].notna(), "spf_prev_open"] = dataframe[
            "spf open"
        ].shift(1)

        dataframe.loc[dataframe["spf close"].notna(), "spf_prev_close"] = dataframe[
            "spf close"
        ].shift(
            1,
        )

        # Build condition for
        # presence of necessary data
        necessary_data_present = (
            dataframe["spf open"].notna()
            & dataframe["spf close"].notna()
            & dataframe["spf_prev_open"].notna()
            & dataframe["spf_prev_close"].notna()
        )

        # And compute the signals
        long = (
            necessary_data_present
            & (dataframe["spf open"] > dataframe["spf_prev_open"])
            & (dataframe["spf close"] < dataframe["spf_prev_close"])
            & (dataframe["spf close"] < dataframe["spf open"])
        )

        dataframe.loc[long, "spf_signal"] = LONG_SIGNAL

        short = (
            necessary_data_present
            & (dataframe["spf open"] < dataframe["spf_prev_open"])
            & (dataframe["spf close"] > dataframe["spf_prev_close"])
            & (dataframe["spf close"] > dataframe["spf open"])
        )

        dataframe.loc[short, "spf_signal"] = SHORT_SIGNAL
