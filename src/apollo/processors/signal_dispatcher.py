from apollo.backtesters.backtesting_runner import BacktestingRunner
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.core.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.errors.system_invariants import (
    DispatchedPositionAlreadyExistsError,
    NeitherOpenNorOptimizedPositionExistsError,
)
from apollo.models.position import Position, PositionStatus
from apollo.providers.price_data_enhancer import PriceDataEnhancer
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.settings import (
    BACKTESTING_CASH_SIZE,
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    START_DATE,
)
from apollo.utils.configuration import Configuration


class SignalDispatcher:
    """Signal Dispatcher class."""

    def __init__(self) -> None:
        """
        Construct Signal Dispatcher.

        Initialize Database Connector.
        Initialize Price Data Provider.
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

        # At this point, we should manage
        # either open or optimized position
        if existing_optimized_position:
            self._generate_signal_and_brackets(existing_optimized_position)

    def _generate_signal_and_brackets(
        self,
        position: Position,
    ) -> None:
        """
        Generate signal and limit entry price, stop loss, and take profit.

        :param position: Position object.
        """

        # Get price data for the position ticker
        price_dataframe = self._price_data_provider.get_price_data(
            position.ticker,
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        # Limit to last 30 years

        # Query optimized parameters
        # for the position ticker
        optimized_parameters = self._database_connector.get_optimized_parameters(
            position.ticker,
        )

        # Given that we have parameters,
        # we now run the backtesting process
        # over each strategy until we hit a signal
        for optimized_parameter_set in optimized_parameters:
            # Copy price dataframe to avoid
            # altering the data with each iteration
            clean_price_dataframe = price_dataframe.copy()

            # Get file-defined parameter set
            # that contains additional specifications
            parameter_set = self._configuration.get_parameter_set(
                optimized_parameter_set.strategy,
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
                optimized_parameter_set.strategy,
                (STRATEGY_CATALOGUE_MAP[optimized_parameter_set.strategy],),
                {},
            )

            # Instantiate the strategy
            # with the optimized parameters
            strategy_instance = strategy_class(
                dataframe=clean_price_dataframe,
                window_size=int(optimized_parameter_set.parameters["window_size"]),
                **strategy_specific_parameters,
            )

            # Model the trading signals
            strategy_instance.model_trading_signals()

            # Instantiate the backtesting runner and run the backtesting process
            backtesting_runner = BacktestingRunner(
                dataframe=clean_price_dataframe,
                strategy_name=optimized_parameter_set.strategy,
                lot_size_cash=BACKTESTING_CASH_SIZE,
                sl_volatility_multiplier=optimized_parameter_set.parameters[
                    "sl_volatility_multiplier"
                ],
                tp_volatility_multiplier=optimized_parameter_set.parameters[
                    "tp_volatility_multiplier"
                ],
            )

            stats = backtesting_runner.run()

            print(stats)  # noqa: T201
