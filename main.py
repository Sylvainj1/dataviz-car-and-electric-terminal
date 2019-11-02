# -*coding:utf8 *-
import json

import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd



import scraping_EV_BS as scraping

import car_evolution

TOKEN = open("mapbox_token").read()



#geojson du tracé des routes principales francaises
#le json de base avait des values inutilisées dans notre cas que nous avons supprimés
#nous avons aussi réduit la précision des coordonnées, tout cela pour allèger la taille du geosjon
#la taille est passé de 3,6 Mo à 1,3 Mo -> le chargement est un poil plus rapide
with open("routes_compress_all.json") as geofile:
    geojson_layer = json.load(geofile)



#création des différentes dataframe necessaires
borne_public = pd.read_csv("bornedata.csv", sep=';', na_values='nan', encoding="UTF-8")
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

borne_power_list = set(borne_public_dataframe["puiss_max"])

#certain nom de columns on été renommés pour une homogénéité entre les df
borne_tesla_partenaire = pd.read_csv("irve_tesla_partenaire.csv", sep=';', encoding="utf-8")
borne_tesla_partenaire_dataframe = borne_tesla_partenaire.drop(columns="ID_station")
borne_tesla_partenaire_dataframe = borne_tesla_partenaire_dataframe.rename(columns={"Xlatitude":"Ylatitude"})

borne_tesla_supercharger = pd.read_csv("irve-tesla-supercharger.csv", sep=';', encoding="utf-8")
borne_tesla_supercharger_dataframe = borne_tesla_supercharger.drop(columns="ID_station")

borne_tesla_dataframe = pd.concat([borne_tesla_partenaire_dataframe, borne_tesla_supercharger_dataframe], ignore_index=True)


borne_ionity = pd.read_csv("irve_ionity.csv", sep=';', na_values='nan', encoding="UTF-8")
borne_ionity_dataframe = borne_ionity.dropna()


def select_dataframe(filename):
    if filename == "bornedata.csv":
        return borne_public_dataframe

    if filename == "irve_tesla.csv":
        return borne_tesla_dataframe

    if filename == "irve_ionity.csv":
        return borne_ionity_dataframe

    return ""




proxyDict = {}

#decommenter ces lignes pour contourner le proxy de l'esiee
# proxy_adress = 'http://147.215.1.189:3128/'

# proxyDict = {
#     "http" : proxy_adress,
#     "https" : proxy_adress
# }


#recupération des données sur les voitures depuis un site web
car = scraping.scrap_EV("https://ev-database.org/compare/efficiency-electric-vehicle-most-efficient", proxy=proxyDict)

remove_trailing_space = []

for car_name in car["name"].tolist():
    car_name = car_name.strip()
    remove_trailing_space.append(car_name)

car["name"] = remove_trailing_space

car = car.sort_values("name")
carList = car.set_index("name", inplace=False)


#figure vide car app.Callback est appelé à l'initialisation de l'appli et créer la figure
#pas besoin donc de créer une figure entière, ici on créer donc une figure vide
fig = go.Figure()
car_time_fig = go.Figure()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div([
        html.H1(
            children=f'Passer au tout électrique ?',
            style={"text-align":"center", "font-family":"Courier New", "color":"#3b61d4"}
        ),
        html.P(
            '''
            Aujourd'hui nous entendons beaucoup parler des voitures électriques, notamment face
            à l'urgence écologique. Mais beaucoup de questions se posent lorsque l'on considère acheter un véhicule electrique :
            Y a t-il assez de chargeurs ? Quel est le temps de charge ? Quelle autonomie dois-je considerer ?
            Est t'il le temps pour vous de passer au tout électrique et laisser votre bon vieux thermique de coté ?''',
            style={"font-family":"Arial", "font-size":18}
        ),
    ]),
    html.Div([
        dcc.Dropdown(
            id='select-charger-type',
            style={"width":300, "font-family":"Arial"},
            options=[
                {'label': 'Tesla Superchargeur & Partenaires Tesla', 'value': "irve_tesla.csv"},
                {'label': 'Ionity Fast chargeur', 'value': 'irve_ionity.csv'},
                {'label': 'Bornes publiques', 'value': "bornedata.csv"},
            ],
            value="bornedata.csv",
            clearable=False
        ),
        dcc.Checklist(
            id='routes-checkbox',
            style={"margin-top": 20, "margin-left": 20, "font-family":"Arial"},
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

    html.P(
        '''
        Les grandes villes Francaises sont plutot bien servie au niveau des bornes de recharges, mais le plus important ici
        est de voir que les grands axes routiers sont très bien desservis. Il est tout a fait possible de partir de Paris pour aller dans le sud
        de la France sans tomber à sec d'essence étant donné que les grandes autoroutes possèdent sur leur chemin de nombreuses borne de recharge.
        Les bornes Tesla et ses partenaires sont très bien placés et permettent au client de la marque de bénéficier des bornes à charge rapide de la marque.
        Le reseaux Ionoty quant à lui est moins developpé en France, néanmoins il a l'avantage de pouvoir charger n'importe quel véhicule, jusqu'à 350 kW
        pour les véhicules le supportant, ce qui permet de charger une voiture comme par exemple une Porsche Taycan en moins de 40min pour 10% à 100%.
        ''',
        style={"font-family":"Arial", "font-size":17}
    ),


    html.Div(children=[
        html.H1(
            children=f'Evolution du nombre de bornes de recharge en France',
            style={"font-family":"Courier New", "margin-top":70}
        ),
        html.P('''
        Le nombre de bornes ne cesse croître pour pouvoir répondre à l'augmentation du nombre de véhicules électriques.
        ''', style={"font-family":"Arial"}),
        dcc.Graph(
            id='car_evolution',
            figure=car_evolution.construct_car_evolution()
        ),
    ]),

    html.Div(children=[
        html.H1(
            children=f'Autonomie et temps de recharge des voitures électriques',
            style={"font-family":"Courier New"}
        ),
        html.Label(
            [
                html.P("Sélectionnez une voiture", style={"font-family":"Arial"}),
                dcc.Dropdown(
                    id="selectbox",
                    style={"width":600, "font-family":"Arial"},
                    options=[{'label': i, 'value': i} for i in car["name"]],
                    multi=True,
                    value=['Audi Q4 e-tron']
                ),
            ]
        ),
        html.Label(
            [
                html.P("Sélectionnez La puissance de la borne en kW", style={"font-family":"Arial"}),
                dcc.Dropdown(
                    id="bornepower",
                    style={"width":300, "font-family":"Arial"},
                    options=[{'label': i, 'value': i} for i in sorted(borne_power_list)],
                    value=3,
                    clearable=False
                ),
            ]
        ),

        dcc.Graph(
            id='autonomy',
            figure=car_time_fig
        ),
    ]),

    html.Div(
        id="data-link",
        style={"font-family":"Arial"},
        children=[
            html.P("Lien vers les jeux de données utilisés : "),
            html.A("Evolution du nombre de points de recharge", href="https://data.enedis.fr/explore/dataset/nombre-total-de-points-de-charge/information/?flg=fr&sort=-trimestre", target="_blank"),
            html.Br(),
            html.A("Data des bornes electriques", href="https://public.opendatasoft.com/explore/dataset/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques-irve/information/?flg=fr", target="_blank"),
            html.Br(),
            html.A("Superchargeur Tesla", href="https://www.data.gouv.fr/fr/datasets/stations-supercharger-tesla/", target="_blank"),
            html.Br(),
            html.A("Partenaires Tesla", href="https://www.data.gouv.fr/fr/datasets/recharge-a-destination-tesla/", target="_blank"),
            html.Br(),
            html.A("Superchargeur Ionity", href="https://www.data.gouv.fr/fr/datasets/stations-de-recharge-ionity/", target="_blank"),
            html.Br(),
            html.A("Reseau routier francais", href="https://www.data.gouv.fr/fr/datasets/bornage-du-reseau-routier-national/", target="_blank"),
            html.P("Données des véhicules electriques scrapés depuis ce lien grâce en utilisant beautiful soup"),
            html.A("Données véhicules electriques", href="https://ev-database.org/compare/newest-upcoming-electric-vehicle", target="_blank"),
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
         Input(component_id='routes-checkbox', component_property='value')]
    )
def update_map_figure(input_value, route_show):
    route = route_show
    layer = []
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
    
    if input_value is None:
        input_value = "bornedata.csv"

    borne_data = select_dataframe(input_value)
    puiss = borne_data["puiss_max"]
    fig = go.Figure()
    fig.add_trace(
        go.Scattermapbox(
            lat=borne_data["Ylatitude"],
            lon=borne_data['Xlongitude'],
            hovertext=puiss,
            hoverinfo='text',
            mode="markers",
            marker=go.scattermapbox.Marker(
                color=borne_data["puiss_max"],
                colorscale="Picnic",
                size=4,
                reversescale=False, #inverse le sens du colorscale
                colorbar=dict(
                    title="Puissance de charge (Kw)",
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

    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=TOKEN, height=700)
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    return fig


@app.callback(
        Output(component_id='autonomy', component_property='figure'),
        [Input(component_id='selectbox', component_property='value'),
         Input(component_id='bornepower', component_property='value'),]
    )
def update_autonomy_figure(input_value, input_borne_power):
    # print(type(float(input_borne_power)))
    x_name = input_value
    y_range = [carList.loc[i, "range"] for i in input_value]
    battery = [float(carList.loc[i, "battery"]) for i in input_value]

    #évite une erreur si l'utilisateur efface la puissance de la borne
    if input_borne_power is None:
        borne_power = 1.0
    else:
        borne_power = float(input_borne_power)

    charge_time = [round(b/borne_power, 2) for b in battery]

    car_time_fig = go.Figure()
    car_time_fig.add_trace(
        go.Bar(
            x=x_name,
            y=y_range,
            text=charge_time,
            hovertext='Temps de recharge en heure',
            hoverinfo='text',
            textfont=dict(
                color="blue",
                size=14
            ),
            textposition="auto",
            # name="Autonomie de la voiture"

            )
    )

    car_time_fig.update_traces(marker_color='rgb(87, 154, 222)', marker_line_color='blue', marker_line_width=1.5, opacity=0.6,)
    car_time_fig.update_layout(
        yaxis_title="Autonomie (en Km)",
    )
    return car_time_fig


app.run_server(debug=True)
