#!/usr/bin/env python
# coding: utf-8
# TODO Pasar todo esto a un notebook y luego exportarlo a pdf, recordar poner el link a Github.

# Imports para Dash
from dash import Dash, html, dcc, dash_table
import plotly.express as px
import os

# Imports para Data Analisis
import pandas as pd
import numpy as np

# Colores para los gráficos y la página
colors = {
    'background': '#111111',
    'text': '#f3f6f4'
}

# Creamos el DataFrame (df) del Archivo
# df = pd.read_csv("./synergy_logistics_database.csv")
df = pd.read_csv("https://raw.githubusercontent.com/luis-barrera/emtech-proyecto-2/main/synergy_logistics_database.csvhttps://raw.githubusercontent.com/luis-barrera/emtech-proyecto-2/main/synergy_logistics_database.csv")

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
# Párrafo con texto explicando lá gráfica y los resultados
par_count = html.P(children='''
    El siguiente gráfico muestra la distribución de las importaciones y
    exportaciones medido por la cantidad de operaciones en cada ruta.''',
                   style={'width': '60%', 'margin': '0 auto', 'textAlign': 'center', 'color': colors['text']})
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
# Párrafo con texto explicando lá gráfica y los resultados
par_sum = html.P(children='''
    En este otro gráfico podemos ver las rutas de importación y exportación
    entre países con su monto total.''',
                   style={'width': '60%', 'margin': '0 auto', 'textAlign': 'center', 'color': colors['text']})
# Colores del gráfico
heatmap_sum.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
# Párrafo con texto explicando lá gráfica y los resultados
par_rutas_conc = html.P(children='''
    Cómo podemos ver, no hay relación entre las rutas que más operaciones
    tienen y las que más monto manejan. Por lo que no se recomienda implementar
    una estrategia basada en la cantidad de importaciones y exportaciones''',
                   style={'width': '60%', 'margin': '0 auto', 'textAlign': 'center', 'color': colors['text']})



# Medios de transporte más importantes
# Agrupamos el df original a partir del medio de transporte y sumamos su mont
transportes = (df.groupby(['year', 'transport_mode'], group_keys=False)
                    .sum().reset_index())
# Eliminamos las columnas que no nos interesan y nos quedamos solo con la de
#   nombres de los medios de transporte y el monto de cada uno
transportes.drop(['register_id'], axis=1, inplace=True)
# Cambiamos el nombre de las columnas
transportes.rename(columns={'transport_mode': 'Medio de Transporte',
                            'total_value': 'Monto total',
                            'year': 'Año'},
                   inplace=True)

# Creamos un gráfico tipo line con los datos del df transportes
plot_medios_transporte = px.line(transportes,
                                x='Año',
                                y='Monto total',
                                color='Medio de Transporte',
                                title='Medios de transporte por monto generado')
# Colores del plot
plot_medios_transporte.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
# Tabla en html a partir del df
transportes_html = dash_table.DataTable(
                    data=transportes.head(10).to_dict('records'),
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    })
# Párrafo con texto explicando lá gráfica y los resultados
par_transportes = html.P(children='''
     Los tres medios de transportes más importantes para Synergy Logistics son
     Air, Rail y Sea. Una estrategia recomendada sería crear un plan para
     sustituir Road por los otros medios de transportes.''',
                         style={'margin': '0', 'textAlign': 'center', 'color': colors['text']})


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
# Párrafos con texto explicando lá gráfica y los resultados
par_origin = html.P(children='''
    En las primera gráfica, tenemos los países de origen con la cantidad de
    rutas que pertenecen a estos. En la segunda gráfica tenemos los países
    que generan el 80% del monto con su respectiva cantidad de rutas.''',
                   style={'width': '60%', 'margin': '0 auto', 'textAlign': 'center', 'color': colors['text']})
par_origin_conc = html.P(children='''Vemos que reducimos 7 países si aplicamos
    esta estrategia. Si consideramos que tener instalaciones en cada país tiene
    costos de operación, si tenemos menos países dónde no se genera tanto valor
    entonces es una buena estrategia para ahorrar costos. Así, nos podemos
    enfocar en los países que más valor tienen sin gastar tanto.''',
                   style={'width': '60%', 'margin': '0 auto', 'textAlign': 'center', 'color': colors['text']})


# Mostramos los países descartados
paises_descartados = []
list_100 = count_origin_100['País de origen'].tolist()
list_80 = count_origin_80['País de origen'].tolist()

for pais in list_100:
    if pais not in list_80:
        paises_descartados.append(pais)

# Vamos agregando los países de la lista al elemento html
par_paises_descartados = html.P(children=['Los paises descartados usando el 80% son: '],
                                style={'width': '60%', 'margin': '0 auto', 'textAlign': 'center', 'color': colors['text']})
for i in range(len(paises_descartados)):
    par_paises_descartados.children.append(paises_descartados[i])
    if i < len(paises_descartados) - 2:
        par_paises_descartados.children.append(", ")
    if i == len(paises_descartados) - 2:
        par_paises_descartados.children.append(" y ")

par_paises_descartados.children.append(".")


# Dash
# Creamos la app en Dash
app = Dash(__name__)

server = app.server

# Declaramos el layout
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

        html.Hr(),

        html.H2(children='Rutas más importantes', style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        par_count,

        dcc.Graph(
            id='heatmap_count',
            figure=heatmap_count,
            style={'height': '90vh'}
        ),

        par_sum,

        dcc.Graph(
            id='heatmap_sum',
            figure=heatmap_sum,
            style={'height': '100vh'}
        ),

        par_rutas_conc,

        html.Hr(),

        html.H2(children='Medios de transporte',
                style={ 'textAlign': 'center', 'color': colors['text']}),

        html.Div(
            children=[
                html.Div(children=[
                            html.Div(par_transportes)],
                            # html.Div(par_transportes),
                            # transportes_html],
                         style={'margin': 'auto',
                                'height': '100%',
                                'display': 'grid',
                                'padding': '20%',
                                'grid-template-rows': '2fr 3fr'}),
                dcc.Graph(
                    id='plot_medios_transporte',
                    figure=plot_medios_transporte,
                    style={'height': '100%', 'margin': 'auto'})],
            style={'height': '80vh',
                    'display': 'grid',
                    'width': '80%',
                    'margin': '0 auto',
                    # 'justify-content': 'center',
                    # 'align-items': 'center',
                    # 'gap': '4px',
                    'grid-template-columns': '2fr 3fr'}),


        html.Hr(),

        html.H2(children='Rutas del 80% del monto generado', style={
                'textAlign': 'center',
                'color': colors['text']
            }),

        par_origin,

        html.Div(children=[
            dcc.Graph(
                id='bar_origin_100',
                figure=bar_origin_100,
                style={'height': '90vh', 'width': '90vh', 'margin': '0 auto'}
            ),
            dcc.Graph(
                id='bar_origin_80',
                figure=bar_origin_80,
                style={'height': '90vh', 'width': '90vh', 'margin': '0 auto'}
            )],
            style={'display': 'grid',
                    'width': '100%',
                    'margin': '0 auto',
                    'grid-template-columns': '1fr 1fr'}),

        par_paises_descartados,
        par_origin_conc,

        html.Div(style={'height': '40px'}),

        html.Footer(children=[
                    html.P(children=[
                            'Creado por ',
                            html.A(children='luis-barrera', href='https://github.com/luis-barrera'),
                            ', repositorio del proyecto en ',
                            html.A(children='GitHub', href='https://github.com/luis-barrera/proyecto2-dash'),
                           ])],
                    style={'display': 'flex',
                            'justify-content': 'center',
                            'padding': '5px',
                            'background-color': '#45a1ff',
                            'color': '#111'}),
])

if __name__ == '__main__':
    app.run_server(debug=True)

