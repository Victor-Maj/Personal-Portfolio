from dash import Dash, html, dcc, Output, Input
import math
from scipy.stats import norm



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.Label("Current Asset Price:"),
        dcc.Input(id='Asset_price_Input', type='number', value=10),
        html.Br(),

        html.Label("Strike Price:"),
        dcc.Input(id='Strike_Price_Input', type='number', value=10),
        html.Br(),

        html.Label("Time to Maturity (Years):"),
        dcc.Input(id='Time_Maturity_Input', type='number', value=1),
        html.Br(),

        html.Label("Volatility (σ):"),
        dcc.Input(id='Volatility_Input', type='number', value=0.25),
        html.Br(),

        html.Label("Risk Free Rate:"),
        dcc.Input(id='RF_Rate_Input', type='number', value=0.05),

    ], className="two columns"),

    html.Div([
        html.H4("The Price of the Option is:"),
        html.Div(id='Call_Price')
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


def calculate_price_of_a_option(Asset_price_Input, Strike_Price_Input, Time_Maturity_Input, Volatility_Input, RF_Rate_Input):
    try:
        S = Asset_price_Input
        K = Strike_Price_Input
        T = Time_Maturity_Input
        sigma = Volatility_Input
        r = RF_Rate_Input
            
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
    
        call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    
        return call_price
    except:
        return "Please enter valid numbers"
    


if __name__ == '__main__':
    app.run(debug=True)
