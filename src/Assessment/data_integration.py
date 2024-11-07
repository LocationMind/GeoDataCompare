import sys
import os
import osmnx as ox
import time
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.Utils import utils
from src.Assessment import osm
from src.Assessment import omf

# Number of seconds in total
total = 0

# Database and schema names
schema_omf = "omf"
schema_osm = "osm"

createBoundingBoxTable = True

# Get connection initialise DuckDB and postgreSQL
connection = utils.getConnection()
utils.initialiseDuckDB()
utils.initialisePostgreSQL(connection)

# Get engine for geopandas
engine = utils.getEngine()

# Create bounding box table if needed
if createBoundingBoxTable:
    utils.createBoundingboxTable(connection)
    print("Bounding box table is created")
else:
    print("The bounding box table was not created")

# Limit date of data
ox.settings.overpass_settings = (
    '[out:json][timeout:{timeout}]{maxsize}[date:"2024-09-30T23:59:59Z"]'
)

curdir = os.getcwd()

# Load the 3 bbox that we will use from the json file
pathJson = os.path.join(curdir, "Data", "bboxs.json")
folderSave = os.path.join(curdir, ".temp")

# Create save folder if it does not exists
if not os.path.isdir(folderSave):
    os.makedirs(folderSave)

# Template names for layers
placeTable = "place_{}"
buildingTable = "building_{}"
edgeTable = "edge_with_cost_{}"
nodeTable = "node_{}"

# If true, will recreate all tables even if they already exists
skipBuildingCheck = False
skipPlaceCheck = False
skipGraphCheck = False

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
        connection=connection,
        wktGeom=wktGeom,
        aeraName=area.capitalize(),
        tableName="bounding_box",
    )

    end = time.time()
    print(f"Insert bounding box of {area}: {end - start} seconds")

    print()

    ### Places ###
    ## OMF
    # Check if the process has already been done
    if not utils.isProcessAlreadyDone(
        connection, placeTable.format(area), schema_omf, skipPlaceCheck
    ):

        omf.createPlaceFromBbox(
            bbox=bbox, savePathFolder=folderSave, area=area, schema=schema_omf
        )

        end = time.time()
        print(f"OMF places of {area}: {end - start} seconds")

    else:
        print("OMF places already downloaded")

    ## OSM
    # Check if the process has already been done
    if not utils.isProcessAlreadyDone(
        connection, placeTable.format(area), schema_osm, skipPlaceCheck
    ):

        osm.createPlaceFromBbox(
            connection=connection,
            engine=engine,
            bbox=bbox,
            area=area,
            schema=schema_osm,
        )

        end = time.time()
        print(f"OSM places of {area}: {end - start} seconds")

    else:
        print("OSM places already downloaded")

    print()

    ### Buildings ###
    ## OMF
    # Check if the process has already been done
    if not utils.isProcessAlreadyDone(
        connection, buildingTable.format(area), schema_omf, skipBuildingCheck
    ):

        omf.createBuildingFromBbox(
            bbox=bbox, savePathFolder=folderSave, area=area, schema=schema_omf
        )

        end = time.time()
        print(f"OMF buildings of {area}: {end - start} seconds")

    else:
        print("OMF buildings already downloaded")

    ## OSM
    # Check if the process has already been done
    if not utils.isProcessAlreadyDone(
        connection, buildingTable.format(area), schema_osm, skipBuildingCheck
    ):

        osm.createBuildingFromBbox(
            engine=engine, bbox=bbox, area=area, schema=schema_osm
        )

        end = time.time()
        print(f"OSM buildings of {area}: {end - start} seconds")

    else:
        print("OSM buildings already downloaded")

    print()

    ### Graph ###
    ## OMF
    # Check if the process has already been done
    if not (
        utils.isProcessAlreadyDone(
            connection, edgeTable.format(area), schema_omf, skipGraphCheck
        )
        and utils.isProcessAlreadyDone(
            connection, nodeTable.format(area), schema_omf, skipGraphCheck
        )
    ):

        # New version
        omf.createGraphFromBboxNewVersion(
            bbox=bbox,
            savePathFolder=folderSave,
            area=area,
            connection=connection,
            schema=schema_omf,
        )

        end = time.time()
        print(f"OMF graph of {area}: {end - start} seconds")

    else:
        print("OMF graph already downloaded")

    ## OSM
    # Check if the process has already been done
    if not (
        utils.isProcessAlreadyDone(
            connection, edgeTable.format(area), schema_osm, skipGraphCheck
        )
        and utils.isProcessAlreadyDone(
            connection, nodeTable.format(area), schema_osm, skipGraphCheck
        )
    ):

        osm.createGraphFromBbox(
            connection=connection,
            engine=engine,
            bbox=bbox,
            area=area,
            schema=schema_osm,
        )

        end = time.time()
        print(f"OSM graph of {area}: {end - start} seconds")

    else:
        print("OSM graph already downloaded")

    end = time.time()
    print(f"Download everything for {area}: {end - start} seconds")
    print()

    total += end - start


print(f"It took {total} seconds in total")
