#!/usr/bin/env python
# coding: utf-8
# TODO aumentar la altura de los heatmap

# Imports para Dash
from dash import Dash, html, dcc
import plotly.express as px

# Imports para Data Analisis
import pandas as pd
import numpy as np

# Colores para los gráficos y la página
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Creamos el DataFrame (df) del Archivo
df = pd.read_csv("synergy_logistics_database.csv")

# Rutas importaciones y exportaciones
# Copiamos el df original
rutas = df.copy()
# Creamos una columna para guardar la cuenta
rutas['count'] = 1
# Agrupamos los datos a partir del tipo, el país de origen y de origen y
#   guardamos la cantidad de rows similares
rutas.groupby(['direction', 'origin', 'destination']).agg('count')
# Reiniciamos el índice
rutas.reset_index()
# Cambiamos el nombre de la columnas para que sean más fácil de entender
rutas.rename(columns={'direction': 'Dirección',
                 'origin': 'País de origen',
                 'destination': 'País de destino',
                 # inplace=True es necesario para que se guarden los cambios
                 'count': 'Movimientos'}, inplace=True)

# Creamos el gráfico tipo heatmap
heatmap_count = px.density_heatmap(
                    # Los datos son los que están en el df rutas
                    rutas,
                    # En el eje y ponemos el país de origen
                    y="País de origen",
                    # En el eje x ponemos el país de destino
                    x="País de destino",
                    # El valor que usamos para crear el heat map es la
                    #  cantidad de Movimientos
                    z="Movimientos",
                    # Agregamos texto a los cuadrados
                    text_auto=True,
                    # Título del gráfico
                    title="Relación origen-destino por cantidad")

# Tabla de exportaciones e importaciones por monto y no cantidad
# Copiamos el df original
rutas_sum = df.copy()
# Agrupamos por dirección, origen y destino, luego sumamos el valor total
rutas_sum = (rutas_sum.groupby(['direction', 'origin', 'destination'])['total_value']
                        .sum().reset_index())
# Cambiamos el nombre de las columnas
rutas_sum.rename(columns={'direction': 'Dirección',
                 'origin': 'País de origen',
                 'destination': 'País de destino',
                 'total_value': 'Monto'}, inplace=True)

# Este heatmap es muy similar a heatmap_count
heatmap_sum = px.density_heatmap(rutas_sum,
                            y="País de origen",
                            x="País de destino",
                            # Usamos la columna de Monto para el eje z
                            z="Monto",
                            text_auto=True,
                            title="Relación origen-destino por monto")


# Medios de transporte más importantes
# Agrupamos el df original a partir del medio de transporte
transportes = (df.groupby(['transport_mode'], group_keys=False)
                    .sum().reset_index())
# Eliminamos las columnas que no nos interesan y nos quedamos solo con la de
#   nombres de los medios de transporte y el monto de cada uno
transportes.drop(['register_id', 'year'], axis=1, inplace=True)
# Cambiamos el nombre de las columnas
transportes.rename(columns={'transport_mode': 'Medio de Transporte',
                            'total_value': 'Monto total'},
                   inplace=True)

pie_medios_transporte = px.pie(transportes,
                               values='Monto total',
                               names='Medio de Transporte',
                               title='Medios de transporte por monto generado')


# 80% del valor de exportaciones y importaciones
rutas_importantes = df.copy()
rutas_importantes = rutas_importantes.groupby(['origin', 'destination'],
                          group_keys=False)['total_value'].sum().reset_index()
rutas_importantes.sort_values('total_value', ascending=False, inplace=True)

gran_total = rutas_importantes['total_value'].sum()
rutas_importantes['porcentaje'] = rutas_importantes['total_value'].cumsum() / gran_total

count_origin_100 = rutas_importantes.groupby(['origin']).count().reset_index()
count_origin_100.drop(['total_value'], axis=1, inplace=True)
count_origin_100.rename(columns={'porcentaje': 'Cantidad de rutas',
                            'origin': 'País de origen'}, inplace=True)

rutas_importantes_80 = rutas_importantes.loc[rutas_importantes['porcentaje'] <= 0.8].reset_index()

# Elegimos solos los países de acuerdo al origin.
count_origin_80 = rutas_importantes_80.groupby(['origin']).count().reset_index()
count_origin_80.drop(['total_value'], axis=1, inplace=True)
count_origin_80.rename(columns={'porcentaje': 'Cantidad de rutas',
                            'origin': 'País de origen'}, inplace=True)

bar_origin_100 = px.bar(count_origin_100,
                        x="País de origen",
                        y="Cantidad de rutas",
                        title="Rutas por países de origen del valor total")

bar_origin_80 = px.bar(count_origin_80,
                        x="País de origen",
                        y="Cantidad de rutas",
                        title="Rutas por países del 80% del valor")

paises_descartados = []

list_100 = count_origin_100['País de origen'].tolist()
list_80 = count_origin_80['País de origen'].tolist()

for pais in list_100:
    if pais not in list_80:
        paises_descartados.append(pais)

# Creamos la app en Dash
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='heatmap_count',
        figure=heatmap_count
    ),

    dcc.Graph(
        id='heatmap_sum',
        figure=heatmap_sum
    ),

    dcc.Graph(
        id='pie_medios_transporte',
        figure=pie_medios_transporte
    ),

    dcc.Graph(
        id='bar_origin_100',
        figure=bar_origin_100
    ),

    dcc.Graph(
        id='bar_origin_80',
        figure=bar_origin_80
    )


])

if __name__ == '__main__':
    app.run_server(debug=True)
