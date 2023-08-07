import dash
from dash import dcc, html
from dash_bootstrap_components import Row, Col


exposed_params = [
    html.P('A(H1N1)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, value=0.8,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 0},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('A(H3N2)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, value=0.7,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 1},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('B', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, value=0.1,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 2},
               tooltip={"placement": "bottom", "always_visible": True})
    ]

