* Use Adj Close for calculations
* Privatize field
* Unit tests for api connector, calculators, backtesting
* Break down base params and strategy params into separate files
* Multiprocess parameter optimization
* Include commissions into backtesting
* Backtest during GFC (and other prolonged periods) and optimize; build new strategies

Missing calculations that didn't prove themselves, but worth trying again:

* RSI
* Markov Chains
* Support Resistance
* Accumulative Swing Index

Nice to haves:

1. MyPy

Meta steps:

Equities --> ETF Options --> Crypto Options

https://stackoverflow.com/questions/50155464/using-pytest-with-a-src-layer

IBKR commission ratio = 0.05% from 100% = (0.0005 from 1.0)
NOTE: this is an example; we're not using IBKR
due to their client not running without human involvement