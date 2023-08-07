from dash import Dash, html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from components import multi_age, multi_strain, multi_age_strain


layout = \
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2(children='Parameters', id='params', style={'margin': '20px 20px'}),
                html.H5('Choose incidence type', style={'margin': '20px 20px'}),
                dcc.RadioItems(
                    options=[{'label': 'multi age ', 'value': 'age-group'},
                             {'label': 'multi strain ', 'value': 'strain'},
                             {'label': 'multi strain-age ', 'value': 'strain_age-group'}],
                    value='age-group', id='incidence', inline=True,
                    inputStyle={"marginRight": "4px",
                                "marginLeft": "15px"}, style={'margin': '10px 5px'}),

                html.H3(children='exposed', id='exp_title', style={'margin': '20px 20px'}),
                html.Div(children=multi_age['exposed'],
                         id='exp-sliders-container'),

                html.H3(children='lambda', style={'margin': '0px 20px'}),
                html.Div(children=multi_age['lambda'], id='lambda-sliders-container'),

                html.H3(children='a', style={'margin': '0px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1, step=0.01, value=0.15517896068381203,
                               marks={0: '0', 1: '1'}, id='a',
                               tooltip={"placement": "bottom", "always_visible": True})
                    ]),
                html.H3(children='mu', style={'margin': '20px 20px'}),
                dcc.Slider(min=0, max=1, step=0.001, value=0.169,
                           marks={0: '0', 1: '1'}, id='mu',
                           tooltip={"placement": "bottom", "always_visible": True}),
                html.H3(children='delta',  style={'margin': '20px 20px'}),
                dcc.Slider(min=0, max=100, step=1, value=35,
                           marks={0: '0', 100: '1'}, id='delta',
                           tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Button("Make simulation", color="primary",
                           id='simulation-button', style={'margin': '40px 20px 0px 20px'})  # 'display': 'none'

            ], xs=4, md=4, lg=4, xl=4),
            dbc.Col([
                html.Div([dcc.Graph(id='model-fit')],
                         style={'margin': '40px'})
            ], xs=7, md=7, lg=7, xl=7)
        ]),
    ], fluid=True, className='container-fluid')
