from unittest.mock import patch

import pytest
from numpy import datetime64

from apollo.utils.common import ensure_environment_is_configured, to_default_date_string


def test__to_default_date_string__with_proper_inputs() -> None:
    """
    Test to_default_date_string with proper inputs.

    Function must return date string in YYYY-MM-DD format.
    """

    assert to_default_date_string(datetime64("2021-01-01")) == "2021-01-01"


@patch("apollo.utils.common.TICKER", None)
def test__ensure_environment_is_configured__for_correctly_checking_env_variables() -> (
    None
):
    """
    Test ensure_environment_is_configured for properly checking env variables.

    Function must raise an exception if any of the required variables are not set.
    """

    exception_message = str(
        "TICKER, EXCHANGE, STRATEGY, START_DATE, END_DATE, "
        "INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_TOKEN, INFLUXDB_URL "
        "environment variables must be set.",
    )

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        ensure_environment_is_configured()

    assert str(exception.value) == exception_message
