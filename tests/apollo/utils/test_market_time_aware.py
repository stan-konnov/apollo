from freezegun import freeze_time

from apollo.utils.market_time_aware import MarketTimeAware


# Assume today date is Friday, 2025-06-20
# Assume current time is within trading hours
@freeze_time("2024-07-12 16:00:00")
def test__get_market_time_metrics__for_correctly_calculating_metrics_on_trading_day_trading_hours() -> (  # noqa: E501
    None
):
    """Test _get_market_time_metrics method for correct metrics."""

    market_time_aware = MarketTimeAware()

    market_time_metrics = market_time_aware._get_market_time_metrics()  # noqa: SLF001

    assert market_time_metrics.is_business_day is True
    assert market_time_metrics.is_market_holiday is False
