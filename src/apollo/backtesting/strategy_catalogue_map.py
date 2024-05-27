"""
Strategy Catalogue Map.

Dictionary that maps strategy names to related classes.

Is used during parameter optimization to instantiate
the correct strategy class based on the configured name.

Acts as a central registry for all available strategies.
"""

from apollo.strategies.arima_trend_mean_reversion import ARIMATrendMeanReversion
from apollo.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)
from apollo.strategies.logistic_regression_forecast import LogisticRegressionForecast
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)
from apollo.strategies.swing_events_mean_reversion import SwingEventsMeanReversion
from apollo.utils.types import StrategyCatalogueMap

STRATEGY_CATALOGUE_MAP: StrategyCatalogueMap = {
    "ARIMATrendMeanReversion": ARIMATrendMeanReversion,
    "SwingEventsMeanReversion": SwingEventsMeanReversion,
    "LogisticRegressionForecast": LogisticRegressionForecast,
    "LinearRegressionChannelMeanReversion": LinearRegressionChannelMeanReversion,
    "SkewnessKurtosisVolatilityTrendFollowing": SkewnessKurtosisVolatilityTrendFollowing,  # noqa: E501
}
