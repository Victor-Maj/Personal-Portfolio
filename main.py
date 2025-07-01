from dash import Dash, html, dcc, Output, Input
import math
from scipy.stats import norm
import plotly.express as px
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

empty_fig = px.line(title="Stock Price Simulation")
empty_fig.update_layout(showlegend=True)

app.layout = html.Div([
    html.Div([
        html.Label("Current Asset Price:"),
        dcc.Input(id='Asset_price_Input', type='number', value=100),
        html.Br(),

        html.Label("Strike Price:"),
        dcc.Input(id='Strike_Price_Input', type='number', value=100),
        html.Br(),

        html.Label("Time to Maturity (Years):"),
        dcc.Input(id='Time_Maturity_Input', type='number', value=1),
        html.Br(),

        html.Label("Volatility (σ):"),
        dcc.Input(id='Volatility_Input', type='number', value=0.25),
        html.Br(),

        html.Label("Risk-Free Rate (r):"),
        dcc.Input(id='RF_Rate_Input', type='number', value=0.05),
        html.Br(),

        html.Label("Number of Simulations:"),
        dcc.Input(id='Num_Simulations_Input', type='number', value=100),
        html.Br(),
        
    ], className="two columns"),

    html.Div([
        html.H4("Black-Scholes Option Price:"),
        html.Div(id='Call_Price'),
        html.Br(),
        
        html.H4("Monte Carlo Simulated Option Price:"),
        html.Div(id='Simulated_Call_Price'),
        html.Br(),

        html.H2("Monte Carlo Stock Price Simulation"),
        dcc.Graph(id='stock-simulation-graph', figure=empty_fig)

    ], className="ten columns"),
], className="row")


@app.callback(
    Output('Call_Price', 'children'),
    [
        Input('Asset_price_Input', 'value'),
        Input('Strike_Price_Input', 'value'),
        Input('Time_Maturity_Input', 'value'),
        Input('Volatility_Input', 'value'),
        Input('RF_Rate_Input', 'value')
     ]
)
def calculate_price_of_a_option(S, K, T, sigma, r):
    try:
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        return f"${call_price:.2f}"
    except:
        return "Please enter valid numbers"


@app.callback(
    [Output('stock-simulation-graph', 'figure'),
     Output('Simulated_Call_Price', 'children')],
    [
        Input('Asset_price_Input', 'value'),
        Input('Volatility_Input', 'value'),
        Input('Time_Maturity_Input', 'value'),
        Input('Strike_Price_Input', 'value'),
        Input('RF_Rate_Input', 'value'),
        Input('Num_Simulations_Input', 'value')
    ]
)
def update_stock_simulation_and_price(S, sigma, T, K, r, num_sim):
    if None in [S, sigma, T, K, r, num_sim]:
        return empty_fig, "N/A"
    
    try:
        future_prices = monte_carlo_stock_price(S, r, sigma, T, num_sim)

        simulated_price = simulated_price_of_european_call_option(
            ST=future_prices,
            K=K,
            r=r,
            T=T
        )
        
        # Plot price paths
        days = np.arange(0, T * 252 + 1)
        df = pd.DataFrame({
            'Day': np.tile(days, num_sim),
            'Price': np.concatenate([np.insert(prices, 0, S) for prices in future_prices]),
            'Simulation': np.repeat(np.arange(1, num_sim + 1), len(days))
        })
        
        fig = px.line(df, x='Day', y='Price', color='Simulation',
                      title=f"Monte Carlo Stock Price Simulation ({num_sim} paths)")
        fig.update_traces(line=dict(width=1), opacity=0.7)
        fig.update_layout(showlegend=False)
        
        return fig, f"${simulated_price:.2f}"
    except Exception as e:
        print(f"Error: {e}")
        return empty_fig, "Error in calculation"


def monte_carlo_stock_price(S, r, sigma, T, num_simulations):
    T_days = int(T * 252)
    dt = 1 / T_days
    
    Z = np.random.normal(0, 1, (num_simulations, T_days))
    daily_returns = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    cumulative_returns = np.cumsum(daily_returns, axis=1)
    future_prices = S * np.exp(cumulative_returns)
    
    return future_prices


def simulated_price_of_european_call_option(ST, K, r, T):
    final_prices = ST[:, -1]
    payoffs = np.maximum(0, final_prices - K)
    call_price = np.exp(-r * T) * np.mean(payoffs)
    return call_price


if __name__ == '__main__':
    app.run(debug=True)
