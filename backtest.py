import numpy as np
import pandas as pd

class Backtest:
    def __init__(self, ohlc: pd.DataFrame, signal: pd.Series):
        self.prices                = ohlc['close']
        self.returns               = np.log(self.prices).diff().shift(-1)
        self.signal                = signal
        self.signal_returns        =  self.signal * self.returns


    """Risk Metrics """
    def calculate_max_drawdown(self, use_signal=False):
        returns = self.signal_returns if use_signal else self.returns
        cumulative_returns = (1 + returns.fillna(0)).cumprod()
        cumulative_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - cumulative_max) / cumulative_max
        return drawdown.min() * 100 

    def calculate_sharpe_ratio(self, risk_free_rate=0.0, periods_per_year=252, use_signal=False):
        returns = self.signal_returns if use_signal else self.returns
        excess_returns = returns - (risk_free_rate / periods_per_year)
        return np.mean(excess_returns) / np.std(returns) * np.sqrt(periods_per_year)

    def calculate_volatility(self, periods_per_year=252, use_signal=False):
        returns = self.signal_returns if use_signal else self.returns
        return returns.std() * np.sqrt(periods_per_year)

    def calculate_value_at_risk(self, confidence_level=0.95, horizon=1, use_signal=False):
        returns = self.signal_returns if use_signal else self.returns
        VaR_historical = -np.percentile(returns.dropna(), (1 - confidence_level) * 100)
        return VaR_historical * np.sqrt(horizon)
    
    #def calculate_beta(self, market_returns):
    #    covariance = np.cov(self.returns, market_returns)[0, 1]
    #    beta = covariance / market_returns.var()
    #    return beta
    

    """ Return Metrics """

    def calculate_cagr(self, periods_per_year=252, use_signal=False):
        returns = self.signal_returns if use_signal else self.returns
        cumulative_return = (1 + returns.dropna()).prod()
        n_periods = len(returns.dropna()) / periods_per_year
        return cumulative_return ** (1 / n_periods) - 1

    def calculate_total_return(self, use_signal=False):
        returns = self.signal_returns if use_signal else self.returns
        return (1 + returns.dropna()).prod() - 1

    def calculate_profit_factor(self, use_signal=False):
        returns = self.signal_returns if use_signal else self.returns
        positive_returns = returns[returns > 0].sum()
        negative_returns = returns[returns < 0].abs().sum()
        return positive_returns / negative_returns if negative_returns != 0 else np.inf
    


    """Performance Consistency"""
    
    #def calculate_win_rate(self):
    #    return None



    def generate_report(self, periods_per_year=252, risk_free_rate=0.0, confidence_level=0.95, horizon=1):
        report = {}

        # UNDERLYING
        report['Underlying'] = {
            'Total Return': f"{self.calculate_total_return(use_signal=False):.2%}",
            'CAGR': f"{self.calculate_cagr(periods_per_year=periods_per_year, use_signal=False):.2%}",
            'Volatility': f"{self.calculate_volatility(periods_per_year=periods_per_year, use_signal=False):.2%}",
            'Sharpe Ratio': f"{self.calculate_sharpe_ratio(risk_free_rate, periods_per_year, use_signal=False):.2f}",
            'Max Drawdown': f"{self.calculate_max_drawdown(use_signal=False):.2f}%",
            'Profit Factor': f"{self.calculate_profit_factor(use_signal=False):.2f}",
            'Value at Risk (VaR)': f"{self.calculate_value_at_risk(confidence_level, horizon, use_signal=False):.4f}"
        }

        # STRATEGY
        report['Strategy'] = {
            'Total Return': f"{self.calculate_total_return(use_signal=True):.2%}",
            'CAGR': f"{self.calculate_cagr(periods_per_year=periods_per_year, use_signal=True):.2%}",
            'Volatility': f"{self.calculate_volatility(periods_per_year=periods_per_year, use_signal=True):.2%}",
            'Sharpe Ratio': f"{self.calculate_sharpe_ratio(risk_free_rate, periods_per_year, use_signal=True):.2f}",
            'Max Drawdown': f"{self.calculate_max_drawdown(use_signal=True):.2f}%",
            'Profit Factor': f"{self.calculate_profit_factor(use_signal=True):.2f}",
            'Value at Risk (VaR)': f"{self.calculate_value_at_risk(confidence_level, horizon, use_signal=True):.4f}"
        }

        return pd.DataFrame(report)



