from datetime import datetime
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
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import theme as t
import criterion as c
from template_layer import DefaultGeneralValues, GeneralValues


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


def getCriterion(criteria_classes:dict[str, c.Criterion],
                 criterion:str) -> c.Criterion:
    """Return the criterion class for the 

    Args:
        criteria_classes (dict[str, c.Criterion]): 
        Dictionnary with the class corresponding to the criterion name
        criterion (str): Name of the criterion

    Returns:
        c.Criterion: Criterion class to be instancied later
    """
    return criteria_classes[criterion]


### Variables used in the application ###

## Constant values ##

# Engine for geodatframe query
engine = getEngine()

# Dict of the different criterion (group by theme) 
quality_criteria_choices = {
    "Graph" : {
        "road_network":c.RoadNetwork.displayNameMap,
        "conn_comp":c.ConnectedComponents.displayNameMap,
        "strongly_comp":c.StrongComponents.displayNameMap,
        "isolated_nodes":c.IsolatedNodes.displayNameMap,
        "overlap_indicator":c.OverlapIndicator.displayNameMap,
        "corresponding_nodes":c.CorrespondingNodes.displayNameMap,
    },
    "Building" : {
        "buildings_coverage":c.BuildingCoverage.displayNameMap,
        "buildings_density":c.BuildingDensity.displayNameMap,
    },
    "Place" : {
        "places_density":c.PlaceDensity.displayNameMap,
    }
}

# Classes for each criterion
criteria_classes = {
    "road_network":c.RoadNetwork,
    "conn_comp":c.ConnectedComponents,
    "strongly_comp":c.StrongComponents,
    "isolated_nodes":c.IsolatedNodes,
    "overlap_indicator":c.OverlapIndicator,
    "corresponding_nodes":c.CorrespondingNodes,
    "buildings_coverage":c.BuildingCoverage,
    "buildings_density":c.BuildingDensity,
    "places_density":c.PlaceDensity,
}

# Template name of layers per criterion
template_layers_name = {
    "road_network": {
        "OSM" : [("osm.edge_with_cost_{}", lon.PathLayer), ("osm.node_{}", lon.ScatterplotLayer)],
        "OMF" : [("omf.edge_with_cost_{}", lon.PathLayer), ("omf.node_{}", lon.ScatterplotLayer)],
    },
    "buildings": {
        "OSM" : [("osm.building_{}", lon.PolygonLayer)],
        "OMF" : [("omf.building_{}", lon.PolygonLayer)],
    },
    "places": {
        "OSM" : [("osm.place_{}", lon.ScatterplotLayer)],
        "OMF" : [("omf.place_{}", lon.ScatterplotLayer)],
    }
}

# Icons from font-awesome

ICONS = {
    "nodes":fa.icon_svg("circle-nodes"),
    "edges":fa.icon_svg("road"),
    "buildings":fa.icon_svg("building"),
    "places":fa.icon_svg("location-dot"),
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
# Variable for the last area, criterion and theme chosen
currentArea = reactive.value("")
currentCriterion = reactive.value(c.DefaultCriterion())
currentTheme = reactive.value(t.DefaultTheme())
generalValues = reactive.value(DefaultGeneralValues())

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

# Variable for the area in km2
areaKm2 = reactive.value(0)

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
    
    crs = areasCRS[area]
    
    # Read and get the value
    currentAreaValue = currentArea()
    currentThemeValue = currentTheme()
    currentCriterionValue = currentCriterion()
    
    # Get current map state (we take OSM for both maps) if the map is loaded
    if currentAreaValue != "":
        view_state = reactive_read(osm_map.widget, 'view_state')
        formerMapState.set(view_state)
    
    # If the area has changed, the data must change too
    if currentAreaValue != area:
        # Do not keep former map state
        keepFormerMapState.set(False)
        
        # Change the last area chosen and get area in km2
        currentArea.set(area)
        
        areaKm2.set(bounding_box_gdf[bounding_box_gdf["name"] == area]["area"].iloc[0])
        
        # Get general values
        generalValues.set(GeneralValues(area, engine))
        
    else:
        # If the area is the same, we keep the former map state
        keepFormerMapState.set(True)
    
    criterionClass = getCriterion(criteria_classes, criterion)
    
    # If the area changed or the criterion changed, we download the data for the criterion
    if (not isinstance(currentCriterionValue, criterionClass)) or (currentAreaValue != area):
        # Create criterion instance
        currentCriterion.set(criterionClass(area, areaKm2(), crs, engine))
    
    
    # Get theme of the criterion and compare it to the current theme
    criterionTheme = currentCriterion().theme
    
    # If the theme is different or the area changed, we recalculate the value 
    if not isinstance(currentThemeValue, criterionTheme) or (currentAreaValue != area):
        currentTheme.set(criterionTheme(area, crs, engine))
        

### Website content ###
## General content ##
# Add icon
logo = "LM_icon_32-32.png"
logo_omf = "logo-omf.png"

# Get today's date
today = datetime.today().strftime('%m/%d/%Y')

# Include CSS
ui.head_content(
    ui.tags.link(href="style.css", rel="stylesheet"),
    ui.tags.link(rel="icon", type="image/png", sizes="32x32", href=logo),
)

# Add page title and sidebar
ui.page_opts(
    title=f"OpenStreetMap (OSM) and Overture Maps Fundation (OMF) dataset comparison - {today}",
    full_width=True,
    window_title="OSM / OMF comparison",
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
            
            ui.input_numeric("width_min_pixels", "Width min pixel (line)", 1, min=1, max=10)
            
            ui.input_numeric("line_min_pixel", "Line min pixel (polygon)", 0, min=0, max=10)
        
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
                    "Colors":["#0e4d0e", "#ff6a01", "#c401c0", "#b16d25"]
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
                        return generalValues().nbNodesOSM
                    
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFNodes() -> str:
                        """Render text function.
                        
                        Get the number of OMF nodes for the area.

                        Returns:
                            str: Number of OMF nodes.
                        """
                        return generalValues().nbNodesOMF
        
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
                        return generalValues().nbEdgesOSM
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFEdges() -> str:
                        """Render text function.
                        
                        Get the number of OMF edges for the area.

                        Returns:
                            str: Number of OMF edges.
                        """
                        return generalValues().nbEdgesOMF
        
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
                        return generalValues().nbBuildingsOSM
                    
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFBuildings() -> str:
                        """Render text function.
                        
                        Get the number of OMF buildings for the area.

                        Returns:
                            str: Number of OMF buildings.
                        """
                        return generalValues().nbBuildingsOMF
        
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
                        return generalValues().nbPlacesOSM
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFPlaces() -> str:
                        """Render text function.
                        
                        Get the number of OMF places for the area.

                        Returns:
                            str: Number of OMF places.
                        """
                        return generalValues().nbPlacesOMF
        
        with ui.card(id = "card_quality_criterion", class_ = "card_data"):
            
            with ui.card_header():
                
                @render.ui
                def getCardHeaderCriterion() -> str:
                    """Render ui function.
                    
                    Get the card header for the criterion.

                    Returns:
                        str: Card header.
                    """
                    return currentCriterion().icon, f" {currentCriterion().displayNameCriterion}"
            
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
                        return currentCriterion().osmValue
                
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
                        return currentCriterion().omfValue

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
                    if not isinstance(currentCriterion(), c.DefaultCriterion):
                        header = f"OpenStreetMap - {currentCriterion().area}: {currentCriterion().displayNameMap}"
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
                layers = [currentCriterion().osmLayer] + currentCriterion().osmOtherLayers
                
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
                    if not isinstance(currentCriterion(), c.DefaultCriterion):
                        header = f"Overture Maps Foundation - {currentCriterion().area}: {currentCriterion().displayNameMap}"
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
                layers = [currentCriterion().omfLayer] + currentCriterion().omfOtherLayers
                        
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
                    if not isinstance(currentCriterion(), c.DefaultCriterion):
                        header = f"{header}: {currentTheme().dfHeader}"
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
                df = currentTheme().osmClasses
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
                    if not isinstance(currentCriterion(), c.DefaultCriterion):
                        header = f"{header}: {currentTheme().dfHeader}"
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
                df = currentTheme().omfClasses
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
                    layer.get_line_color = [0, 255, 0, 0]
                    layer.get_line_width = 5
                
                elif type(layer) == lon._layer.PathLayer:
                    layer.width_min_pixels = width
                
                elif type(layer) == lon._layer.PolygonLayer:
                    layer.line_width_min_pixels = polygonWidth
    
    # If the layer is not special, the layer style is changed
    if (isinstance(currentCriterion(), (c.RoadNetwork, c.BuildingCoverage, c.BuildingDensity, c.PlaceDensity))):
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
    # Verify criterion (overlap, corresponding and isolated nodes)
    if isinstance(currentCriterion(), (c.OverlapIndicator, c.IsolatedNodes, c.CorrespondingNodes)):
        
        # Get map layers
        osmLayers = reactive_read(osm_map.widget, "layers")
        omfLayers = reactive_read(omf_map.widget, "layers")
        
        # Get colors corresponding to the criterion
        if isinstance(currentCriterion(), c.IsolatedNodes):
            # Reverse for isolated nodes, as they DO NOT intersects if they are isolated
            colorTrue = getColorFromColorPicker(colorPickerNotIsolated)
            colorFalse = getColorFromColorPicker(colorPickerIsolated)
            
        elif isinstance(currentCriterion(), c.CorrespondingNodes):
            colorTrue = getColorFromColorPicker(colorPickerCorresponding)
            colorFalse = getColorFromColorPicker(colorPickerNotCorresponding)
            
        elif isinstance(currentCriterion(), c.OverlapIndicator):
            colorTrue = getColorFromColorPicker(colorPickerOverlap)
            colorFalse = getColorFromColorPicker(colorPickerNotOverlap)
    
        # Check all layers
        for layer in omfLayers + osmLayers:            
            # Copy the layer GeoDataFrame for checking the color
            if layer in omfLayers:
                gdfcopy = currentCriterion().omfGdf.copy()
            else:
                gdfcopy = currentCriterion().osmGdf.copy()
            
            # Keep only intersecting columns
            gdfcopy = gdfcopy[["id", currentCriterion().columnCriterion]]
            
            # Create the 'color' column with a custom function depending
            # on the value of the true / false value
            gdfcopy['color'] = gdfcopy[currentCriterion().columnCriterion].apply(lambda x: colorTrue if x else colorFalse)

            # Convert to dictionary
            colorMap = gdfcopy.set_index('id')['color'].to_dict()
            
            if type(layer) == lon._layer.ScatterplotLayer:
                # Apply new style to the layer
                layer.get_fill_color = apply_categorical_cmap(
                    values = gdfcopy["id"],
                    cmap = colorMap
                )
            
            elif type(layer) == lon._layer.PathLayer:
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
    if isinstance(currentCriterion(), (c.ConnectedComponents, c.StrongComponents)):
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
                    gdfcopy = currentCriterion().omfGdf.copy()
                else:
                    gdfcopy = currentCriterion().osmGdf.copy()
                
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