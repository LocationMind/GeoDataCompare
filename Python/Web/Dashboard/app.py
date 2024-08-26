import geopandas as gpd
import pandas as pd
import faicons as fa
from shiny import reactive
from shiny.express import input, ui, render
from shinywidgets import render_widget, reactive_read
import sqlalchemy
import ipywidgets
import lonboard as lon
from pathlib import Path
from lonboard.colormap import apply_categorical_cmap
from matplotlib.colors import is_color_like, to_hex, to_rgb
from dotenv import load_dotenv
import numpy as np
import os
import utm
import shapely


### Static functions used in the rest of the script ###
def getEngine() -> sqlalchemy.engine.base.Engine:
    """Get engine from .env file.
    This file must be in the same folder than the app.py script.

    Returns:
        sqlalchemy.engine.base.Engine:
        Engine used for (geo)pandas sql queries.
    """
    # Create .env path
    dotenv_path =  Path(__file__).parent / ".env"
    
    # Read environnment variables
    load_dotenv(dotenv_path)
    
    database = os.getenv("POSTGRES_DATABASE")
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    port = os.getenv("POSTGRES_PORT")
    
    # Create engine
    engine = sqlalchemy.create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    return engine


def getAllAreas(engine:sqlalchemy.engine.base.Engine,
                tableName:str = "bounding_box",
                schema:str = "public") -> gpd.GeoDataFrame:
    """Get all areas stored in the `bounding_box` table.
    Calculate the area in km2 of each in the same time.

    Args:
        engine (sqlalchemy.engine.base.Engine):
        Engine used for (geo)pandas sql queries.
        tableName (str, optional): Name of the table. Defaults to "bounding_box".
        schema (str, optional): Name of the schema. Defaults to "public".

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with all entries in the table.
    """
    # Get all the entity from bounding box table
    sqlQueryTable = f"""SELECT *, ST_Area(geom::geography) / 1000000 AS area FROM {schema}.{tableName};"""
    
    bounding_box = gpd.GeoDataFrame.from_postgis(sqlQueryTable, engine)
    
    return bounding_box


def getNbRowTable(engine:sqlalchemy.engine.base.Engine,
                  tableName:str) -> str:
    """Get the number of elements in a table directly store in PostgreSQL.

    Args:
        engine (sqlalchemy.engine.base.Engine):
        Engine used for (geo)pandas sql queries.
        tableName (str, optional): Name of the table
        (with the schema already on it).

    Returns:
        str: Number of entity in the table.
    """
    # Get all the entity from bounding box table
    sqlQueryTable = f"""SELECT count(*) as nb FROM {tableName};"""
    
    result = pd.read_sql(sqlQueryTable, engine)
    
    # Take the first element of the result
    number = result.iloc[0,0]
    
    return str(number)


def getDataFrameGraph(gdf:gpd.GeoDataFrame,
                      crs:int,
                      columnType:str = None) -> pd.DataFrame:
    """Return the dataframe to display for the graph theme.
    It corresponds to the length and number of edges per classes

    Args:
        gdf (gpd.GeoDataFrame): edges GeoDataFrame.
        crs (int): crs to use for the calculation.
        columnType (str, optional): Type of the column to aggregate on.
        Only used in getDataFramePlaces function.
        Default value is None.

    Returns:
        pd.DataFrame: Dataframe with values for each classes
    """
    # Copy the DataFrame to prevent problems
    gdfCopy = gdf.copy()
    # If it is empty, create an empty DataFrame
    if gdfCopy.empty:
        gdfSumup = pd.DataFrame()
    else:
        # Set geometry column and project to another crs
        gdfCopy = gdfCopy.set_geometry("geom")
        gdfProj = gdfCopy.to_crs(crs)
        
        # Calculate length based on the projected geometry in km
        gdfCopy['length'] = gdfProj['geom'].length / 1000
        
        # Agregate per class and calculate the sum and count for each class
        gdfSumup = gdfCopy[['class', 'length']].groupby('class', dropna = False)['length'].agg(['sum', 'count'])
        
        # Reset index to export class
        gdfSumup.reset_index(inplace=True)
    
    return gdfSumup


def getDataFrameBuilding(gdf:gpd.GeoDataFrame,
                         crs:int) -> pd.DataFrame:
    """Return a DataFrame with length and number of edges per classes.

    Args:
        gdf (gpd.GeoDataFrame): edge GeoDataFrame

    Returns:
        pd.DataFrame: Dataframe with values for each classes
    """
    # Copy the DataFrame to prevent problems
    gdfCopy = gdf.copy()
    # If it is empty, create an empty DataFrame
    if gdfCopy.empty:
        gdfSumup = pd.DataFrame()
    else:
        # Set geometry column and project to another crs
        gdfCopy = gdfCopy.set_geometry("geom")
        gdfProj = gdfCopy.to_crs(crs)
        
        # Calculate area based on the projected geometry in km
        gdfCopy['area'] = gdfProj['geom'].area / 1000000
        
        # Agregate per class and calculate the sum and count for each class
        gdfSumup = gdfCopy[['class', 'area']].groupby('class', dropna = False)['area'].agg(['sum', 'count'])
        
        # Reset index to export class
        gdfSumup.reset_index(inplace=True)
    
    return gdfSumup


def getDataFramePlace(gdf:gpd.GeoDataFrame,
                      crs:int) -> pd.DataFrame:
    """Return a DataFrame with length and number of edges per classes.

    Args:
        edgeGDF (gpd.GeoDataFrame): edge GeoDataFrame

    Returns:
        pd.DataFrame: Dataframe with values for each classes
    """
    # Copy the DataFrame to prevent problems
    gdfCopy = gdf.copy()
    # If it is empty, create an empty DataFrame
    if gdfCopy.empty:
        gdfSumup = pd.DataFrame()
    
    else:
        # Set geometry column and project to another crs
        gdfCopy = gdfCopy.set_geometry("geom")
        
        # Check first value not null of categories
        value = gdfCopy[gdfCopy['categories'].notnull()]["categories"].iloc[0]
        
        # If it is a dictionnary, it is OMF dataset. We take the main category
        if type(value) == dict:
            gdfCopy['category'] = gdfCopy['categories'].apply(lambda categories: categories['main'] if (categories is not None) else None)
        # Otherwise, we rename the column to 'category'
        else:
            gdfCopy = gdfCopy.rename(columns = {'categories':'category'})
        
        # Agregate per categories and calculate the sum and count for each category
        gdfSumup = gdfCopy[['category']].groupby('category', dropna = False)['category'].agg(['size'])
        
        # Reset index to export class
        gdfSumup.reset_index(inplace=True)
        
        # Replace NaN value by 'Null'
        gdfSumup = gdfSumup.fillna('Null')
    
    return gdfSumup


def getTotalLength(gdf:gpd.GeoDataFrame) -> str:
    """Get indicator value for base layer.
    Sum up the distance from the dataframe of length per class.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame of length per class.

    Returns:
        str: Value of the indicator.
    """
    # Check if the dataframe is empty
    if gdf.empty:
        value = ""
    else:
        value = round(gdf["sum"].sum())
    return str(value)


def getCoverage(gdf:gpd.GeoDataFrame,
                area:str) -> str:
    """Get buildings coverage of the area.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame of length per class.
        area (str): Name of the area.

    Returns:
        str: Value of the indicator.
    """
    # Copy the GeoDataFrame to prevent error
    gdfCopy = gdf.copy()
    
    # Missing value if the GeoDataFrame is empty
    if gdfCopy.empty:
        value = ""
    
    else:
        # Set geometry column
        gdfCopy = gdfCopy.set_geometry("geom")
        
        # Get crs for the area and project to this crs
        crs = areasCRS[area]
        gdfProj = gdfCopy.to_crs(crs)
        
        # Calculate area based on the projected geometry in km
        gdfCopy['area'] = gdfProj['geom'].area
        
        # Get area in km2 of the area
        areaKm2 = bounding_box_gdf[bounding_box_gdf["name"] == area]["area"].iloc[0]
        
        # Calculate the sum of the buildings area in km2
        buildingsArea = gdfCopy["area"].sum() / 1000000
        
        # Calculate the coverage
        value = f"{round((buildingsArea / areaKm2), 2)} %"
    
    return str(value)


def getDensity(gdf:gpd.GeoDataFrame,
               area:str) -> str:
    """Get indicator value for base layer.
    Sum up the distance from the dataframe of length per class.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame of length per class.
        area (str): Name of the area.

    Returns:
        str: Value of the indicator.
    """
    # Missing value if the GeoDataFrame is empty
    if gdf.empty:
        value = ""
    
    else:
        # Get number of POI
        number = gdf.shape[0]
        
        # Get area in km2 of the area
        areaKm2 = bounding_box_gdf[bounding_box_gdf["name"] == area]["area"].iloc[0]
        
        # Calculate the density
        value = f"{round((number / areaKm2), 2)} / km2"
    
    return str(value)


def getGroupByComp(gdf:gpd.GeoDataFrame,
                   column:str = "component") -> str:
    """Get indicator value for (strongly) connected components criterion.
    Aggregate the GeoDataFrame on the given column and count the number
    of aggregation.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame for the criterion.
        column (str, optional): Name of the column to aggregate on.
        Defaults to "component".

    Returns:
        str: Value of the indicator.
    """
    # Missing value if the GeoDataFrame is empty
    if gdf.empty:
        value = ""

    else:
        # Aggregate on the column and count the number of aggregation
        gdfSumup = gdf[[column]].groupby(column, dropna = False)[column].agg(['count'])
        
        # Reset index and take the number
        gdfSumup.reset_index(inplace=True)
        value = gdfSumup.shape[0]
    
    return str(value)
    

def getNbElem(gdf:gpd.GeoDataFrame,
              column:str = "intersects") -> str:
    """Get indicator value for isolated nodes criterion.
    Aggregate the GeoDataFrame on the given column and count the number
    of row that do not intersects.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame for the criterion.
        column (str, optional): Name of the column to aggregate on.
        Defaults to "intersects".

    Returns:
        str: Value of the indicator.
    """
    # Missing value if the GeoDataFrame is empty
    if gdf.empty:
        value = ""

    else:
        # Aggregate on the column and count the number of aggregation
        gdfSumup = gdf[[column]].groupby(column, dropna = False)[column].agg(['count'])
        
        # Reset index
        gdfSumup.reset_index(inplace=True)
        value = 0
        
        for _, row in gdfSumup.iterrows():
            # Take the number of nodes that do not intersects
            if row[column] == False:
                value = row['count']
    
    return str(value)


def getOverlapIndicator(gdf:gpd.GeoDataFrame,
                        area:str,
                        column:str = "overlap") -> str:
    """Get indicator value for the overlap indicator criterion.
    Calculate the total length of overlapping roads and return
    the proportion of length overlapping over the total length.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame for the criterion.
        area (str): Name of the area.
        column (str, optional): Name of the column to aggregate on.
        Defaults to "overlap".

    Returns:
        str: Value of the indicator.
    """
    # Copy the GeoDataFrame to prevent error
    gdfCopy = gdf.copy()

    # Missing value if the GeoDataFrame is empty
    if gdfCopy.empty:
        value = ""
        
    else:
        # Set geometry column
        gdfCopy = gdfCopy.set_geometry("geom")
        
        # Get crs for the area and project to this crs
        crs = areasCRS[area]
        gdfProj = gdfCopy.to_crs(crs)
        
        # Calculate length based on the projected geometry in km
        gdfCopy['length'] = gdfProj['geom'].length / 1000
        
        # Agregate per class and calculate sum for each class
        gdfSumup = gdfCopy[[column, 'length']].groupby(column, dropna = False)['length'].agg(['sum'])
        
        # Reset index to export class
        gdfSumup.reset_index(inplace=True)
        
        # Get overlapping length and total length
        overlapLength = 0
        totalLength = 0
        
        for _, row in gdfSumup.iterrows():
            if row[column] == True:
                overlapLength = row['sum']
            totalLength += row['sum']
        
        # Calculate the proporion in %
        value = round((overlapLength / totalLength) * 100, 2)
        value = f"{value} %"
    
    return str(value)


def getCorrespondingNodes(gdf:gpd.GeoDataFrame,
                          column:str = "intersects") -> str:
    """Get indicator value for the corresponding nodes criterion.
    Calculate the total number of corresponding nodes and return
    a string with this number and the proportion of corresponding
    nodes in the dataset.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame for the criterion.
        column (str, optional): Name of the column to aggregate on.
        Defaults to "intersects".

    Returns:
        str: Value of the indicator.
    """
    # Copie the GeoDataFrame to prevent error
    if gdf.empty:
        value = ""

    else:
        # Aggregate on the column and count the number of rows
        gdfSumup = gdf[[column]].groupby(column, dropna = False)[column].agg(['count'])
        
        # Reset index
        gdfSumup.reset_index(inplace=True)
        
        # Get number of corresponding nodes and number of total nodes
        totalNodes = 0
        correspondingNodes = 0
        for _, row in gdfSumup.iterrows():
            if row[column] == True:
                correspondingNodes = row['count']
            totalNodes += row['count']
        
        # Calculate proportion and create string value
        percentage = round((correspondingNodes / totalNodes) * 100, 2)
        value = f"{correspondingNodes} - {percentage} %"
    
    return str(value)


def getColorFromColorPicker(
    widgetName:render_widget[ipywidgets.ColorPicker]) -> list[int, int, int]:
    """Get color from color picker and convert it to a RGB list.

    Args:
        widgetName (render_widget[ipywidgets.ColorPicker]):
        Name of the color picker widget.

    Returns:
        list[int, int, int]: RGB values stores as a list.
    """
    # Read value
    hex = reactive_read(widgetName.widget, "value")
    
    # Transforme value to a RGB list by reading value as int in base 16
    color = list(int(hex[i:i+2], 16) for i in (1, 3, 5))
    return color


def hexToRgb255(hex:str) -> list[int, int, int]:
    """Convert a hew value (str) to a list of RGB values.
    Each value is an integer between 0 and 255.

    Args:
        hex (str): hex value

    Returns:
        list[int, int, int]: RGB Values between 0 and 255.
    """
    rgb = to_rgb(hex)
    return [int (255 * x) for x in rgb]


def getColorComponents(cardinality:int,
                       data:list) -> list[int, int, int]:
    """Get color for components layers.

    Args:
        cardinality (int): Cardinality of the component.
        data (list): List representing the component DataFrame.

    Returns:
        list[int, int, int]: Color as a RGB list values.
    """
    # First color
    if data[0][0] <= cardinality <= data[0][1]:
        color = data[0][2]
    # Second color
    if data[1][0] <= cardinality <= data[1][1]:
        color = data[1][2]
    # Third color
    if data[2][0] <= cardinality <= data[2][1]:
        color = data[2][2]
    # Last color
    else:
        color = data[3][2]
    return color


def getAreasCRS(gdf:gpd.GeoDataFrame,
                columnName:str = "name") -> dict[str, int]:
    """Get UTM projection from a gdf

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame from bounding box table.

    Returns:
        dict[str, int]: UTM projection for each areas, in a dict form.
    """
    # Get copy of the geodataframe 
    gdfCopy = gdf.copy()
    
    # Get centroid of all geometries
    gdfCopy["centroid"] = gdfCopy["geom"].centroid
    
    # Calculate crs from all centroid
    gdfCopy["crs"] = gdfCopy['centroid'].apply(getUTMProj, lambda point: utm.from_latlon(point.y, point.x))
    
    dictCRS = gdfCopy.set_index(columnName)["crs"].to_dict()
    
    return dictCRS
    

def getUTMProj(point: shapely.Point) -> int:
    """Get UTM projection for a specific point

    Args:
        point (shapely.Point): Point representing the centroid of the geometry.

    Returns:
        int: UTM projection crs id
    """
    # Get zone number
    zone = utm.from_latlon(point.y, point.x)[2]
    
    # Return formatted string
    epsgCode = f"326{zone:02d}" if point.y >= 0 else f"327{zone:02d}"
    
    return int(epsgCode)


def setMapState(view_state:dict,
                map:lon.Map):
    """Set a view state for a map.

    Args:
        view_state (_type_): View state of the map
        map (lon.Map): Map to set the view state
    """
    # Set view state of OSM map
    map.set_view_state(
        longitude = view_state.longitude,
        latitude = view_state.latitude,
        zoom = view_state.zoom,
        pitch = view_state.pitch,
        bearing = view_state.bearing)


### Variables used in the application ###

## Constant values ##

# Engine for geodatframe query
engine = getEngine()

# Variable for the map rendering
radiusMinPixels = 2
widthMinPixels = 2

# Dict of the different criterion (group by theme) 
quality_criteria_choices = {
    "Graph" : {
        "base":"Original dataset",
        "conn_comp":"Connected components",
        "strongly_comp":"Strongly connected components",
        "isolated_nodes":"Isolated nodes",
        "overlap_indicator":"Overlap indicator",
        "corresponding_nodes":"Corresponding nodes",
    },
    "Building" : {
        "buildings":"Buildings (coverage)",
        "buildings_density":"Buildings (density)",
    },
    "Place" : {
        "places":"Places / Points of interest (density)",
    }
}

# Construct the quality_criteria variable from the choices
quality_criteria = {}

# Dict that link each criterion with a theme (Graph, Building or Place)
criteria_theme = {}

for theme in quality_criteria_choices:
    for elem in quality_criteria_choices[theme]:
        quality_criteria[elem] = quality_criteria_choices[theme][elem]
        criteria_theme[elem] = theme


# Put a function for each theme
theme_function = {
    "Graph":getDataFrameGraph,
    "Building":getDataFrameBuilding,
    "Place":getDataFramePlace,
}

# Dataframe header per theme
theme_dataframe_header = {
    "Graph":"Number of edges and total length (in km) per class in {}",
    "Building":"Number of buildings and total area (in km2) per class in {}",
    "Place":"Number of places per category in {}",
}

# Name of the columns to rename per theme
theme_column_names = {
    "Graph":{
        "class":"Class",
        "sum": "Total length (km)",
        "count":"Number of edges",
    },
    "Building":{
        "class":"Class",
        "sum": "Total area (km2)",
        "count":"Number of buildings",
    },
    "Place":{
        "category":"Category",
        "size":"Number of places",
    },
}

# Base layers per theme
theme_template_layer = {
    "Graph": {
        "OSM" : "osm.edge_with_cost_{}",
        "OMF" : "omf.edge_with_cost_{}",
    },
    "Building": {
        "OSM" : "osm.building_{}",
        "OMF" : "omf.building_{}",
    },
    "Place": {
        "OSM" : "osm.place_{}",
        "OMF" : "omf.place_{}",
    },
}

# Dict of the criterion to display (for the card)
quality_criteria_display = {
    "":"Criteria display",
    "base":"Total length (km)",
    "buildings":"Buildings coverage (%)",
    "buildings_density":"Density of buildings (nb / km2)",
    "places":"Density of POI (nb / km2)",
    "conn_comp":"Number of connected components",
    "strongly_comp":"Number of strongly connected components",
    "isolated_nodes":"Number of isolated nodes",
    "overlap_indicator":"Overlap indicator (%)",
    "corresponding_nodes":"Corresponding nodes (Total number - %)",
}

# Template name of layers per criterion
template_layers_name = {
    "base": {
        "OSM" : [("osm.edge_with_cost_{}", lon.PathLayer), ("osm.node_{}", lon.ScatterplotLayer)],
        "OMF" : [("omf.edge_with_cost_{}", lon.PathLayer), ("omf.node_{}", lon.ScatterplotLayer)],
    },
    "buildings": {
        "OSM" : [("osm.building_{}", lon.PolygonLayer)],
        "OMF" : [("omf.building_{}", lon.PolygonLayer)],
    },
    "buildings_density": {
        "OSM" : [("osm.building_{}", lon.PolygonLayer)],
        "OMF" : [("omf.building_{}", lon.PolygonLayer)],
    },
    "places": {
        "OSM" : [("osm.place_{}", lon.ScatterplotLayer)],
        "OMF" : [("omf.place_{}", lon.ScatterplotLayer)],
    },
    "conn_comp": {
        "OSM" : [("results.connected_components_{}_osm", lon.ScatterplotLayer), ("osm.edge_with_cost_{}", lon.PathLayer)],
        "OMF" : [("results.connected_components_{}_omf", lon.ScatterplotLayer), ("omf.edge_with_cost_{}", lon.PathLayer)],
    },
    "strongly_comp": {
        "OSM" : [("results.strong_components_{}_osm", lon.ScatterplotLayer), ("osm.edge_with_cost_{}", lon.PathLayer)],
        "OMF" : [("results.strong_components_{}_omf", lon.ScatterplotLayer), ("omf.edge_with_cost_{}", lon.PathLayer)],
    },
    "isolated_nodes": {
        "OSM" : [("results.isolated_nodes_{}_osm", lon.ScatterplotLayer)],
        "OMF" : [("results.isolated_nodes_{}_omf", lon.ScatterplotLayer)],
    },
    "overlap_indicator": {
        "OSM" : [("results.overlap_indicator_{}_osm", lon.PathLayer)],
        "OMF" : [("results.overlap_indicator_{}_omf", lon.PathLayer)],
    },
    "corresponding_nodes": {
        "OSM" : [("results.corresponding_nodes_{}_osm", lon.ScatterplotLayer)],
        "OMF" : [("results.corresponding_nodes_{}_omf", lon.ScatterplotLayer)],
    },
}

# Icons from font-awesome
ICONS = {
    "":fa.icon_svg("star"),
    "nodes":fa.icon_svg("circle-nodes"),
    "edges":fa.icon_svg("road"),
    "base":fa.icon_svg("ruler"),
    "criteria":fa.icon_svg("calculator"),
    "buildings":fa.icon_svg("building"),
    "buildings_density":fa.icon_svg("city"),
    "places":fa.icon_svg("location-dot"),
    "conn_comp":fa.icon_svg("arrows-left-right"),
    "strongly_comp":fa.icon_svg("arrow-right"),
    "isolated_nodes":fa.icon_svg("circle-dot"),
    "overlap_indicator":fa.icon_svg("grip-lines"),
    "corresponding_nodes":fa.icon_svg("clone"),
    "github":fa.icon_svg("github", height="2em", width="2em"),
}

# Bounding box table
bounding_box_gdf = getAllAreas(engine)

nameColumn = "name"

# Get areas from it
areas = bounding_box_gdf[nameColumn].tolist()
areas.sort()

# Get bounding boxs for each areas
areasCRS = getAreasCRS(bounding_box_gdf, nameColumn)

# Get path of help.md and licenses.md files (used after)
pathHelpMD = Path(__file__).parent / "help.md"
pathLicensesMD = Path(__file__).parent / "licenses.md"

## Reactive values ##
# Mandatory layer to add to the map (calculation are made on it)
layerOSM = reactive.value(gpd.GeoDataFrame())
layerOMF = reactive.value(gpd.GeoDataFrame())

# Other layers to add to the map (no calculation on them)
otherLayersOSM = reactive.value([])
otherLayersOMF = reactive.value([])

# DataFrame for the number of edges / length per class
classesOSM = reactive.value(pd.DataFrame())
classesOMF = reactive.value(pd.DataFrame())

# Variable for the last area, criterion and theme chosen
currentArea = reactive.value("")
currentCriterion = reactive.value("")
currentTheme = reactive.value("")

# Variable for the map state
formerMapState = reactive.value(lon.models.ViewState(
    latitude=36.390,
    longitude=138.812,
    zoom=7,
    pitch=0,
    bearing=0)
)

# Boolean to keep the former map state or not
keepFormerMapState = reactive.value(False)

# Variable for the cards
nbNodesOSM = reactive.value("")
nbNodesOMF = reactive.value("")
nbEdgesOSM = reactive.value("")
nbEdgesOMF = reactive.value("")
nbBuildingsOSM = reactive.value("")
nbBuildingsOMF = reactive.value("")
nbPlacesOSM = reactive.value("")
nbPlacesOMF = reactive.value("")


# This function must be before the main script to be launched before the maps
@reactive.effect
@reactive.event(input.submit)
def getData():
    """Reactive function triggered by the submit button event.
    
    Calculate the data used in the rest of the application, depending
    on the area and criterion values.
    """
    # Get input
    area = input.select_area()
    criterion = input.select_criterion()
    
    # Get theme of the criterion
    theme = criteria_theme[criterion]
    
    # Read and get the value
    currentAreaValue = currentArea()
    currentCriterionValue = currentCriterion()
    currentThemeValue = currentTheme()
    
    # Get current map state (we take OSM for both maps) if the map is loaded
    if currentAreaValue != "":
        view_state = reactive_read(osm_map.widget, 'view_state')
        formerMapState.set(view_state)
    
    # If the area has changed, the data must change too
    if currentAreaValue != area:
        # Do not keep former map state
        keepFormerMapState.set(False)
        
        # Change the last area chosen
        currentArea.set(area)
        currentTheme.set(theme)
    
        # Reset reactive values
        nbNodesOSM.set("")
        nbNodesOMF.set("")
        nbEdgesOSM.set("")
        nbEdgesOMF.set("")
        nbBuildingsOSM.set("")
        nbBuildingsOMF.set("")
        nbPlacesOSM.set("")
        nbPlacesOMF.set("")
        
        # Populate the cards number
        nbNodesOSM.set(getNbRowTable(engine, template_layers_name["base"]["OSM"][0][0].format(area.lower())))
        nbNodesOMF.set(getNbRowTable(engine, template_layers_name["base"]["OMF"][0][0].format(area.lower())))
        nbEdgesOSM.set(getNbRowTable(engine, template_layers_name["base"]["OSM"][1][0].format(area.lower())))
        nbEdgesOMF.set(getNbRowTable(engine, template_layers_name["base"]["OMF"][1][0].format(area.lower())))
        nbBuildingsOSM.set(getNbRowTable(engine, template_layers_name["buildings"]["OSM"][0][0].format(area.lower())))
        nbBuildingsOMF.set(getNbRowTable(engine, template_layers_name["buildings"]["OMF"][0][0].format(area.lower())))
        nbPlacesOSM.set(getNbRowTable(engine, template_layers_name["places"]["OSM"][0][0].format(area.lower())))
        nbPlacesOMF.set(getNbRowTable(engine, template_layers_name["places"]["OMF"][0][0].format(area.lower())))
    else:
        # If the area is the same, we keep the former map state
        keepFormerMapState.set(True)
    
    # If the area changed or the criterion changed, we download the data for the criterion
    if (currentCriterionValue != criterion) or (currentAreaValue != area):
        
        # Change the last criterion chosen
        currentCriterion.set(criterion)
        
        # Empty the variable
        layerOSM.set(gpd.GeoDataFrame())
        layerOMF.set(gpd.GeoDataFrame())
        
        otherLayersOSM.set([])
        otherLayersOMF.set([])
        
        # Get table for the mandatory layer (first element)
        osmTable = template_layers_name[criterion]["OSM"][0][0]
        omfTable = template_layers_name[criterion]["OMF"][0][0]
        
        # Set reactive values
        layerOSM.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {osmTable.format(area.lower())}", engine))
        layerOMF.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {omfTable.format(area.lower())}", engine))
        
        # Get other layers if they exists
        # OSM
        if len(template_layers_name[criterion]["OSM"]) > 1:
            layersOSM = []
            # Iterate over the layers
            for index in range(1, len(template_layers_name[criterion]["OSM"])):
                osmTable = template_layers_name[criterion]["OSM"][index][0]
                layersOSM.append(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {osmTable.format(area.lower())}", engine))
            otherLayersOSM.set(otherLayersOSM() + layersOSM)
        
        # OMF
        if len(template_layers_name[criterion]["OMF"]) > 1:
            layersOMF = []
            # Iterate over the layers
            for index in range(1, len(template_layers_name[criterion]["OMF"])):
                omfTable = template_layers_name[criterion]["OMF"][index][0]
                layersOMF.append(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {omfTable.format(area.lower())}", engine))
            otherLayersOMF.set(otherLayersOMF() + layersOMF)
    
    # If the theme or area has changed, change the classes dataframe
    if (currentThemeValue != theme) or (currentAreaValue != area):
        
        # Change the current theme
        currentTheme.set(theme)
        # Reset reactive values
        classesOSM.set(pd.DataFrame())
        classesOMF.set(pd.DataFrame())
        
        # Calculate the length and number of edges per class for each dataset
        crs = areasCRS[area]
        functionDataFrame = theme_function[theme]
        
        # Because the graph dataframe needs edge layer, we check if the layer imported is the good one
        templateLayerClassesOSM = theme_template_layer[theme]["OSM"]
        osmTable = template_layers_name[criterion]["OSM"][0][0]
        # If it is the same layer, we can just take it
        if templateLayerClassesOSM == osmTable:
            classesOSM.set(functionDataFrame(layerOSM(), crs))
        else:
            # Otherwise, we get the data for the theme
            layerclassesOSM = gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {templateLayerClassesOSM.format(area.lower())}", engine)
            classesOSM.set(functionDataFrame(layerclassesOSM, crs))
            
        # Same for OMF data
        templateLayerClassesOMF = theme_template_layer[theme]["OMF"]
        omfTable = template_layers_name[criterion]["OMF"][0][0]
        # If it is the same layer, we can just take it
        if templateLayerClassesOMF == omfTable:
            classesOMF.set(functionDataFrame(layerOMF(), crs))
        else:
            # Otherwise, we get the data for the theme
            layerclassesOMF = gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {templateLayerClassesOMF.format(area.lower())}", engine)
            classesOMF.set(functionDataFrame(layerclassesOMF, crs))


### Website content ###
## General content ##
# Add icon
logo = "LM_icon_32-32.png"
logo_omf = "logo-omf.png"

# Include CSS
ui.head_content(
    ui.tags.link(href="style.css", rel="stylesheet"),
    ui.tags.link(rel="icon", type="image/png", sizes="32x32", href=logo),
)

# Add page title and sidebar
ui.page_opts(
    title="OpenStreetMap (OSM) and Overture Maps Fundation (OMF) dataset comparison : Japan example",
    full_width=True,
    window_title="Test Dashboard shiny / lonboard",
    fillable=True
)

## Switch dark / light mode ##
with ui.nav_control():
    ui.input_dark_mode()

## Sidebar ##
with ui.sidebar(open="desktop", bg="#f8f8f8", width=350):
    
    ## Input for the layer and criterion to display ##
    ui.input_select("select_area", "Area", choices = areas)

    ui.input_select("select_criterion", "Show", choices = quality_criteria_choices)
    
    ui.input_action_button("submit", "Load layers", class_ = "btn btn-outline-warning")
    
    ## Accordion for the different styles ##
    with ui.accordion(id="acc", open=True):
        
        # Common style
        with ui.accordion_panel("Common styles", class_= "background-sidebar"):
            
            ui.input_numeric("radius_min_pixels", "Radius min pixel (point)", 2, min=1, max=10)
            
            ui.input_numeric("width_min_pixels", "Width min pixel (line)", 2, min=1, max=10)
            
            ui.input_numeric("line_min_pixel", "Line min pixel (polygon)", 0, min=0, max=10)
        
        # # Style base layer
        # with ui.accordion_panel("Style base", class_= "background-sidebar"):
            
            @render_widget
            def colorPickerPoint() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for the point style.

                Returns:
                    ipywidgets.ColorPicker: color picker for points style.
                """
                color_picker_point = ipywidgets.ColorPicker(concise=True, description='Point color', value='#0000FF')
                return color_picker_point

            @render_widget
            def colorPickerLine() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for the line style.

                Returns:
                    ipywidgets.ColorPicker: color picker for lines style.
                """
                color_picker_line = ipywidgets.ColorPicker(concise=True, description='Line color', value='#FF0000')
                return color_picker_line
            
            @render_widget
            def colorPickerPolygonFill() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for the polygon fill style.

                Returns:
                    ipywidgets.ColorPicker: color picker for lines style.
                """
                color_picker_polygon_fill = ipywidgets.ColorPicker(concise=True, description='Polygon color (fill)', value='#00FF00')
                return color_picker_polygon_fill
            
            @render_widget
            def colorPickerPolygonLine() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for the polygon line style.

                Returns:
                    ipywidgets.ColorPicker: color picker for lines style.
                """
                color_picker_polygon_line = ipywidgets.ColorPicker(concise=True, description='Polygon color (line)', value='#000000')
                return color_picker_polygon_line
        
        # Style (strongly) connected components layers
        with ui.accordion_panel("Style components", class_= "background-sidebar"):
            
            "Choose a color and copy it to the table"
            
            @render_widget
            def colorPickerComponents() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for the component part.

                Returns:
                    ipywidgets.ColorPicker: color picker for components section.
                """
                color_picker_components = ipywidgets.ColorPicker(id = "color-picker-components")
                return color_picker_components
            
            ui.div(style = "padding: 0.5em;")
            
            @render.data_frame
            def legendComponents() -> render.DataGrid:
                """Render data frame function.
                
                Create a DataFrame with initial values and custom style
                to change component layers style.

                Returns:
                    render.DataGrid: Data grid to change component layers style.
                """
                data = {
                    "Min value":[1, 6, 16, 251],
                    "Max value":[5, 15, 250, "max"],
                    "Colors":["#0e9f0e", "#ffa601", "#01f2ff", "#ffd7ad"]
                }
                
                dataFrame = pd.DataFrame(data)
                
                # Style of the DataFrame
                stylesDF = [
                    {
                        "class":"text-center",
                        "style": {"th { font-weight": "bold; }"},
                    },
                    # Highlight with the good colors
                    {
                        "cols": [2],
                        "rows": [0],
                        "class":"first-color-df",
                        "style": {"background-color": data["Colors"][0]},
                    },
                    {
                        "cols": [2],
                        "rows": [1],
                        "class":"second-color-df",
                        "style": {"background-color": data["Colors"][1]},
                    },
                    {
                        "cols": [2],
                        "rows": [2],
                        "class":"third-color-df",
                        "style": {"background-color": data["Colors"][2]},
                    },
                    {
                        "cols": [2],
                        "rows": [3],
                        "class":"fourth-color-df",
                        "style": {"background-color": data["Colors"][3]},
                    },
                    
                ]
                
                return render.DataGrid(
                    dataFrame,
                    styles = stylesDF,
                    editable=True
                )
        
        # Style isolated nodes layers
        with ui.accordion_panel("Style isolated nodes", class_= "background-sidebar"):
            
            @render_widget
            def colorPickerIsolated() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for isolated nodes style.

                Returns:
                    ipywidgets.ColorPicker: color picker for isolated nodes style.
                """
                color_picker_isolated = ipywidgets.ColorPicker(concise=True, description='Isolated nodes color', value='#FF0000')
                return color_picker_isolated

            @render_widget
            def colorPickerNotIsolated() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for the non isolated nodes style.

                Returns:
                    ipywidgets.ColorPicker: color picker
                    for non isolated nodes style.
                """
                color_picker_not_isolated = ipywidgets.ColorPicker(concise=True, description='Non isolated nodes color', value='#00FF00')
                return color_picker_not_isolated
        
        # Style overlap indicator layers
        with ui.accordion_panel("Style overlap indicator", class_= "background-sidebar"):
        
            @render_widget
            def colorPickerOverlap() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for overlapped road style.

                Returns:
                    ipywidgets.ColorPicker: color picker for
                    overlapped road style.
                """
                color_picker_overlap = ipywidgets.ColorPicker(concise=True, description='Overlap color', value='#00FF00')
                return color_picker_overlap

            @render_widget
            def colorPickerNotOverlap() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for non overlapped road style.

                Returns:
                    ipywidgets.ColorPicker: color picker for
                    non overlapped road style.
                """
                color_picker_not_overlap = ipywidgets.ColorPicker(concise=True, description='Non overlap color', value='#FF0000')
                return color_picker_not_overlap
        
        # Style corresponding nodes layer
        with ui.accordion_panel("Style corresponding nodes", class_= "background-sidebar"):
            
            @render_widget
            def colorPickerCorresponding() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for corresponding nodes style.

                Returns:
                    ipywidgets.ColorPicker: color picker for
                    corresponding nodes style.
                """
                color_picker_corresponding = ipywidgets.ColorPicker(concise=True, description='Corresponding color', value='#00FF00')
                return color_picker_corresponding

            @render_widget
            def colorPickerNotCorresponding() -> ipywidgets.ColorPicker:
                """Render widget function.
                
                Create a color picker for non corresponding nodes style.

                Returns:
                    ipywidgets.ColorPicker: color picker for
                    non corresponding nodes style.
                """
                color_picker_not_corresponding = ipywidgets.ColorPicker(concise=True, description='Non corresponding color', value='#FF0000')
                return color_picker_not_corresponding
    
    # Div used to update the DataFrame style
    ui.div(id = "style-dataframe")

### Dasboard ###
with ui.nav_panel("Dashboard"):
    
    ## Cards ##
    with ui.layout_columns(fill=False):
        
        # Number of nodes
        with ui.card():
            
            ui.card_header(ICONS["nodes"], " Number of nodes")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def getOSMNodes() -> str:
                        """Render text function.
                        
                        Get the number of OSM nodes for the area.

                        Returns:
                            str: Number of OSM nodes.
                        """
                        return nbNodesOSM()
                    
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFNodes() -> str:
                        """Render text function.
                        
                        Get the number of OMF nodes for the area.

                        Returns:
                            str: Number of OMF nodes.
                        """
                        return nbNodesOMF()
        
        # Number of edges
        with ui.card():
            
            ui.card_header(ICONS["edges"], " Number of edges")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def getOSMEdges() -> str:
                        """Render text function.
                        
                        Get the number of OSM edges for the area.

                        Returns:
                            str: Number of OSM edges.
                        """
                        return nbEdgesOSM()
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFEdges() -> str:
                        """Render text function.
                        
                        Get the number of OMF edges for the area.

                        Returns:
                            str: Number of OMF edges.
                        """
                        return nbEdgesOMF()
        
        # Number of buildings
        with ui.card():
            
            ui.card_header(ICONS["buildings"], " Number of buildings")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def getOSMBuildings() -> str:
                        """Render text function.
                        
                        Get the number of OSM buildings for the area.

                        Returns:
                            str: Number of OSM buildings.
                        """
                        return nbBuildingsOSM()
                    
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFBuildings() -> str:
                        """Render text function.
                        
                        Get the number of OMF buildings for the area.

                        Returns:
                            str: Number of OMF buildings.
                        """
                        return nbBuildingsOMF()
        
        # Number of places
        with ui.card():
            
            ui.card_header(ICONS["places"], " Number of places")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def getOSMPlaces() -> str:
                        """Render text function.
                        
                        Get the number of OSM places for the area.

                        Returns:
                            str: Number of OSM places.
                        """
                        return nbPlacesOSM()
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFPlaces() -> str:
                        """Render text function.
                        
                        Get the number of OMF places for the area.

                        Returns:
                            str: Number of OMF places.
                        """
                        return nbPlacesOMF()
        
        # Criterion value (hidden if base layer is selected)
        with ui.card(id = "card_quality_criterion", class_ = "card_data"):
            
            with ui.card_header():
                
                @render.ui
                def getCardHeaderCriterion() -> str:
                    """Render ui function.
                    
                    Get the card header for the criterion.

                    Returns:
                        str: Card header.
                    """
                    return getCardHeader()
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    @reactive.event(input.submit)
                    def getOSMQualityValue() -> str:
                        """Render text function triggered by the submit button event.
                        
                        Get the criterion value for OSM.

                        Returns:
                            str: Criterion value.
                        """
                        OSMValue, _ = getCriterionInformation()
                        return OSMValue
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    @reactive.event(input.submit)
                    def getOMFQualityValue() -> str:
                        """Render text function triggered by the submit button event.
                        
                        Get the criterion value for OMF.

                        Returns:
                            str: Criterion value.
                        """
                        _, OMFValue = getCriterionInformation()
                        return OMFValue

    ## Maps and DataFrames
    with ui.layout_columns(col_widths=[6, 6, 6, 6], row_heights=[2, 1]):
        
        # Map OSM
        with ui.card(full_screen=True):
            
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                
                @render.text
                def getMapHeaderOSM() -> str:
                    """Render text function.
                    
                    Get the map header for OSM map.
                    It depends on the area and criterion displayed.

                    Returns:
                        str: Map header for OSM map.
                    """
                    if currentCriterion() in quality_criteria:
                        if currentArea() != "":
                            header = f"OpenStreetMap - {currentArea()}: {quality_criteria[currentCriterion()]}"
                    else:
                        header = "OpenStreetMap"
                    return header

            @render_widget
            @reactive.event(input.submit)
            def osm_map() -> lon._map.Map:
                """Render widget function triggered by the submit button event.
                
                Create a lonboard map with OSM layer(s) to add.

                Returns:
                    lon._map.Map: Map with OSM layers
                """
                # Layers to display on the map
                layers = []
                
                # If the layer are empty, an empty map is returned
                if layerOSM().empty:
                    
                    m = lon.Map([])
                    # Set zoom over Japan
                    m.set_view_state(
                        latitude=36.390,
                        longitude=138.812,
                        zoom = 7
                    )
                    return m
                
                # Add mandatory layer
                criterion = input.select_criterion()
                # Get the class to add the layer (they all have a from_gropandas method)
                lonboardClass = template_layers_name[criterion]["OSM"][0][1]
                layer = lonboardClass.from_geopandas(layerOSM())
                
                layers.append(layer)
                
                # Check if there are other elements to add
                if len(otherLayersOSM()) > 0:
                    # Add each element by taking the corresponding class in the template_layers_name dict
                    for index in range(len(otherLayersOSM())):
                        data = otherLayersOSM()[index]
                        
                        lonboardClass = template_layers_name[criterion]["OSM"][index + 1][1]
                        layer = lonboardClass.from_geopandas(data)
                        layers.append(layer)
                
                # Construct map
                m = lon.Map(layers = layers)
                
                # Check if the map state must be changed
                if keepFormerMapState():
                    # Set map state from the former view
                    setMapState(formerMapState(), m)
                
                # Construct map with the layers
                return m
        
        # Map OMF
        with ui.card(full_screen=True):
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                @render.text
                def getMapHeaderOMF() -> str:
                    """Render text function.
                    
                    Get the map header for OMF map.
                    It depends on the area and criterion displayed.

                    Returns:
                        str: Map header for OMF map.
                    """
                    if currentCriterion() in quality_criteria:
                        if currentArea() != "":
                            header = f"Overture Maps Foundation - {currentArea()}: {quality_criteria[currentCriterion()]}"
                    else:
                        header = "Overture Maps Foundation"
                    return header
                
            @render_widget
            @reactive.event(input.submit)
            def omf_map() -> lon._map.Map:
                """Render widget function triggered by the submit button event.
                
                Create a lonboard map with OMF layer(s) to add.

                Returns:
                    lon._map.Map: Map with OMF layers
                """
                # Layers to display on the map
                layers = []
                
                # If the layer are empty,an empty map is returned
                if layerOMF().empty:
                    
                    m = lon.Map([])
                    # Set zoom over Japan
                    m.set_view_state(
                        latitude=36.390,
                        longitude=138.812,
                        zoom = 7
                    )
                    
                    return m
                
                # Add mandatory layer
                criterion = input.select_criterion()
                # Get the class to add the layer (they all have a from_gropandas method)
                lonboardClass = template_layers_name[criterion]["OMF"][0][1]
                layer = lonboardClass.from_geopandas(layerOMF())
                
                layers.append(layer)
                
                # Check if there are other elements to add
                if len(otherLayersOMF()) > 0:
                    # Add each element by taking the corresponding class in the template_layers_name dict
                    for index in range(len(otherLayersOMF())):
                        data = otherLayersOMF()[index]
                        
                        lonboardClass = template_layers_name[criterion]["OMF"][index + 1][1]
                        layer = lonboardClass.from_geopandas(data)
                        layers.append(layer)   
                        
                # Construct map
                m = lon.Map(layers = layers)
                
                # Check if the map state must be changed
                if keepFormerMapState():
                    # Set map state from the former view
                    setMapState(formerMapState(), m)
                
                # Construct map with the layers
                return m

        # Dataframe OSM
        with ui.card(full_screen=True):
            
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                
                @render.text
                def getDFHeaderOSM() -> str:
                    """Render text function.
                    
                    Get the DataFrame card header for OSM.

                    Returns:
                        str: Dataframe card header for OSM.
                    """
                    header = "OpenStreetMap"
                    if currentTheme() != "":
                        header = f"{header}: {theme_dataframe_header[currentTheme()].format(currentArea())}"
                    return header
            
            @render.data_frame
            def lengthPerClassOSM() -> render.DataGrid:
                """Render data frame function.
                
                Render the data frame of total length and number of edges
                per class for OSM.

                Returns:
                    render.DataGrid: Data grid with length and number of edges
                    for each OSM class.
                """
                df = classesOSM()
                if currentTheme() != "":
                    newNamesColumns = theme_column_names[currentTheme()]
                    df = df.rename(columns = newNamesColumns)
                return render.DataGrid(df.round(2)) 

        # Dataframe OMF
        with ui.card(full_screen=True):
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                @render.text
                def getDFHeaderOMF() -> str:
                    """Render text function.
                    
                    Get the DataFrame card header for OMF.

                    Returns:
                        str: Dataframe card header for OMF.
                    """
                    header = "Overture Maps Foundation"
                    if currentTheme() != "":
                        header = f"{header}: {theme_dataframe_header[currentTheme()].format(currentArea())}"
                    return header
            
            @render.data_frame
            def lengthPerClassOMF() -> render.DataGrid:
                """Render data frame function.
                
                Render the data frame of total length and number of edges
                per class for OMF.

                Returns:
                    render.DataGrid: Data grid with length and number of edges
                    for each OMF class.
                """
                df = classesOMF()
                if currentTheme() != "":
                    newNamesColumns = theme_column_names[currentTheme()]
                    df = df.rename(columns = newNamesColumns)
                return render.DataGrid(df.round(2))


### Help ###
with ui.nav_panel("Help"):
    # Open help.md file to render the markdown as HTML
    with open(pathHelpMD, 'r', encoding="utf-8") as f:
        helpMD = f.read()
    ui.markdown(helpMD)


### Ressources ###
with ui.nav_panel("Licenses"):
    # Open licenses.md file to render the markdown as HTML
    with open(pathLicensesMD, 'r', encoding="utf-8") as f:
        licensesMD = f.read()
    ui.markdown(licensesMD)


### Links ###
## LocationMind ##
with ui.nav_control():
    ui.a(
        ui.img(
            src=logo,
            alt="LocationMind Inc. logo",
            style="width:32px;height:32px;"
        ),
        href = "https://locationmind.com",
        target = "_blank",
        rel = "noopener noreferrer"
    )


## GitHub project ##
with ui.nav_control():
    ui.a(
        ICONS["github"],
        href = "https://github.com/LocationMind/OSM_Overture_Works",
        target = "_blank",
        rel = "noopener noreferrer"
    )


## OpenStreetMap ##
with ui.nav_control():
    ui.a(
        ui.img(
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Openstreetmap_logo.svg/32px-Openstreetmap_logo.svg.png?20220919103849",
            alt="OpenStreetMaps logo",
            style="width:32px;height:32px;",
        ),
        href = "https://openstreetmaps.org",
        target = "_blank",
        rel = "noopener noreferrer",
        title = "Ken Vermette based on https://commons.wikimedia.org/wiki/File:OpenStreetMap-Logo-2006.svg, CC BY-SA 2.0 &lt;https://creativecommons.org/licenses/by-sa/2.0&gt;, via Wikimedia Commons"
    )


## Overture Maps Foundation ##
with ui.nav_control():
    ui.a(
        ui.img(
            src = logo_omf,
            alt="Overture Maps Fundation logo",
            style="width:32px;height:32px;"
        ),
        href = "https://overturemaps.org/",
        target = "_blank",
        rel = "noopener noreferrer",
    )


### Reactive calculations and reactive effects functions ###
## Card header for the criterion
@reactive.calc
def getCardHeader() -> str:
    """Reactive calculation function.
    
    Get card header for the value.
    This header depends on the value of the current criterion.

    Returns:
        str: Card header with a logo
    """
    return ICONS[currentCriterion()], f" {quality_criteria_display[currentCriterion()]}"


## Calculation of criterion information
@reactive.calc
@reactive.event(input.submit)
def getCriterionInformation() -> tuple[str, str]:
    """Reactive calculation function triggered by the submit button.
    
    Get the information depending on the current criterion.
    Each criterion calls a specific function to get that information.

    Returns:
        tuple[str, str]: Value of the criterion.
        The first value is for OSM, the other for OMF.
    """
    OSMValue, OMFValue = "", ""
    # Get input
    area = input.select_area()
    criterion = input.select_criterion()
    # Base (total length)
    if criterion == "base":
        OSMValue = getTotalLength(classesOSM())
        OMFValue = getTotalLength(classesOMF())
    # Coverage
    elif criterion == "buildings":
        OSMValue = getCoverage(layerOSM(), area)
        OMFValue = getCoverage(layerOMF(), area)
    # Density
    elif criterion == "buildings_density" or criterion == "places":
        OSMValue = getDensity(layerOSM(), area)
        OMFValue = getDensity(layerOMF(), area)
    # (Strongly) connected components
    elif criterion == "conn_comp" or criterion == "strongly_comp":
        OSMValue = getGroupByComp(layerOSM())
        OMFValue = getGroupByComp(layerOMF())
    # Isolated nodes
    elif criterion == "isolated_nodes":
        OSMValue = getNbElem(layerOSM())
        OMFValue = getNbElem(layerOMF())
    # Overlap indicator
    elif criterion == "overlap_indicator":
        OSMValue = getOverlapIndicator(layerOSM(), area)
        OMFValue = getOverlapIndicator(layerOMF(), area)
    # Corresponding nodes
    elif criterion == "corresponding_nodes":
        OSMValue = getCorrespondingNodes(layerOSM())
        OMFValue = getCorrespondingNodes(layerOMF())
    
    return OSMValue, OMFValue


## Style components DataFrame
@reactive.effect
def updateStyleDataFrame():
    """Reactive effect function.
    
    Change the style of the DataFrame every time that a cell is changed
    """
    # Get the changed colors
    editData = legendComponents.data_view()["Colors"]
    editData = editData.to_list()
    
    # Change the style 
    style = f"""
    .first-color-df {{ background-color: {editData[0]} !important; }}
    .second-color-df {{ background-color: {editData[1]} !important; }}
    .third-color-df {{ background-color: {editData[2]} !important; }}
    .fourth-color-df {{ background-color: {editData[3]} !important; }}
    """
    
    # Remove previous style balise
    ui.remove_ui(
        selector="#style-dataframe style"
    )
    
    # Import new style balise
    ui.insert_ui(
        ui.tags.style(
            style
        ),
        "#style-dataframe",
        where="beforeend"
    )


## Update maps
@reactive.effect
def updateOMFMapViewState():
    """Reactive effect function.
    
    Change the view of OMF map whenever OSM map view is changed.
    """
    # Get current view state of OSM map
    view_state = reactive_read(osm_map.widget, 'view_state')
    
    # Set view state of OMF map
    omf_map.widget.set_view_state(
        longitude = view_state.longitude,
        latitude = view_state.latitude,
        zoom = view_state.zoom,
        pitch = view_state.pitch,
        bearing = view_state.bearing)


@reactive.effect
def updateOSMMapViewState():
    """Reactive effect function.
    
    Change the view of OSM map whenever OMF map view is changed.
    """
    # Get current view state of OMF map
    view_state = reactive_read(omf_map.widget, 'view_state')
    
    # Set view state of OSM map
    osm_map.widget.set_view_state(
        longitude = view_state.longitude,
        latitude = view_state.latitude,
        zoom = view_state.zoom,
        pitch = view_state.pitch,
        bearing = view_state.bearing)


@reactive.effect
def updateLayers():
    """Reactive effect function.
    
    Update layers with common styles and colors for the base layers.
    """
    # Point color and radius
    colorPoint = getColorFromColorPicker(colorPickerPoint)

    radius = input.radius_min_pixels()
    
    # Line color and width
    colorLine = getColorFromColorPicker(colorPickerLine)
    
    width = input.width_min_pixels()
    
    
    # Polygon colors and line width
    colorFillPolygon = getColorFromColorPicker(colorPickerPolygonFill)
    colorLinePolygon = getColorFromColorPicker(colorPickerPolygonLine)
    
    polygonWidth = input.line_min_pixel()
    
    # Get map layers
    osmLayers = reactive_read(osm_map.widget, "layers")
    omfLayers = reactive_read(omf_map.widget, "layers")
    
    # Check if the inputs are correct
    if type(radius) == int and type(width) == int and type(polygonWidth) == int:
        if radius >= 1 and width >= 1 and polygonWidth >= 0:
            
            # Check all layers
            for layer in osmLayers + omfLayers:
                
                # Change the width according to the type
                if type(layer) == lon._layer.ScatterplotLayer:
                    layer.radius_min_pixels = radius
                
                elif type(layer) == lon._layer.PathLayer:
                    layer.width_min_pixels = width
                
                elif type(layer) == lon._layer.PolygonLayer:
                    layer.line_width_min_pixels = polygonWidth
    
    # If it is base layer, the color is changed too.
    if currentCriterion() == "base" or currentCriterion() == "buildings" or currentCriterion() == "buildings_density" or currentCriterion() == "places":
        # Check all layers
        for layer in osmLayers + omfLayers:
            
                if type(layer) == lon._layer.ScatterplotLayer:
                    layer.get_fill_color = colorPoint
                
                elif type(layer) == lon._layer.PathLayer:
                    layer.get_color = colorLine
                
                elif type(layer) == lon._layer.PolygonLayer:
                    layer.get_fill_color = colorFillPolygon
                    layer.get_line_color = colorLinePolygon


@reactive.effect
def colorBoolean():
    """Reactive effect function.
    
    Change the style of layers having a "false / true"
    values.
    """
    # Verify criterion
    if currentCriterion() in ["isolated_nodes", "corresponding_nodes", "overlap_indicator"]:
        
        # Get map layers
        osmLayers = reactive_read(osm_map.widget, "layers")
        omfLayers = reactive_read(omf_map.widget, "layers")
        
        # Get colors corresponding to the criterion
        if currentCriterion() == "isolated_nodes":
            # Reverse for isolated nodes, as they DO NOT intersects if they are isolated
            colorTrue = getColorFromColorPicker(colorPickerNotIsolated)
            colorFalse = getColorFromColorPicker(colorPickerIsolated)
            
        elif currentCriterion() == "corresponding_nodes":
            colorTrue = getColorFromColorPicker(colorPickerCorresponding)
            colorFalse = getColorFromColorPicker(colorPickerNotCorresponding)
            
        elif currentCriterion() == "overlap_indicator":
            colorTrue = getColorFromColorPicker(colorPickerOverlap)
            colorFalse = getColorFromColorPicker(colorPickerNotOverlap)
    
        # Check all layers
        for layer in omfLayers + osmLayers:
            
            # If the layer is of point type, we change with the appropriate propriety
            if type(layer) == lon._layer.ScatterplotLayer:
                
                if layer in omfLayers:
                    gdfcopy = layerOMF().copy()
                else:
                    gdfcopy = layerOSM().copy()
                
                # Keep only intersecting columns
                gdfcopy = gdfcopy[["id", "intersects"]]
                
                # Create the 'color' column with a custom function depending
                # on the value of the true / false value
                gdfcopy['color'] = gdfcopy['intersects'].apply(lambda x: colorTrue if x else colorFalse)

                # Convert to dictionary
                colorMap = gdfcopy.set_index('id')['color'].to_dict()
                
                # Apply new style to the layer
                layer.get_fill_color = apply_categorical_cmap(
                    values = gdfcopy["id"],
                    cmap = colorMap
                )
            
            # If the layer is a line, then it is the overlap indicator 
            if type(layer) == lon._layer.PathLayer:
                
                if layer in omfLayers:
                    gdfcopy = layerOMF().copy()
                else:
                    gdfcopy = layerOSM().copy()
                
                gdfcopy = gdfcopy[["id", "overlap"]]
                
                # Create the 'color' column with a custom function depending
                # on the value of the true / false value 
                gdfcopy['color'] = gdfcopy['overlap'].apply(lambda x: colorTrue if x else colorFalse)

                # Convert to dictionary
                colorMap = gdfcopy.set_index('id')['color'].to_dict()
                
                # Apply new style to the layer
                layer.get_color = apply_categorical_cmap(
                    values = gdfcopy["id"],
                    cmap = colorMap
                )


@reactive.effect
def colorRange():
    """Reactive effect function.
    
    Change the style of components layers depending on
    the value of the DataFrame.
    """
    if currentCriterion() in ["conn_comp", "strongly_comp"]:
        # Get map layers
        osmLayers = reactive_read(osm_map.widget, "layers")
        omfLayers = reactive_read(omf_map.widget, "layers")
        
        # Take a copy to prevent changes to the original DataFrame
        editData = legendComponents.data_view().copy()
        
        # Change color to rgb
        editData["Colors"] = editData["Colors"].apply(hexToRgb255)
        
        editData = editData.values.tolist()
        
        # Check all layers
        for layer in omfLayers + osmLayers:
            
            # If the layer is of type point, we change with the appropriate 
            if type(layer) == lon._layer.ScatterplotLayer:

                if layer in omfLayers:
                    gdfcopy = layerOMF().copy()
                else:
                    gdfcopy = layerOSM().copy()
                
                # Keep only interseting column
                gdfcopy = gdfcopy[["id", "cardinality"]]
                
                # Create the 'color' column by applying a custom function
                gdfcopy['color'] = gdfcopy['cardinality'].apply(getColorComponents, args=(editData, ))

                # Convert to dictionary
                colorMap = gdfcopy.set_index('id')['color'].to_dict()
                
                # Apply new style to the layer
                layer.get_fill_color = apply_categorical_cmap(
                    values = gdfcopy["id"],
                    cmap = colorMap
                )
            
            # Edges with cost for connected components
            if type(layer) == lon._layer.PathLayer:
                # Line color and width
                colorLine = getColorFromColorPicker(colorPickerLine)
                
                width = input.width_min_pixels()
                
                layer.width_min_pixels = width

                layer.get_color = colorLine


### Components Dataframe modification handler ###
@legendComponents.set_patches_fn
async def patchesFn(*, patches: list[render.CellPatch]) -> list[render.CellPatch]:
    """Async function trigger by an edit of the components DataFrame.
    
    Check if the changment is possible and if it is, change the
    edit cell and other if needed.

    Args:
        patches (list[render.CellPatch]): List of edit cell to check.

    Returns:
        list[render.CellPatch]: List of possibly multiple edit cells. 
    """
    # Get former data
    currentData = legendComponents.data_view()
    currentData = currentData.values.tolist()
    
    # List to return
    returnPatches = []
    
    # Check if the data view is sorted
    if legendComponents.sort():
        await legendComponents.update_sort(None)
        return returnPatches
    
    # Check the changes
    for patch in patches:
        # Copy the value and get the other
        returnPatch = patch.copy()
        
        row = returnPatch["row_index"]
        col = returnPatch["column_index"]
        val = returnPatch["value"]
        
        # First min value
        if patch["column_index"] == 0 and patch["row_index"] == 0:
            returnPatch["value"] = 1

        # Last max value
        elif patch["column_index"] == 1 and patch["row_index"] == 3:
            returnPatch["value"] = "max"

        # First column and is a number
        elif patch["column_index"] in [0, 1] and patch["value"].isnumeric():
            returnPatch["value"] = int(patch["value"])
            val = int(val)
            
            # If the value is not superior to 0, we do not change it
            if returnPatch["value"] > 0:  
                aboveValue = None
                underValue = None
                
                # First row, we assign 0 to the above value
                if row == 0:
                    aboveValue = 0
                    underValue = currentData[row+1][col]
                # Last row, we assign value + 2 to the under value
                elif row == 3:
                    aboveValue = currentData[row-1][col]
                    underValue = returnPatch["value"] + 2
                # Else, take the current values
                else:
                    aboveValue = currentData[row-1][col]
                    underValue = currentData[row+1][col]
                
                # If the value to compare is the max, we change it to ensure that the comparison is okay
                if underValue == "max":
                    underValue = returnPatch["value"] + 2
                
                # Check if the changed value is between the other limits
                if aboveValue < returnPatch["value"]  < underValue:
                    # Change max value
                    if col == 1:
                        row +=1
                        col = 0
                        val +=1

                    # Change min value
                    else:
                        col += 1
                        row -= 1
                        val -= 1
                    
                    # Change the other value according to this one
                    returnPatches.append(
                        {
                            "row_index":row,
                            "column_index":col,
                            "value":val
                        }
                    )
                
                # If the value is not between these values, we put the same value as before
                else:
                    returnPatch["value"] = currentData[row][col]
            # Correct the edit if the value is not superior to 0
            else:
                    returnPatch["value"] = currentData[row][col]

        # Or a string for the color column
        else:
            # Check if it is a valid color
            if is_color_like(returnPatch["value"]):
                # If so, convert it to an hex value
                returnPatch["value"] = to_hex(returnPatch["value"])
            else:
                # Otherwise, correct the edit
                returnPatch["value"] = currentData[row][col]
        
        # Add the edit cell to the return list
        returnPatches.append(returnPatch)
    return returnPatches