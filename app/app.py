import dash
import pandas as pd

from dash import Dash, html, dcc, Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

from build_model import get_data_and_model, prepare_exposed_list
from optimizers.aux_functions import data_functions as dtf
from optimizers.aux_functions import weights_for_data_functions as weights_for_data


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

exposed_sliders = [
                    dcc.Slider(min=0, max=1, step=0.001, value=0.55,
                               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 0},
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1, step=0.001, value=0.2,
                               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 1},
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1, step=0.001, value=0.61,
                               marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 2},
                               tooltip={"placement": "bottom", "always_visible": True})
                ]
lambda_sliders = [
                    dcc.Slider(min=0, max=1.5, step=0.0001, value=0.19,
                               marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 0},
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1.5, step=0.0001, value=0.06,
                               marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 1},
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1.5, step=0.0001, value=0.197,
                               marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 2},
                               tooltip={"placement": "bottom", "always_visible": True})
                ]
app.layout = \
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2(children='Parameters', id='params', style={'margin': '20px 20px'}),
                html.H5('Choose incidence type', style={'margin': '20px 20px'}),
                dcc.RadioItems(
                    options=[{'label': 'multi age ', 'value': 'age-group'},
                             {'label': 'multi strain ', 'value': 'strain'},
                             {'label': 'multi strain-age ', 'value': 'strain_age-group'}],
                    value='age-group', id='incidence', inline=True),

                html.H3(children='exposed', id='exp_title', style={'margin': '20px 20px'}),
                html.Div(children=exposed_sliders,
                         id='exp-sliders-container'),

                html.H3(children='lambda', style={'margin': '0px 20px'}),
                html.Div(children=lambda_sliders, id='lambda-sliders-container'),

                html.H3(children='a', style={'margin': '0px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1, step=0.01, value=0.12,
                               marks={0: '0', 1: '1'}, id='a',
                               tooltip={"placement": "bottom", "always_visible": True})
                    ]),
                html.H3(children='mu', style={'margin': '20px 20px'}),
                dcc.Slider(min=0, max=1, step=0.01, value=0.5,
                           marks={0: '0', 1: '1'}, id='mu',
                           tooltip={"placement": "bottom", "always_visible": True}),
                html.H3(children='delta',  style={'margin': '20px 20px'}),
                dcc.Slider(min=0, max=100, step=1, value=0,
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


@app.callback(
    [Output('exp-sliders-container', 'children'),
     Output('lambda-sliders-container', 'children')],

    Input('incidence', 'value')
)
def update_components(incidence):
    global exposed_sliders, lambda_sliders
    if incidence == 'age-group':
        reduced_exposed_sliders = [
            dcc.Slider(min=0, max=1, step=0.001, value=0.55,
                       marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 0},
                       tooltip={"placement": "bottom", "always_visible": True}),
            dcc.Slider(min=0, max=1, step=0.001, value=0.2,
                       marks={0: '0', 1: '1'}, id={'type': 'exposed', 'index': 1},
                       tooltip={"placement": "bottom", "always_visible": True})
        ]
        reduced_lambda_sliders = [
            dcc.Slider(min=0, max=1.5, step=0.0001, value=0.19,
                       marks={0: '0', 1.5: '1.5'}, id={'type': 'lambda', 'index': 0},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]
        return [reduced_exposed_sliders, reduced_lambda_sliders]

    return [exposed_sliders, lambda_sliders]


@app.callback(
    Output('model-fit', 'figure'),
    Input('simulation-button', 'n_clicks'),
    State('incidence', 'value'),

    State({'type': 'exposed', 'index': ALL}, 'value'),
    State({'type': 'lambda', 'index': ALL}, 'value'),

    State('a', 'value'),
    State('mu', 'value'),
    State('delta', 'value'),
    prevent_initial_call=True
)
def update_output_div(_, incidence, exposed_values,
                      lambda_values, a, mu, delta):
    print(dash.callback_context.inputs_list)
    print(exposed_values, lambda_values, a)

    colors = ['blue', 'green', 'orange']
    groups = []

    if incidence == 'age-group':
        groups = ['0-14', '15 и ст.']

    elif incidence == 'strain':
        groups = ['A(H1N1)pdm09', 'A(H3N2)', 'B']

    exposed_list = exposed_values
    lam_list = lambda_values
    a_list = [a]
    exposed_list = prepare_exposed_list(incidence, exposed_list)

    epid_data, model_obj, year = get_data_and_model(mu, incidence)
    model_obj.init_simul_params(exposed_list=exposed_list, lam_list=lam_list, a=a_list)
    model_obj.set_attributes()
    simul_data, _, _, _ = model_obj.make_simulation()
    shape = simul_data.shape
    simul_data = simul_data.reshape(shape[0] * shape[1], shape[2])
    simul_data = pd.DataFrame(simul_data.T, columns=groups)

    days_num = simul_data.shape[0]
    wks_num = int(days_num / 7.0)
    simul_weekly = simul_data.aggregate(func=lambda x: [x[i * 7: i * 7 + 7].sum() for i in range(wks_num)])

    epid_data.index = epid_data.reset_index().index + delta
    m, n = epid_data.index[0], epid_data.index[-1]
    data_weights = weights_for_data.getWeights4Data(epid_data, groups)
    res2_list = dtf.find_residuals_weighted_list(epid_data, groups, data_weights)

    sum_list = []

    for group in groups:
        x = epid_data[group]
        y = simul_weekly[group]
        sum_ = sum([data_weights[group][i] * pow(x[m + i] - y[m + i], 2) for i in range(len(x))])
        sum_list.append(sum_)

    r_squared = [1 - fun_val / res2 for fun_val, res2 in zip(sum_list, res2_list)]

    fig = go.Figure()
    for i, group in enumerate(simul_data.columns):
        fig.add_trace(go.Scatter(x=epid_data[group].index,
                                 y=epid_data[group],
                                 mode='markers',
                                 legendgroup='data',
                                 marker={'color': colors[i]},
                                 name='Data ' + group)
                      )

    for i, group in enumerate(simul_data.columns):
        fig.add_trace(go.Scatter(x=simul_weekly[group].index[:n + 15],
                                 y=simul_weekly[group][:n + 15],
                                 mode='lines',
                                 legendgroup='model-fit',
                                 marker={'color': colors[i]},
                                 name='Model fit ' + group))
    for i, r2 in enumerate(r_squared):
        fig.add_annotation(text='R2: '+str(round(r2, 2)), showarrow=False,
                           x=1, xshift=0, yshift=i*15 + 100, font={'color': colors[i]})
    fig.update_layout(
        template='plotly_white',
        autosize=True,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="white",
        title={
            'text': f"Saint Petersburg, {year}-{year + 1}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.update_layout(legend=dict(orientation="h", yanchor="top", xanchor="left", y=-0.3, x=0))
    fig.update_xaxes(title_text="Weeks")
    fig.update_yaxes(title_text="Incidence, cases")

    return fig


if __name__ == '__main__':
    app.run(debug=True)
