"""
First: for any regression analysis time series must be made stationary.

This, of course includes ARIMA, as well as linear regression models.

Therefor, the first step is to make the time
series stationary by removing trends and seasonality.

This has to happen via data preprocessing
(e.g. differencing, or seasonal differencing) in parent class.
This concerns all regression model, not only ARIMA!

E.g., apply differencing to all aspect of OHLCV data.
And only then feed it into the model.

NOTE: consider SARIMA, which is a seasonal ARIMA model.
"""
