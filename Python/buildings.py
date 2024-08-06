import duckdb
import geopandas as gpd
import osmnx as ox
import os
import utils
import data_integration as di


def createBuildingTableOMF(bbox: str,
                           savePathFolder: str,
                           area:str,
                           buildingTable:str,
                           schema:str = "public",
                           deleteDataWhenFinish:bool = True):
    """Create building table from a bbox using overturemaps.py tool.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        aeraName (str): Name of the area.
        buildingTable (str): Name of the building table to create.
        schema (str, optional): Name of the schema for saving the tables.
        Defaults to "public".
        deleteDataWhenFinish (bool, optional): Delete downloaded at the end of the
        process if True. Defaults to True.
    """
    # Download building data
    pathBuildingFile = utils.downloadOMFTypeBbox(bbox, savePathFolder, "building")
    
    # Create the road table and get its extent
    di.createBuildingTable(pathBuildingFile, buildingTable, schema = schema)
    
    # Delete the downloaded data if user wants
    if deleteDataWhenFinish:
        # Segment file
        if os.path.isfile(pathBuildingFile):
            os.remove(pathBuildingFile)
            print(f"{pathBuildingFile} has been deleted")
        else:
            print(f"{pathBuildingFile} is not a file")


def createBuildingTableOSM(bbox: str) -> gpd.GeoDataFrame:
    """Create building table from a bbox.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
    """
    # Tags to download buildings only
    tags = {"building": True}
    
    # Bbox 
    bboxTuple = utils.bboxCSVToTuple(bbox)
    
    # Download building data
    gdf = ox.features_from_bbox(bbox=bboxTuple, tags=tags)
    
    # Rename geometry clumn and export
    gdf = gdf.rename(columns={'geometry':'geom'})
    gdf = gdf.set_geometry("geom")
    
    return gdf

if __name__ == "__main__":
    import time
    import json
    start = time.time()
    
    # Database and schema names
    database = "pgrouting"
    
    # Get connection initialise DuckDB and postgreSQL
    connection = utils.getConnection(database)
    utils.initialisePostgreSQL(connection)
    utils.initialiseDuckDB(database)
    
    # Get engine for geopandas
    engine = utils.getEngine(database)
    
    # Limit date of data
    ox.settings.overpass_settings = '[out:json][timeout:{timeout}]{maxsize}[date:"2024-05-01T00:00:00Z"]'
    
    # Load the 3 bbox that we will use from the json file
    pathJson = os.path.join(".", "Data", "Bbox", "bboxs.json")
    folderSave = os.path.join(".", "Data", ".temp")
    
    with open(pathJson, "r") as f:
        bboxJson = json.load(f)
    
    # Create tables for each bbox
    for elem in bboxJson["bboxs"]:
        # Get the element we need from the json
        bbox = elem["bbox"]
        areaBbox = elem["area"]
        area = elem["area"].lower()
        
        if area == 'tokyo':
            
            print(f"Start process {areaBbox}")
            extractBuilding = f"building_{area}"
            
            ## OMF
            # Create OMF table
            createBuildingTableOMF(
                bbox = bbox,
                savePathFolder= folderSave,
                area = area,
                buildingTable = extractBuilding,
                schema = "omf",
                deleteDataWhenFinish = True)
            
            ## OSM
            # Download OSM data
            # gdf = createBuildingTableOSM(bbox)
            
            # gdf = gdf.loc["way"][:]
            
            # print(gdf)
            
            # print(gdf.index)
            
            # # Export gdf to PostGIS
            # gdf.to_postgis(extractBuilding, engine, if_exists="replace", schema="osm", index=True, index_label="osmid")