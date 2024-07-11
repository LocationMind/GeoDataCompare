import geopandas as gpd
import pandas as pd
from shiny import reactive
from shiny.express import input, ui
from shinywidgets import render_widget, reactive_read
import sqlalchemy
import ipywidgets
from lonboard import Map, ScatterplotLayer, PathLayer

def getEngine(database:str,
              host:str="127.0.0.1",
              user:str="postgres",
              password:str="postgres",
              port:str="5432") -> sqlalchemy.engine.base.Engine:
    """Get sqlalchemy engine to connect to the database.
    
    Args:
        database (str): Database to connect to.
        host (str, optional): Ip address for the database connection. The default is "127.0.0.1"
        user (str, optional): Username for the database connection. The default is "postgres".
        password (str, optional): Password for the database connection. The default is "postgres".
        port (str, optional): Port for the connection. The default is "5432".

    Returns:
        sqlalchemy.engine.base.Engine: Engine with the database connection.
    """
    engine = sqlalchemy.create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    return engine

engine = getEngine("pgrouting")

sqlQueryTable = """SELECT table_catalog, table_schema, table_name FROM information_schema.tables AS t
WHERE t.table_schema != 'pg_catalog' AND t.table_schema != 'information_schema'
ORDER BY t.table_schema, t.table_name"""

tables = pd.read_sql_query(sqlQueryTable, engine)

print(type(tables))

tables[["table_schema"]]

tables.to_numpy()
 
# schemas = tables[["table_schema"]].unique()

# schemas

# schemas = pd.unique(tables[["table_schema"]])

# schemas

# ui.input_select("select_schema", "Choose a schema", choices=schemas[["table_schema"]])



@render_widget
def colorPickerPoint():
    color_picker_point = ipywidgets.ColorPicker(concise=True, description='Point color', value='#000000')
    return color_picker_point

@render_widget
def colorPickerLine():
    color_picker_line = ipywidgets.ColorPicker(concise=True, description='Line color', value='#000000')
    return color_picker_line

@render_widget
def map():
    gdf = gpd.GeoDataFrame.from_postgis("SELECT * FROM omf.node_tokyo", engine)
    layer = ScatterplotLayer.from_geopandas(gdf, radius_min_pixels=2)
    gdf_line = gpd.GeoDataFrame.from_postgis("SELECT * FROM omf.edge_with_cost_tokyo", engine)
    line = PathLayer.from_geopandas(gdf_line, width_min_pixels=2)
    return Map([layer, line])


@reactive.effect
def set_fill_color():
    # Point
    # map.widget.layers[0].get_fill_color = colors_point[input.color_select_point()]
    
    hexPoint = reactive_read(colorPickerPoint.widget, "value")
    colorPoint = list(int(hexPoint[i:i+2], 16) for i in (1, 3, 5))
    map.widget.layers[0].get_fill_color = colorPoint
    
    
    # Line
    # map.widget.layers[1].get_fill_color = colors_line[input.color_select_line()]
    
    hexLine = reactive_read(colorPickerLine.widget, "value")
    colorLine = list(int(hexLine[i:i+2], 16) for i in (1, 3, 5))
    map.widget.layers[1].get_color = colorLine