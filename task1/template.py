import pandas as pd
import numpy as np
import yfinance as yf

def calculate_moving_averages(prices, short_window=20, long_window=50):
    short_ma = prices.rolling(window=short_window).mean()
    long_ma = prices.rolling(window=long_window).mean()
    return short_ma, long_ma

def backtest_strategy(prices, short_ma, long_ma):
    signals = pd.DataFrame(index=prices.index)
    signals['price'] = prices
    signals['short_ma'] = short_ma
    signals['long_ma'] = long_ma
    signals['signal'] = 0
    signals['signal'][short_ma > long_ma] = 1
    signals['signal'][short_ma <= long_ma] = 0
    signals['positions'] = signals['signal'].diff()
    return signals

def plot_signals(signals):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(14, 7))
    plt.plot(signals['price'], label='Price')
    plt.plot(signals['short_ma'], label='20-day MA')
    plt.plot(signals['long_ma'], label='50-day MA')
    plt.plot(signals[signals['positions'] == 1].index, signals['short_ma'][signals['positions'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')
    plt.plot(signals[signals['positions'] == -1].index, signals['short_ma'][signals['positions'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
    plt.legend()
    plt.show()

# Example usage
data = yf.download('AAPL', start='2020-01-01', end='2022-01-01')
prices = data['Close']
short_ma, long_ma = calculate_moving_averages(prices)
signals = backtest_strategy(prices, short_ma, long_ma)
plot_signals(signals)
