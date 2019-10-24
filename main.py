# -*coding:utf8 *-
import plotly_express as px
import plotly
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd


filename = "bornedata.csv"
df = pd.read_csv(filename,sep=';',na_values = 'nan')
borne_dataframe = df.dropna()

lat = []
lon = []
df_tolist = borne_dataframe["Coordonnees"].tolist()

for coord in df_tolist:
    sp = coord.split(',')
    lat.append(float(sp[0]))
    lon.append(float(sp[1]))

borne_dataframe["lat"] = lat
borne_dataframe["lon"] = lon


fig = px.scatter_mapbox(borne_dataframe, lat="lat", lon="lon", hover_name="Aménageur",color="Puissance délivrée",
                        color_discrete_sequence=["blue"], zoom=5)
fig.update_layout(mapbox_style="open-street-map",)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

