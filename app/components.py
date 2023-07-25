import dash
from dash import html, dcc, Input, Output, State, ALL, MATCH

multi_strain = {'exposed': [
    html.P('A(H1N1)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.55,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 0},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('A(H3N2)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.2,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 1},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('B', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.61,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 2},
               tooltip={"placement": "bottom", "always_visible": True})
],
    'lambda': [
        html.P('A(H1N1)', style={'margin': '5px 20px'}),
        dcc.Slider(min=0, max=1.5, step=0.0001, value=0.19,
                   marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 0},
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.P('A(H3N2)', style={'margin': '5px 20px'}),
        dcc.Slider(min=0, max=1.5, step=0.0001, value=0.06,
                   marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 1},
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.P('B', style={'margin': '5px 20px'}),
        dcc.Slider(min=0, max=1.5, step=0.0001, value=0.197,
                   marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 2},
                   tooltip={"placement": "bottom", "always_visible": True})
    ]
}

multi_age = {'exposed': [
    html.P('0-14', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.55,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 0},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('15+', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.2,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 1},
               tooltip={"placement": "bottom", "always_visible": True})
],
    'lambda': [
        html.P('generic', style={'margin': '5px 20px'}),
        dcc.Slider(min=0, max=1.5, step=0.0001, value=0.19,
                   marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 0},
                   tooltip={"placement": "bottom", "always_visible": True}),
    ],
}


multi_age_strain = {'exposed': [
    html.H6('0-14', style={'margin': '5px 20px'}),
    html.P('A(H1N1)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.55,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 0},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('A(H3N2)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.2,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 1},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('B', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.61,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 2},
               tooltip={"placement": "bottom", "always_visible": True}),

    html.H6('15+', style={'margin': '5px 20px'}),
    html.P('A(H1N1)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.55,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 3},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('A(H3N2)', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.2,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 4},
               tooltip={"placement": "bottom", "always_visible": True}),
    html.P('B', style={'margin': '5px 20px'}),
    dcc.Slider(min=0, max=1, step=0.001, value=0.61,
               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 5},
               tooltip={"placement": "bottom", "always_visible": True})
],
    'lambda': [
        html.P('A(H1N1)', style={'margin': '5px 20px'}),
        dcc.Slider(min=0, max=1.5, step=0.0001, value=0.19,
                   marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 0},
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.P('A(H3N2)', style={'margin': '5px 20px'}),
        dcc.Slider(min=0, max=1.5, step=0.0001, value=0.06,
                   marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 1},
                   tooltip={"placement": "bottom", "always_visible": True}),
        html.P('B', style={'margin': '5px 20px'}),
        dcc.Slider(min=0, max=1.5, step=0.0001, value=0.197,
                   marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 2},
                   tooltip={"placement": "bottom", "always_visible": True})
    ]}
