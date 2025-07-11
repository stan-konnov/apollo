from unittest import mock
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from apollo.errors.system_invariants import (
    DispatchedPositionAlreadyExistsError,
    NeitherOpenNorOptimizedPositionExistsError,
)
from apollo.models.position import Position, PositionStatus
from apollo.models.signal_notification import SignalNotification
from apollo.models.strategy_parameters import StrategyParameters
from apollo.processors.generation.signal_generator import SignalGenerator
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    LONG_SIGNAL,
    MAX_PERIOD,
    START_DATE,
    STRATEGY,
    TICKER,
    Events,
)
from tests.fixtures.window_size_and_dataframe import WINDOW_SIZE, SameDataframe


def mock_get_position_by_status(
    position_status: PositionStatus,
) -> Position | None:
    """
    Conditional mock for get_position_by_status.

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


def test__generate_signals__for_raising_error_if_dispatched_position_exists() -> None:
    """Test generate_signals for raising error if dispatched position already exists."""

    signal_generator = SignalGenerator()

    signal_generator._configuration = Mock()  # noqa: SLF001
    signal_generator._database_connector = Mock()  # noqa: SLF001
    signal_generator._price_data_provider = Mock()  # noqa: SLF001
    signal_generator._price_data_enhancer = Mock()  # noqa: SLF001

    signal_generator._database_connector.get_position_by_status.return_value = Position(  # noqa: SLF001
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
        signal_generator.generate_signals()

    assert str(exception.value) == exception_message


def test__generate_signals__for_raising_error_if_open_and_optimized_positions_do_not_exist() -> (  # noqa: E501
    None
):
    """Test generate_signals for raising error if open and optimized positions do not exist."""  # noqa: E501

    signal_generator = SignalGenerator()

    signal_generator._configuration = Mock()  # noqa: SLF001
    signal_generator._database_connector = Mock()  # noqa: SLF001
    signal_generator._price_data_provider = Mock()  # noqa: SLF001
    signal_generator._price_data_enhancer = Mock()  # noqa: SLF001

    signal_generator._database_connector.get_position_by_status.return_value = None  # noqa: SLF001

    exception_message = (
        "Neither open nor optimized position exists. "
        "System invariant violated, position was not opened or optimized."
    )

    with pytest.raises(
        NeitherOpenNorOptimizedPositionExistsError,
        match=exception_message,
    ) as exception:
        signal_generator.generate_signals()

    assert str(exception.value) == exception_message


def test__generate_signals__for_calling_signal_generation_method() -> None:
    """Test generate_signals for calling signal generation method."""

    signal_generator = SignalGenerator()

    signal_generator._configuration = Mock()  # noqa: SLF001
    signal_generator._database_connector = Mock()  # noqa: SLF001
    signal_generator._price_data_provider = Mock()  # noqa: SLF001
    signal_generator._price_data_enhancer = Mock()  # noqa: SLF001

    signal_generator._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    signal_generator._generate_signal = Mock()  # noqa: SLF001
    signal_generator._generate_signal.return_value = (  # noqa: SLF001
        LONG_SIGNAL,
        100.0,
        101.0,
        99.0,
    )

    signal_generator.generate_signals()

    signal_generator._generate_signal.assert_has_calls(  # noqa: SLF001
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


def test__generate_signals__for_updating_optimized_position_to_dispatched() -> None:
    """Test generate_signals for updating optimized position to dispatched."""

    signal_generator = SignalGenerator()

    signal_generator._configuration = Mock()  # noqa: SLF001
    signal_generator._database_connector = Mock()  # noqa: SLF001
    signal_generator._price_data_provider = Mock()  # noqa: SLF001
    signal_generator._price_data_enhancer = Mock()  # noqa: SLF001

    # Ensure open and optimized position exist
    signal_generator._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    signal_generator._generate_signal = Mock()  # noqa: SLF001

    stop_loss = 99.9
    take_profit = 100.1
    target_entry_price = 100.0

    # Ensure we generate a signal for open and optimized position
    signal_generator._generate_signal.return_value = (  # noqa: SLF001
        LONG_SIGNAL,
        stop_loss,
        take_profit,
        target_entry_price,
    )

    signal_generator.generate_signals()

    # Ensure optimized position is updated to dispatched
    signal_generator._database_connector.update_position_by_status.assert_called_once_with(  # noqa: SLF001
        position_id="test",
        position_status=PositionStatus.DISPATCHED,
    )

    # Ensure open and dispatched positions are updated with correct values
    signal_generator._database_connector.update_position_on_signal_generation.assert_has_calls(  # noqa: SLF001
        [
            mock.call(
                position_id="test",
                direction=LONG_SIGNAL,
                stop_loss=stop_loss,
                take_profit=take_profit,
                target_entry_price=target_entry_price,
            ),
            mock.call(
                position_id="test",
                direction=LONG_SIGNAL,
                stop_loss=stop_loss,
                take_profit=take_profit,
                target_entry_price=target_entry_price,
            ),
        ],
    )


@pytest.mark.usefixtures("dataframe", "enhanced_dataframe")
def test__generate_signals__for_correct_signal_generation(
    dataframe: pd.DataFrame,
    enhanced_dataframe: pd.DataFrame,
) -> None:
    """Test generate_signals for correct signal of optimized position."""

    with patch(
        "apollo.processors.generation.signal_generator.OrderBracketsCalculator",
        Mock(),
    ) as mocked_order_brackets_calculator:
        signal_generator = SignalGenerator()

        signal_generator._configuration = Mock()  # noqa: SLF001
        signal_generator._database_connector = Mock()  # noqa: SLF001
        signal_generator._price_data_provider = Mock()  # noqa: SLF001
        signal_generator._price_data_enhancer = Mock()  # noqa: SLF001

        signal_generator._price_data_provider.get_price_data.return_value = dataframe  # noqa: SLF001
        signal_generator._price_data_enhancer.enhance_price_data.return_value = (  # noqa: SLF001
            enhanced_dataframe
        )

        optimized_position = Position(
            id="test",
            ticker=str(TICKER),
            status=PositionStatus.OPTIMIZED,
        )

        signal_generator._configuration.get_parameter_set.return_value = {  # noqa: SLF001
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

        signal_generator._database_connector.get_optimized_parameters.return_value = [  # noqa: SLF001
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
        generated_signal = signal_generator._generate_signal(  # noqa: SLF001
            optimized_position,
        )

        # Ensure price data is requested
        signal_generator._price_data_provider.get_price_data.assert_called_once_with(  # noqa: SLF001
            optimized_position.ticker,
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        # Ensure optimized parameters are retrieved
        signal_generator._database_connector.get_optimized_parameters.assert_called_once_with(  # noqa: SLF001
            optimized_position.ticker,
        )

        # Ensure price data is enhanced
        signal_generator._price_data_enhancer.enhance_price_data.assert_called_once_with(  # noqa: SLF001
            # Please see tests/fixtures/window_size_and_dataframe.py
            # for explanation on SameDataframe class
            SameDataframe(dataframe),
            ["VIX"],
        )

        # Ensure configuration is retrieved
        signal_generator._configuration.get_parameter_set.assert_called_once_with(  # noqa: SLF001
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
        assert generated_signal == (
            LONG_SIGNAL,
            long_sl,
            long_tp,
            long_limit,
        )


@pytest.mark.parametrize(
    "event_emitter",
    ["apollo.processors.generation.signal_generator.event_emitter"],
    indirect=True,
)
def test__generate_signals__for_calling_event_emitter_to_notify_execution_module(
    event_emitter: Mock,
) -> None:
    """Test generate_signals for calling event emitter to notify execution module."""

    signal_generator = SignalGenerator()

    signal_generator._configuration = Mock()  # noqa: SLF001
    signal_generator._database_connector = Mock()  # noqa: SLF001
    signal_generator._price_data_provider = Mock()  # noqa: SLF001
    signal_generator._price_data_enhancer = Mock()  # noqa: SLF001

    # Ensure open and optimized position exist
    signal_generator._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    signal_generator._generate_signal = Mock()  # noqa: SLF001
    signal_generator._generate_signal.return_value = (  # noqa: SLF001
        LONG_SIGNAL,
        100.0,
        101.0,
        99.0,
    )

    signal_generator.generate_signals()

    # Ensure event emitter is called to notify execution module
    event_emitter.emit.assert_called_once_with(
        Events.SIGNAL_GENERATED.value,
        SignalNotification(
            open_position=True,
            dispatched_position=True,
        ),
    )
