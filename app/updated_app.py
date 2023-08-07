import dash
from dash import html, dcc

import dash_bootstrap_components as dbc
from dash_bootstrap_components import Row, Col, Container
from components import multi_age

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
data_title = Row([
    Col([
        html.H3('Данные', id='data-title', style={'margin': '20px 0px'})
    ], xs=12, sm=12, md=12, lg=12, xl=12)
])


data_params_row = Row([
    Col([
        html.P('Выберите город'),
        dcc.Dropdown(options=[{'label': 'Санкт-Петербург', 'value': 'spb'},
                              {'label': 'Москва', 'value': 'msc'},
                              {'label': 'Новосибирск', 'value': 'novosib'}],
                     value='spb')
    ]),
    Col([
        html.P('Выберите год'),
        dcc.Dropdown(options=['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019'],
                     value='2010')
    ]),
    Col([
        html.P('Выберите детализированность данных'),
        dcc.Dropdown(options=[{'label': 'возрастные группы', 'value': 'age-group'},
                              {'label': 'штаммы', 'value': 'strain'},
                              {'label': 'возрастные группы и штаммы', 'value': 'strain_age-group'},
                              {'label': 'агренированные данные', 'value': 'total'}],
                     value='age-group')
    ])
])

model_title = Row([
    Col([
        html.H3('Параметры модели', id='model-title', style={'margin': '30px 0px 20px 0px'})
    ], xs=12, sm=12, md=12, lg=12, xl=12)
])

exposed_params = Row([
    Col([
        html.H3(children='exposed', id='exp_title', style={'margin': '20px 20px'}),
        html.Div(children=multi_age['exposed'], id='exp-sliders-container'),
    ])
])

app.layout = Container([
            data_title,
            data_params_row,
            model_title,
            exposed_params
        ])


if __name__ == '__main__':
    app.run(debug=True)
