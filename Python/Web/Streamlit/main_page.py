import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import leafmap.foliumap as foliumap
import plotly.graph_objects as go
import streamlit as st
from owslib.wms import (WebMapService, wms111, wms130)

# conn = st.connection("pgrouting")

# @st.cache_data
# def load_data(schema, table):
#     ## Load data from an omf table
#     df = conn.query(f"""
#     SELECT e.*
#     FROM {schema}.{table} AS e 
#     ORDER BY e.id""")
    
#     return df

# @st.cache_data
# def load_data_gdf(schema, table, _con):
#     ## Load data from an omf table
#     sql = f"""
#     SELECT e.*
#     FROM {schema}.{table} AS e 
#     ORDER BY e.id"""
    
#     try:
#         gdf = leafmap.read_postgis(sql, _con)
#     except:
#         pass
    
#     return gdf



# def app():
    
#     st.title('Test Streamlit - OSM and OMF comparison')

#     st.write("welcome to the main page")

    
#     layerName = "edge_with_cost_tokyo"

#     con = leafmap.connect_postgis(
#             database="pgrouting", host="127.0.0.1", user='postgres', password='postgres', port=5432
#         )
    
#     col1, col2 = st.columns(2)

    
#     st.write("OSM Roads")
#     gdfOSM = load_data_gdf('osm', layerName, con)
    
#     gdfOSMProj = gdfOSM.to_crs(6691)
    
#     gdfOSM['length'] = gdfOSMProj['geom'].length / 1000
    
#     gdf = gdfOSM[['class', 'length']].groupby('class')['length'].agg(['sum', 'count'])
    
#     gdf
    
#     st.bar_chart(gdf)


#     st.write("OMF Roads")
#     gdfOMF = load_data_gdf('omf', layerName, con)
    
#     gdfOMFProj = gdfOMF.to_crs(6691)
    
#     gdfOMF['length'] = gdfOMFProj['geom'].length / 1000
    
#     gdf = gdfOMF[['class', 'length']].groupby('class')['length'].agg(['sum', 'count'])
    
#     gdf
    
#     st.bar_chart(gdf)
        

# app()

st.set_page_config(layout="wide")


def app():

    url = st.text_input(
        "Enter a WMS URL:", value="http://localhost:8080/geoserver/test/wms?"
    )
    empty = st.empty()

    if url:
        try:
            wms = WebMapService(url)
            
            options = list(wms.contents)
            
            layers = empty.multiselect(
                "Select WMS layers to add to the map:", options
            )
            
            fig = go.Figure()
            fig.add_trace(go.Scattermapbox())
            
            mapURL = wms.getOperationByName('GetMap').methods[0]['url']
            version = wms.identification.version

            source = "{}&VERSION={}&request=GetMap&layers={}&bbox={{bbox-epsg-3857}}&width=256&height=256&TRANSPARENT=True&crs=EPSG:3857&format=image/png"

            # Set parameters
            fig.update_layout(
                margin ={'l':0,'t':0,'b':0,'r':0},
                mapbox = {
                    'center': {'lon': 139.7912, 'lat': 35.7327},
                    'zoom': 10,
                    'style': "open-street-map",
                    },
                width=600,
                height=600)
            
            m = foliumap.Map(center=(35.7327, 139.7912), zoom=10)
            
            if layers is not None:
                mapbox_layers = []
                for layer in layers:
                    
                    # Mapbox version
                    layerSource = source.format(mapURL, version, layer)
                    
                    mapbox_layers.append(
                        {
                            "sourcetype": "raster",
                            "name":layer,
                            "sourceattribution": "OvertureMap Fundation",
                            "source":[layerSource]
                        })
                    
                    fig.update_layout(mapbox_layers=mapbox_layers)
                    
                    # LeafMap version
                    m.add_wms_layer(
                            url, layers=layer, name=layer, attribution="OvertureMap Fundation", transparent=True
                    )
                    
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.title("Figure Plotly")
                st.plotly_chart(fig)
            
            with col2:
                st.title("Figure Leafmap")
                m.to_streamlit()
                
        except:
            st.error("The url is not valid, no WMS layers could be added")

app()