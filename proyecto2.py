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
    'text': '#f3f6f4'
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

# Colores del gráfico
heatmap_count.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

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
                            'total_value': 'Monto'},
                 inplace=True)

# Este heatmap es muy similar a heatmap_count
heatmap_sum = px.density_heatmap(
                    rutas_sum,
                    y="País de origen",
                    x="País de destino",
                    # Usamos la columna de Monto para el eje z
                    z="Monto",
                    text_auto=True,
                    title="Relación origen-destino por monto")

# Colores del gráfico
heatmap_sum.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)


# Medios de transporte más importantes
# Agrupamos el df original a partir del medio de transporte y sumamos su mont
transportes = (df.groupby(['transport_mode'], group_keys=False)
                    .sum().reset_index())
# Eliminamos las columnas que no nos interesan y nos quedamos solo con la de
#   nombres de los medios de transporte y el monto de cada uno
transportes.drop(['register_id', 'year'], axis=1, inplace=True)
# Cambiamos el nombre de las columnas
transportes.rename(columns={'transport_mode': 'Medio de Transporte',
                            'total_value': 'Monto total'},
                   inplace=True)

# Creamos un gráfico tipo pie con los datos del df transportes
pie_medios_transporte = px.pie(transportes,
                               values='Monto total',
                               names='Medio de Transporte',
                               title='Medios de transporte por monto generado')

pie_medios_transporte.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

# 80% del valor de exportaciones y importaciones
# Copiamos el df original
rutas_importantes = df.copy()
# Agrupamos por origen y destino y sumamos su monto
rutas_importantes = rutas_importantes.groupby(['origin', 'destination'],
                          group_keys=False)['total_value'].sum().reset_index()
# Ordenamos el df de manera descendente respecto al monto
rutas_importantes.sort_values('total_value', ascending=False, inplace=True)

# Guardamos el total de sumar todos lo montos
gran_total = rutas_importantes['total_value'].sum()
# Agregamos el porcentaje diviendo el monto total con la suma acumulativa de
#   los montos por renglones ordenados de mayor a menor
rutas_importantes['porcentaje'] = rutas_importantes['total_value'].cumsum() / gran_total

# Creamos un df con todos los países de origen contamos la cantidad de rutas
# que salen de ese país
count_origin_100 = rutas_importantes.groupby(['origin']).count().reset_index()
# Nos quedamos solo con la columan del nombre del país y de la cantidad de
#   rutas que salen de ese país
count_origin_100.drop(['total_value'], axis=1, inplace=True)
# Cambiamos el nombre de las columnas
count_origin_100.rename(columns={'porcentaje': 'Cantidad de rutas',
                            'origin': 'País de origen'}, inplace=True)

# Obtenemos las rutas de aquellas que tiene un porcentaje acumulado igual o
#   menor al 80%
rutas_importantes_80 = rutas_importantes.loc[rutas_importantes['porcentaje'] <= 0.8].reset_index()

# Elegimos solos los países de acuerdo al origin.
count_origin_80 = (rutas_importantes_80 .groupby(['origin'])
                    .count().reset_index())
# Nos quedamos solo con la columna del nombre del país y de la cantidad de
#   rutas que salen de ese país
count_origin_80.drop(['total_value'], axis=1, inplace=True)
# Cambiamos el nombre de las columnas
count_origin_80.rename(columns={'porcentaje': 'Cantidad de rutas',
                            'origin': 'País de origen'}, inplace=True)

# Creamos una gráfica de barras con los datos de los df
bar_origin_100 = px.bar(count_origin_100,
                        y="País de origen",
                        x="Cantidad de rutas",
                        title="Rutas por países de origen del valor total")
bar_origin_80 = px.bar(count_origin_80,
                        y="País de origen",
                        x="Cantidad de rutas",
                        title="Rutas por países del 80% del valor")
# Cambiamos los colores
bar_origin_80.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
bar_origin_100.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

paises_descartados = []

list_100 = count_origin_100['País de origen'].tolist()
list_80 = count_origin_80['País de origen'].tolist()

for pais in list_100:
    if pais not in list_80:
        paises_descartados.append(pais)

# Creamos la app en Dash
app = Dash(__name__)

app.layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=[
        html.H1(children='Synergy Logistics', style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        html.Div(children='''
            Análisis de datos de importación y exportación para el diseño de
            una nueva estrategía en el año 2021
        ''', style={
                'textAlign': 'center',
                'color': colors['text']
            }),


        html.H2(children='Rutas más importantes', style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        dcc.Graph(
            id='heatmap_count',
            figure=heatmap_count,
            style={'height': '90vh'}
        ),

        dcc.Graph(
            id='heatmap_sum',
            figure=heatmap_sum,
            style={'height': '100vh'}
        ),


        html.H2(children='Medios de transporte', style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        dcc.Graph(
            id='pie_medios_transporte',
            figure=pie_medios_transporte,
            style={'width': '60vh', 'margin': '0 auto'}
        ),


        html.H2(children='Rutas del 80% del monto generado', style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        dcc.Graph(
            id='bar_origin_100',
            figure=bar_origin_100,
            style={'height': '90vh', 'width': '100vh', 'margin': '0 auto'}
        ),

        dcc.Graph(
            id='bar_origin_80',
            figure=bar_origin_80,
            style={'height': '90vh', 'width': '100vh', 'margin': '0 auto'}

        )


])

if __name__ == '__main__':
    app.run_server(debug=True)
