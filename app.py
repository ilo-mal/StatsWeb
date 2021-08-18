import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from collections import deque
import datetime
import psutil
import time

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID])

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

logged = psutil.users()
users = [x[0] for x in logged]
X = deque(maxlen=30)
X.append(datetime.datetime.now().strftime('%H:%M:%S'))
Y = deque(maxlen=30)
Y.append(1)
Z = deque(maxlen=30)
Z.append(1)
N = deque(maxlen=30)
N.append(1)


@app.callback(Output('net-graph', 'figure'),
              [Input('net-update', 'n_intervals')])
def network_graph(net):
    p = psutil.net_io_counters(pernic=True)
    network = list(p.items())
    net = network[4]
    net_bytes = net[1][0] + net[1][1]
    time.sleep(1)
    p = psutil.net_io_counters(pernic=True)
    network = list(p.items())
    net_bytes2 = network[4][1][0] + network[4][1][1]
    N.append(net_bytes2 - net_bytes)
    data = go.Scatter(x=list(X), y=list(N), name='Scatter',
                      fill="tozeroy", fillcolor="#0ec4bc", )

    return {'data': [data], 'layout': go.Layout({'xaxis': {'range': [X[0], X[-1]]}, 'yaxis': {'range': [min(N), 100000]}},
            title='Network traffic:', plot_bgcolor='#e1e2e2', paper_bgcolor='#e1e2e2')}


@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def cpu_graph_scatter(input_data):
    X.append(datetime.datetime.now().strftime('%H:%M:%S'))
    cpu_per = psutil.cpu_percent(1)
    Y.append(cpu_per)
    data = go.Scatter(
        x=list(X), y=list(Y),
        name='Scatter', fill="tozeroy", fillcolor="#e8c23c", )
    return {'data': [data], 'layout': go.Layout({'xaxis': {'range': [X[0], X[-1]]}, 'yaxis': {'range': [0, 100]}},
            title='PCU usage in percent:', plot_bgcolor='#e1e2e2', paper_bgcolor='#e1e2e2', )}


@app.callback(Output('my-graph', 'figure'),
              [Input('update', 'n_intervals')])
def memory_graph_scatter(inp_data):
    memory = psutil.virtual_memory()[2]
    Z.append(memory)
    data = go.Scatter(
        x=list(X), y=list(Z),
        name='Scatter', fill="tozeroy", fillcolor="#66c40e")
    return {'data': [data], 'layout': go.Layout({'xaxis': {'range': [X[0], X[-1]]}, 'yaxis': {'range': [0, 100]}},
            title='Memory usage in percent:', plot_bgcolor='#e1e2e2', paper_bgcolor='#e1e2e2', )}

app.layout = html.Div(

    [
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id='live-graph', animate=False, style={'height': 300}),
                         dcc.Interval(id='graph-update', interval=1 * 2000, ), ], width=7,
                        style={'border': '2px solid red', 'border-radius': '25px', 'backgroundColor': '#e1e2e2'}),
                dbc.Col([
                    html.Div(
                        [html.H2('Logged users', style={'textAlign': 'center', }), html.Ul([html.Li(u) for u in users],
                                                 style={'textAlign': 'center'})], )
                ], style={'border': '2px solid red', 'border-radius': '25px', 'backgroundColor': '#e1e2e2'})], style={'margin': '10px', }),
        dbc.Row([
            dbc.Col([dcc.Graph(id='my-graph', animate=False, style={'height': 300}),
                     dcc.Interval(id='update', interval=1 * 2000)], width=7,
                    style={'border': '2px solid red', 'border-radius': '25px', 'backgroundColor': '#e1e2e2'}),
            dbc.Col([dcc.Graph(id='net-graph', animate=False, style={'height': 300}),
                     dcc.Interval(id='net-update', interval=1 * 2000)], width=5,
                    style={'border': '2px solid red', 'border-radius': '25px', 'backgroundColor': '#e1e2e2'}),
        ], style={'margin': '10px',}),
    ], )


if __name__ == '__main__':
    app.run_server(debug=True)
