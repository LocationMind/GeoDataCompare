import json
import os
import time

start = time.time()

# Path of the github project, where we can find the bbox file
path = 'C:\\Users\\Mathis.Rouillard\\Documents\\OSM_Overture_Works'

# Path of the folder to save the layers
pathSave = os.path.join(path, "Data", "Result", "QGIS", "Overlap_results.gpkg")

# Proportion result variable to write into a file
result = ""
pathResult = os.path.join(path, "Data", "Result", "Comparison_OSM-OMF_PgRouting", "Overlap.txt")

# Load the 3 bbox that we will use from the json file
pathJSON = os.path.join(path, "Data", "Bbox", "bboxs.json")
with open(pathJSON, "r") as f:
    bboxJson = json.load(f)

# Template strings for the table we need and save path
OSMDatabase = 'postgres://dbname=\'osm-pgrouting\' host=127.0.0.1 port=5432 key=\'tid\' srid=4326 type=LineString checkPrimaryKeyUnicity=\'0\' table="public"."{}_with_cost" (geom)'

OMFDatabase = 'postgres://dbname=\'overturemap-pgrouting\' host=127.0.0.1 port=5432 key=\'id\' srid=4326 type=LineString checkPrimaryKeyUnicity=\'1\' table="public"."edge_with_cost_{}" (geom)'

pathSaveTemplate = 'ogr:dbname=\'{}\' table="{}" (geom)'

# For each area, we calculate the overlapping of OSM over OMF and vice versa
for elem in bboxJson["bboxs"]:
    # Get the area name
    area = elem["area"]
    
    print(f"Start process for {area}")
    
    # Get the OSM and OMF tables
    OSMTable = OSMDatabase.format(area)
    OMFTable = OMFDatabase.format(area)
    
    # Create the two save paths
    pathSaveOSM = pathSaveTemplate.format(pathSave.replace('\\', '/'), f"Overlap_OSM_OMF_{area}")
    
    pathSaveOMF = pathSaveTemplate.format(pathSave.replace('\\', '/'), f"Overlap_OMF_OSM_{area}")
    
    print(pathSaveOSM)
    
    # Run the script for OSM roads overlapping OMF roads
    proportionOSM = processing.run("script:overlapindicator", {
        'INPUT':OSMTable,
        'INTERSECT':OMFTable,
        'BUFFERDIST':1,
        'TARGETEPSG':QgsCoordinateReferenceSystem('EPSG:6691'),
        'OUTPUT':pathSaveOSM})['PROPORTION']
        
    end = time.time()
    print(f"It took {end - start} seconds")
    
    proportionOMF = processing.run("script:overlapindicator", {
        'INPUT':OMFTable,
        'INTERSECT':OSMTable,
        'BUFFERDIST':1,
        'TARGETEPSG':QgsCoordinateReferenceSystem('EPSG:6691'),
        'OUTPUT':pathSaveOMF})['PROPORTION']
        
    end = time.time()
    print(f"It took {end - start} seconds")
    
    result += f"{area} - OSM Value : {proportionOSM}\n"
    result += f"{area} - OMF Value : {proportionOMF}\n"

# Write the result as a file
with open(pathResult, 'w') as f:
    f.writelines(result)

end = time.time()
print(f"It took {end - start} seconds in total")