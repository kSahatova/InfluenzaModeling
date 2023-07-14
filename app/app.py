import pandas as pd

from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

from build_model import get_data_and_model


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = \
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2(children='Parameters', id='params', style={'margin': '20px 20px'}),
                html.H3(children='exposed', id='exp_title', style={'margin': '20px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1, step=0.01, value=0.44,
                               marks={0: '0', 1: '1'}, id='exposed_AH1N1',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1, step=0.01, value=0.25,
                               marks={0: '0', 1: '1'}, id='exposed_AH3N2',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1, step=0.01, value=0.55,
                               marks={0: '0', 1: '1'}, id='exposed_B',
                               tooltip={"placement": "bottom", "always_visible": True})
                ]),
                html.H3(children='lambda', style={'margin': '0px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1.5, step=0.0001, value=0.18,
                               marks={0: '0', 1.5: '1.5'}, id='lambda_AH1N1',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1.5, step=0.0001, value=0.07,
                               marks={0: '0', 1.5: '1.5'}, id='lambda_AH3N2',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1.5, step=0.0001, value=0.21,
                               marks={0: '0', 1.5: '1.5'}, id='lambda_B',
                               tooltip={"placement": "bottom", "always_visible": True})
                ]),

                html.H3(children='a', style={'margin': '0px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1, step=0.01, value=0.05,
                               marks={0: '0', 1: '1'}, id='a',
                               tooltip={"placement": "bottom", "always_visible": True})
                    ]),
                html.H3(children='mu', style={'margin': '20px 20px'}),
                dcc.Slider(min=0, max=1, step=0.01, value=0.2,
                           marks={0: '0', 1: '1'}, id='mu',
                           tooltip={"placement": "bottom", "always_visible": True}),
                html.H3(children='delta',  style={'margin': '20px 20px'}),
                dcc.Slider(min=0, max=1000, step=1, value=40,
                           marks={0: '0', 1: '1'}, id='delta',
                           tooltip={"placement": "bottom", "always_visible": True}),
                dbc.Button("Make simulation", color="primary",
                           id='simulation-button', style={'margin': '40px 20px 0px 20px'})

            ], xs=4, md=4, lg=4, xl=4),
            dbc.Col([
                html.Div([dcc.Graph(id='model-fit')],
                         style={'margin': '40px'})
            ], xs=7, md=7, lg=7, xl=7)

        ]),
    ], fluid=True, className='container-fluid')


@app.callback(
    Output('model-fit', 'figure'),
    Input('simulation-button', 'n_clicks'),
    State('exposed_AH1N1', 'value'),
    State('exposed_AH3N2', 'value'),
    State('exposed_B', 'value'),

    State('lambda_AH1N1', 'value'),
    State('lambda_AH3N2', 'value'),
    State('lambda_B', 'value'),

    State('a', 'value'),
    State('mu', 'value'),
    State('delta', 'value')
)
def update_output_div(_, exp_AH1N1, exp_AH3N2, exp_B,
                      lambda_AH1N1, lambda_AH3N2, lambda_B,
                      a, mu, delta):
    print(exp_AH1N1, exp_AH3N2, exp_B, lambda_AH1N1, lambda_AH3N2, lambda_B, a)
    colors = ['blue', 'green', 'orange']
    exposed_list = [exp_AH1N1, exp_AH3N2, exp_B]

    sum_exposed = sum(exposed_list)
    if sum_exposed < 1:
        exposed_list.append(1 - sum_exposed)
    else:
        exposed_list = [item / sum_exposed for item in exposed_list]
        exposed_list.append(0)

    lam_list = [lambda_AH1N1, lambda_AH3N2, lambda_B]
    a_list = [a]

    epid_data, model_obj = get_data_and_model(mu)
    model_obj.init_simul_params(exposed_list=exposed_list, lam_list=lam_list, a=a_list)
    simul_data, _, _, _ = model_obj.make_simulation()

    days_num = simul_data.shape[2]
    wks_num = int(days_num / 7.0)
    simul_weekly = [simul_data[0, :, i * 7: i * 7 + 7].sum(axis=1) for i in range(wks_num)]
    simul_data = pd.DataFrame(simul_weekly, columns=['A(H1N1)pdm09', 'A(H3N2)', 'B'])
    simul_data = simul_data.iloc[:epid_data.index[-1], :]

    fig = go.Figure()
    for i, strain in enumerate(simul_data.columns):
        fig.add_trace(go.Scatter(x=epid_data[strain].index,
                                 y=epid_data[strain],
                      mode='markers',
                      marker={'color': colors[i]},
                      name='Calibration data ' + strain)
                      )

    for i, strain in enumerate(simul_data.columns):
        fig.add_trace(go.Scatter(x=simul_data[strain].index + delta,
                                 y=simul_data[strain],
                      mode='lines',
                      marker={'color': colors[i]},
                      name=strain))
    fig.update_layout(
        autosize=False,
        width=1200,
        height=600,
        margin=dict(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ),
        paper_bgcolor="white",
    )
    fig.update_xaxes(title_text="Weeks")
    fig.update_yaxes(title_text="Incidence, cases")

    return fig


if __name__ == '__main__':
    app.run(debug=True)
