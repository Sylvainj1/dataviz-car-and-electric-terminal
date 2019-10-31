import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_html_components as html
import dash

file ="electric_vehicules_dataset.csv"
car = pd.read_csv(file,sep=";", encoding="UTF-8")
remove_trailing_space = []

for car_name in car["name"].tolist():
    car_name = car_name.strip()
    remove_trailing_space.append(car_name)

car["name"] = remove_trailing_space

car=car.sort_values("name")
carList=car.set_index("name",inplace=False)

fig=go.Figure()

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
        figure=fig
    ),
])

@app.callback(
        Output(component_id='autonomy', component_property='figure'),
        [Input(component_id='selectbox', component_property='value'),]
    )
def update_autonomy_figure(input_value):
    xName=input_value
    yRange=[carList.loc[i,"range"] for i in input_value]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x = xName, 
            y=yRange, 
            text= yRange,
            textposition="auto",
            # name="Autonomie de la voiture"

            )
    )
    
    fig.update_traces(marker_color='rgb(119,136,153)', marker_line_color='rgb(112,128,144)',marker_line_width=1.5, opacity=0.6)
    return fig


app.run_server(debug=True)
