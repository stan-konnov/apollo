from datetime import datetime

from freezegun import freeze_time
from zoneinfo import ZoneInfo

from apollo.utils.price_data_availability_helper import PriceDataAvailabilityHelper


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

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is True


# Assume today date is Friday, 2024-07-12
# Assume current time is after 16:00 ET >= 20:00 UTC
@freeze_time("2024-07-12 21:00:00")
def test__check_if_price_data_needs_update__with_last_record_prev_b_day_ah() -> None:
    """
    Test check_if_price_data_needs_update with last record being previous business day.

    And time is past exchange close time = data should be available from exchange.

    Function should return True.
    """

    # Assume last available record date is Thursday, 2024-07-11
    last_record_date = datetime(2024, 7, 11, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is True


# Assume today date is Friday, 2024-07-12
# Assume current time is trading hours 13:00 ET = 17:00 UTC
@freeze_time("2024-07-12 17:00:00")
def test__check_if_price_data_needs_update__with_last_record_prev_b_day_id() -> None:
    """
    Test check_if_price_data_needs_update with last record being previous business day.

    And time is during exchange trading hours = data should not be available.

    Function should return False.
    """

    # Assume last available record date is Thursday, 2024-07-11
    last_record_date = datetime(2024, 7, 11, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is False


# Assume today date is Saturday, 2024-07-13
@freeze_time("2024-07-13")
def test__check_if_price_data_needs_update__with_last_record_prev_b_day_we() -> None:
    """
    Test check_if_price_data_needs_update with last record being previous business day.

    And current date is weekend = data should not be available.

    Function should return False.
    """

    # Assume last available record date is Friday, 2024-07-12
    last_record_date = datetime(2024, 7, 12, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is False


# Assume today date is Saturday, 2024-07-13
# Assume current time is after 16:00 ET >= 20:00 UTC
@freeze_time("2024-07-13 21:00:00")
def test__check_if_price_data_needs_update__with_last_record_prev_b_day_we_ah() -> None:
    """
    Test check_if_price_data_needs_update with last record being previous business day.

    And current date is weekend after exchange closed = data should not be available.

    Function should return False.
    """

    # Assume last available record date is Friday, 2024-07-12
    last_record_date = datetime(2024, 7, 12, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is False


# Assume today date is Saturday, 2024-07-13
@freeze_time("2024-07-13 21:00:00")
def test__check_if_price_data_needs_update__with_last_record_before_prev_b_day_we() -> (
    None
):
    """
    Test check_if_price_data_needs_update with last record before previous business day.

    And current date is weekend = data (for Friday) should be available.

    Function should return True.
    """

    # Assume last available record date is Thursday, 2024-07-11
    last_record_date = datetime(2024, 7, 11, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is True


# Assume today date is Monday, 2024-07-15
# Assume current time is trading hours 13:00 ET = 17:00 UTC
@freeze_time("2024-07-15 17:00")
def test__check_if_price_data_needs_update__with_last_record_prev_b_day_awe() -> None:
    """
    Test check_if_price_data_needs_update with last record being previous business day.

    And current date is business day after weekend = data should not be available.

    Function should return False.
    """

    # Assume last available record date is Friday, 2024-07-12
    last_record_date = datetime(2024, 7, 12, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is False


# Assume today date is Monday, 2024-07-15
# Assume current time is after 16:00 ET >= 20:00 UTC
@freeze_time("2024-07-15 21:00")
def test__check_if_price_data_needs_update__with_last_record_prev_b_day_awe_ah() -> (
    None
):
    """
    Test check_if_price_data_needs_update with last record being previous business day.

    And current date is business day after weekend, after close = data available.

    Function should return True.
    """

    # Assume last available record date is Friday, 2024-07-12
    last_record_date = datetime(2024, 7, 12, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_needs_update(
        last_record_date,
    )

    assert result is True


# Assume today date is Monday, 2024-07-15
# Assume current time is trading hours 13:00 ET = 17:00 UTC
@freeze_time("2024-07-15 17:00")
def test__check_if_price_data_includes_intraday__with_last_query_intraday() -> None:
    """
    Test check_if_price_data_includes_intraday with last query today during intraday.

    Function should return True.
    """

    # Assume last queried record date is Monday, 2024-07-15
    last_queried_date = datetime(2024, 7, 15, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_includes_intraday(
        last_queried_date,
    )

    assert result is True


# Assume today date is Monday, 2024-07-15
# Assume current time is after 16:00 ET >= 20:00 UTC
@freeze_time("2024-07-15 21:00")
def test__check_if_price_data_includes_intraday__with_last_query_after_hours() -> None:
    """
    Test check_if_price_data_includes_intraday with last query today after hours.

    Function should return False.
    """

    # Assume last queried record date is Monday, 2024-07-15
    last_queried_date = datetime(2024, 7, 15, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_includes_intraday(
        last_queried_date,
    )

    assert result is False


# Assume today date is Monday, 2024-07-15
# Assume current time is trading hours 13:00 ET = 17:00 UTC
@freeze_time("2024-07-15 17:00")
def test__check_if_price_data_includes_intraday__with_last_query_before_today() -> None:
    """
    Test check_if_price_data_includes_intraday with last query before today.

    Function should return False.
    """

    # Assume last queried record date is Friday, 2024-07-12
    last_queried_date = datetime(2024, 7, 12, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_includes_intraday(
        last_queried_date,
    )

    assert result is False


# Assume today date is Saturday, 2024-07-13
# Assume current time is after 16:00 ET >= 20:00 UTC
@freeze_time("2024-07-13 21:00")
def test__check_if_price_data_includes_intraday__with_last_query_before_today_we() -> (
    None
):
    """
    Test check_if_price_data_includes_intraday with last query before today.

    And today is weekend after hours.

    Function should return False.
    """

    # Assume last queried record date is Friday, 2024-07-12
    last_queried_date = datetime(2024, 7, 12, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_includes_intraday(
        last_queried_date,
    )

    assert result is False


# Assume today date is Saturday, 2024-07-13
# Assume current time is trading hours 13:00 ET = 17:00 UTC
@freeze_time("2024-07-13 17:00")
def test__check_if_price_data_includes_intraday__with_last_query_before_today_id() -> (
    None
):
    """
    Test check_if_price_data_includes_intraday with last query before today.

    And today is weekend during trading hours.

    Function should return False.
    """

    # Assume last queried record date is Friday, 2024-07-12
    last_queried_date = datetime(2024, 7, 12, tzinfo=ZoneInfo("UTC")).date()

    result = PriceDataAvailabilityHelper.check_if_price_data_includes_intraday(
        last_queried_date,
    )

    assert result is False
