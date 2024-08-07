import pandas as pd

from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import END_DATE, FREQUENCY, MAX_PERIOD, START_DATE, VIX_TICKER


class VixReinforcedStrategy:
    """
    VIX Reinforced Strategy class.

    Uses VIX index close prices to reinforce
    signal generation logic of specialized strategies.

    Requests VIX index close prices from the price data
    provider and enriches the supplied dataframe with them.

    Calculates Conners' VIX reversals and generates VIX reinforced signal.

    This strategy takes long positions when:

    * VIX hight at T is greater than the VIX highest high within the last window.

    * VIX close at T is lower than VIX open at T.

    * VIX close at T-1 is greater than VIX open at T-1.

    * VIX close at T is greater than the VIX highest close within the last window.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, _: int) -> None:
        """
        Construct VIX Reinforced Strategy.

        Initialize PriceDataProvider with VIX index ticker,
        request VIX prices and enrich price dataframe with them.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        self._price_data_provider = PriceDataProvider(
            ticker=str(VIX_TICKER),
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        vix_prices = self._price_data_provider.get_price_data()

        # Enrich price dataframe with VIX open, high, and close
        dataframe["vix_open"] = vix_prices["open"]
        dataframe["vix_high"] = vix_prices["high"]
        dataframe["vix_close"] = vix_prices["close"]
