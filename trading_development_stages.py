"""
This file will mainly comprices of 4 stages do determine if a strategy is profitable.

Stage 1: In-sample Excellence
Stage 2: In-sample Permuation test
Stage 3: Walk Forward Test
Stage 4: Walk Forward Permuation Test

The In-sample Excellence Basiclly is just if i finde a strategi that makes money, then i try to optimze the strategi. 
Once i have a strategi i want to make sure i doesn't have data mining Bias. To check for this i will be using a In-sample Permutaion Test. 
This will insure that i am not just finding patterns in noise. 

The In-sample Permuation test will have the null hypothesis that the strategy is overfitting.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from backtest import Backtest


def donchian_breakout(ohlc: pd.DataFrame, lookback: int):
    upper = ohlc['close'].rolling(lookback - 1).max().shift(1)
    lower = ohlc['close'].rolling(lookback - 1).min().shift(1)
    signal = pd.Series(np.nan, index=ohlc.index)
    signal.loc[ohlc['close'] > upper] = 1
    signal.loc[ohlc['close'] < lower] = -1
    signal = signal.ffill()
    return signal

def optimize_donchian(ohlc: pd.DataFrame):
    best_pf = 0
    best_lookback = -1
    r = np.log(ohlc['close']).diff().shift(-1)
    for lookback in range(12, 169):
        signal = donchian_breakout(ohlc, lookback)
        bt = Backtest(ohlc, signal)
        pf = bt.calculate_profit_factor(use_signal=True)
        if pf  > best_pf:
            best_pf = pf 
            best_lookback = lookback
    return best_lookback, best_pf

if __name__ == '__main__':
    df = yf.download("BTC-USD", interval="1h", start="2024-07-01", end="2025-07-01")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0).str.lower()

df.dropna(inplace=True)

df.index = df.index.tz_localize(None)

df = df[(df.index.year >= 2024) & (df.index.year < 2025)]

best_lookback, best_real_pf = optimize_donchian(df)

signal = donchian_breakout(df, best_lookback)
bt = Backtest(df, signal)
report = bt.generate_report()
print(report)


df['r'] = np.log(df['close']).diff().shift(-1)
df['donch_r'] = df['r'] * signal

plt.style.use("dark_background")
df['donch_r'].cumsum().plot(color='red')
plt.title("In-Sample Donchian Breakout")
plt.ylabel('Cumulative Log Return')
plt.show()