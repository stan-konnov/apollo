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
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Construct VIX Reinforced Strategy.

        Initialize PriceDataProvider with VIX index ticker.
        """

        self._price_data_provider = PriceDataProvider(
            ticker=str(VIX_TICKER),
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        dataframe["vix close"] = 1
