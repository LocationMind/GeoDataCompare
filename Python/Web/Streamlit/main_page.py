import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import shapely
import leafmap
import leafmap.foliumap as foliumap


conn = st.connection("pgrouting")

@st.cache_data
def load_data(schema, table):
    ## Load data from an omf table
    df = conn.query(f"""
    SELECT e.*
    FROM {schema}.{table} AS e 
    ORDER BY e.id""")
    
    return df

@st.cache_data
def load_data_gdf(schema, table, _con):
    ## Load data from an omf table
    sql = f"""
    SELECT e.*
    FROM {schema}.{table} AS e 
    ORDER BY e.id"""
    
    try:
        gdf = leafmap.read_postgis(sql, _con)
    except:
        pass
    
    return gdf



def app():
    
    st.title('Test Streamlit - OSM and OMF comparison')

    st.write("welcome to the main page")

    
    layerName = "edge_with_cost_tokyo"

    con = leafmap.connect_postgis(
            database="pgrouting", host="127.0.0.1", user='postgres', password='postgres', port=5432
        )
    
    col1, col2 = st.columns(2)

    
    st.write("OSM Roads")
    gdfOSM = load_data_gdf('osm', layerName, con)
    
    gdfOSMProj = gdfOSM.to_crs(6691)
    
    gdfOSM['length'] = gdfOSMProj['geom'].length / 1000
    
    gdf = gdfOSM[['class', 'length']].groupby('class').agg('sum', 'count')
    
    gdf
    
    st.bar_chart(gdf)


    st.write("OMF Roads")
    gdfOMF = load_data_gdf('omf', layerName, con)
    
    gdfOMFProj = gdfOMF.to_crs(6691)
    
    gdfOMF['length'] = gdfOMFProj['geom'].length / 1000
    
    gdf = gdfOMF[['class', 'length']].groupby('class').agg('sum')
    
    st.bar_chart(gdf)
        

app()
