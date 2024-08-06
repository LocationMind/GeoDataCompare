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
import os
import utm
import shapely


### Functions used in the rest of the script ###
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

    Args:
        engine (sqlalchemy.engine.base.Engine):
        Engine used for (geo)pandas sql queries.
        tableName (str, optional): Name of the table. Defaults to "bounding_box".
        schema (str, optional): Name of the schema. Defaults to "public".

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with all entries in the table.
    """
    # Get all the entity from bounding box table
    sqlQueryTable = f"""SELECT * FROM {schema}.{tableName};"""
    
    bounding_box = gpd.GeoDataFrame.from_postgis(sqlQueryTable, engine)
    
    return bounding_box


def getLengthPerClass(edgeGDF:gpd.GeoDataFrame,
                      crs:int) -> pd.DataFrame:
    """Return a DataFrame with length and number of edges per classes.

    Args:
        edgeGDF (gpd.GeoDataFrame): edge GeoDataFrame

    Returns:
        pd.DataFrame: Dataframe with values for each classes
    """
    # Copy the DataFrame to prevent problems
    edgeCopy = edgeGDF.copy()
    # If it is empty, create an empty DataFrame
    if edgeCopy.empty:
        gdfSumup = pd.DataFrame()
    else:
        # Set geometry column and project to another crs
        edgeCopy = edgeCopy.set_geometry("geom")
        gdfProj = edgeCopy.to_crs(crs)
        
        # Calculate length based on the projected geometry in km
        edgeCopy['length'] = gdfProj['geom'].length / 1000
        
        # Agregate per class and calculate the sum and count for each class
        gdfSumup = edgeCopy[['class', 'length']].groupby('class')['length'].agg(['sum', 'count'])
        
        # Reset index to export class
        gdfSumup.reset_index(inplace=True)
    
    return gdfSumup


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
        gdfSumup = gdf[[column]].groupby(column)[column].agg(['count'])
        
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
        gdfSumup = gdf[[column]].groupby(column)[column].agg(['count'])
        
        # Reset index
        gdfSumup.reset_index(inplace=True)
        value = 0
        
        for _, row in gdfSumup.iterrows():
            # Take the number of nodes that do not intersects
            if row[column] == False:
                value = row['count']
    
    return str(value)


def getOverlapIndicator(gdf:gpd.GeoDataFrame,
                        column:str = "overlap") -> str:
    """Get indicator value for the overlap indicator criterion.
    Calculate the total length of overlapping roads and return
    the proportion of length overlapping over the total length.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame for the criterion.
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
        crs = areasCRS[currentArea()]
        gdfProj = gdfCopy.to_crs(crs)
        
        # Calculate length based on the projected geometry in km
        gdfCopy['length'] = gdfProj['geom'].length / 1000
        
        # Agregate per class and calculate sum for each class
        gdfSumup = gdfCopy[[column, 'length']].groupby(column)['length'].agg(['sum'])
        
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
        gdfSumup = gdf[[column]].groupby(column)[column].agg(['count'])
        
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


### Variables used in the application ###

## Constant values ##

# Engine for geodatframe query
engine = getEngine()

# Variable for the map rendering
radiusMinPixels = 2
widthMinPixels = 2

# Dict of the different criterion
quality_criteria = {
    "base":"Original dataset",
    "conn_comp":"Connected components",
    "strongly_comp":"Strongly connected components",
    "isolated_nodes":"Isolated nodes",
    "overlap_indicator":"Overlap indicator",
    "corresponding_nodes":"Corresponding nodes",
}

# Template name of layers per criterion
template_layers_name = {
    "base": {
        "OSM" : [("osm.node_{}", "Point"), ("osm.edge_with_cost_{}", "LineString")],
        "OMF" : [("omf.node_{}", "Point"), ("omf.edge_with_cost_{}", "LineString")],
    },
    "conn_comp": {
        "OSM" : [("results.connected_components_{}_osm", "Point")],
        "OMF" : [("results.connected_components_{}_omf", "Point")],
    },
    "strongly_comp": {
        "OSM" : [("results.strong_components_{}_osm", "Point")],
        "OMF" : [("results.strong_components_{}_omf", "Point")],
    },
    "isolated_nodes": {
        "OSM" : [("results.isolated_nodes_{}_osm", "Point")],
        "OMF" : [("results.isolated_nodes_{}_omf", "Point")],
    },
    "overlap_indicator": {
        "OSM" : [("results.overlap_indicator_{}_osm", "LineString")],
        "OMF" : [("results.overlap_indicator_{}_omf", "LineString")],
    },
    "corresponding_nodes": {
        "OSM" : [("results.corresponding_nodes_{}_osm", "Point")],
        "OMF" : [("results.corresponding_nodes_{}_omf", "Point")],
    },
}

# Icons from font-awesome
ICONS = {
    "nodes": fa.icon_svg("circle-nodes"),
    "edges": fa.icon_svg("road"),
    "length": fa.icon_svg("ruler"),
    "criteria": fa.icon_svg("calculator"),
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
# GeoDataFrame with the node and edge of the area
nodeOSM = reactive.value()
edgeOSM = reactive.value()
nodeOMF = reactive.value()
edgeOMF = reactive.value()

# GeoDataframe for the quality results
qualityOSM = reactive.value(gpd.GeoDataFrame())
qualityOMF = reactive.value(gpd.GeoDataFrame())

# DataFrame for the number of edges / length per class
classesOSM = reactive.value(pd.DataFrame())
classesOMF = reactive.value(pd.DataFrame())

# Variable for the last area and criterion chosen
currentArea = reactive.value("")
currentCriterion = reactive.value("")
currentNbClasses = reactive.value(0)


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
    
    # Read and get the value
    currentAreaValue = currentArea()
    currentCriterionValue = currentCriterion()
    
    # If the area has changed, the data must change too
    if currentAreaValue != area:
        
        # Change the last area chosen
        currentArea.set(area)
    
        # Reset reactive values
        nodeOSM.set(gpd.GeoDataFrame())
        edgeOSM.set(gpd.GeoDataFrame())
        nodeOMF.set(gpd.GeoDataFrame())
        edgeOMF.set(gpd.GeoDataFrame())
        classesOSM.set(pd.DataFrame())
        classesOMF.set(pd.DataFrame())
        
        # Set new value for reactive values, depending on the area
        nodeOSM.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM osm.node_{area.lower()}", engine))
        edgeOSM.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM osm.edge_with_cost_{area.lower()}", engine))
        nodeOMF.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM omf.node_{area.lower()}", engine))
        edgeOMF.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM omf.edge_with_cost_{area.lower()}", engine))
        
        # Calculate the length and number of edges per class for each dataset
        crs = areasCRS[area]
        dfOSM = getLengthPerClass(edgeOSM(), crs)
        dfOMF = getLengthPerClass(edgeOMF(), crs)
        
        # Set the reactive value with the precalculated values
        classesOSM.set(dfOSM)
        classesOMF.set(dfOMF)
        
    # If the area changed or the criterion changed, we download the data for the criterion
    if (currentCriterionValue != criterion) or (currentAreaValue != area):
        
        # Change the last criterion chosen
        currentCriterion.set(criterion)
        
        # Empty the variable
        qualityOSM.set(gpd.GeoDataFrame())
        qualityOMF.set(gpd.GeoDataFrame())
        
        # If the criterion is "base", the data has already been downloaded
        if criterion != "base":
            
            osmTable = template_layers_name[criterion]["OSM"][0][0]
            omfTable = template_layers_name[criterion]["OMF"][0][0]
            
            qualityOSM.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {osmTable.format(area.lower())}", engine))
            qualityOMF.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {omfTable.format(area.lower())}", engine))


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

    ui.input_select("select_criterion", "Show", choices = quality_criteria)
    
    ui.input_action_button("submit", "Load layers", class_ = "btn btn-outline-warning")
    
    ## Accordion for the different styles ##
    with ui.accordion(id="acc", open=True):
        
        # Common style
        with ui.accordion_panel("Common styles", class_= "background-sidebar"):
            
            ui.input_numeric("radius_min_pixels", "Radius min pixel", 2, min=1, max=10)
            
            ui.input_numeric("width_min_pixels", "Width min pixel", 2, min=1, max=10)
        
        # Style base layer
        with ui.accordion_panel("Style base", class_= "background-sidebar"):
            
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
                        return str(nodeOSM().shape[0])
                    
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFNodes() -> str:
                        """Render text function.
                        
                        Get the number of OMF nodes for the area.

                        Returns:
                            str: Number of OMF nodes.
                        """
                        return str(nodeOMF().shape[0])
        
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
                        return str(edgeOSM().shape[0])
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFEdges() -> str:
                        """Render text function.
                        
                        Get the number of OMF edges for the area.

                        Returns:
                            str: Number of OMF edges.
                        """
                        return str(edgeOMF().shape[0])
        
        # Total length in km
        with ui.card():
            
            ui.card_header(ICONS["length"], " Total length (in kilometer)")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def totalLengthOSM() -> str:
                        """Render text function.
                        
                        Get the total length of OSM edges for the area.

                        Returns:
                            str: Total length of OSM edges.
                        """
                        df = classesOSM()
                        if df.empty:
                            value = ""
                        else:
                            value = round(df["sum"].sum())
                        return str(value)
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def totalLengthOMF() -> str:
                        """Render text function.
                        
                        Get the total length of OMF edges for the area.

                        Returns:
                            str: Total length of OMF edges.
                        """
                        df = classesOMF()
                        if df.empty:
                            value = ""
                        else:
                            value = round(df["sum"].sum())
                        return str(value)
        
        
        # Criterion value (hidden if base layer is selected)
        with ui.panel_conditional("input.select_criterion != 'base'"):
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
                            header = f"OSM - {currentArea()} : {quality_criteria[currentCriterion()]}"
                        else:
                            header = f"OSM - {currentArea()} : {quality_criteria[currentCriterion()]}"
                    else:
                        header = "OSM"
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
                
                # If the layer are empty,an empty map is returned
                if nodeOSM().empty or edgeOSM().empty:
                    
                    m = lon.Map([])
                    # Set zoom over Japan
                    m.set_view_state(
                        latitude=36.390,
                        longitude=138.812,
                        zoom = 7
                    )
                    return m
                
                # If the criterion is base, nodes AND edges are displayed
                if input.select_criterion() == "base":
                    
                    # Construct point layer
                    nodeLayer = lon.ScatterplotLayer.from_geopandas(
                        nodeOSM(),
                        radius_min_pixels = 2)
                    
                    # Construct edge layer
                    edgeLayer = lon.PathLayer.from_geopandas(
                        edgeOSM(),
                        width_min_pixels = 2)
                    
                    layers = [nodeLayer, edgeLayer]
                
                # Otherwise, check the geometry type of the layer to add
                else:
                    for _, geomType in template_layers_name[input.select_criterion()]["OSM"]:
                        if geomType == "Point":
                            layer = lon.ScatterplotLayer.from_geopandas(
                                qualityOSM(),
                                radius_min_pixels = 2)
                            
                        elif geomType == "LineString":
                            layer = lon.PathLayer.from_geopandas(
                                qualityOSM(),
                                width_min_pixels = 2)
                        
                        layers = [layer]
                
                # Construct map with the layers
                return lon.Map(layers = layers)
        
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
                            header = f"OMF - {currentArea()} : {quality_criteria[currentCriterion()]}"
                        else:
                            header = f"OMF - {currentArea()} : {quality_criteria[currentCriterion()]}"
                    else:
                        header = "OMF"
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
                if nodeOMF().empty or edgeOMF().empty:
                    
                    m = lon.Map([])
                    # Set zoom over Japan
                    m.set_view_state(
                        latitude=36.390,
                        longitude=138.812,
                        zoom = 7
                    )
                    return m
                
                # If the criterion is base, nodes AND edges are displayed
                if input.select_criterion() == "base":
                    # Construct point layer
                    nodeLayer = lon.ScatterplotLayer.from_geopandas(
                        nodeOMF(),
                        radius_min_pixels = 2)
                    
                    # Construct edge layer
                    edgeLayer = lon.PathLayer.from_geopandas(
                        edgeOMF(),
                        width_min_pixels = 2)
                    
                    layers = [nodeLayer, edgeLayer]
                
                # Otherwise, check the geometry type of the layer to add
                else:
                    for _, geomType in template_layers_name[input.select_criterion()]["OSM"]:
                        if geomType == "Point":
                            layer = lon.ScatterplotLayer.from_geopandas(
                                qualityOMF(),
                                radius_min_pixels = 2)
                            
                        elif geomType == "LineString":
                            layer = lon.PathLayer.from_geopandas(
                                qualityOMF(),
                                width_min_pixels = 2)
                        
                        layers = [layer]
                
                # Construct map with the layers
                return lon.Map(layers = layers)

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
                    if currentArea() != "":
                        header = f"OSM: Number of edges and total length (in km) per class in {currentArea()}"
                    else:
                        header = "OSM: Number of edges and total length (in km) per class"
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
                df = df.rename(columns = {
                    "class":"Class",
                    "sum": "Total length (km)",
                    "count":"Number of edges",
                })
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
                    if currentArea() != "":
                        header = f"OMF: Number of edges and total length (in km) per class in {currentArea()}"
                    else:
                        header = "OMF: Number of edges and total length (in km) per class"
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
                df = df.rename(columns = {
                    "class":"Class",
                    "sum": "Total length (km)",
                    "count":"Number of edges",
                })
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
    if currentCriterion() != "base" and currentCriterion() != "":
        return ICONS[currentCriterion()], f" {quality_criteria[currentCriterion()]}"
    else:
        return ""


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
    # (Strongly) connected components
    if input.select_criterion() == "conn_comp" or input.select_criterion() == "strongly_comp":
        OSMValue = getGroupByComp(qualityOSM())
        OMFValue = getGroupByComp(qualityOMF())
    # Isolated nodes
    if input.select_criterion() == "isolated_nodes":
        OSMValue = getNbElem(qualityOSM())
        OMFValue = getNbElem(qualityOMF())
    # Overlap indicator
    if input.select_criterion() == "overlap_indicator":
        OSMValue = getOverlapIndicator(qualityOSM())
        OMFValue = getOverlapIndicator(qualityOMF())
    # Corresponding nodes
    if input.select_criterion() == "corresponding_nodes":
        OSMValue = getCorrespondingNodes(qualityOSM())
        OMFValue = getCorrespondingNodes(qualityOMF())
    
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
    
    # Get map layers
    osmLayers = reactive_read(osm_map.widget, "layers")
    omfLayers = reactive_read(omf_map.widget, "layers")
    
    # Check if the inputs are correct
    if type(radius) == int and type(width) == int:
        if radius >= 1 and width >= 1:
            
            # Check all layers
            for layer in osmLayers + omfLayers:
                
                # If the layer is of point type, we change with the appropriate
                if type(layer) == lon._layer.ScatterplotLayer:
                    layer.radius_min_pixels = radius
                
                elif type(layer) == lon._layer.PathLayer:
                    layer.width_min_pixels = width
    
    # If it is base layer, the color is changed too.
    if currentCriterion() == "base":
        # Check all layers
        for layer in osmLayers + omfLayers:
            
                if type(layer) == lon._layer.ScatterplotLayer:
                    layer.get_fill_color = colorPoint
                elif type(layer) == lon._layer.PathLayer:
                    layer.get_color = colorLine


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
                    gdfcopy = qualityOMF().copy()
                else:
                    gdfcopy = qualityOSM().copy()
                
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
                    gdfcopy = qualityOMF().copy()
                else:
                    gdfcopy = qualityOSM().copy()
                
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
            
            # If the layer is of point type, we change with the appropriate 
            if type(layer) == lon._layer.ScatterplotLayer:

                if layer in omfLayers:
                    gdfcopy = qualityOMF().copy()
                else:
                    gdfcopy = qualityOSM().copy()
                
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