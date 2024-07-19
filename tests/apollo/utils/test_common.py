from unittest.mock import patch

import pytest
from numpy import datetime64

from apollo.backtesting.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.settings import (
    END_DATE,
    EXCHANGE,
    FREQUENCY,
    INFLUXDB_BUCKET,
    INFLUXDB_MEASUREMENT,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    POSTGRES_URL,
    START_DATE,
    TICKER,
)
from apollo.utils.common import ensure_environment_is_configured, to_default_date_string
from tests.fixtures.env_and_constants import STRATEGY


def test__to_default_date_string__with_proper_inputs() -> None:
    """
    Test to_default_date_string with proper inputs.

    Function must return date string in YYYY-MM-DD format.
    """

    assert to_default_date_string(datetime64("2021-01-01")) == "2021-01-01"


# As we test for the absence of at least one
# environment variable patching only one of them is enough
@patch("apollo.utils.common.TICKER", None)
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
        "POSTGRES_URL": POSTGRES_URL,
        "INFLUXDB_BUCKET": INFLUXDB_BUCKET,
        "INFLUXDB_ORG": INFLUXDB_ORG,
        "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
        "INFLUXDB_URL": INFLUXDB_URL,
        "INFLUXDB_MEASUREMENT": INFLUXDB_MEASUREMENT,
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


@patch("apollo.utils.common.STRATEGY", "SomeNonExistentStrategy")
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
