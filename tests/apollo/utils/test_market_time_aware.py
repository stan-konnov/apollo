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


# Assume today date is Monday, 2025-06-23
@freeze_time("2025-06-23 23:00:00")
def test__determine_if_generate_or_execute__to_generate_after_market_hours() -> None:
    """Test _determine_if_generate_or_execute method to generate after MH."""

    market_time_aware = MarketTimeAware()

    can_generate, _ = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_generate is True


# Assume today date is Saturday, 2025-06-21
@freeze_time("2025-06-21 16:00:00")
def test__determine_if_generate_or_execute__to_not_execute_on_the_weekend() -> None:
    """Test _determine_if_generate_or_execute method to not execute on the weekend."""

    market_time_aware = MarketTimeAware()

    _, can_execute = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_execute is False


# Assume today date is Thursday, 2025-06-19
@freeze_time("2025-06-19 16:00:00")
def test__determine_if_generate_or_execute__to_not_execute_on_market_holiday() -> None:
    """Test _determine_if_generate_or_execute method to not execute on MH."""

    market_time_aware = MarketTimeAware()

    _, can_execute = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_execute is False


# Assume today date is Monday, 2025-06-23
@freeze_time("2025-06-23 23:00:00")
def test__determine_if_generate_or_execute__to_not_execute_after_market_hours() -> None:
    """Test _determine_if_generate_or_execute method to not execute after MH."""

    market_time_aware = MarketTimeAware()

    _, can_execute = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_execute is False


# Assume today date is Monday, 2025-06-23
@freeze_time("2025-06-23 16:00:00")
def test__determine_if_generate_or_execute__to_execute_during_market_hours() -> None:
    """Test _determine_if_generate_or_execute method to execute during MH."""

    market_time_aware = MarketTimeAware()

    _, can_execute = market_time_aware._determine_if_generate_or_execute()  # noqa: SLF001

    assert can_execute is True


# Assume today date is Saturday, 2025-06-21
@freeze_time("2025-06-21 16:00:00")
def test__determine_if_market_is_closing__to_be_falsy_on_weekend() -> None:
    """Test _determine_if_market_is_closing method to be falsy on the weekend."""

    market_time_aware = MarketTimeAware()

    is_closing = market_time_aware._determine_if_market_is_closing()  # noqa: SLF001

    assert is_closing is False


# Assume today date is Thursday, 2025-06-19
@freeze_time("2025-06-19 16:00:00")
def test__determine_if_market_is_closing__to_to_be_falsy_on_market_holiday() -> None:
    """Test _determine_if_market_is_closing method to be falsy on MH."""

    market_time_aware = MarketTimeAware()

    is_closing = market_time_aware._determine_if_market_is_closing()  # noqa: SLF001

    assert is_closing is False


# Assume today date is Monday, 2025-06-23, 10:00
@freeze_time(
    datetime(
        2025,
        6,
        23,
        10,
        0,
        0,
        tzinfo=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]),
    ),
)
def test__determine_if_market_is_closing__to_to_be_falsy_during_market_hours() -> None:
    """Test _determine_if_market_is_closing method to be falsy during MH."""

    market_time_aware = MarketTimeAware()

    is_closing = market_time_aware._determine_if_market_is_closing()  # noqa: SLF001

    assert is_closing is False


# Assume today date is Monday, 2025-06-23
@freeze_time("2025-06-23 22:30:00")
def test__determine_if_market_is_closing__to_be_falsy_after_market_close() -> None:
    """Test _determine_if_market_is_closing method to be falsy after MH."""

    market_time_aware = MarketTimeAware()

    is_closing = market_time_aware._determine_if_market_is_closing()  # noqa: SLF001

    assert is_closing is False


# Assume today date is Monday, 2025-06-23
@freeze_time("2025-06-23 19:45:01")
def test__determine_if_market_is_closing__to_be_truthy_soon_before_market_close() -> (
    None
):
    """Test _determine_if_market_is_closing method to be truthy soon."""

    market_time_aware = MarketTimeAware()

    is_closing = market_time_aware._determine_if_market_is_closing()  # noqa: SLF001

    assert is_closing is True
