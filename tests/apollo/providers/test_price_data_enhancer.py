from unittest.mock import Mock

import pandas as pd
import pytest

from apollo.providers.price_data_enhancer import PriceDataEnhancer
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import MISSING_DATA_PLACEHOLDER, SUPPORTED_DATA_ENHANCERS


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


@pytest.mark.usefixtures("dataframe", "enhanced_dataframe")
def test__enhance_price_data__with_enhanced_data_partially_missing(
    dataframe: pd.DataFrame,
    enhanced_dataframe: pd.DataFrame,
) -> None:
    """
    Test enhance_price_data method with enhanced data partially missing.

    Price Data Enhancer should fill missing values with inf if there
    is more data in the price dataframe than in the enhanced dataframe.

    NOTE: we are using here enhanced_dataframe, even though it
    does not correspond to the actual enhanced data, but is
    already modified dataframe for the sake of this test.
    """

    # Remove first 5 rows from enhanced dataframe
    enhanced_dataframe = enhanced_dataframe[5:]

    price_data_enhancer = PriceDataEnhancer()
    price_data_enhancer._price_data_provider = Mock(PriceDataProvider)  # noqa: SLF001
    price_data_enhancer._price_data_provider.get_price_data.return_value = (  # noqa: SLF001
        enhanced_dataframe
    )

    control_dataframe = price_data_enhancer.enhance_price_data(
        price_dataframe=dataframe,
        additional_data_enhancers=["VIX"],
    )

    assert all(control_dataframe.iloc[:5]["vix open"] == MISSING_DATA_PLACEHOLDER)
    assert all(control_dataframe.iloc[:5]["vix close"] == MISSING_DATA_PLACEHOLDER)


@pytest.mark.usefixtures("dataframe", "enhanced_dataframe")
def test__enhance_price_data__for_correctly_enhancing_price_data(
    dataframe: pd.DataFrame,
    enhanced_dataframe: pd.DataFrame,
) -> None:
    """
    Test enhance_price_data method for correctly enhancing price data.

    Price Data Enhancer must insert additional columns with enhanced data.
    Additional column values should match the values from the enhanced dataframe.

    NOTE: we are using here enhanced_dataframe, even though it
    does not correspond to the actual enhanced data, but is
    already modified dataframe for the sake of this test.
    """

    price_data_enhancer = PriceDataEnhancer()
    price_data_enhancer._price_data_provider = Mock(PriceDataProvider)  # noqa: SLF001
    price_data_enhancer._price_data_provider.get_price_data.return_value = (  # noqa: SLF001
        enhanced_dataframe
    )

    control_dataframe = price_data_enhancer.enhance_price_data(
        price_dataframe=dataframe,
        additional_data_enhancers=["VIX"],
    )

    assert all(control_dataframe["vix open"] == enhanced_dataframe["open"])
    assert all(control_dataframe["vix close"] == enhanced_dataframe["close"])
