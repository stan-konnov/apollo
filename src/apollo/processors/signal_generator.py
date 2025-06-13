from logging import getLogger

import pandas as pd

from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.core.order_brackets_calculator import OrderBracketsCalculator
from apollo.core.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.errors.system_invariants import (
    DispatchedPositionAlreadyExistsError,
    NeitherOpenNorOptimizedPositionExistsError,
)
from apollo.events.emitter import emitter
from apollo.models.position import Position, PositionStatus
from apollo.models.signal_notification import SignalNotification
from apollo.providers.price_data_enhancer import PriceDataEnhancer
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    LONG_SIGNAL,
    MAX_PERIOD,
    NO_SIGNAL,
    SHORT_SIGNAL,
    START_DATE,
    Events,
)
from apollo.utils.configuration import Configuration

logger = getLogger(__name__)


class SignalGenerator:
    """
    Signal Generator class.

    Produces signals for open and optimized positions.

    Dispatches intra-system events to notify
    the execution module about generated signals.
    """

    def __init__(self) -> None:
        """
        Construct Signal Generator.

        Initialize Configuration.
        Initialize Database Connector.
        Initialize Price Data Provider.
        Initialize Price Data Enhancer.
        """

        self._configuration = Configuration()
        self._database_connector = PostgresConnector()
        self._price_data_provider = PriceDataProvider()
        self._price_data_enhancer = PriceDataEnhancer()

    def generate_signals(self) -> None:
        """
        Generate signals, update positions, and notify execution module.

        Handle system invariants related to dispatching step.
        """

        # Query existing dispatched position
        existing_dispatched_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.DISPATCHED,
            )
        )

        # Raise an error if the
        # dispatched position already exists
        if existing_dispatched_position:
            raise DispatchedPositionAlreadyExistsError(
                "Dispatched position for "
                f"{existing_dispatched_position.ticker} already exists. "
                "System invariant violated, position was not opened or cancelled.",
            )

        # Query existing open position
        existing_open_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.OPEN,
            )
        )

        # Query existing optimized position
        existing_optimized_position = (
            self._database_connector.get_existing_position_by_status(
                PositionStatus.OPTIMIZED,
            )
        )

        # Raise an error if neither
        # open nor optimized position exists
        if not existing_open_position and not existing_optimized_position:
            raise NeitherOpenNorOptimizedPositionExistsError(
                "Neither open nor optimized position exists. "
                "System invariant violated, position was not opened or optimized.",
            )

        logger.info("Generation process started.")

        signal_notification = SignalNotification()

        # At this point, manage
        # open or optimized position
        if existing_open_position:
            # Generate signal
            open_position_signal = self._generate_signal(
                existing_open_position,
            )

            # Flip the flag if we got one
            if open_position_signal:
                signal_notification.open_position = True

                # Unpack the signal values
                direction, stop_loss, take_profit, target_entry_price = (
                    open_position_signal
                )

                # Update the position with signal details
                self._database_connector.update_position_on_signal_generation(
                    position_id=existing_open_position.id,
                    direction=direction,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    target_entry_price=target_entry_price,
                )

        if existing_optimized_position:
            # Generate signal
            dispatched_position_signal = self._generate_signal(
                existing_optimized_position,
            )

            # Flip the flag if we got one
            if dispatched_position_signal:
                signal_notification.dispatched_position = True

                # Unpack the signal values
                direction, stop_loss, take_profit, target_entry_price = (
                    dispatched_position_signal
                )

                # Update the positions to dispatched status
                self._database_connector.update_existing_position_by_status(
                    position_id=existing_optimized_position.id,
                    position_status=PositionStatus.DISPATCHED,
                )

                # Update the position with signal details
                self._database_connector.update_position_on_signal_generation(
                    position_id=existing_optimized_position.id,
                    direction=direction,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    target_entry_price=target_entry_price,
                )

        logger.info("Generation process complete.")

        # Finally, dispatch the signal for execution
        if signal_notification.open_position or signal_notification.dispatched_position:
            logger.info("Dispatching signals for execution.")
            emitter.emit(Events.SIGNAL_GENERATED.value, signal_notification)

    def _generate_signal(
        self,
        position: Position,
    ) -> tuple[int, float, float, float] | None:
        """
        Generate direction, limit entry price, stop loss, and take profit.

        :param position: Position object.
        :returns: Tuple containing signal values or None.
        """

        # Initialize signal values
        #
        # NOTE: use the existing direction
        # for open position, or default to
        # NO_SIGNAL for optimized position
        direction: int = (
            position.direction
            if position.direction and position.status == PositionStatus.OPEN.value
            else NO_SIGNAL
        )

        stop_loss: float = 0.0
        take_profit: float = 0.0
        target_entry_price: float = 0.0

        # Get price data for the position ticker
        price_dataframe = self._price_data_provider.get_price_data(
            position.ticker,
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        # Since optimization process
        # is based on last 30 years of data,
        # here we also filter the queried dataset
        price_dataframe = price_dataframe[
            price_dataframe.index >= pd.Timestamp.now() - pd.DateOffset(years=30)
        ]

        # Query sharpe-sorted optimized
        # parameters for the position ticker
        optimized_parameters = self._database_connector.get_optimized_parameters(
            position.ticker,
        )

        # Given that we have parameters,
        # we now run the signal modeling
        # over each strategy until we hit a signal
        for optimized_parameter_set in optimized_parameters:
            # Get strategy name
            strategy_name = optimized_parameter_set.strategy

            # Get optimized parameters
            optimized_parameters = optimized_parameter_set.parameters

            # Copy price dataframe to avoid
            # altering the data with each iteration
            clean_price_dataframe = price_dataframe.copy()

            # Get file-defined parameter set
            # that contains additional specifications
            parameter_set = self._configuration.get_parameter_set(
                strategy_name,
            )

            # Enhance the price data based on the configuration
            clean_price_dataframe = self._price_data_enhancer.enhance_price_data(
                clean_price_dataframe,
                parameter_set["additional_data_enhancers"],
            )

            # Extract the strategy-specific parameters
            strategy_specific_parameters = {
                key: optimized_parameter_set.parameters[key]
                for key in parameter_set["strategy_specific_parameters"]
            }

            # Instantiate the strategy class by typecasting
            # the strategy name from optimized set to the correct class
            strategy_class = type(
                strategy_name,
                (STRATEGY_CATALOGUE_MAP[strategy_name],),
                {},
            )

            # Instantiate the strategy
            # with the optimized parameters
            strategy_instance = strategy_class(
                dataframe=clean_price_dataframe,
                window_size=int(optimized_parameters["window_size"]),
                **strategy_specific_parameters,
            )

            # Model the trading signals
            strategy_instance.model_trading_signals()

            # If we got the signal, set the direction
            if clean_price_dataframe.iloc[-1]["signal"] != NO_SIGNAL:
                direction = clean_price_dataframe.iloc[-1]["signal"]

            # Get close price
            close_price = clean_price_dataframe.iloc[-1]["close"]

            # Get average true range
            average_true_range = clean_price_dataframe.iloc[-1]["atr"]

            # Calculate trailing stop loss and take profit
            long_sl, long_tp, short_sl, short_tp = (
                OrderBracketsCalculator.calculate_trailing_stop_loss_and_take_profit(
                    close_price=close_price,
                    average_true_range=average_true_range,
                    sl_volatility_multiplier=optimized_parameters[
                        "sl_volatility_multiplier"
                    ],
                    tp_volatility_multiplier=optimized_parameters[
                        "tp_volatility_multiplier"
                    ],
                )
            )

            # Calculate limit entry price for long and short signals
            long_limit, short_limit = (
                OrderBracketsCalculator.calculate_limit_entry_price(
                    close_price=close_price,
                    average_true_range=average_true_range,
                    tp_volatility_multiplier=optimized_parameters[
                        "tp_volatility_multiplier"
                    ],
                )
            )

            # Set brackets based on the direction
            if direction == LONG_SIGNAL:
                stop_loss = long_sl
                take_profit = long_tp
                target_entry_price = long_limit

            elif direction == SHORT_SIGNAL:
                stop_loss = short_sl
                take_profit = short_tp
                target_entry_price = short_limit

            # Break the loop if it is open position
            # or if we got the signal for optimized
            if position.status == PositionStatus.OPEN or (
                position.status == PositionStatus.OPTIMIZED and direction != NO_SIGNAL
            ):
                break

        # Return identified signal or None
        return (
            (direction, stop_loss, take_profit, target_entry_price)
            if direction != NO_SIGNAL
            else None
        )
