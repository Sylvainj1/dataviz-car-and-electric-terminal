import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_html_components as html
import dash

import scraping_EV_BS as scraping


car = scraping.scrap_EV("https://ev-database.org/compare/efficiency-electric-vehicle-most-efficient")

remove_trailing_space = []

for car_name in car["name"].tolist():
    car_name = car_name.strip()
    remove_trailing_space.append(car_name)

car["name"] = remove_trailing_space

car=car.sort_values("name")
carList=car.set_index("name",inplace=False)

car_time_fig=go.Figure()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children= f'Autonomie et temps de recharge des voitures électriques',
    ),

    html.P(
        "Sélectionner une voiture"
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
])

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
