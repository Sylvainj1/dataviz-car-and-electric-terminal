import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

file ="nombre_total_de_points_de_charge.csv"
borne = pd.read_csv(file,sep=";", encoding="UTF-8")
borne=borne.sort_values(["Trimestre"],ascending=True)

x=borne["Trimestre"]
yParticulier=borne["Particulier"]
ySociete=borne["Société"]
yPublic=borne["Accessible au public"]

fig = go.Figure(go.Bar(x =x, y=ySociete, name='Société'))
fig.add_trace(go.Bar(x=x, y=yParticulier, name='Particulier'))
fig.add_trace(go.Bar(x=x, y=yPublic, name='Accessible au public'))

fig.update_layout(barmode='stack', xaxis={'categoryorder':'category ascending'})
fig.show()