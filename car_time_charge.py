import pandas as pd
import dash_core_components as dcc
import plotly.graph_objects as go
import dash_html_components as html
import dash

file ="electric_vehicules_dataset.csv"
car = pd.read_csv(file,sep=";", encoding="UTF-8")
car=car.sort_values("name")

x=car["name"]
yRange=car["range"]
fig = go.Figure(go.Bar(x =x, y=yRange, name="Autonomie de la voiture"))
    

def carList(car):
    options=[]
    for i in car["name"]:
        options.append({'label':i,'value':i})
    return options

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children= f'Autonomie et temps de recharge des voitures électrique',
    ),
    
    dcc.Dropdown(
    id="selectbox",
    options=carList(car),
    multi=True
    ),

    dcc.Graph(
        id='autonomy',
        figure=fig
    ),
])

app.run_server(debug=True)
