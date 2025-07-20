from dash import html, dcc, Input, Output, callback, register_page
import plotly.express as px
import numpy as np
import pandas as pd
from utils.calculations import (
    black_scholes_call_price,
    monte_carlo_stock_price,
    simulated_call_option_price
)

register_page(__name__, path='/simulation', name="Simulation")

# Initial empty figure
empty_fig = px.line(title="Stock Price Simulation")

layout = html.Div([
    html.H2("Option Pricing Simulator"),

    html.Div([
        html.Label("Current Asset Price:"),
        dcc.Input(id='Asset_price_Input', type='number', value=100),

        html.Label("Strike Price:"),
        dcc.Input(id='Strike_Price_Input', type='number', value=100),

        html.Label("Time to Maturity (Years):"),
        dcc.Input(id='Time_Maturity_Input', type='number', value=1),

        html.Label("Volatility (σ):"),
        dcc.Input(id='Volatility_Input', type='number', value=0.25),

        html.Label("Risk-Free Rate (r):"),
        dcc.Input(id='RF_Rate_Input', type='number', value=0.05),

        html.Label("Number of Simulations:"),
        dcc.Input(id='Num_Simulations_Input', type='number', value=100),
    ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top"}),

    html.Div([
        html.H4("Black-Scholes Option Price:"),
        html.Div(id='Call_Price'),

        html.H4("Monte Carlo Simulated Option Price:"),
        html.Div(id='Simulated_Call_Price'),

        html.H2("Monte Carlo Stock Price Simulation"),
        dcc.Graph(id='stock-simulation-graph', figure=empty_fig)
    ], style={"width": "68%", "display": "inline-block", "paddingLeft": "2%"}),
])

@callback(
    Output('Call_Price', 'children'),
    Input('Asset_price_Input', 'value'),
    Input('Strike_Price_Input', 'value'),
    Input('Time_Maturity_Input', 'value'),
    Input('Volatility_Input', 'value'),
    Input('RF_Rate_Input', 'value'),
)
def update_bs_price(S, K, T, sigma, r):
    price = black_scholes_call_price(S, K, T, sigma, r)
    return f"${price:.2f}" if price else "Invalid input"

@callback(
    Output('stock-simulation-graph', 'figure'),
    Output('Simulated_Call_Price', 'children'),
    Input('Asset_price_Input', 'value'),
    Input('Volatility_Input', 'value'),
    Input('Time_Maturity_Input', 'value'),
    Input('Strike_Price_Input', 'value'),
    Input('RF_Rate_Input', 'value'),
    Input('Num_Simulations_Input', 'value'),
)
def update_simulation(S, sigma, T, K, r, num_sim):
    if None in [S, sigma, T, K, r, num_sim]:
        return empty_fig, "Invalid input"

    ST = monte_carlo_stock_price(S, r, sigma, T, num_sim)
    sim_price = simulated_call_option_price(ST, K, r, T)

    days = np.arange(0, T * 252 + 1)
    df = pd.DataFrame({
        'Day': np.tile(days, num_sim),
        'Price': np.concatenate([np.insert(path, 0, S) for path in ST]),
        'Simulation': np.repeat(np.arange(1, num_sim + 1), len(days))
    })

    fig = px.line(df, x='Day', y='Price', color='Simulation', title=f"{num_sim} Simulated Paths")
    fig.update_layout(showlegend=False)
    return fig, f"${sim_price:.2f}"
