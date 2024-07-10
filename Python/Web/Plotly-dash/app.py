# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import shapely
import numpy as np
import time

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Python import utils

start = time.time()

def getData(schema, table, con):
    sql = f"""
        SELECT e.id, e.source, e.target, e.class, e.geom
        FROM {schema}.{table} AS e 
        ORDER BY e.id"""
    
    df = gpd.read_postgis(sql, con)
    
    return df
    
# Connect to the database
connection = utils.getEngine("pgrouting")

# Incorporate data
gdf = getData('omf', 'edge_with_cost_tateyama', connection)

gdfProj = gdf.to_crs(6691)
    
gdf['length'] = gdfProj['geom'].length / 1000

gdfSumup = gdf[['class', 'length']].groupby('class')['length'].agg(['sum', 'count'])

# Initialize the app
app = Dash()

# Map
fig = go.Figure()
fig.add_trace(go.Scattermapbox())

source = "http://localhost:8080/geoserver/test/wms?SERVICE=WMS&VERSION=1.1.0&request=GetMap&layers=test:{}&bbox={{bbox-epsg-3857}}&width=256&height=256&TRANSPARENT=True&crs=EPSG:3857&styles=&format=image/png"

layerName = "edge_with_cost_tokyo"

# Set parameters
fig.update_layout(
    mapbox = {
        'center': {'lon': 139.7912, 'lat': 35.7327},
        'zoom': 15,
        'style': "open-street-map",
        },
    width=600,
    height=600,
    mapbox_layers=[
        {
            "sourcetype": "raster",
            "sourceattribution": "OvertureMap Fundation",
            "source":[source.format(layerName)]
        }]
    )

fig.update_layout(margin ={'l':0,'t':0,'b':0,'r':0})

# App layout
app.layout = [
    html.Div(children='My First App with Data, Graph, and Controls'),
    dash_table.DataTable(data=gdf.drop(columns=['geom']).to_dict('records'), page_size=10),
    dcc.Graph(figure=fig)
]

end = time.time()
print(f"It took {end - start} seconds")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)