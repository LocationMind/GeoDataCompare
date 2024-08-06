import duckdb
import geopandas as gpd
import osmnx as ox
import os
import utils
import data_integration as di


def createPlaceTableOMF(bbox: str,
                        savePathFolder: str,
                        area:str,
                        placeTable:str,
                        schema:str = "public",
                        deleteDataWhenFinish:bool = True):
    """Create place table from a bbox using overturemaps.py tool.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        aeraName (str): Name of the area.
        placeTable (str): Name of the place table to create.
        schema (str, optional): Name of the schema for saving the tables.
        Defaults to "public".
        deleteDataWhenFinish (bool, optional): Delete downloaded at the end of the
        process if True. Defaults to True.
    """
    # Create file names
    placeFile = f"place_{area}"
    
    # Download place data
    pathPlaceFile = utils.downloadOMFTypeBbox(bbox, savePathFolder, "place", placeFile)
    
    # Create the road table and get its extent
    di.createPlaceTable(pathPlaceFile, placeTable, schema = schema)
    
    # Delete the downloaded data if user wants
    if deleteDataWhenFinish:
        # Segment file
        if os.path.isfile(pathPlaceFile):
            os.remove(pathPlaceFile)
            print(f"{pathPlaceFile} has been deleted")
        else:
            print(f"{pathPlaceFile} is not a file")


def createPlaceTableOSM(bbox: str) -> gpd.GeoDataFrame:
    """Create building table from a bbox.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
    """
    # Tags to download buildings only
    tags = {"amenity": True, "shop" : True}
    
    # Bbox
    bboxTuple = utils.bboxCSVToTuple(bbox)
    
    # Download poi data
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
    ox.settings.overpass_settings = '[out:json][timeout:{timeout}]{maxsize}[date:"2024-05-01T23:59:59Z"]'
    
    curdir = os.getcwd()
    
    print(curdir)
    
    # Load the 3 bbox that we will use from the json file
    pathJson = os.path.join(curdir, "Data", "Bbox", "bboxs.json")
    folderSave = os.path.join(curdir, "Data", ".temp")
    
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
            
            extractPlace = f"place_{area}"
            
            ## OMF
            # Create OMF table
            # createPlaceTableOMF(
            #     bbox = bbox,
            #     savePathFolder= folderSave,
            #     area = area,
            #     placeTable = extractPlace,
            #     schema = "omf",
            #     deleteDataWhenFinish = True)
            
            end = time.time()
            print(f"OMF : {end - start} seconds")
            
            ## OSM
            # Download OSM data
            gdf = createPlaceTableOSM(bbox)
            
            # Reset index and set only osmid as the index
            gdf = gdf.reset_index()
            gdf = gdf.set_index('osmid')
            
            # Colunmns that needs to be keepen
            columnsToKeep = [
                'amenity',
                'shop',
                'addr:full',
                'geom',
                'name',
                'brand',
                'phone',
                'source',
                'website',
                'lolikolol',
                'email'
            ]
            
            # columns that needs to be renamed
            columnsRenamed = {
                'addr:full' : 'address',
                'lolikolol' : 'kokoko',
            }
            
            # Filter on column name, so if there are no column no error will be raised
            columnsBool = gdf.columns.isin(columnsToKeep)
            columns = gdf.columns[columnsBool]
            
            # Filter only columns find in the data
            gdf = gdf[columns]
            
            # Rename column
            gdf = gdf.rename(columns=columnsRenamed)
            
            # Get centroid of geometry
            gdf["geom"] = gdf["geom"].centroid
            
            # Export gdf to PostGIS
            gdf.to_postgis(extractPlace, engine, if_exists="replace", schema="osm", index=True, index_label="id")
            
            end = time.time()
            print(f"OSM : {end - start} seconds")