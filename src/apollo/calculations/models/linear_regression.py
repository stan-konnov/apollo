import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class LinearRegressionModelCalculator(BaseCalculator):
    """
    Linear Regression Model Calculator.

    Since there are multiple linear regression models one can
    apply to given time series, this class acts as a model selector
    based on several statistical tests that quantify the goodness of fit.

    We apply two most commonly used metrics: R-squared and Mean Squared Error.
    The model with the highest R-squared and lowest MSE is used for rolling forecast.

    Linear regression models that we consider are:

    * Ordinary Least Squares (OLS)
    * Lasso Regression
    * Ridge Regression
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Linear Regression Model Calculator.

        :param dataframe: Dataframe to calculate ATR for.
        :param window_size: Window size for rolling ATR calculation.
        """

        super().__init__(dataframe, window_size)
