from unittest.mock import patch

import pytest
from numpy import datetime64

from apollo.core.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.core.utils.common import (
    ensure_environment_is_configured,
    to_default_date_string,
)
from apollo.settings import (
    END_DATE,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    FREQUENCY,
    INFLUXDB_BUCKET,
    INFLUXDB_MEASUREMENT,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    POSTGRES_URL,
    SCREENING_LIQUIDITY_THRESHOLD,
    SCREENING_WINDOW_SIZE,
    SP500_COMPONENTS_URL,
    SP500_FUTURES_TICKER,
    START_DATE,
    STRATEGY,
    SUPPORTED_DATA_ENHANCERS,
    TICKER,
    VIX_TICKER,
    PriceDataFrequency,
)


def test__to_default_date_string__with_proper_inputs() -> None:
    """
    Test to_default_date_string with proper inputs.

    Function must return date string in YYYY-MM-DD format.
    """

    assert to_default_date_string(datetime64("2021-01-01")) == "2021-01-01"


# As we test for the absence of at least one
# environment variable patching only one of them is enough
@patch("apollo.core.utils.common.TICKER", None)
def test__ensure_environment_is_configured__for_correctly_checking_env_variables() -> (
    None
):
    """
    Test ensure_environment_is_configured for properly checking env variables.

    Function must raise an exception if any of the required variables are not set.
    """

    required_variables = {
        "TICKER": TICKER,
        "EXCHANGE": EXCHANGE,
        "STRATEGY": STRATEGY,
        "START_DATE": START_DATE,
        "END_DATE": END_DATE,
        "FREQUENCY": FREQUENCY,
        "VIX_TICKER": VIX_TICKER,
        "POSTGRES_URL": POSTGRES_URL,
        "INFLUXDB_URL": INFLUXDB_URL,
        "INFLUXDB_ORG": INFLUXDB_ORG,
        "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
        "INFLUXDB_BUCKET": INFLUXDB_BUCKET,
        "INFLUXDB_MEASUREMENT": INFLUXDB_MEASUREMENT,
        "SP500_COMPONENTS_URL": SP500_COMPONENTS_URL,
        "SP500_FUTURES_TICKER": SP500_FUTURES_TICKER,
        "SCREENING_WINDOW_SIZE": SCREENING_WINDOW_SIZE,
        "SUPPORTED_DATA_ENHANCERS": SUPPORTED_DATA_ENHANCERS,
        "SCREENING_LIQUIDITY_THRESHOLD": SCREENING_LIQUIDITY_THRESHOLD,
    }

    exception_message = (
        f"{', '.join(required_variables)} environment variables must be set."
    )

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        ensure_environment_is_configured()

    assert str(exception.value) == exception_message


@patch("apollo.core.utils.common.STRATEGY", "SomeNonExistentStrategy")
def test__ensure_environment_is_configured__for_invalidating_strategy() -> None:
    """
    Test ensure_environment_is_configured for invalidating strategy.

    Function must raise an exception if the strategy is not a valid strategy.
    """

    exception_message = str(
        "Invalid STRATEGY environment variable: SomeNonExistentStrategy. "
        f"Accepted values: {', '.join(STRATEGY_CATALOGUE_MAP)}",
    )

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        ensure_environment_is_configured()

    assert str(exception.value) == exception_message


@patch("apollo.core.utils.common.EXCHANGE", "ABCD")
def test__ensure_environment_is_configured__for_invalidating_exchange() -> None:
    """
    Test ensure_environment_is_configured for invalidating exchange.

    Function must raise an exception if the exchange is not a valid exchange.
    """

    exception_message = str(
        "Invalid EXCHANGE environment variable: ABCD. "
        f"Accepted values: {', '.join(EXCHANGE_TIME_ZONE_AND_HOURS)}",
    )

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        ensure_environment_is_configured()

    assert str(exception.value) == exception_message


@patch("apollo.core.utils.common.FREQUENCY", "inf")
def test__ensure_environment_is_configured__for_invalidating_frequency() -> None:
    """
    Test ensure_environment_is_configured for invalidating frequency.

    Function must raise an exception if the frequency is not a valid frequency.
    """

    exception_message = str(
        "Invalid FREQUENCY environment variable: inf. "
        f"Accepted values: {', '.join([f.value for f in PriceDataFrequency])}",
    )

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        ensure_environment_is_configured()

    assert str(exception.value) == exception_message
