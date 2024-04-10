## Meta

</br>

```
FREQUENCY

One day (1d) as per Yahoo API. Test all possible variations.

Interval: ValidYahooApiFrequencies.
```


```
WINDOW_SIZE

5 trading days as desired swing (1 week). Test from 5 until 252 trading days (one year market cycle).

Interval: 1.0.
```

</br>

## Calculators

```
KURTOSIS_THRESHOLD

3.0 as statistical default. Test from 0.0 until 3.0.

Interval: 0.1.
```

```
CHANNEL_STANDARD_DEVIATION_SPREAD

3.0 as statistical outlier. Test from 1.0 until 3.0.

Interval: 0.1.
```

```
VOLATILITY_MULTIPLIER

2.0 as suggested by Kaufman, TSM, 2020, 6th ed. Test from 1.0 until 3.0.

Interval: 0.1.
```

```
SWING_FILTER

0.005 as default. Test from 0.005 until 0.1.

Interval: 0.001.
```