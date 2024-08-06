import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Python import utils
from Python import osm
from Python import omf
import osmnx as ox
import time
import json


# Number of seconds in total
total = 0

# Database and schema names
database = "locationmind"
schema_omf = "omf"
schema_osm = "osm"

# Get connection initialise DuckDB and postgreSQL
connection = utils.getConnection(database)
utils.initialisePostgreSQL(connection)
utils.initialiseDuckDB(database)

# Get engine for geopandas
engine = utils.getEngine(database)

# Create bounding box table
utils.createBoundingboxTable(connection)

print("Bounding box table is created")

# Limit date of data
ox.settings.overpass_settings = '[out:json][timeout:{timeout}]{maxsize}[date:"2024-06-07T23:59:59Z"]'

curdir = os.getcwd()

print(curdir)

# Load the 3 bbox that we will use from the json file
pathJson = os.path.join(curdir, "Data", "Bbox", "bboxs.json")
folderSave = os.path.join(curdir, "Data", ".temp")

with open(pathJson, "r") as f:
    bboxJson = json.load(f)

# Create tables for each bbox
for elem in bboxJson["bboxs"]:
    # Reset timer
    start = time.time()
    # Get the element we need from the json
    bbox = elem["bbox"]
    area = elem["area"].lower()
    
    print(f"Start process {area.capitalize()}")
    
    ## Insert bounding box
    # Tranform bbox to OGC WKT format and insert into bounding box table 
    wktGeom = utils.bboxCSVToBboxWKT(bbox)

    # Insert bbox in bounding box table
    utils.insertBoundingBox(
        connection = connection,
        wktGeom = wktGeom,
        aeraName = area.capitalize(),
        tableName = "bounding_box")
    
    end = time.time()
    print(f"Insert bounding box of {area}: {end - start} seconds")
    
    if area == "paris" or area == "higashihiroshima":
        
        print(f"Download OSM buildings for {area}")
        
        osm.createBuildingFromBbox(
            engine = engine,
            bbox = bbox,
            area = area,
            schema = schema_osm
        )
        
        end = time.time()
        print(f"OSM buildings of {area}: {end - start} seconds")
    
#     print()
    
#     ### Places ###
#     ## OMF
    
#     omf.createPlaceFromBbox(
#         bbox = bbox,
#         savePathFolder = folderSave,
#         area = area,
#         schema = schema_omf
#     )
    
#     end = time.time()
#     print(f"OMF places of {area}: {end - start} seconds")
    
#     ## OSM
    
#     osm.createPlaceFromBbox(
#         engine = engine,
#         bbox = bbox,
#         area = area,
#         schema = schema_osm
#     )
    
#     end = time.time()
#     print(f"OSM places of {area}: {end - start} seconds")
    
#     print()
    
#     ### Buildings ###
#     ## OMF
    
#     omf.createBuildingFromBbox(
#         bbox = bbox,
#         savePathFolder = folderSave,
#         area = area,
#         schema = schema_omf
#     )
    
#     end = time.time()
#     print(f"OMF buildings of {area}: {end - start} seconds")
    
#     ## OSM
    
#     osm.createBuildingFromBbox(
#         engine = engine,
#         bbox = bbox,
#         area = area,
#         schema = schema_osm
#     )
    
#     end = time.time()
#     print(f"OSM buildings of {area}: {end - start} seconds")
    
#     print()
    
#     ### Graph ###
#     ## OMF
    
#     omf.createGraph(
#         bbox = bbox,
#         savePathFolder = folderSave,
#         area = area,
#         connection = connection,
#         schema = schema_omf
#     )
    
#     end = time.time()
#     print(f"OMF graph of {area}: {end - start} seconds")
    
#     ## OSM
    
#     osm.createGraph(
#         connection = connection,
#         engine = engine,
#         bbox = bbox,
#         area = area,
#         schema = schema_osm
#     )
    
#     end = time.time()
#     print(f"OSM graph of {area}: {end - start} seconds")
    
#     end = time.time()
#     print(f"Download everything for {area}: {end - start} seconds")
#     print()
    
#     total += end
    

# print(f"It took {total} seconds in total")