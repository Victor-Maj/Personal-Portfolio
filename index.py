from dash import html, dcc, page_container
from app import app

app.layout = html.Div([
    html.H1("📊 Option Pricing Dashboard", style={'textAlign': 'center'}),
    html.Div([
        dcc.Link("Home", href="/", style={"marginRight": "15px"}),
        dcc.Link("Simulation", href="/simulation"),
    ], style={"textAlign": "center", "marginBottom": "30px"}),

    page_container
])

if __name__ == "__main__":
    app.run(debug=True) 
    