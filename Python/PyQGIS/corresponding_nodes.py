import json
import os
import time

start = time.time()

# Path of the github project, where we can find the bbox file
path = 'C:\\Users\\Mathis.Rouillard\\Documents\\OSM_Overture_Works'

# Proportion result variable to write into a file
result = ""
pathResult = os.path.join(path, "Data", "Result", "Comparison_OSM-OMF_PgRouting", "Corresponding_nodes.txt")

# Database connection
OSMDatabase = QgsDataSourceUri()
OSMDatabase.setConnection("127.0.0.1", "5432", "osm-pgrouting", 'postgres', 'postgres')
OSMDatabase.setGeometryColumn('geom')
OSMDatabase.setSchema('public')

OMFDatabase = QgsDataSourceUri()
OMFDatabase.setConnection("127.0.0.1", "5432", "overturemap-pgrouting", 'postgres', 'postgres')
OMFDatabase.setGeometryColumn('geom')
OMFDatabase.setSchema('public')

# Bounding box
OMFDatabase.setTable('bounding_box')
boundingBox = QgsVectorLayer(OMFDatabase.uri(), 'bounding_box', 'postgres')

end = time.time()
print(f"Database connection : {end - start} seconds")

# Load the 3 bbox that we will use from the json file
pathJSON = os.path.join(path, "Data", "Bbox", "bboxs.json")
with open(pathJSON, "r") as f:
    bboxJson = json.load(f)

# For each area, we calculate the overlapping of OSM over OMF and vice versa
for elem in bboxJson["bboxs"]:
    # Get the area name
    area = elem["area"]
    
    print(f"Start process for {area}")
    
    # Change OSM and OMF table
    OSMDatabase.setTable(f"node_{area}")
    OMFDatabase.setTable(f"vertice_{area}")
    
    # Load layers
    OSMLayer = QgsVectorLayer(OSMDatabase.uri(), f"node_{area} algo", 'postgres')
    OMFLayer = QgsVectorLayer(OMFDatabase.uri(), f"vertice_{area} algo", 'postgres')
    
    end = time.time()
    print(f"Load layers : {end - start} seconds")
    
    # Add them temporary
    
    QgsProject.instance().addMapLayer(OSMLayer, False)
    QgsProject.instance().addMapLayer(OMFLayer, False)
    
    # Select OMF nodes only in the bounding box
    processing.run("native:selectbylocation", {
        'INPUT':OMFLayer,
        'INTERSECT':boundingBox,
        'PREDICATE':[0],
        'METHOD':0})
    
    # Take the number of nodes inside the bbox as the total number of nodes for OMF dataset
    totalFeatureOMF = OMFLayer.selectedFeatureCount()
    
    end = time.time()
    print(f"OMF selection over bounding box : {end - start} seconds")
    
    # OSM dataset
    processing.run("native:selectbylocation", {
        'INPUT':OSMLayer,
        'INTERSECT':QgsProcessingFeatureSourceDefinition(OMFLayer.id(), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'PREDICATE':[0],
        'METHOD':0})
    
    totalFeatureOSM = OSMLayer.dataProvider().featureCount()
    selectedFeatureOSM = OSMLayer.selectedFeatureCount()
    
    end = time.time()
    print(f"OSM selection : {end - start} seconds")
    
    processing.run("native:selectbylocation", {
        'INPUT':OMFLayer,
        'INTERSECT':OSMLayer,
        'PREDICATE':[0],
        'METHOD':2})
    
    selectedFeatureOMF = OMFLayer.selectedFeatureCount()
    
    # Remove selection
    OSMLayer.removeSelection()
    OMFLayer.removeSelection()
    
    # Remove layer
    QgsProject.instance().removeMapLayer(OSMLayer.id())
    QgsProject.instance().removeMapLayer(OMFLayer.id())
    
    end = time.time()
    print(f"OMF Final selection : {end - start} seconds")
    
    # Add result to the file
    result += f"{area} - OSM Total nodes : {totalFeatureOSM}\n"
    result += f"{area} - OSM Corresponding nodes : {selectedFeatureOSM}\n"
    result += f"{area} - OSM Proportion : {selectedFeatureOSM / totalFeatureOSM} ({(selectedFeatureOSM / totalFeatureOSM) * 100} %)\n"
    result += f"{area} - OMF Total nodes : {totalFeatureOMF}\n"
    result += f"{area} - OMF Corresponding nodes : {selectedFeatureOMF}\n"
    result += f"{area} - OMF Proportion : {selectedFeatureOMF / totalFeatureOMF} ({(selectedFeatureOMF / totalFeatureOMF) * 100} %)\n"
    
# Write the result as a file
with open(pathResult, 'w') as f:
    f.writelines(result)

end = time.time()
print(f"It took {end - start} seconds in total")