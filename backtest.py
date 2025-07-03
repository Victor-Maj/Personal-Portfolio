import numpy as np
import pandas as pd

class Backtest:
    def __init__(self, prices: pd.Series):
        self.prices = prices
        self.returns = self.prices.pct_change().dropna()


    """Risk Metrics """

    def calculate_max_drawdown(self):
        cumulative_returns = (1 + self.returns).cumprod()
        cumulative_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - cumulative_max) / cumulative_max
        return drawdown.min() * 100 
    
    #def calculate_sharp_ratio(self):
    #    sharp_ratio = (self.returns - 0.0436)/ self.returns.std()
    #    return sharp_ratio

    def calculate_volatility(self, periods_per_year=252):
        return self.returns.std() * np.sqrt(periods_per_year)
    
    def calculate_value_at_risk(self, confidence_level = 0.95, horizon = 1):
        VaR_historical = -np.percentile(self.returns, (1 - confidence_level) * 100)
        scaled_var = VaR_historical * np.sqrt(horizon)
        return scaled_var
    
    def calculate_beta(self, market_returns):
        covariance = np.cov(self.returns, market_returns)[0, 1]
        beta = covariance / market_returns.var()
        return beta



    