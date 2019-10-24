# -*coding:utf8 *-
import plotly_express as px
import plotly
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd



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

fig = px.scatter_mapbox(
    first_borne_data,
    lat="Ylatitude",
    lon="Xlongitude",
    hover_name="Ylatitude",
    # hover_data=["Puissance délivrée","Type de prise","Condition d'accès"],
    # color="Puissance délivrée",
    color_continuous_scale=px.colors.sequential.YlOrRd,
    zoom=5
    )
fig.update_layout(mapbox_style="open-street-map")
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

    dcc.Graph(
        id='map',
        figure=fig
    )
])


@app.callback(
        Output(component_id='map', component_property='figure'),
        [Input(component_id='select-charger-type', component_property='value')]
    )
def update_map_figure(input_value):
    borne_data = create_df_borne(input_value)
    fig = px.scatter_mapbox(
        borne_data,
        lat="Ylatitude",
        lon="Xlongitude",
        hover_name="Ylatitude",
        # hover_data=["Puissance délivrée","Type de prise","Condition d'accès"],
        # color="Puissance délivrée",
        color_continuous_scale=px.colors.sequential.YlOrRd,
        zoom=5
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


app.run_server(debug=True)

