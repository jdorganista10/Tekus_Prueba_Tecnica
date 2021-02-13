### Librerias
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table

import pandas as pd
import numpy as np
import os
import pyodbc

from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

from lib.functions import runQuery, graph_movement_vs_days, graph_movement_vs_hours, get_top_movements_cities, get_top_ollas

###==============================================CODIGO===========================================================
# Conexion al servidor---------------------------------------
server = 'proyecto.tekus.co'
port = '1433'
database = 'DataTest'
username = 'datatest'
password = '9cUQ*48AAX8Q'
try:
    conexion = pyodbc.connect('DRIVER={SQL Server};SERVER=' +
                              server+';PORT='+port+';DATABASE='+database+';UID='+username+';PWD='+ password)
except Exception as e:
    print("Ocurrió un error al conectar a SQL Server: ", e)

# Lectura de datos------------------------------------------
pots = runQuery("SELECT * FROM POTs ")
pots['Id'] = pots.index
cities = runQuery("SELECT * FROM Cities ")
all_data = pd.read_csv('data/all_data_v2.csv')
data_filter = pd.read_csv('data/data_filter.csv')

# Generacion de graficas
graph_days = graph_movement_vs_days(data_filter)
graph_hours = graph_movement_vs_hours(data_filter)

table_top_cities = get_top_movements_cities(data_filter,pots,cities)
table_top_ollas = get_top_ollas(data_filter,pots)

fig = graph_movement_vs_hours(data_filter)

fig_dur_vs_Id = px.scatter(all_data, x='id_olla', y='Duration',
                 hover_data =['Duration','MovementDuration','MovementInteractions','ArkboxInteractions'])
fig_movDur_vs_Id = px.scatter(all_data, x='id_olla', y='MovementDuration',
                hover_data = ['Duration', 'MovementDuration','MovementInteractions','ArkboxInteractions'])
fig_movInt_vs_Id = px.scatter(all_data, x='id_olla', y='MovementInteractions',
                hover_data = ['Duration', 'MovementDuration','MovementInteractions','ArkboxInteractions'])
fig_ArkInt_vs_Id = px.scatter(all_data, x='id_olla', y='ArkboxInteractions',
                hover_data = ['Duration', 'MovementDuration','MovementInteractions','ArkboxInteractions'])
###===========================================APLICACION==========================================================
### Aplicacion
app=dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

#server = app.server

### Estilos
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
}

SUBTITLES = {"text-align": "center"}

### Layout
sidebar = html.Div(
    [
        html.H2("Tekus", className="display-4"),
        html.P("Tecnología en tiempo real"),
        html.Hr(),
        html.P(
            "Oprime en los botones siguientes para navegar por las diferentes páginas", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Dashboard", href="/", active="exact"),
                dbc.NavLink("Análisis", href="/eda", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout= html.Div(children=[
    dcc.Location(id="url"), sidebar, content
])

#,

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div(
            [
                dbc.Row([
                    html.H1(['Ollanosepega 3000'], id='title'),
                ],justify="center", align="center", className="h-50"
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                            html.Div([
                                html.H3(['Desplazamiento por días'], id='title-graph-1',style=SUBTITLES,),
                                dcc.Graph(figure = graph_days, id = 'bar_days')
                            ]),
                            html.Div([
                                html.H3(['Desplazamiento por horas'], id='title-graph-2',style=SUBTITLES,),
                                dcc.Graph(figure = graph_hours, id = 'bar_days2')
                            ])
                        ]),
                        dbc.Col(html.Div(
                            dash_table.DataTable(id = 'table_ollas_keys',
                                                columns=[{"name": i, "id": i} for i in ['Id','Serial']],
                                                data=pots[['Id','Serial']].to_dict('records'),
                                                page_size=10
                                                )
                        )),
                    ],
                    align="center",
                    justify="center",
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Div([
                            html.H3(['Top ciudades con mas movimientos'], id='title-table-1',style=SUBTITLES,),
                            dash_table.DataTable(id = 'table_top_cities',
                                                columns=[{"name": i, "id": i} for i in table_top_cities.columns],
                                                data=table_top_cities.to_dict('records'),
                                                page_size=10
                                                )
                        ])),
                        dbc.Col(html.Div([
                            html.H3(['Top ollas con mas interacciones'], id='title-table-2',style=SUBTITLES,),
                            dash_table.DataTable(id = 'Table_top_ollas',
                                                columns=[{"name": i, "id": i} for i in table_top_ollas.columns],
                                                data=table_top_ollas.to_dict('records'),
                                                page_size=10
                                                )
                        ])),
                    ],
                    align="center",
                    justify="center",
                ),
            ]
        )
    elif pathname == "/eda":
        return html.Div([
            html.H2(['Duración de interacción por olla'], id='title-p2-Graph-1',style=SUBTITLES,),
            dcc.Graph(figure=fig_dur_vs_Id, id='scatter1'),
            html.H2(['Duración de movimiento por olla'], id='title-p2-Graph-2',style=SUBTITLES,),
            dcc.Graph(figure=fig_movDur_vs_Id, id='scatter2'),
            html.H2(['Número de interacciones por olla'], id='title-p2-Graph-3',style=SUBTITLES,),
            dcc.Graph(figure=fig_movInt_vs_Id, id='scatter3'),
            html.H2(['Interacciones Arkbox por olla'], id='title-p2-Graph-4',style=SUBTITLES,),
            dcc.Graph(figure=fig_ArkInt_vs_Id, id='scatter4')
        ])
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"La url {pathname} no fue reconocida"),
        ]
    )

if __name__=='__main__':
    app.run_server(host='0.0.0.0', port='8050', debug=True)