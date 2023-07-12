import pandas as pd

from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

from build_model import build_model


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = \
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2(children='Parameters', id='params', style={'margin': '20px 20px'}),
                html.H3(children='exposed', id='exp_title', style={'margin': '20px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1, step=0.01, value=0.5,
                               marks={0: '0', 1: '1'}, id='exposed_AH1N1',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1, step=0.01, value=0.5,
                               marks={0: '0', 1: '1'}, id='exposed_AH3N2',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1, step=0.01, value=0.5,
                               marks={0: '0', 1: '1'}, id='exposed_B',
                               tooltip={"placement": "bottom", "always_visible": True})
                ]),
                html.H3(children='lambda', style={'margin': '0px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1.5, step=0.01, value=0.5,
                               marks={0: '0', 1.5: '1.5'}, id='lambda_AH1N1',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1.5, step=0.01, value=0.5,
                               marks={0: '0', 1.5: '1.5'}, id='lambda_AH3N2',
                               tooltip={"placement": "bottom", "always_visible": True}),
                    dcc.Slider(min=0, max=1.5, step=0.01, value=0.5,
                               marks={0: '0', 1.5: '1.5'}, id='lambda_B',
                               tooltip={"placement": "bottom", "always_visible": True})
                ]),

                html.H3(children='a', style={'margin': '0px 20px'}),
                html.Div([
                    dcc.Slider(min=0, max=1, step=0.01, value=0.5,
                               marks={0: '0', 1: '1'}, id='a',
                               tooltip={"placement": "bottom", "always_visible": True})
                    ]),
                dbc.Button("Make simulation", color="primary",
                           id='simulation-button', style={'margin': '40px 20px 0px 20px'})

            ], xs=5, md=5, lg=5, xl=5),

        ]),
        dbc.Row([
            dbc.Col([
                html.Div([dcc.Graph(id='model-fit')])
            ], xs=11, md=11, lg=11, xl=11)
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

    State('a', 'value')
)
def update_output_div(_, exp_AH1N1, exp_AH3N2, exp_B, lambda_AH1N1, lambda_AH3N2, lambda_B, a):
    print(exp_AH1N1, exp_AH3N2, exp_B, lambda_AH1N1, lambda_AH3N2, lambda_B, a)

    exposed_list = [exp_AH1N1, exp_AH3N2, exp_B]

    sum_exposed = sum(exposed_list)
    if sum_exposed < 1:
        exposed_list.append(1 - sum_exposed)
    else:
        exposed_list = [item / sum_exposed for item in exposed_list]
        exposed_list.append(0)

    lam_list = [lambda_AH1N1, lambda_AH3N2, lambda_B]
    a_list = [a]

    model_obj = build_model()
    model_obj.init_simul_params(exposed_list=exposed_list, lam_list=lam_list, a=a_list)
    simul_data, _, _, _ = model_obj.make_simulation()

    days_num = simul_data.shape[2]
    wks_num = int(days_num / 7.0)
    simul_weekly = [simul_data[0, :, i * 7: i * 7 + 7].sum(axis=1) for i in range(wks_num)]
    simul_data = pd.DataFrame(simul_weekly, columns=['AH1N1', 'AH3N2', 'B']).iloc[:60, :]

    fig = go.Figure()
    for strain in simul_data.columns:
        fig.add_trace(go.Scatter(x=simul_data[strain].index,
                                 y=simul_data[strain],
                      mode='lines',
                      name=strain))
    fig.update_xaxes(title_text="Weeks")
    fig.update_yaxes(title_text="Incidence, cases")

    return fig


if __name__ == '__main__':
    app.run(debug=True)
