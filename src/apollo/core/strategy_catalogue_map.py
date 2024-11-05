"""
Strategy Catalogue Map.

Dictionary that maps strategy names to related classes.

Used during parameter optimization to instantiate
the correct strategy class based on the configured name.

Acts as a central registry for all available strategies.
"""

from apollo.core.strategies.avg_dir_mov_index_mean_reversion import (
    AverageDirectionalMovementIndexMeanReversion,
)
from apollo.core.strategies.combinatory_elliot_waves import CombinatoryElliotWaves
from apollo.core.strategies.combinatory_futures_patterns import (
    CombinatoryFuturesPatterns,
)
from apollo.core.strategies.engulfing_vix_mean_reversion import (
    EngulfingVIXMeanReversion,
)
from apollo.core.strategies.keltner_chaikin_mean_reversion import (
    KeltnerChaikinMeanReversion,
)
from apollo.core.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)
from apollo.core.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)
from apollo.core.strategies.swing_events_mean_reversion import SwingEventsMeanReversion
from apollo.core.strategies.vix_fut_con_div_trend_following import (
    VIXFuturesConvergenceDivergenceTrendFollowing,
)
from apollo.core.strategies.wilders_swing_index_trend_following import (
    WildersSwingIndexTrendFollowing,
)
from apollo.core.utils.types import StrategyCatalogueMap

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
