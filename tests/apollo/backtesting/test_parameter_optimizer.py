from typing import cast

import pandas as pd

from apollo.backtesting.parameter_optimizer import ParameterOptimizer
from apollo.utils.types import ParameterSet

RANGE_MIN = 1.0
RANGE_MAX = 2.0
RANGE_STEP = 1.0


# @pytest.mark.usefixtures("dataframe")
# @patch("apollo.utils.configuration.PARM_DIR", PARM_DIR)
# @patch("apollo.utils.configuration.STRATEGY", STRATEGY)
def test__parameter_optimizer__for_correct_combination_ranges() -> None:
    """
    Test Parameter Optimizer for correct combination ranges.

    _get_combination_ranges() must return Series with correct combination ranges.
    """

    parameter_optimizer = ParameterOptimizer()

    control_combination_ranges = pd.Series([RANGE_MIN, RANGE_MAX])

    combination_ranges = parameter_optimizer._get_combination_ranges(  # noqa: SLF001
        RANGE_MIN,
        RANGE_MAX,
        RANGE_STEP,
    )

    pd.testing.assert_series_equal(control_combination_ranges, combination_ranges)


def test__parameter_optimizer__for_correct_parameter_combinations() -> None:
    """
    Test Parameter Optimizer for correct combination ranges.

    _get_combination_ranges must return tuple of parameter keys and product of ranges.
    """

    parameter_optimizer = ParameterOptimizer()

    parameters = {
        "stop_loss_level": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "take_profit_level": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
    }

    control_combinations = [
        (RANGE_MIN, RANGE_MIN),
        (RANGE_MIN, RANGE_MAX),
        (RANGE_MAX, RANGE_MIN),
        (RANGE_MAX, RANGE_MAX),
    ]

    keys, combinations = parameter_optimizer._construct_parameter_combinations(  # noqa: SLF001
        cast(ParameterSet, parameters),
    )

    assert keys == parameters.keys()
    assert control_combinations == list(combinations)
