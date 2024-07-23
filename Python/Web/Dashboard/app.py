import geopandas as gpd
import pandas as pd
import time
from functools import partial
import faicons as fa
import numpy as np
from shiny import reactive
from shiny.ui import page_navbar
import shiny.experimental as exp
from shiny.express import input, ui, render
from shinywidgets import render_widget, reactive_read, output_widget
import sqlalchemy
import ipywidgets
import lonboard as lon
from pathlib import Path
from lonboard.colormap import apply_categorical_cmap
from matplotlib.colors import is_color_like, to_hex, to_rgb
from dotenv import load_dotenv
import os

def getEngine():
    dotenv_path =  Path(__file__).parent / ".env"

    ## Read environnment variable
    load_dotenv(dotenv_path)

    database = os.getenv("POSTGRES_DATABASE")
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    port = os.getenv("POSTGRES_PORT")

    engine = sqlalchemy.create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    return engine


def getAllAreas(columnName:str = "name",
                tableName:str = "bounding_box",
                schema:str = "public"):
    # Get all the area through the bounding box table
    sqlQueryTable = f"""SELECT * FROM {schema}.{tableName}"""

    bounding_box = gpd.GeoDataFrame.from_postgis(sqlQueryTable, engine)
    
    # Convert the dataframe to a list
    areas = bounding_box[columnName].tolist()
    areas.sort()
    
    return areas

# Engine for geodatframe query
engine = getEngine()

# Variable for the map rendering
radiusMinPixels = 2
widthMinPixels = 2

quality_criterias = {
    "base":"Original dataset",
    "conn_comp":"Connected components",
    "strongly_comp":"Strongly connected components",
    "isolated_nodes":"Isolated nodes",
    "overlap_indicator":"Overlap indicator",
    "corresponding_nodes":"Corresponding nodes",
}

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

# GeoDataFrame with the node and edge of the area
nodeOSM = reactive.value()
edgeOSM = reactive.value()
nodeOMF = reactive.value()
edgeOMF = reactive.value()

# GeoDataframe for the quality results
qualityOSM = reactive.value(gpd.GeoDataFrame())
qualityOMF = reactive.value(gpd.GeoDataFrame())

# Variable for the last area and criterion chosen
currentArea = reactive.value("")
currentCriterion = reactive.value("")
currentNbClasses = reactive.value(0)

# Get all areas stored in the bounding box table
areas = getAllAreas()


### Reactive functions and calculations ###
@reactive.effect
@reactive.event(input.submit)
def getData():
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
    
        # Get data for the Area
        nodeOSM.set(gpd.GeoDataFrame())
        edgeOSM.set(gpd.GeoDataFrame())
        nodeOMF.set(gpd.GeoDataFrame())
        edgeOMF.set(gpd.GeoDataFrame())
        
        nodeOSM.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM osm.node_{area.lower()}", engine))
        edgeOSM.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM osm.edge_with_cost_{area.lower()}", engine))
        nodeOMF.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM omf.node_{area.lower()}", engine))
        edgeOMF.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM omf.edge_with_cost_{area.lower()}", engine))
    
    # If the area changed or the criterion changed, we download the data for the criterion
    if (currentCriterionValue != criterion) or (currentAreaValue != area):
        # Change the last criterion chosen
        currentCriterion.set(criterion)
        
        # Empty the variable
        qualityOSM.set(gpd.GeoDataFrame())
        qualityOMF.set(gpd.GeoDataFrame())
        
        # If the criterion is base, then the data is already download
        if criterion != "base":
            
            osmTable = template_layers_name[criterion]["OSM"][0][0]
            omfTable = template_layers_name[criterion]["OMF"][0][0]
            
            qualityOSM.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {osmTable.format(area.lower())}", engine))
            qualityOMF.set(gpd.GeoDataFrame.from_postgis(f"SELECT * FROM {omfTable.format(area.lower())}", engine))


### Add main content ###
# Add icon
logo = "LM_icon_32-32.png"
logo_omf = "logo-omf.png"

# Include CSS
ui.head_content(
    ui.tags.link(href="style.css", rel="stylesheet"),
    ui.tags.link(rel="icon", type="image/png", sizes="32x32", href=logo),
)

# Get path of help.md and licenses.md files
pathHelpMD = Path(__file__).parent / "help.md"
pathLicensesMD = Path(__file__).parent / "licenses.md"

## Add page title and sidebar
ui.page_opts(
    title="OpenStreetMap (OSM) and Overture Maps Fundation (OMF) dataset comparison : Japan example",
    full_width=True,
    window_title="Test Dashboard shiny / lonboard",
    fillable=True
)

### Switch dark / light mode ###
with ui.nav_control():
    ui.input_dark_mode()

### Sidebar ###
with ui.sidebar(open="desktop", bg="#f8f8f8", width=350):

    ui.input_select("select_area", "Area", choices = areas)

    ui.input_select("select_criterion", "Show", choices = quality_criterias)
    
    ui.input_action_button("submit", "Load layers", class_ = "btn btn-outline-warning")
    
    with ui.accordion(id="acc", open=True):
        with ui.accordion_panel("Common styles", class_= "background-grey"):
            
            ui.input_numeric("radius_min_pixels", "Radius min pixel", 2, min=1, max=10)
            
            ui.input_numeric("width_min_pixels", "Width min pixel", 2, min=1, max=10)
            
        with ui.accordion_panel("Style base", class_= "background-grey"):
            
            @render_widget
            def colorPickerPoint():
                color_picker_point = ipywidgets.ColorPicker(concise=True, description='Point color', value='#0000FF')
                return color_picker_point

            @render_widget
            def colorPickerLine():
                color_picker_line = ipywidgets.ColorPicker(concise=True, description='Line color', value='#FF0000')
                return color_picker_line
            
        with ui.accordion_panel("Style components", class_= "background-grey"):
            
            "Choose a color and copy it to the table"
            
            @render_widget
            def colorPickerComponents():
                color_picker_components = ipywidgets.ColorPicker(id = "color-picker-components")
                return color_picker_components
            
            ui.div(style = "padding: 0.5em;")
            
            @render.data_frame
            def legendComponents():
                data = {
                    "Min value":[1, 6, 16, 251],
                    "Max value":[5, 15, 250, "max"],
                    "Colors":["#0e9f0e", "#ffa601", "#01f2ff", "#ffd7ad"]
                }
                
                dataFrame = pd.DataFrame(data)
                
                # Style of the dataframe
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
            
        with ui.accordion_panel("Style isolated nodes", class_= "background-grey"):
            
            @render_widget
            def colorPickerIsolated():
                color_picker_isolated = ipywidgets.ColorPicker(concise=True, description='Isolated nodes color', value='#FF0000')
                return color_picker_isolated

            @render_widget
            def colorPickerNotIsolated():
                color_picker_not_isolated = ipywidgets.ColorPicker(concise=True, description='Non isolated nodes color', value='#00FF00')
                return color_picker_not_isolated
            
        with ui.accordion_panel("Style overlap indicator", class_= "background-grey"):
        
            @render_widget
            def colorPickerOverlap():
                color_picker_overlap = ipywidgets.ColorPicker(concise=True, description='Overlap color', value='#00FF00')
                return color_picker_overlap

            @render_widget
            def colorPickerNotOverlap():
                color_picker_not_overlap = ipywidgets.ColorPicker(concise=True, description='Non overlap color', value='#FF0000')
                return color_picker_not_overlap
            
        with ui.accordion_panel("Style corresponding nodes", class_= "background-grey"):
            
            @render_widget
            def colorPickerCorresponding():
                color_picker_corresponding = ipywidgets.ColorPicker(concise=True, description='Corresponding color', value='#00FF00')
                return color_picker_corresponding

            @render_widget
            def colorPickerNotCorresponding():
                color_picker_not_corresponding = ipywidgets.ColorPicker(concise=True, description='Non corresponding color', value='#FF0000')
                return color_picker_not_corresponding

### Dasboard ###
with ui.nav_panel("Dashboard"):
    
    ## Cards ##
    with ui.layout_columns(fill=False):
        with ui.card():
            
            ui.card_header(ICONS["nodes"], " Number of nodes")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def getOSMNodes():
                        return nodeOSM().shape[0]
                    
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFNodes():
                        return nodeOMF().shape[0]
        
        with ui.card():
            
            ui.card_header(ICONS["edges"], " Number of edges")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def getOSMEdges():
                        return edgeOSM().shape[0]
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def getOMFEdges():
                        return edgeOMF().shape[0]
        
        with ui.card():
            
            ui.card_header(ICONS["length"], " Total length (in kilometer)")
            
            with ui.layout_column_wrap(width=1 / 2):
                with ui.value_box(class_ = "value-box"):
                    "OSM"
                    
                    @render.text
                    def printTotalLengthOSM():
                        df = getLengthPerClassOSM()
                        if df.empty:
                            value = "No value"
                        else:
                            value = round(df["sum"].sum())
                        return value
                
                with ui.value_box(class_ = "value-box"):
                    "OMF"
                    
                    @render.text
                    def printTotalLengthOMF():
                        df = getLengthPerClassOMF()
                        if df.empty:
                            value = "No value"
                        else:
                            value = round(df["sum"].sum())
                        return value
        
        
        with ui.panel_conditional("input.select_criterion != 'base'"):
            with ui.card(id = "card_quality_criterion", class_ = "card_data"):
                
                with ui.card_header():
                    
                    @render.ui
                    def getCardHeader():
                        return getCardHeader()
                
                with ui.layout_column_wrap(width=1 / 2):
                    with ui.value_box(class_ = "value-box"):
                        "OSM"
                        
                        @render.text
                        @reactive.event(input.submit)
                        def getOSMQualityValue():
                            OSMValue, _ = getCriterionInformation()
                            return OSMValue
                    
                    with ui.value_box(class_ = "value-box"):
                        "OMF"
                        
                        @render.text
                        @reactive.event(input.submit)
                        def getOMFQualityValue():
                            _, OMFValue = getCriterionInformation()
                            return OMFValue

    ## Maps and dataframes
    with ui.layout_columns(col_widths=[6, 6, 6, 6], row_heights=[2, 1]):
        
        # Map OSM
        with ui.card(full_screen=True):
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                @render.text
                def getMapHeaderOSM():
                    if currentCriterion() in quality_criterias:
                        if currentArea() != "":
                            header = f"OSM - {currentArea()} : {quality_criterias[currentCriterion()]}"
                        else:
                            header = f"OSM - {currentArea()} : {quality_criterias[currentCriterion()]}"
                    else:
                        header = "OSM"
                    return header

            @render_widget
            @reactive.event(input.submit)
            def osm_map():
                
                layers = []
                
                # First, the layer are not chosen so we return only the empty map
                if nodeOSM().empty or edgeOSM().empty:
                    
                    m = lon.Map([])
                    m.set_view_state(
                        latitude=36.390,
                        longitude=138.812,
                        zoom = 7
                    )
                    return m
                
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
                return lon.Map(layers = layers)
        
        # Map OMF
        with ui.card(full_screen=True):
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                @render.text
                def getMapHeaderOMF():
                    if currentCriterion() in quality_criterias:
                        if currentArea() != "":
                            header = f"OMF - {currentArea()} : {quality_criterias[currentCriterion()]}"
                        else:
                            header = f"OMF - {currentArea()} : {quality_criterias[currentCriterion()]}"
                    else:
                        header = "OMF"
                    return header
                
            @render_widget
            @reactive.event(input.submit)
            def omf_map():
                
                layers = []
                
                # First, the layer are not chosen so we return only the empty map
                if nodeOMF().empty or edgeOMF().empty:
                    
                    m = lon.Map([])
                    m.set_view_state(
                        latitude=36.390,
                        longitude=138.812,
                        zoom = 7
                    )
                    return m
                
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
                
                return lon.Map(layers = layers)

        # Dataframe OSM
        with ui.card(full_screen=True):
            
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                @render.text
                def getDFHeaderOSM():
                    if currentArea() != "":
                        header = f"OSM: Number of edges and total length (in km) per class in {currentArea()}"
                    else:
                        header = "OSM: Number of edges and total length (in km) per class"
                    return header
                
            @render.data_frame
            def printLengthPerClassOSM():
                df = getLengthPerClassOSM()
                df = df.rename(columns = {
                    "class":"Class",
                    "sum": "Total length (km)",
                    "count":"Number of entity",
                })
                return render.DataGrid(df.round(2), selection_mode="rows") 

        # Dataframe OMF
        with ui.card(full_screen=True):
            with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                @render.text
                def getDFHeaderOMF():
                    if currentArea() != "":
                        header = f"OMF: Number of edges and total length (in km) per class in {currentArea()}"
                    else:
                        header = "OMF: Number of edges and total length (in km) per class"
                    return header
            
            @render.data_frame
            def printLengthPerClassOMF():
                df = getLengthPerClassOMF()
                df = df.rename(columns = {
                    "class":"Class",
                    "sum": "Total length (km)",
                    "count":"Number of entity",
                })
                return render.DataGrid(df.round(2), selection_mode="rows")

### Help ###
with ui.nav_panel("Help"):
    with open(pathHelpMD, 'r', encoding="utf-8") as f:
        helpMD = f.read()
    ui.markdown(helpMD)

### Ressources ###
with ui.nav_panel("Licenses"):
    with open(pathLicensesMD, 'r', encoding="utf-8") as f:
        licensesMD = f.read()
    ui.markdown(licensesMD)

### Links ###
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
    
with ui.nav_control():
    ui.a(
        ICONS["github"],
        href = "https://github.com/LocationMind/OSM_Overture_Works",
        target = "_blank",
        rel = "noopener noreferrer"
    )

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

@reactive.calc
@reactive.event(input.submit)
def getLengthPerClassOSM():
    edgeCopy = edgeOSM().copy()
    if edgeCopy.empty:
        gdfSumup = pd.DataFrame()
        
    else:
        edgeCopy = edgeCopy.set_geometry("geom")
        
        gdfProj = edgeCopy.to_crs(6691)
        
        edgeCopy['length'] = gdfProj['geom'].length / 1000

        gdfSumup = edgeCopy[['class', 'length']].groupby('class')['length'].agg(['sum', 'count'])
        
        gdfSumup.reset_index(inplace=True)
    
    return gdfSumup
    
@reactive.calc
@reactive.event(input.submit)
def getLengthPerClassOMF():
    edgeCopy = edgeOMF().copy()

    if edgeCopy.empty:
        gdfSumup = pd.DataFrame()
        
    else:
        edgeCopy = edgeCopy.set_geometry("geom")
        
        gdfProj = edgeCopy.to_crs(6691)
        
        edgeCopy['length'] = gdfProj['geom'].length / 1000

        gdfSumup = edgeCopy[['class', 'length']].groupby('class')['length'].agg(['sum', 'count'])
        
        gdfSumup.reset_index(inplace=True)
    
    return gdfSumup


@reactive.calc
def getCardHeader():
    if currentCriterion() != "base" and currentCriterion() != "":
        return ICONS[currentCriterion()], f" {quality_criterias[currentCriterion()]}"
    else:
        return ""

@reactive.calc
@reactive.event(input.submit)
def getCriterionInformation():
    OSMValue, OMFValue = None, None
    if input.select_criterion() == "conn_comp" or input.select_criterion() == "strongly_comp":
        OSMValue = getGroupByComp(qualityOSM())
        OMFValue = getGroupByComp(qualityOMF())
        
    if input.select_criterion() == "isolated_nodes":
        OSMValue = getNbElem(qualityOSM())
        OMFValue = getNbElem(qualityOMF())
        
    if input.select_criterion() == "overlap_indicator":
        OSMValue = f"{getOverlapIndicator(qualityOSM())} %"
        OMFValue = f"{getOverlapIndicator(qualityOMF())} %"
        
    if input.select_criterion() == "corresponding_nodes":
        OSMValue = getCorrespondingNodes(qualityOSM())
        OMFValue = getCorrespondingNodes(qualityOMF())
    
    return OSMValue, OMFValue

def getGroupByComp(gdf:gpd.GeoDataFrame,
                   column:str = "component"):
    if gdf.empty:
        value = None

    else:
        gdfSumup = gdf[[column]].groupby(column)[column].agg(['count'])
        
        gdfSumup.reset_index(inplace=True)
        
        value = gdfSumup.shape[0]
    return value
    

def getNbElem(gdf:gpd.GeoDataFrame,
              column:str = "intersects"):
    if gdf.empty:
        value = None

    else:
        gdfSumup = gdf[[column]].groupby(column)[column].agg(['count'])
        
        gdfSumup.reset_index(inplace=True)
        
        value = 0
        for _, row in gdfSumup.iterrows():
            if row[column] == False:
                value = row['count']
            
    return value


def getOverlapIndicator(gdf:gpd.GeoDataFrame,
                        column:str = "overlap"):
    gdfCopy = gdf.copy()

    if gdfCopy.empty:
        value = None
        
    else:
        gdfCopy = gdfCopy.set_geometry("geom")
        
        gdfProj = gdfCopy.to_crs(6691)
        
        gdfCopy['length'] = gdfProj['geom'].length / 1000

        gdfSumup = gdfCopy[[column, 'length']].groupby(column)['length'].agg(['sum'])
        
        gdfSumup.reset_index(inplace=True)
        
        overlapLength = 0
        totalLength = 0
        
        for _, row in gdfSumup.iterrows():
            if row[column] == True:
                overlapLength = row['sum']
            totalLength += row['sum']
        
        value = round((overlapLength / totalLength) * 100, 2)
    
    return value


def getCorrespondingNodes(gdf:gpd.GeoDataFrame,
                          column:str = "intersects"):
    if gdf.empty:
        value = None

    else:
        gdfSumup = gdf[[column]].groupby(column)[column].agg(['count'])
        
        gdfSumup.reset_index(inplace=True)
        
        totalNodes = 0
        intersectNodes = 0
        for _, row in gdfSumup.iterrows():
            if row[column] == True:
                intersectNodes = row['count']
            totalNodes += row['count']
       
        percentage = round((intersectNodes / totalNodes) * 100, 2)
        
        value = f"{intersectNodes} - {percentage} %"
       
    return value

## Handle dataframe modification
@legendComponents.set_patches_fn
async def patchesFn(*, patches: list[render.CellPatch]):
    # Get former data
    currentData = legendComponents.data_view()
    currentData = currentData.values.tolist()
    
    returnPatches = []
    # Check if the data view is sorted
    if legendComponents.sort():
        await legendComponents.update_sort(None)
        return returnPatches
    
    # Else, we check the changes
    for patch in patches:
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
                
                # First row, we assign 0 to the value
                if row == 0:
                    aboveValue = 0
                    underValue = currentData[row+1][col]
                # Same for the last one
                elif row == 3:
                    aboveValue = currentData[row-1][col]
                    # This way we know that we will not have problem comparing it
                    underValue = returnPatch["value"] + 2
                else:
                    aboveValue = currentData[row-1][col]
                    underValue = currentData[row+1][col]
                    
                # If the value to compare is the max, we change it to ensure that the comparison is okay
                if underValue == "max":
                    underValue = returnPatch["value"] + 2
                
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
            else:
                    returnPatch["value"] = currentData[row][col]
        # Or a string for the color column
        else:
            # Check if it is a valid color
            if is_color_like(returnPatch["value"]):
                returnPatch["value"] = to_hex(returnPatch["value"])
            else:
                returnPatch["value"] = currentData[row][col]
        returnPatches.append(returnPatch)
    return returnPatches

# Update the style of the dataFrame when changing rows
@reactive.effect
def updateStyleDataFrame():
    editData = legendComponents.data_view()["Colors"]
    editData = editData.to_list()
    style = f"""
    .first-color-df {{ background-color: {editData[0]}; }}
    .second-color-df {{ background-color: {editData[1]}; }}
    .third-color-df {{ background-color: {editData[2]}; }}
    .fourth-color-df {{ background-color: {editData[3]}; }}
    """
    
    ui.tags.style(
        style
    )

# Update maps when moving the canvas
@reactive.effect
def updateOSMMapViewState():
    view_state = reactive_read(omf_map.widget, 'view_state')
    
    osm_map.widget.set_view_state(
        longitude = view_state.longitude,
        latitude = view_state.latitude,
        zoom = view_state.zoom,
        pitch = view_state.pitch,
        bearing = view_state.bearing)
    
    
@reactive.effect
def updateOMFMapViewState():
    view_state = reactive_read(osm_map.widget, 'view_state')
    
    omf_map.widget.set_view_state(
        longitude = view_state.longitude,
        latitude = view_state.latitude,
        zoom = view_state.zoom,
        pitch = view_state.pitch,
        bearing = view_state.bearing)


def getColorFromColorPicker(widgetName:render_widget[ipywidgets.ColorPicker]):
    hex = reactive_read(widgetName.widget, "value")
    color = list(int(hex[i:i+2], 16) for i in (1, 3, 5))
    return color

# Update layers from the value of the sidebar
@reactive.effect
def updateLayers():
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
    
    # Check which layer is uploaded
    if currentCriterion() == "base":
        # Check all layers
        for layer in osmLayers + omfLayers:
            
                if type(layer) == lon._layer.ScatterplotLayer:
                    layer.get_fill_color = colorPoint
                elif type(layer) == lon._layer.PathLayer:
                    layer.get_color = colorLine


# Update layers from the value of the sidebar
@reactive.effect
def colorBoolean():
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
            
            # If the layer is of point type, we change with the appropriate 
            if type(layer) == lon._layer.ScatterplotLayer:
                
                if layer in omfLayers:
                    gdfcopy = qualityOMF().copy()
                else:
                    gdfcopy = qualityOSM().copy()
                
                gdfcopy = gdfcopy[["id", "intersects"]]
                
                # Create the 'color' column
                gdfcopy['color'] = gdfcopy['intersects'].apply(lambda x: colorTrue if x else colorFalse)

                # Convert to dictionary
                colorMap = gdfcopy.set_index('id')['color'].to_dict()
                
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
                
                # Create the 'color' column
                gdfcopy['color'] = gdfcopy['overlap'].apply(lambda x: colorTrue if x else colorFalse)

                # Convert to dictionary
                colorMap = gdfcopy.set_index('id')['color'].to_dict()
                
                layer.get_color = apply_categorical_cmap(
                    values = gdfcopy["id"],
                    cmap = colorMap
                )

# Update layers from the value of the sidebar
@reactive.effect
def colorRange():
    if currentCriterion() in ["conn_comp", "strongly_comp"]:
        # Get map layers
        osmLayers = reactive_read(osm_map.widget, "layers")
        omfLayers = reactive_read(omf_map.widget, "layers")
        
        # Take a copy to prevent changes to the original dataframe
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
                
                gdfcopy = gdfcopy[["id", "cardinality"]]
                
                # Create the 'color' column with the good function
                gdfcopy['color'] = gdfcopy['cardinality'].apply(getColorComponents, args=(editData, ))

                # Convert to dictionary
                colorMap = gdfcopy.set_index('id')['color'].to_dict()
                
                layer.get_fill_color = apply_categorical_cmap(
                    values = gdfcopy["id"],
                    cmap = colorMap
                )

def hexToRgb255(hex):
    rgb = to_rgb(hex)
    return [int (255 * x) for x in rgb]
    
def getColorComponents(cardinality:int,
                       data:list):
    color = []
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