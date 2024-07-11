import streamlit as st

conn = st.connection("pgrouting")

# @st.cache_data
# def getTables(schema, table):
#     ## Load data from an omf table
#     df = conn.query(f"""
#     SELECT e.*
#     FROM {schema}.{table} AS e 
#     ORDER BY e.id""")
    
#     return df

st.radio("Choix",
         options=["test without colon", "Test:It works?", "Test\:It works with backslah?"])