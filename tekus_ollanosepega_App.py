### Librerias
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc


### Aplicacion
app=dash.Dash(__name__)


### Layout
app.layout= html.Div(children=[
html.H1(['Ollanosepega 3000'], id='title')

])




if __name__=='__main__':
    app.run_server(host='0.0.0.0', port='8050', debug=True)