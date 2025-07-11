import pandas as pd

from apollo.calculators.base_calculator import BaseCalculator


class AverageDirectionalMovementIndexCalculator(BaseCalculator):
    """
    Average Directional Movement Index Calculator.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Wilder, "Selection and Direction", Technical Analysis in Commodities, 1980.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct ADX Calculator.

        :param dataframe: Dataframe to calculate ADX for.
        :param window_size: Window size for rolling ADX calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_average_directional_movement_index(self) -> None:
        """Calculate rolling ADX via DX and EMA."""

        # Precalculate previous low
        self._dataframe["prev_low"] = self._dataframe["adj low"].shift(1)

        # Precalculate previous high
        self._dataframe["prev_high"] = self._dataframe["adj high"].shift(1)

        # Precalculate Minus Directional Movement (MDM)
        self._dataframe["mdm"] = (
            self._dataframe["adj low"] - self._dataframe["prev_low"]
        )

        # Precalculate Plus Directional Movement (PDM)
        self._dataframe["pdm"] = (
            self._dataframe["adj high"] - self._dataframe["prev_high"]
        )

        # Now, smooth PDM and MDM
        # with Wilder's Exponential Moving Average
        self._dataframe["pdm"] = (
            self._dataframe["pdm"]
            .ewm(
                alpha=1 / self._window_size,
                min_periods=self._window_size,
                adjust=False,
            )
            .mean()
        )

        self._dataframe["mdm"] = (
            self._dataframe["mdm"]
            .ewm(
                alpha=1 / self._window_size,
                min_periods=self._window_size,
                adjust=False,
            )
            .mean()
        )

        # NOTE: since all our strategies are volatility-based,
        # this calculator implicitly has access to ATR
        # which is the smoothed True Range series

        # Given that we have PDM, MDM, and ATR,
        # we can calculate Directional Movement Indicators (DMI)
        self._dataframe["pdi"] = self._dataframe["pdm"] / self._dataframe["atr"]
        self._dataframe["mdi"] = self._dataframe["mdm"] / self._dataframe["atr"]

        # Given PDI and MDI, we can
        # calculate True Directional Movement (DX)
        # expressed as normalized difference between
        # PDI and MDI subtraction and PDI and MDI addition
        # NOTE: we normalize the result by multiplying by 100
        self._dataframe["dx"] = 100 * (
            abs(self._dataframe["pdi"] - self._dataframe["mdi"])
            / (self._dataframe["pdi"] + self._dataframe["mdi"])
        )

        # Finally, we reach ADX by smoothing DX
        # with Wilder's Exponential Moving Average
        self._dataframe["adx"] = (
            self._dataframe["dx"]
            .ewm(
                alpha=1 / self._window_size,
                min_periods=self._window_size,
                adjust=False,
            )
            .mean()
        )

        # Calculate the amplitude between DX and ADXR
        self._dataframe["dx_adx_ampl"] = abs(self._dataframe["dx"]) - abs(
            self._dataframe["adx"],
        )

        # Shift PDI and MDI by one observation each
        self._dataframe["prev_pdi"] = self._dataframe["pdi"].shift(1)
        self._dataframe["prev_mdi"] = self._dataframe["mdi"].shift(1)

        # Shift DX by one observation
        self._dataframe["prev_dx"] = self._dataframe["dx"].shift(1)

        # Shift the amplitude by one observation
        self._dataframe["prev_dx_adx_ampl"] = self._dataframe["dx_adx_ampl"].shift(1)

        # Drop unnecessary columns
        self._dataframe.drop(
            columns=["prev_low", "prev_high", "mdm", "pdm", "adx"],
            inplace=True,
        )
