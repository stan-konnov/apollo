"""
First: for any regression analysis time series must be made stationary.

This, of course includes ARIMA, as well as linear regression models.

Therefor, the first step is to make the time
series stationary by removing trends and seasonality.

This has to happen via transformer and, perhaps, applied to all other calculations.

NOTE: consider SARIMA, which is a seasonal ARIMA model.
"""
