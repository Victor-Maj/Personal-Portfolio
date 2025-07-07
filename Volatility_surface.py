import pandas as pd
import numpy as np
import yfinance as yf

class VolatilitySurface:
    def __init__(self, ticker, dividend_yield, rf_rate, min_percentage = 0.2, max_percentage = 2):
        self.ticker         = ticker
        self.dividend_yield = dividend_yield
        self.rf_rate        = rf_rate
        self.stock, self.spot_prices, self.spot_price = self.get_stock_info()
        self.min_strike_price = self.spot_price * min_percentage
        self.max_strike_price = self.spot_price * max_percentage  

    def get_stock_info(self, period = "1y"):
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

    def calculate_implied_volatility(calls_data, spot_price, risk_free_rate, dividend_yield):
        imp_vol_data = pd.DataFrame(columns=["ContractSymbol", "StrikePrice", "TimeToExpiry", "ImpliedVolatility"])
        df_index = 0


if __name__ == '__main__':
    vs = VolatilitySurface("AAPL", dividend_yield=0.01, rf_rate=0.04)
    option_data, expirations = vs.get_option_data()
    print(option_data)
    print(expirations)

