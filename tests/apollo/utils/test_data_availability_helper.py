from datetime import datetime

from freezegun import freeze_time
from zoneinfo import ZoneInfo

from apollo.utils.data_availability_helper import DataAvailabilityHelper


# Assume today date is Friday, 2024-07-12
@freeze_time("2024-07-12")
def test__check_if_price_data_needs_update__with_last_record_before_prev_b_day() -> (
    None
):
    """
    Test check_if_price_data_needs_update with last record before previous business day.

    Function should return True.
    """

    # Assume last available record date is Monday, 2024-07-01
    last_record_date = datetime(2024, 7, 1, tzinfo=ZoneInfo("UTC")).date()

    result = DataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is True


# Assume today date is Friday, 2024-07-12
# Assume current time is after 16:00 ET = 20:00 UTC
@freeze_time("2024-07-12 21:00:00")
def test__check_if_price_data_needs_update__with_last_record_being_prev_b_day() -> None:
    """
    Test check_if_price_data_needs_update with last record being previous business day.

    And time is past exchange close time = data should be available from exchange.

    Function should return True.
    """

    # Assume last available record date is Thursday, 2024-07-11
    last_record_date = datetime(2024, 7, 1, tzinfo=ZoneInfo("UTC")).date()

    result = DataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is True
