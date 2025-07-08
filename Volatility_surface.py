import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from scipy.stats import norm
from scipy import optimize
import plotly.graph_objects as go
from scipy.interpolate import griddata

class VolatilitySurface:
    def __init__(self, ticker, dividend_yield, rf_rate, min_percentage=0.2, max_percentage=2):
        self.ticker = ticker
        self.dividend_yield = dividend_yield
        self.rf_rate = rf_rate
        self.stock, self.spot_prices, self.spot_price = self.get_stock_info()
        self.min_strike_price = self.spot_price * min_percentage
        self.max_strike_price = self.spot_price * max_percentage

    def get_stock_info(self, period="1y"):
        stock = yf.Ticker(self.ticker)
        spot_prices = stock.history(period=period)["Close"].to_frame()
        spot_data = stock.history(period="1d")["Close"]

        if not spot_data.empty:
            spot_price = spot_data.iloc[-1]
        else:
            spot_price = spot_prices.iloc[-1, 0] if not spot_prices.empty else None
        if spot_price is None:
            raise ValueError(f"No data available for ticker {self.ticker}. Please check the ticker symbol or try again later.")
    
        return stock, spot_prices, spot_price
    
    def get_option_data(self):
        expirations = self.stock.options
        all_data = []

        for expiry in expirations:
            try:
                opt_chain = self.stock.option_chain(expiry)
                calls = opt_chain.calls
                puts = opt_chain.puts

                calls["type"] = "call"
                puts["type"] = "put"

                df = pd.concat([calls, puts], ignore_index=True)
                df["expiration"] = pd.to_datetime(expiry)
                all_data.append(df)
            except Exception as e:
                print(f"Error fetching data for expiry {expiry}: {e}")

        option_data = pd.concat(all_data, ignore_index=True)
        return option_data, expirations

    def call_bs_value(self, S, X, r, T, v, q):
        d_1 = (np.log(S / X) + (r - q + v ** 2 * 0.5) * T) / (v * np.sqrt(T))
        d_2 = d_1 - v * np.sqrt(T)
        return S * np.exp(-q * T) * norm.cdf(d_1) - X * np.exp(-r * T) * norm.cdf(d_2)

    def call_iv_obj_function(self, S, X, r, T, v, q, call_price):
        return call_price - self.call_bs_value(S, X, r, T, v, q)

    def call_iv(self, S, X, r, T, call_price, q, a=0.001, b=5.0, xtol=0.000001):
        def fcn(v):
            return self.call_iv_obj_function(S, X, r, T, v, q, call_price)
        try:
            result = optimize.brentq(fcn, a=a, b=b, xtol=xtol)
            return np.nan if result <= xtol else result
        except ValueError:
            return np.nan

    def calculate_implied_volatility(self, option_data):
        imp_vol_data = pd.DataFrame(columns=["ContractSymbol", "StrikePrice", "TimeToExpiry", "ImpliedVolatility"])
        df_index = 0
        today = pd.Timestamp.now(tz='UTC')  # Use timezone-aware timestamp

        for i in range(len(option_data)):
            time_to_expiry = (option_data.iloc[i]["expiration"].tz_localize('UTC') - today).days / 365
            if time_to_expiry > 0:
                S = self.spot_price
                K = option_data.iloc[i]['strike']
                T = time_to_expiry
                r = self.rf_rate
                call_price = option_data.iloc[i]["lastPrice"]
                
                # Skip if price is invalid
                if call_price <= 0:
                    continue
                    
                iv = self.call_iv(
                    S=S,
                    X=K,
                    r=r,
                    T=T,
                    call_price=call_price,
                    q=self.dividend_yield
                )
                
                imp_vol_data.loc[df_index] = [
                    option_data.iloc[i]['contractSymbol'],
                    option_data.iloc[i]["strike"],
                    time_to_expiry,
                    iv
                ]
                df_index += 1
        return imp_vol_data.dropna().reset_index(drop=True)

    def get_plot_data(self, filtered_df):
        X = filtered_df['TimeToExpiry'].values
        Y = filtered_df['StrikePrice'].values
        Z = filtered_df['ImpliedVolatility'].values * 100
        return X, Y, Z

    def plot_implied_volatility(self, X, Y, Z):
        xi = np.linspace(X.min(), X.max(), 50)
        yi = np.linspace(Y.min(), Y.max(), 50)
        xi, yi = np.meshgrid(xi, yi)

        zi = griddata((X, Y), Z, (xi, yi), method='linear')

        fig = go.Figure(data=[go.Surface(x=xi, y=yi, z=zi, colorscale='Viridis')])
        fig.update_layout(
            title='Implied Volatility Surface',
            scene=dict(
                xaxis_title='Time to Expiration (years)',
                yaxis_title='Strike Price ($)',
                zaxis_title='Implied Volatility (%)'
            )
        )
        return fig

if __name__ == '__main__':
    vs = VolatilitySurface("AAPL", dividend_yield=0.01, rf_rate=0.04)
    option_data, expirations = vs.get_option_data()
    iv_data = vs.calculate_implied_volatility(option_data)
    filtered_df = iv_data[
        (iv_data['StrikePrice'] >= vs.min_strike_price) & 
        (iv_data['StrikePrice'] <= vs.max_strike_price)
    ]
    X, Y, Z = vs.get_plot_data(filtered_df)
    fig = vs.plot_implied_volatility(X, Y, Z)
    fig.show()