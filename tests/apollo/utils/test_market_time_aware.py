from datetime import datetime

from freezegun import freeze_time
from zoneinfo import ZoneInfo

from apollo.settings import DEFAULT_TIME_FORMAT, EXCHANGE, EXCHANGE_TIME_ZONE_AND_HOURS
from apollo.utils.market_time_aware import MarketTimeAware


# Assume today date is Friday, 2025-06-20
@freeze_time("2025-06-20 16:00:00")
def test__get_market_time_metrics__for_correctly_calculating_metrics_on_trading_day() -> (  # noqa: E501
    None
):
    """Test _get_market_time_metrics method for correct metrics."""

    market_time_aware = MarketTimeAware()

    market_time_metrics = market_time_aware._get_market_time_metrics()  # noqa: SLF001

    assert market_time_metrics.is_business_day is True
    assert market_time_metrics.is_market_holiday is False


# Assume today date is Thursday, 2025-06-19
@freeze_time("2025-06-19 16:00:00")
def test__get_market_time_metrics__for_correctly_calculating_metrics_on_non_trading_day() -> (  # noqa: E501
    None
):
    """Test _get_market_time_metrics method for correct metrics."""

    market_time_aware = MarketTimeAware()

    market_time_metrics = market_time_aware._get_market_time_metrics()  # noqa: SLF001

    assert market_time_metrics.is_business_day is True
    assert market_time_metrics.is_market_holiday is True


# Assume today date is Saturday, 2025-06-21
@freeze_time("2025-06-21 16:00:00")
def test__get_market_time_metrics__for_correctly_calculating_metrics_non_weekend() -> (
    None
):
    """Test _get_market_time_metrics method for correct metrics."""

    market_time_aware = MarketTimeAware()

    market_time_metrics = market_time_aware._get_market_time_metrics()  # noqa: SLF001

    assert market_time_metrics.is_business_day is False
    assert market_time_metrics.is_market_holiday is False


# Assume today date is Monday, 2025-06-23
@freeze_time("2025-06-23 16:00:00")
def test__get_market_time_metrics__for_correctly_calculating_brackets_during_trading_hours() -> (  # noqa: E501
    None
):
    """Test _get_market_time_metrics method for correct metrics."""

    market_time_aware = MarketTimeAware()

    market_time_metrics = market_time_aware._get_market_time_metrics()  # noqa: SLF001

    exchange_timezone = EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]

    control_current_datetime_in_exchange = datetime.now(
        tz=ZoneInfo(exchange_timezone),
    )

    control_current_date_in_exchange = control_current_datetime_in_exchange.date()

    control_open_datetime_in_exchange = datetime.combine(
        control_current_date_in_exchange,
        datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["open"],
            DEFAULT_TIME_FORMAT,
        ).time(),
    ).replace(tzinfo=ZoneInfo(exchange_timezone))

    control_close_datetime_in_exchange = datetime.combine(
        control_current_date_in_exchange,
        datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["close"],
            DEFAULT_TIME_FORMAT,
        ).time(),
    ).replace(tzinfo=ZoneInfo(exchange_timezone))

    assert (
        market_time_metrics.current_date_in_exchange == control_current_date_in_exchange
    )
    assert (
        market_time_metrics.open_datetime_in_exchange
        == control_open_datetime_in_exchange
    )
    assert (
        market_time_metrics.close_datetime_in_exchange
        == control_close_datetime_in_exchange
    )
    assert (
        market_time_metrics.current_datetime_in_exchange
        == control_current_datetime_in_exchange
    )


# Assume today date is Saturday, 2025-06-21
@freeze_time("2025-06-21 16:00:00")
def test__determine_if_generate_or_execute__to_not_generate_on_the_weekend() -> None:
    """Test _determine_if_generate_or_execute method to not generate on the weekend."""

    market_time_aware = MarketTimeAware()

    can_generate, _ = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_generate is False


# Assume today date is Thursday, 2025-06-19
@freeze_time("2025-06-19 16:00:00")
def test__determine_if_generate_or_execute__to_not_generate_on_market_holiday() -> None:
    """Test _determine_if_generate_or_execute method to not generate on MH."""

    market_time_aware = MarketTimeAware()

    can_generate, _ = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_generate is False


# Assume today date is Monday, 2025-06-23
@freeze_time("2025-06-23 16:00:00")
def test__determine_if_generate_or_execute__to_not_generate_during_market_hours() -> (
    None
):
    """Test _determine_if_generate_or_execute method to not generate during MH."""

    market_time_aware = MarketTimeAware()

    can_generate, _ = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_generate is False
