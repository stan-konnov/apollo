from freezegun import freeze_time

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
