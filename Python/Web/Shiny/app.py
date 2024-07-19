import geopandas as gpd
import pandas as pd
import time
from shiny import reactive
from shiny.express import input, ui, render
from shinywidgets import render_widget, reactive_read
import sqlalchemy
import ipywidgets
import lonboard as lon

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

# Get all 
sqlQueryTable = """SELECT table_catalog, table_schema, table_name FROM information_schema.tables AS t
WHERE t.table_schema != 'pg_catalog' AND t.table_schema != 'information_schema'
-- Remove connector and road tables
AND (t.table_name != 'connector' AND t.table_name != 'road')
ORDER BY t.table_schema, t.table_name"""

tables = pd.read_sql_query(sqlQueryTable, engine)

# schemas = pd.unique(tables["table_schema"]).tolist()

# schemas.sort()

firstDict = tables.groupby('table_schema')['table_name'].apply(list).to_dict()

choicesDict = {}


# We create a new dict with the schema as a key
for schema in firstDict:
    values = firstDict[schema]
    choicesDict[schema] = {}
    # Each schema has its own key, 
    for table in values:
        key = f"{schema}.{table}"
        choicesDict[schema][key] = table

# Multiple select for the layer choices
ui.input_selectize("selectize_table",
                   "Layers",
                   choices=choicesDict,
                   width="100%",
                   multiple=True)

# with ui.layout_columns():
#     ui.input_select("select_schema", "Schema", choices=schemas, width="100%")
    
#     ui.input_select("select_table", "Table", choices=[], width="100%", multiple=True)

@reactive.effect
def updateSelectTable():
    result = tables[tables["table_schema"] == input.select_schema()]["table_name"].to_list()

    result.sort()
    ui.update_select("select_table",
                     label= f"Tables for {input.select_schema()} schema",
                     choices=result)

with ui.layout_columns():
    @render_widget
    def colorPickerPoint():
        color_picker_point = ipywidgets.ColorPicker(concise=True, description='Point color', value='#000000')
        return color_picker_point

    @render_widget
    def colorPickerLine():
        color_picker_line = ipywidgets.ColorPicker(concise=True, description='Line color', value='#000000')
        return color_picker_line


radiusMinPixels = 2
widthMinPixels = 2

dictTablenameLayer = reactive.value({})

ui.input_checkbox_group(
    "checkbox_group",
    "Layers",
    choices = {}
)

@render_widget
@reactive.event(input.selectize_table)
def map():
    layers = []
    dictTablenameLayer.set({})
    dictSet = {}
    for tableName in input.selectize_table():
        gdf = gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {tableName}", engine)
        layer = None
        # Check the geometry type 
        if gdf.geom_type.iloc[0] == 'Point':
            layer = lon.ScatterplotLayer.from_geopandas(gdf, radius_min_pixels = radiusMinPixels)
        elif gdf.geom_type.iloc[0] == 'LineString':
            layer = lon.PathLayer.from_geopandas(gdf, width_min_pixels = widthMinPixels)
        
        # If the layer has been created, we add it to the map
        if layer != None:
            layers.append(layer)
            dictSet[tableName] = layer
    
    dictTablenameLayer.set(dictSet)
    return lon.Map(layers = layers)

@reactive.effect
@reactive.event(input.selectize_table)
def updateChecboxGroup():
    
    print("Selectize table - update checbox group")
    print(input.selectize_table())
    ui.update_checkbox_group("checkbox_group",
                             choices=input.selectize_table(),
                             selected=list(input.selectize_table()))

@reactive.effect
@reactive.event(input.checkbox_group)
def updateCheckoxes():
    elements = []
    
    print("Checkbox group - updates checkbox")
    print(input.checkbox_group())
    
    for tableName in input.checkbox_group():
        layer = dictTablenameLayer()[tableName]
        
        layer.visible = True
        
        checkbox = ipywidgets.Checkbox(
            value=True,
            description=tableName,
            disabled=False,
            indent=False
        )
        
        ipywidgets.dlink(
            (checkbox, 'value'),
            (layer, 'visible')
        )
        
        
    
    # checkboxesLayers.widget.children = tuple(elements)

# @reactive.effect
# def setFillColor():
#     # Point
#     # map.widget.layers[0].get_fill_color = colors_point[input.color_select_point()]
    
#     hexPoint = reactive_read(colorPickerPoint.widget, "value")
#     colorPoint = list(int(hexPoint[i:i+2], 16) for i in (1, 3, 5))
#     map.widget.layers[0].get_fill_color = colorPoint
    
    
#     # Line
#     # map.widget.layers[1].get_fill_color = colors_line[input.color_select_line()]
    
#     hexLine = reactive_read(colorPickerLine.widget, "value")
#     colorLine = list(int(hexLine[i:i+2], 16) for i in (1, 3, 5))
#     map.widget.layers[1].get_color = colorLine

@render.text
def selectizeTables():
    return input.selectize_table()

