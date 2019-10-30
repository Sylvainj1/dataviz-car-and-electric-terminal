import pandas as pd
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_html_components as html
import dash

file ="electric_vehicules_dataset.csv"
car = pd.read_csv(file,sep=";", encoding="UTF-8")
car=car.sort_values("name")
carList=car.set_index("name",inplace=False)

fig=go.Figure()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children= f'Autonomie et temps de recharge des voitures électriques',
    ),
    
    dcc.Dropdown(
    id="selectbox",
    options=[{'label': i, 'value': i} for i in car["name"]],
    multi=True,
    value= 'Lightyear One '
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
    xName=[]
    xName.append(input_value)
    yRange=[carList.loc[input_value]["range"] for i in carList]
    
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x = xName, 
            y=yRange, 
            name="Autonomie de la voiture")
    )
    return fig


app.run_server(debug=True)
