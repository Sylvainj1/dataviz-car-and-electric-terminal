# -*coding:utf8 *-
token = open("mapbox_token").read() 
import plotly_express as px
import plotly
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import geopandas as gpd

import json

import car_evolution




#geojson du tracé des routes principales francaises
#le json de base avait des values inutilisées dans notre cas que nous avons supprimés
#nous avons aussi réduit la précision des coordonnées, tout cela pour allèger la taille du geosjon
#la taille est passé de 3,6 Mo à 1,3 Mo -> le chargement est un poil plus rapide
with open("routes_compress_all.json") as geofile:
    geojson_layer = json.load(geofile)



#création des différentes dataframe necessaires
borne_public = pd.read_csv("bornedata.csv",sep=';',na_values = 'nan', encoding="UTF-8")
borne_public_dataframe = borne_public.dropna()

lat = []
lon = []
df_tolist = borne_public_dataframe["Coordonnees"].tolist()

for coord in df_tolist:
    sp = coord.split(',')
    lat.append(float(sp[0]))
    lon.append(float(sp[1]))

borne_public_dataframe["Ylatitude"] = lat
borne_public_dataframe["Xlongitude"] = lon
borne_public_dataframe = borne_public_dataframe.rename(columns={"Puissance délivrée":"puiss_max"})



borne_tesla = pd.read_csv("irve_tesla.csv",sep=';', encoding="utf-8")
borne_tesla_dataframe = borne_tesla.drop(columns="ID_station")
borne_tesla_dataframe = borne_tesla_dataframe.rename(columns={"Xlatitude":"Ylatitude"})


borne_ionity = pd.read_csv("irve_ionity.csv",sep=';',na_values = 'nan', encoding="UTF-8")
borne_ionity_dataframe = borne_ionity.dropna()


def select_dataframe(filename):
    if filename == "bornedata.csv":
        return borne_public_dataframe

    if filename == "irve_tesla.csv":
        return borne_tesla_dataframe

    if filename == "irve_ionity.csv":
        return borne_ionity_dataframe



#figure vide car app.Callback est appelé à l'initialisation de l'appli et créer la figure
#pas besoin donc de créer une figure entière ici
fig = go.Figure()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children= f'Electriques vehicules',
    ),
    
    dcc.Dropdown(
        id='select-charger-type',
        options=[
            {'label': 'Tesla Superchargeur', 'value': "irve_tesla.csv"},
            {'label': 'Ionity Fast chargeur', 'value': 'irve_ionity.csv'},
            {'label': 'Bornes publiques', 'value': "bornedata.csv"},
        ],
        value= "bornedata.csv"
    ),
    dcc.Checklist(
        id='routes-checkbox',
        options=[
            {'label': 'Afficher les routes', 'value': 'routesTrue'}
        ],
        value=[]
    ),

    dcc.Graph(
        id='map',
        figure=fig
    ),

    dcc.Graph(
        id='car_evolution',
        figure=car_evolution.construct_car_evolution()
    )



    #bug avec le loading
    # dcc.Loading(
    #     children=[
    #         dcc.Graph(
    #                 id='map',
    #                 figure=fig
    #             )
    #     ]
    # )
])


@app.callback(
        Output(component_id='map', component_property='figure'),
        [Input(component_id='select-charger-type', component_property='value'),
        Input(component_id ='routes-checkbox', component_property='value')]
    )
def update_map_figure(input_value, route_show):
    route = route_show
    layer =[]
    if route:
        layer = [
            dict(
                type="line",
                sourcetype="geojson",
                source=geojson_layer,
                color='rgb(255,0,0)',
                opacity=0.3,
            )
        ]

    borne_data = select_dataframe(input_value)
    fig = go.Figure()
    fig.add_trace(
        go.Scattermapbox(
            lat=borne_data["Ylatitude"],
            lon=borne_data['Xlongitude'],
            mode="markers",
            marker=go.scattermapbox.Marker(
                color=borne_data["puiss_max"],
                colorscale="Viridis",
                size=4,
                reversescale=True,
                colorbar=dict(
                    title = "Puissance de charge (Kw)",
                ),
            ),
        )
    )
    fig.update_layout(
    mapbox=go.layout.Mapbox(
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=46.227638,
            lon=2.213749
        ),
        zoom=5,
        layers=layer
        )
    )

    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token, height=700)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


app.run_server(debug=True)

