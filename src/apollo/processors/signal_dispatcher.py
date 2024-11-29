import pandas as pd

from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.core.order_brackets_calculator import OrderBracketsCalculator
from apollo.core.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.errors.system_invariants import (
    DispatchedPositionAlreadyExistsError,
    NeitherOpenNorOptimizedPositionExistsError,
)
from apollo.models.dispatchable_signal import DispatchableSignal, PositionSignal
from apollo.models.position import Position, PositionStatus
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
)
from apollo.utils.configuration import Configuration


class SignalDispatcher:
    """Signal Dispatcher class."""

    def __init__(self) -> None:
        """
        Construct Signal Dispatcher.

        Initialize Configuration.
        Initialize Database Connector.
        Initialize Price Data Provider.
        Initialize Price Data Enhancer.
        """

        self._configuration = Configuration()
        self._database_connector = PostgresConnector()
        self._price_data_provider = PriceDataProvider()
        self._price_data_enhancer = PriceDataEnhancer()

    def dispatch_signals(self) -> None:
        """
        Generate and dispatch signals.

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

        # Initialize dispatchable signal
        dispatchable_signal = DispatchableSignal()

        # At this point, we should manage
        # either open or optimized position
        if existing_open_position:
            dispatchable_signal.open_position = self._generate_signal_and_brackets(
                existing_open_position,
            )

        if existing_optimized_position:
            dispatchable_signal.optimized_position = self._generate_signal_and_brackets(
                existing_optimized_position,
            )

        # Now, if we have optimized position, and we
        # identified the signal, we mark it as dispatched
        # NOTE: whatever happens after, is up to execution module
        if existing_optimized_position and dispatchable_signal.optimized_position:
            self._database_connector.update_existing_position_by_status(
                position_id=existing_optimized_position.id,
                position_status=PositionStatus.DISPATCHED,
            )

            # We additionally update the
            # position with dispatching details
            self._database_connector.update_position_upon_dispatching(
                position_id=existing_optimized_position.id,
                strategy=dispatchable_signal.optimized_position.strategy,
                direction=dispatchable_signal.optimized_position.direction,
                stop_loss=dispatchable_signal.optimized_position.stop_loss,
                take_profit=dispatchable_signal.optimized_position.take_profit,
                target_entry_price=dispatchable_signal.optimized_position.target_entry_price,
            )

    def _generate_signal_and_brackets(
        self,
        position: Position,
    ) -> PositionSignal | None:
        """
        Generate signal, limit entry price, stop loss, and take profit.

        :param position: Position object.
        """

        # Initialize position signal
        position_signal = PositionSignal(
            position_id=position.id,
            ticker=position.ticker,
            direction=NO_SIGNAL,
            strategy="",
            stop_loss=0.0,
            take_profit=0.0,
            target_entry_price=0.0,
        )

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
            # the strategy name from configuration to the corresponding class
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

            # Set direction to no signal
            # or use the existing direction
            # in case we are handling open position
            direction = (
                NO_SIGNAL
                if position.status == PositionStatus.OPTIMIZED
                else position.direction
            )

            # If we got the signal, set
            # strategy and (re)set the direction
            if clean_price_dataframe.iloc[-1]["signal"] != NO_SIGNAL:
                position_signal.strategy = strategy_name
                position_signal.direction = clean_price_dataframe.iloc[-1]["signal"]

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
                position_signal.stop_loss = long_sl
                position_signal.take_profit = long_tp
                position_signal.target_entry_price = long_limit

            elif direction == SHORT_SIGNAL:
                position_signal.stop_loss = short_sl
                position_signal.take_profit = short_tp
                position_signal.target_entry_price = short_limit

            # Break the loop if it is open position
            # or if we got the signal for optimized
            if position.status == PositionStatus.OPEN or (
                position.status == PositionStatus.OPTIMIZED
                and position_signal.direction != NO_SIGNAL
            ):
                break

        # Return identified signal or None
        return position_signal if position_signal.direction != NO_SIGNAL else None
