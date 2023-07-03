from dash import Dash, html, dcc

app = Dash(__name__)

app.layout = html.Div([
    html.H3('Data'),
    dcc.Input(id="input_year"),
    dcc.Input(id="mu"),
    html.Div(children='Hello World')
])

if __name__ == '__main__':
    app.run(debug=True)
