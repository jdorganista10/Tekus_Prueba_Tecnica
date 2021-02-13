import pandas as pd
import numpy as np
import os
import pyodbc

from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

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

def runQuery(sql):
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql)
            return pd.DataFrame(np.array(cursor.fetchall()),
                                columns = [column[0] for column in cursor.description])
    except Exception as e:
        print("Ocurrió un error al consultar: ", e)
        return None

def graph_movement_vs_days(df, id_ollas = 'all'):
    if id_ollas == 'all':
        df_days = df.groupby('Weekday').sum()
    else:
        df_days = df[df.id_olla.isin(id_ollas)].groupby('Weekday').sum()
    
    df_days['Day'] = df_days.index.map({0:'Lun',1:'Mar',2:'Mie',3:'Jue',4:'Vie',5:'Sab',6:'Dom'})
    fig = px.bar(df_days, x=df_days.Day, y=df_days.MovementInteractions, color=df_days.Duration,
                 hover_data=['Duration', 'MovementDuration','ArkboxInteractions'])
    return fig

def graph_movement_vs_hours(df, id_ollas = 'all', days = 'all'):
    if id_ollas == 'all':
        df_days = df.groupby('Hour').sum()
    else:
        df_days = df[df.id_olla.isin(id_ollas)].groupby('Hour').sum()
    
    fig = px.bar(df_days, x=df_days.index, y=df_days.MovementInteractions, color=df_days.Duration,
                 hover_data=['Duration', 'MovementDuration','ArkboxInteractions'])
    return fig

def get_top_movements_cities(df,pots,cities):
    df_cities = cities.set_index('CityId')
    dict_cities = {i: df_cities.loc[pots.CityId[i],'Name'] for i in pots.index}
    df['City'] = df.id_olla.map(dict_cities)
    df_out = df.groupby('City').mean().drop(columns=['id_olla','Weekday','Hour','Duration','ArkboxInteractions'])
    
    df_out.reset_index(inplace = True)
    df_out = df_out[['City','MovementInteractions','MovementDuration']]
    return df_out.sort_values(by='MovementInteractions',ascending=False)

def get_top_ollas(df,pots):
    df_out = df.groupby('id_olla').mean().drop(columns=['Weekday','Hour','Duration','MovementDuration','MovementInteractions'])
    #df_out = df_out[['ArkboxInteractions','Duration','MovementDuration','MovementInteractions']]
    
    dict_serial_olla = {i: pots.loc[i,'Serial'] for i in df_out.index}
    df_out['Serial'] = df_out.index.map(dict_serial_olla)
    return df_out.sort_values(by='ArkboxInteractions',ascending=False)