import os
import time

def calculateTranlationBetweenLayers(inputLayer, overlayLayer, path):
    """This function calculate the propotion of area tranlated from the first layer to the second one.
    It also returns the total area in the difference layer and in the inputLayer

    Args:
        inputLayer (_type_): _description_
        overlayLayer (_type_): _description_
    """
    print()

start = time.time()

# Get project and path of the project
project = QgsProject.instance()
projectPath = project.fileName()
(path, fileName) = os.path.split(projectPath)

# Get layers from map
inputLayerName = "epsg_6677_building_bbox"
inputLayer = project.mapLayersByName(inputLayerName)[0]

overlayLayerName = "epsg_6677_buffer_planet_osm_building"
overlayLayer = project.mapLayersByName(overlayLayerName)[0]

## Calculate the difference between the two layers
pathDifference = os.path.join(path, f"Difference_{inputLayer.name()}-{overlayLayer.name()}.gpkg")
tableName = f"Difference_{inputLayer.name()}-{overlayLayer.name()}"

# If the difference has already been calculated, we only take the layer
if len(project.mapLayersByName(tableName)) == 0:
    
    difference = processing.run("native:difference",
        {'INPUT':inputLayer,
        'OVERLAY':overlayLayer,
        'OUTPUT':f"ogr:dbname='{pathDifference}' table=\"{tableName}\"",
        'GRID_SIZE':None})
    
    differenceLayer = QgsVectorLayer(difference["OUTPUT"], tableName, "ogr")
    # Add layer to the map
    project.addMapLayer(differenceLayer)
else:
    differenceLayer = project.mapLayersByName(tableName)[0]


end = time.time()
print(f"Difference took {end-start} seconds")

## Calculate the area of each entity of the difference to calculate the final proportion

# Create an other layer to visualise the difference

pathCopy = os.path.join(path, "Copy_difference.gpkg")
tableNameCopy = "Copy_difference"
# To do a copy, we use an intern algorithm of QGIS
differenceLayer.selectAll()

copyDifferenceLayerPath = processing.run("native:saveselectedfeatures",
    {'INPUT': differenceLayer,
    'OUTPUT': f"ogr:dbname='{pathCopy}' table=\"{tableNameCopy}\""})['OUTPUT']

differenceLayer.removeSelection()

copyDifferenceLayer = QgsVectorLayer(copyDifferenceLayerPath, tableNameCopy, 'ogr')

# Features id to remove from the 
featuresIdToRemove = []

totalAreaDifference = 0
# Parse all features to calculate the area
for feature in differenceLayer.getFeatures():
    featureArea = feature.geometry().area()
    # If the feature area is under 0.01 m2 (= 100cm2), we do not take it and remove it from the copyDifferenceLayer
    if featureArea <= 0.01:
        featuresIdToRemove.append(feature.id())
    else:
        totalAreaDifference += featureArea

end = time.time()
print(f"Total area difference took {end-start} seconds")

# Remove from the clone layer the feature with an area < 500 cm2
with edit(copyDifferenceLayer):
    dataProvider = copyDifferenceLayer.dataProvider()
    dataProvider.deleteFeatures(featuresIdToRemove)

end = time.time()
print(f"Delete features took {end-start} seconds")

## Calculate the total area of the input layer
totalAreaInputLayer = 0
for feature in inputLayer.getFeatures():
    totalAreaInputLayer += feature.geometry().area()

end = time.time()
print(f"Total area input layer took {end-start} seconds")

proportion = totalAreaDifference / totalAreaInputLayer

print(f"The proportion is {proportion} %")

project.addMapLayer(copyDifferenceLayer)

end = time.time()
print(f"The script took {end-start} seconds")

""" TODO
- Calculate area of each entity of the difference, and for those under 1 cm2, do not add them
- Calculate area of each entity in the input layer, and add them to the total entity
- Calculate the proportion
- Do it in the other way (overlay firt and input as overlay)
- Calculate the number of entity in each layer
- Recalculate the nu;ber of entity in each layer, but this time by creating a grid before.
"""