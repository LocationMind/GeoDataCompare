import os

project = QgsProject.instance()

projectPath = project.fileName()

(path, fileName) = os.path.split(projectPath)

inputLayerName = "building_bbox"
overlayLayerName = "epsg_4326_buffer_planet_osm_building"

inputLayer = project.mapLayersByName(inputLayerName)[0]
overlayLayer = project.mapLayersByName(overlayLayerName)[0]

pathDifference = os.path.join(path, f"Difference {inputLayer.name()} - {overlayLayer.name()}")

difference = processing.run("native:difference",
    {'INPUT':inputLayer,
    'OVERLAY':overlayLayer,
    'OUTPUT':pathDifference,
    'GRID_SIZE':None})

""" TODO
- Calculate area of each entity of the difference, and for those under ! cm2, do not add them
- Calculate area of each entity in the input layer, and add them to the total entity
- Calculate the proportion
- Do it in the other way (overlay firt and input as overlay)
- Calculate the number of entity in each layer
- Recalculate the nu;ber of entity in each layer, but this time by creating a grid before.
"""