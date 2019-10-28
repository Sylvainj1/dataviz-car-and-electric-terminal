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


#geojson du tracé des routes principales francaises
with open("routes_geojson.json") as geofile:
    geojson_layer = json.load(geofile)


def create_df_borne(filename):
    if filename == "bornedata.csv":
        df = pd.read_csv(filename,sep=';',na_values = 'nan', encoding="UTF-8")
        borne_dataframe = df.dropna()

        lat = []
        lon = []
        df_tolist = borne_dataframe["Coordonnees"].tolist()

        for coord in df_tolist:
            sp = coord.split(',')
            lat.append(float(sp[0]))
            lon.append(float(sp[1]))

        borne_dataframe["Ylatitude"] = lat
        borne_dataframe["Xlongitude"] = lon
        borne_dataframe = borne_dataframe.rename(columns={"Puissance délivrée":"puiss_max"})
        return borne_dataframe
    
    if filename == "irve_tesla.csv":
        df = pd.read_csv(filename,sep=';', encoding="utf-8")
        borne_dataframe = df.drop(columns="ID_station")
        borne_dataframe = borne_dataframe.rename(columns={"Xlatitude":"Ylatitude"})
        return borne_dataframe
    
    if filename == "irve_ionity.csv":
        df = pd.read_csv(filename,sep=';',na_values = 'nan', encoding="UTF-8")
        borne_dataframe = df.dropna()
        return borne_dataframe


first_borne_data = create_df_borne("bornedata.csv")

fig = go.Figure()
fig.add_trace(
    go.Scattermapbox(
        lat=first_borne_data["Ylatitude"],
        lon=first_borne_data["Xlongitude"],
        mode="markers",
        marker=go.scattermapbox.Marker(
                color=first_borne_data["puiss_max"],
                size=4,
                colorscale="Viridis",
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
        layers=[]
    )
)
fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token, height=700)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children= f'Electrique vehicules',
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

    dcc.Loading(
        id="loading-icon",
        children=[
            html.Div(
                dcc.Graph(
                    id='map',
                    figure=fig
                )
            ),
        ]
    )
])


@app.callback(
        Output(component_id='map', component_property='figure'),
        [Input(component_id='select-charger-type', component_property='value'),
        Input(component_id='routes-checkbox', component_property='value')]
    )
def update_map_figure(input_value,route_show):
    route = route_show
    layer =[]
    if 'routesTrue' in route:
        layer = [
            dict(
                type="line",
                sourcetype="geojson",
                source=geojson_layer,
                color='rgb(255,0,0)',
                opacity=0.3,
            )
        ]

    borne_data = create_df_borne(input_value)
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

