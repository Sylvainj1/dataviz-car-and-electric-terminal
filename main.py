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

import scraping_EV_BS as scraping

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


#certain nom de columns on été renommés pour une homogénéité entre les df
borne_tesla_partenaire = pd.read_csv("irve_tesla_partenaire.csv",sep=';', encoding="utf-8")
borne_tesla_partenaire_dataframe = borne_tesla_partenaire.drop(columns="ID_station")
borne_tesla_partenaire_dataframe = borne_tesla_partenaire_dataframe.rename(columns={"Xlatitude":"Ylatitude"})

borne_tesla_supercharger = pd.read_csv("irve-tesla-supercharger.csv",sep=';', encoding="utf-8")
borne_tesla_supercharger_dataframe = borne_tesla_supercharger.drop(columns="ID_station")

borne_tesla_dataframe = pd.concat([borne_tesla_partenaire_dataframe, borne_tesla_supercharger_dataframe], ignore_index=True)


borne_ionity = pd.read_csv("irve_ionity.csv",sep=';',na_values = 'nan', encoding="UTF-8")
borne_ionity_dataframe = borne_ionity.dropna()


def select_dataframe(filename):
    if filename == "bornedata.csv":
        return borne_public_dataframe

    if filename == "irve_tesla.csv":
        return borne_tesla_dataframe

    if filename == "irve_ionity.csv":
        return borne_ionity_dataframe




proxyDict = {}

#decommenter ces lignes pour contourner le proxy de l'esiee
# proxy_adress = 'http://147.215.1.189:3128/'

# proxyDict = {
#     "http" : proxy_adress,
#     "https" : proxy_adress
# }


#recupération des données sur les voitures depuis un site web
car = scraping.scrap_EV("https://ev-database.org/compare/efficiency-electric-vehicle-most-efficient",proxy=proxyDict)

remove_trailing_space = []

for car_name in car["name"].tolist():
    car_name = car_name.strip()
    remove_trailing_space.append(car_name)

car["name"] = remove_trailing_space

car=car.sort_values("name")
carList=car.set_index("name",inplace=False)



#figure vide car app.Callback est appelé à l'initialisation de l'appli et créer la figure
#pas besoin donc de créer une figure entière, ici on créer donc une figure vide
fig = go.Figure()
car_time_fig=go.Figure()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(
        children= f'Passer au tout électrique ?',
        style={"text-align":"center",}
    ),
    html.P(
        '''
        Aujourd'hui nous entendons beaucoup parler des voitures électriques, notamment face
        à l'urgence écologique. Mais beaucoup de questions se posent lorsque l'on considère acheter un véhicule electrique :
        Y a t-il assez de chargeurs ? Quel est le temps de charge ? Quelle autonomie dois-je considerer ?
        Est t'il le temps pour vous de passer au tout électrique et laisser votre bon vieux thermique de coté ?'''
    ),
    

    ]),
    
    html.Div([
        dcc.Dropdown(
        id='select-charger-type',
        style={"width":300,"display": "inline-block"},
        options=[
            {'label': 'Tesla Superchargeur & Partenaires Tesla', 'value': "irve_tesla.csv"},
            {'label': 'Ionity Fast chargeur', 'value': 'irve_ionity.csv'},
            {'label': 'Bornes publiques', 'value': "bornedata.csv"},
        ],
        value= "bornedata.csv"
    ),
    dcc.Checklist(
        id='routes-checkbox',
        style={"display": "inline-block","margin-left": 60,},
        options=[
            {'label': 'Afficher les routes', 'value': 'routesTrue'}
        ],
        value=[]
    ),

    ]),

    dcc.Graph(
        id='map',
        style={"margin-top":50},
        figure=fig
    ),

    dcc.Graph(
        id='car_evolution',
        figure=car_evolution.construct_car_evolution()
    ),

    html.Div(children=[
        html.H1(
            children= f'Autonomie et temps de recharge des voitures électriques',
        ),

        html.P(
            "Sélectionnez une voiture"
        ),

        dcc.Dropdown(
            id="selectbox",
            options=[{'label': i, 'value': i} for i in car["name"]],
            multi=True,
            value= ['Audi Q4 e-tron']
        ),

        dcc.Graph(
            id='autonomy',
            figure=car_time_fig
        ),
    ]),

    html.Div(
        id="data-link",
        children=[
            html.P("Lien vers les jeux de données utilisés : "),
            html.A("Evolution du nombre de points de recharge", href="https://data.enedis.fr/explore/dataset/nombre-total-de-points-de-charge/information/?flg=fr&sort=-trimestre",target="_blank"),
            html.Br(),
            html.A("Data des bornes electriques", href="https://public.opendatasoft.com/explore/dataset/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques-irve/information/?flg=fr",target="_blank"),
            html.Br(),
            html.A("Superchargeur Tesla", href="https://www.data.gouv.fr/fr/datasets/stations-supercharger-tesla/",target="_blank"),
            html.Br(),
            html.A("Partenaires Tesla", href="https://www.data.gouv.fr/fr/datasets/recharge-a-destination-tesla/",target="_blank"),
            html.Br(),
            html.A("Superchargeur Ionity", href="https://www.data.gouv.fr/fr/datasets/stations-de-recharge-ionity/",target="_blank"),
            html.Br(),
            html.A("Reseau routier francais", href="https://www.data.gouv.fr/fr/datasets/bornage-du-reseau-routier-national/",target="_blank"),
            html.P("Données des véhicules electriques scrapés depuis ce lien grâce en utilisant beautiful soup"),
            html.A("Données véhicules electriques", href="https://ev-database.org/compare/newest-upcoming-electric-vehicle",target="_blank"),
        ]
    ),

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
                colorscale="Picnic",
                size=4,
                reversescale=False, #inverse le sens du colorscale
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


@app.callback(
        Output(component_id='autonomy', component_property='figure'),
        [Input(component_id='selectbox', component_property='value'),]
    )
def update_autonomy_figure(input_value):
    xName=input_value
    yRange=[carList.loc[i,"range"] for i in input_value]
    car_time_fig = go.Figure()
    car_time_fig.add_trace(
        go.Bar(
            x = xName, 
            y=yRange, 
            text= yRange,
            textposition="auto",
            # name="Autonomie de la voiture"

            )
    )
    
    car_time_fig.update_traces(marker_color='rgb(87, 154, 222)', marker_line_color='blue',marker_line_width=1.5, opacity=0.6)
    return car_time_fig


app.run_server(debug=True)

