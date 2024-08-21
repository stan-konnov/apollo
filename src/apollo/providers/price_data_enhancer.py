import pandas as pd

from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
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
                    price_data_provider = PriceDataProvider(
                        ticker=str(VIX_TICKER),
                        frequency=str(FREQUENCY),
                        start_date=str(START_DATE),
                        end_date=str(END_DATE),
                        max_period=bool(MAX_PERIOD),
                    )

                    vix_price_dataframe = price_data_provider.get_price_data()

                    price_dataframe["vix open"] = vix_price_dataframe["open"]
                    price_dataframe["vix close"] = vix_price_dataframe["close"]

                    if any(price_dataframe["vix open"].isna().values):
                        price_dataframe["vix open"].fillna(
                            self.MISSING_VALUE_FILLER,
                            inplace=True,
                        )
                        price_dataframe["vix close"].fillna(
                            self.MISSING_VALUE_FILLER,
                            inplace=True,
                        )

                case _:
                    raise ValueError(
                        "Unsupported data enhancer provided "
                        f"in strategy configuration -- {enhancer}. "
                        f"Supported enhancers: {str(SUPPORTED_DATA_ENHANCERS)[:-2]}.",
                    )

        return price_dataframe
