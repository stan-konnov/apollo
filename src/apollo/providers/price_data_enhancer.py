import pandas as pd

from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    SP500_FUTURES_TICKER,
    START_DATE,
    SUPPORTED_DATA_ENHANCERS,
    VIX_TICKER,
)


class PriceDataEnhancer:
    """
    Price Data Enhancer class.

    Enhances price dataframe with
    additional price data from other instruments.

    Uses Price Data Provider to retrieve enhancing data
    and enrich the original price dataframe with new columns.
    """

    # If there is more data in the price dataframe
    # than in the enhanced dataframe, missing values will be
    # filled with NaNs and subsequently dropped by the strategy
    # We, therefore, avoid this by filling the missing values with 0
    MISSING_VALUE_FILLER = 0

    def __init__(self) -> None:
        """Construct Price Data Enhancer."""

        self._price_data_provider = PriceDataProvider()

    def enhance_price_data(
        self,
        price_dataframe: pd.DataFrame,
        additional_data_enhancers: list[str],
    ) -> pd.DataFrame:
        """
        Enhance price data with additional data sources.

        :param price_dataframe: Price data to enhance.
        :param additional_data_enhancers: List of additional data enhancers to use.
        :returns: Price data enhanced with additional data.

        :raises ValueError: If unsupported data enhancer is provided.
        """

        # Return original price data
        # if no enhancers are provided
        if not additional_data_enhancers:
            return price_dataframe

        # Loop through provided enhancers
        # and match and enhance the price data
        for enhancer in additional_data_enhancers:
            match enhancer:
                case "VIX":
                    vix_price_dataframe = self._price_data_provider.get_price_data(
                        ticker=str(VIX_TICKER),
                        frequency=str(FREQUENCY),
                        start_date=str(START_DATE),
                        end_date=str(END_DATE),
                        max_period=bool(MAX_PERIOD),
                    )

                    price_dataframe[["vix open", "vix close"]] = vix_price_dataframe[
                        ["open", "close"]
                    ]

                    if price_dataframe.shape[0] > vix_price_dataframe.shape[0]:
                        price_dataframe.fillna(
                            {
                                "vix open": self.MISSING_VALUE_FILLER,
                                "vix close": self.MISSING_VALUE_FILLER,
                            },
                            inplace=True,
                        )

                case "SP500 Futures":
                    sp500_futures_price_dataframe = (
                        self._price_data_provider.get_price_data(
                            ticker=str(SP500_FUTURES_TICKER),
                            frequency=str(FREQUENCY),
                            start_date=str(START_DATE),
                            end_date=str(END_DATE),
                            max_period=bool(MAX_PERIOD),
                        )
                    )

                    price_dataframe[["spf open", "spf close"]] = (
                        sp500_futures_price_dataframe[["open", "close"]]
                    )

                    if (
                        price_dataframe.shape[0]
                        > sp500_futures_price_dataframe.shape[0]
                    ):
                        price_dataframe.fillna(
                            {
                                "spf close": self.MISSING_VALUE_FILLER,
                            },
                            inplace=True,
                        )

                case _:
                    raise ValueError(
                        "Unsupported data enhancer provided "
                        f"in strategy configuration -- {enhancer}. "
                        f"Supported enhancers: {str(SUPPORTED_DATA_ENHANCERS)[:-2]}.",
                    )

        return price_dataframe
