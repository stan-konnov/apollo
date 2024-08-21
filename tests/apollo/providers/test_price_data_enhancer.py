import pandas as pd
import pytest

from apollo.providers.price_data_enhancer import PriceDataEnhancer
from apollo.settings import SUPPORTED_DATA_ENHANCERS


@pytest.mark.usefixtures("dataframe")
def test__enhance_price_data__with_unsupported_enhancers(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test enhance_price_data method with unsupported enhancers.

    Price Data Enhancer should raise ValueError if unsupported enhancer is provided.
    """

    data_enhancers = ["unsupported_enhancer"]

    exception_message = (
        "Unsupported data enhancer provided "
        f"in strategy configuration -- {data_enhancers[0]}. "
        f"Supported enhancers: {str(SUPPORTED_DATA_ENHANCERS)[:-2]}."
    )

    price_data_enhancer = PriceDataEnhancer()

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        price_data_enhancer.enhance_price_data(
            price_dataframe=dataframe,
            additional_data_enhancers=data_enhancers,
        )

    assert str(exception.value) == exception_message


def test__enhance_price_data__without_enhancers(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test enhance_price_data method without enhancers.

    Price Data Enhancer should return original price data if no enhancers are provided.
    """

    price_data_enhancer = PriceDataEnhancer()

    control_dataframe = price_data_enhancer.enhance_price_data(
        price_dataframe=dataframe,
        additional_data_enhancers=[],
    )

    pd.testing.assert_frame_equal(control_dataframe, dataframe)
