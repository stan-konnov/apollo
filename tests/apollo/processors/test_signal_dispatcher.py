from unittest import mock
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from apollo.errors.system_invariants import (
    DispatchedPositionAlreadyExistsError,
    NeitherOpenNorOptimizedPositionExistsError,
)
from apollo.models.dispatchable_signal import PositionSignal
from apollo.models.position import Position, PositionStatus
from apollo.models.strategy_parameters import StrategyParameters
from apollo.processors.signal_dispatcher import SignalDispatcher
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    LONG_SIGNAL,
    MAX_PERIOD,
    START_DATE,
    STRATEGY,
    TICKER,
)
from tests.fixtures.window_size_and_dataframe import WINDOW_SIZE, SameDataframe


def mock_get_existing_position_by_status(
    position_status: PositionStatus,
) -> Position | None:
    """
    Conditional mock for get_existing_position_by_status.

    :param position_status: Position status to mock.
    :returns: Position if status is OPEN or OPTIMIZED, None otherwise.
    """

    if position_status in [PositionStatus.OPEN, PositionStatus.OPTIMIZED]:
        return Position(
            id="test",
            ticker=str(TICKER),
            status=position_status,
        )

    return None


def test__dispatch_signals__for_raising_error_if_dispatched_position_exists() -> None:
    """Test dispatch_signals for raising error if dispatched position already exists."""

    signal_dispatcher = SignalDispatcher()

    signal_dispatcher._configuration = Mock()  # noqa: SLF001
    signal_dispatcher._database_connector = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

    signal_dispatcher._database_connector.get_existing_position_by_status.return_value = Position(  # noqa: SLF001, E501
        id="test",
        ticker=str(TICKER),
        status=PositionStatus.DISPATCHED,
    )

    exception_message = (
        "Dispatched position for "
        f"{TICKER} already exists. "
        "System invariant violated, position was not opened or cancelled."
    )

    with pytest.raises(
        DispatchedPositionAlreadyExistsError,
        match=exception_message,
    ) as exception:
        signal_dispatcher.dispatch_signals()

    assert str(exception.value) == exception_message


def test__dispatch_signals__for_raising_error_if_open_and_optimized_positions_do_not_exist() -> (  # noqa: E501
    None
):
    """Test dispatch_signals for raising error if open and optimized positions do not exist."""  # noqa: E501

    signal_dispatcher = SignalDispatcher()

    signal_dispatcher._configuration = Mock()  # noqa: SLF001
    signal_dispatcher._database_connector = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

    signal_dispatcher._database_connector.get_existing_position_by_status.return_value = None  # noqa: E501, SLF001

    exception_message = (
        "Neither open nor optimized position exists. "
        "System invariant violated, position was not opened or optimized."
    )

    with pytest.raises(
        NeitherOpenNorOptimizedPositionExistsError,
        match=exception_message,
    ) as exception:
        signal_dispatcher.dispatch_signals()

    assert str(exception.value) == exception_message


@pytest.mark.parametrize(
    "requests_post_call",
    ["apollo.processors.signal_dispatcher.post"],
    indirect=True,
)
@pytest.mark.usefixtures("requests_post_call")
def test__dispatch_signals__for_calling_signal_generation_method() -> None:
    """Test dispatch_signals for calling signal generation method."""

    signal_dispatcher = SignalDispatcher()

    signal_dispatcher._configuration = Mock()  # noqa: SLF001
    signal_dispatcher._database_connector = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

    signal_dispatcher._database_connector.get_existing_position_by_status.side_effect = mock_get_existing_position_by_status  # noqa: E501, SLF001

    signal_dispatcher._generate_signal_and_brackets = Mock()  # noqa: SLF001

    signal_dispatcher.dispatch_signals()

    signal_dispatcher._generate_signal_and_brackets.assert_has_calls(  # noqa: SLF001
        [
            mock.call(
                Position(
                    id="test",
                    ticker=str(TICKER),
                    status=PositionStatus.OPEN,
                ),
            ),
            mock.call(
                Position(
                    id="test",
                    ticker=str(TICKER),
                    status=PositionStatus.OPTIMIZED,
                ),
            ),
        ],
    )


@pytest.mark.parametrize(
    "requests_post_call",
    ["apollo.processors.signal_dispatcher.post"],
    indirect=True,
)
@pytest.mark.usefixtures("requests_post_call")
def test__dispatch_signals__for_updating_optimized_position_to_dispatched() -> None:
    """Test dispatch_signals for updating optimized position to dispatched."""

    signal_dispatcher = SignalDispatcher()

    signal_dispatcher._configuration = Mock()  # noqa: SLF001
    signal_dispatcher._database_connector = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

    # Ensure optimized position exists
    signal_dispatcher._database_connector.get_existing_position_by_status.side_effect = mock_get_existing_position_by_status  # noqa: E501, SLF001

    signal_dispatcher._generate_signal_and_brackets = Mock()  # noqa: SLF001

    stop_loss = 99.9
    take_profit = 100.1
    target_entry_price = 100.0

    # Ensure we generate a signal for optimized position
    signal_dispatcher._generate_signal_and_brackets.return_value = PositionSignal(  # noqa: SLF001
        position_id="test",
        ticker=str(TICKER),
        direction=LONG_SIGNAL,
        strategy=str(STRATEGY),
        stop_loss=stop_loss,
        take_profit=take_profit,
        target_entry_price=target_entry_price,
    )

    signal_dispatcher.dispatch_signals()

    # Ensure optimized position is updated to dispatched
    signal_dispatcher._database_connector.update_existing_position_by_status.assert_called_once_with(  # noqa: SLF001
        position_id="test",
        position_status=PositionStatus.DISPATCHED,
    )

    # Ensure optimized position is updated with correct values
    signal_dispatcher._database_connector.update_position_upon_dispatching.assert_called_once_with(  # noqa: SLF001
        position_id="test",
        strategy=str(STRATEGY),
        direction=LONG_SIGNAL,
        stop_loss=stop_loss,
        take_profit=take_profit,
        target_entry_price=target_entry_price,
    )


@pytest.mark.usefixtures("dataframe", "enhanced_dataframe")
def test__generate_signal_and_brackets__for_correct_signal_generation(
    dataframe: pd.DataFrame,
    enhanced_dataframe: pd.DataFrame,
) -> None:
    """Test generate_signal_and_brackets for correct signal of optimized position."""

    with patch(
        "apollo.processors.signal_dispatcher.OrderBracketsCalculator",
        Mock(),
    ) as mocked_order_brackets_calculator:
        signal_dispatcher = SignalDispatcher()

        signal_dispatcher._configuration = Mock()  # noqa: SLF001
        signal_dispatcher._database_connector = Mock()  # noqa: SLF001
        signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
        signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

        signal_dispatcher._price_data_provider.get_price_data.return_value = dataframe  # noqa: SLF001
        signal_dispatcher._price_data_enhancer.enhance_price_data.return_value = (  # noqa: SLF001
            enhanced_dataframe
        )

        optimized_position = Position(
            id="test",
            ticker=str(TICKER),
            status=PositionStatus.OPTIMIZED,
        )

        signal_dispatcher._configuration.get_parameter_set.return_value = {  # noqa: SLF001
            "window_size": {
                "step": 5,
                "range": [5, 20],
            },
            "sl_volatility_multiplier": {
                "step": 0.1,
                "range": [0.1, 1.0],
            },
            "tp_volatility_multiplier": {
                "step": 0.1,
                "range": [0.1, 1.0],
            },
            "kurtosis_threshold": {
                "step": 0.5,
                "range": [0.0, 3.0],
            },
            "volatility_multiplier": {
                "step": 0.5,
                "range": [0.5, 1.0],
            },
            "additional_data_enhancers": [
                "VIX",
            ],
            "strategy_specific_parameters": [
                "kurtosis_threshold",
                "volatility_multiplier",
            ],
        }

        sl_volatility_multiplier = 0.1
        tp_volatility_multiplier = 0.3

        signal_dispatcher._database_connector.get_optimized_parameters.return_value = [  # noqa: SLF001
            StrategyParameters(
                strategy=str(STRATEGY),
                parameters={
                    "window_size": WINDOW_SIZE,
                    "kurtosis_threshold": 0.0,
                    "volatility_multiplier": 0.5,
                    "sl_volatility_multiplier": sl_volatility_multiplier,
                    "tp_volatility_multiplier": tp_volatility_multiplier,
                },
            ),
        ]

        long_sl = 99
        long_tp = 101
        short_sl = 101
        short_tp = 99

        long_limit = 100
        short_limit = 100

        mocked_order_brackets_calculator.calculate_trailing_stop_loss_and_take_profit.return_value = (  # noqa: E501
            long_sl,
            long_tp,
            short_sl,
            short_tp,
        )

        mocked_order_brackets_calculator.calculate_limit_entry_price.return_value = (
            long_limit,
            short_limit,
        )

        # To not over-complicate things
        # we know that selected strategy
        # will generate long signal for last entry
        generated_signal = signal_dispatcher._generate_signal_and_brackets(  # noqa: SLF001
            optimized_position,
        )

        # Ensure price data is requested
        signal_dispatcher._price_data_provider.get_price_data.assert_called_once_with(  # noqa: SLF001
            optimized_position.ticker,
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        # Ensure optimized parameters are retrieved
        signal_dispatcher._database_connector.get_optimized_parameters.assert_called_once_with(  # noqa: SLF001
            optimized_position.ticker,
        )

        # Ensure price data is enhanced
        signal_dispatcher._price_data_enhancer.enhance_price_data.assert_called_once_with(  # noqa: SLF001
            # Please see tests/fixtures/window_size_and_dataframe.py
            # for explanation on SameDataframe class
            SameDataframe(dataframe),
            ["VIX"],
        )

        # Ensure configuration is retrieved
        signal_dispatcher._configuration.get_parameter_set.assert_called_once_with(  # noqa: SLF001
            str(STRATEGY),
        )

        # Ensure stop loss and take profit are calculated
        mocked_order_brackets_calculator.calculate_trailing_stop_loss_and_take_profit.assert_called_once_with(
            close_price=enhanced_dataframe.iloc[-1]["close"],
            average_true_range=enhanced_dataframe.iloc[-1]["atr"],
            sl_volatility_multiplier=sl_volatility_multiplier,
            tp_volatility_multiplier=tp_volatility_multiplier,
        )

        # Ensure limit entry price is calculated
        mocked_order_brackets_calculator.calculate_limit_entry_price.assert_called_once_with(
            close_price=enhanced_dataframe.iloc[-1]["close"],
            average_true_range=enhanced_dataframe.iloc[-1]["atr"],
            tp_volatility_multiplier=tp_volatility_multiplier,
        )

        # Assert generated signal
        assert generated_signal == PositionSignal(
            position_id="test",
            ticker=str(TICKER),
            direction=LONG_SIGNAL,
            strategy=str(STRATEGY),
            stop_loss=long_sl,
            take_profit=long_tp,
            target_entry_price=long_limit,
        )
