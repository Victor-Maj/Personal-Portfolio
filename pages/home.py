from dash import html, register_page

register_page(__name__, path='/', name="Home")

layout = html.Div([
    html.H1("Welcome to the Option Pricing Dashboard"),
    html.P("Navigate to the simulation tool to price European call options."),
    html.Br(),
    html.A("Go to Simulation", href="/simulation", style={"fontSize": "20px", "color": "blue"})
])
