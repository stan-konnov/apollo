"""
Strategy Catalogue Map.

Dictionary that maps strategy names to related classes.

Used during parameter optimization and signal dispatching
to instantiate the correct strategy class based on the configured name.

Acts as a central registry for all available strategies.
"""

from apollo.strategies.avg_dir_mov_index_mean_reversion import (
    AverageDirectionalMovementIndexMeanReversion,
)
from apollo.strategies.combinatory_elliot_waves import CombinatoryElliotWaves
from apollo.strategies.combinatory_futures_patterns import (
    CombinatoryFuturesPatterns,
)
from apollo.strategies.engulfing_vix_mean_reversion import (
    EngulfingVIXMeanReversion,
)
from apollo.strategies.keltner_chaikin_mean_reversion import (
    KeltnerChaikinMeanReversion,
)
from apollo.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)
from apollo.strategies.swing_events_mean_reversion import SwingEventsMeanReversion
from apollo.strategies.vix_fut_con_div_trend_following import (
    VIXFuturesConvergenceDivergenceTrendFollowing,
)
from apollo.strategies.wilders_swing_index_trend_following import (
    WildersSwingIndexTrendFollowing,
)
from apollo.utils.types import StrategyCatalogueMap

STRATEGY_CATALOGUE_MAP: StrategyCatalogueMap = {
    "CombinatoryElliotWaves": CombinatoryElliotWaves,
    "SwingEventsMeanReversion": SwingEventsMeanReversion,
    "EngulfingVIXMeanReversion": EngulfingVIXMeanReversion,
    "CombinatoryFuturesPatterns": CombinatoryFuturesPatterns,
    "KeltnerChaikinMeanReversion": KeltnerChaikinMeanReversion,
    "WildersSwingIndexTrendFollowing": WildersSwingIndexTrendFollowing,
    "LinearRegressionChannelMeanReversion": LinearRegressionChannelMeanReversion,
    "SkewnessKurtosisVolatilityTrendFollowing": SkewnessKurtosisVolatilityTrendFollowing,  # noqa: E501
    "AverageDirectionalMovementIndexMeanReversion": AverageDirectionalMovementIndexMeanReversion,  # noqa: E501
    "VIXFuturesConvergenceDivergenceTrendFollowing": VIXFuturesConvergenceDivergenceTrendFollowing,  # noqa: E501
}
