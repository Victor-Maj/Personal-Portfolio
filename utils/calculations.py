import math
import numpy as np
from scipy.stats import norm

def black_scholes_call_price(S, K, T, sigma, r):
    try:
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    except:
        return None

def monte_carlo_stock_price(S, r, sigma, T, num_simulations):
    T_days = int(T * 252)
    dt = 1 / T_days
    
    Z = np.random.normal(0, 1, (num_simulations, T_days))
    daily_returns = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    cumulative_returns = np.cumsum(daily_returns, axis=1)
    future_prices = S * np.exp(cumulative_returns)
    
    return future_prices

def simulated_call_option_price(ST, K, r, T):
    final_prices = ST[:, -1]
    payoffs = np.maximum(0, final_prices - K)
    return np.exp(-r * T) * np.mean(payoffs)