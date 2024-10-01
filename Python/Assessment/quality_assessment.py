import os
import pandas as pd
import psycopg2
import sys
import time
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Python.Utils import utils
from Python.Assessment import quality


# Value for the time taken
start = time.time()

# Get today's date and hour for the result    
now = datetime.datetime.now()
dateTimeMarkdown = now.strftime("%d/%m/%Y %H:%M")

# Path to save the results
fileName = "Automatic_result.md"
curdir = os.getcwd()
pathSave = os.path.join(curdir, "Results", fileName)

# Connect to the database and give table template for OSM and OMF dataset
connection = utils.getConnection()

# Template for OpenStreetMap
osmSchema = 'osm'
osmEdgeTableTemplate = "edge_with_cost_{}"
osmNodeTableTemplate = "node_{}"
osmBuildingTableTemplate = "building_{}"
osmPlaceTableTemplate = "place_{}"

# Template for Overture Map Fundation
omfSchema = 'omf'
omfEdgeTableTemplate = "edge_with_cost_{}"
omfNodeTableTemplate = "node_{}"
omfBuildingTableTemplate = "building_{}"
omfPlaceTableTemplate = "place_{}"


# Variable for markdown results
mappingResult = "### Total kilometer of roads by class"

# Data to add to the dataFrame
data = []

# Schema for saving result as tables
schemaResult = 'results'
# Templates table names for saving (1st : area / 2nd: dataset)
connectedComponentsTemplate = "connected_components_{}_{}"
strongConnectedComponentsTemplate = "strong_components_{}_{}"
isolatedNodesTemplate = "isolated_nodes_{}_{}"
overlapIndicatorTemplate = "overlap_indicator_{}_{}"
correspondingNodesTemplate = "corresponding_nodes_{}_{}"
densityPlacesGridTemplate = "density_places_grid_{}_{}"

# Get list of areas from the bounding box table
bounding_box_table = "bounding_box"
listAreas = quality.getListAreas(connection)

for area in listAreas:
    print(f"Start quality analysis for {area}")
    
    # Get edge and node tables
    osmEdgeTable = osmEdgeTableTemplate.format(area.lower())
    osmNodeTable = osmNodeTableTemplate.format(area.lower())
    osmBuildingTable = osmBuildingTableTemplate.format(area.lower())
    osmPlaceTable = osmPlaceTableTemplate.format(area.lower())
    
    omfEdgeTable = omfEdgeTableTemplate.format(area.lower())
    omfNodeTable = omfNodeTableTemplate.format(area.lower())
    omfBuildingTable = omfBuildingTableTemplate.format(area.lower())
    omfPlaceTable = omfPlaceTableTemplate.format(area.lower())
    
    # Capitalize the area name to be able to filter with the bounding box
    area = area.capitalize()
    
    # Add lines to before and after mapping results
    mappingResult += f"\n\n#### *{area}*:\n\n"
    
    
    # Number of nodes
    OSMValue = quality.getNumberElements(connection, osmSchema, osmNodeTable)    
    OMFValue = quality.getNumberElements(connection, omfSchema, omfNodeTable)
    
    data.append(["**1. Number of nodes**", f"*{area}*", OSMValue, OMFValue])
    
    end = time.time()
    print(f"Number of nodes: {end - start} seconds")
    
    
    # Number of edges
    OSMValue = quality.getNumberElements(connection, osmSchema, osmEdgeTable)
    OMFValue = quality.getNumberElements(connection, omfSchema, omfEdgeTable)
    
    data.append(["**2. Number of edges**", f"*{area}*", OSMValue, OMFValue])
    
    end = time.time()
    print(f"Number of edges: {end - start} seconds")
    
    
    # Total length kilometer
    OSMValue = quality.getTotalLengthKilometer(connection, osmSchema, osmEdgeTable)    
    OMFValue = quality.getTotalLengthKilometer(connection, omfSchema, omfEdgeTable)
    
    data.append(["**3. Total length (km)**", f"*{area}*", OSMValue, OMFValue])
    
    end = time.time()
    print(f"Total length kilometer: {end - start} seconds")
    
    
    # Total length kilometer per class
    listClassesOSM = quality.getLengthKilometerPerClass(connection, osmSchema, osmEdgeTable)
    listClassesOMF = quality.getLengthKilometerPerClass(connection, omfSchema, omfEdgeTable)
    
    markdown = quality.listsToMardownTable(listClassesOSM, listClassesOMF)
    # Add markdown results
    mappingResult += markdown
    
    end = time.time()
    print(f"Total length kilometer per class: {end - start} seconds")
    
    
    # Connected components
    resultOSMTable = connectedComponentsTemplate.format(area.lower(), osmSchema)
    resultOMFTable = connectedComponentsTemplate.format(area.lower(), omfSchema)
    
    OSMValue = quality.getConnectedComponents(connection, osmSchema, osmEdgeTable, resultAsTable=resultOSMTable, schemaResult=schemaResult, nodeTableName=osmNodeTable)
    OMFValue = quality.getConnectedComponents(connection, omfSchema, omfEdgeTable, resultAsTable=resultOMFTable, schemaResult=schemaResult, nodeTableName=omfNodeTable)
    
    data.append(["**4. Number of connected components**", f"*{area}*", OSMValue, OMFValue])
    
    end = time.time()
    print(f"Connected components: {end - start} seconds")
    
    
    # Strong connected components
    resultOSMTable = strongConnectedComponentsTemplate.format(area.lower(), osmSchema)
    resultOMFTable = strongConnectedComponentsTemplate.format(area.lower(), omfSchema)
    
    OSMValue = quality.getStrongConnectedComponents(connection, osmSchema, osmEdgeTable, resultAsTable=resultOSMTable, schemaResult=schemaResult, nodeTableName=osmNodeTable)    
    OMFValue = quality.getStrongConnectedComponents(connection, omfSchema, omfEdgeTable, resultAsTable=resultOMFTable, schemaResult=schemaResult, nodeTableName=omfNodeTable)
    
    data.append(["**5. Number of strong connected components**", f"*{area}*", OSMValue, OMFValue])
    
    end = time.time()
    print(f"Strong connected components: {end - start} seconds")
    
    
    # Isolated nodes
    resultOSMTable = isolatedNodesTemplate.format(area.lower(), osmSchema)
    resultOMFTable = isolatedNodesTemplate.format(area.lower(), omfSchema)
    
    OSMValue = quality.getIsolatedNodes(connection, osmSchema, osmEdgeTable, osmNodeTable, resultAsTable=resultOSMTable, schemaResult=schemaResult)
    OMFValue = quality.getIsolatedNodes(connection, omfSchema, omfEdgeTable, omfNodeTable, resultAsTable=resultOMFTable, schemaResult=schemaResult)
    
    data.append(["**6. Number of isolated nodes**", f"*{area}*", OSMValue, OMFValue])
    
    end = time.time()
    print(f"Isolated nodes: {end - start} seconds")
    
    
    # Overlap indicator
    resultOSMTable = overlapIndicatorTemplate.format(area.lower(), osmSchema)
    resultOMFTable = overlapIndicatorTemplate.format(area.lower(), omfSchema)
    
    OSMValue = quality.getOverlapIndicator(connection, osmSchema, osmEdgeTable, omfSchema, omfEdgeTable, resultAsTable=resultOSMTable, schemaResult=schemaResult)
    
    end = time.time()
    print(f"Overlap indicator 1: {end - start} seconds")
    
    OMFValue = quality.getOverlapIndicator(connection, omfSchema, omfEdgeTable, osmSchema, osmEdgeTable, resultAsTable=resultOMFTable, schemaResult=schemaResult)
    
    end = time.time()
    print(f"Overlap indicator 2: {end - start} seconds")
    
    # Add data to the data list
    data.append([f"**7. Overlap indicator (%)**", f"*{area}*", OSMValue, OMFValue])
    
    
    # Corresponding nodes
    resultOSMTable = correspondingNodesTemplate.format(area.lower(), osmSchema)
    resultOMFTable = correspondingNodesTemplate.format(area.lower(), omfSchema)
    
    OSMValue = quality.getCorrespondingNodes(connection, osmSchema, osmNodeTable, omfSchema, omfNodeTable, resultAsTable=resultOSMTable, schemaResult=schemaResult)
    OMFValue = quality.getCorrespondingNodes(connection, omfSchema, omfNodeTable, osmSchema, osmNodeTable, resultAsTable=resultOMFTable, schemaResult=schemaResult)
    
    # Add two rows in the dataframe (one for the number and the other for percentage)
    data.append(["**8. Number of corresponding nodes**", f"*{area}*", OSMValue[0], OMFValue[0]])
    data.append(["**9. Percentage of corresponding nodes (%)**", f"*{area}*", OSMValue[1], OMFValue[1]])
    
    end = time.time()
    print(f"Corresponding nodes: {end - start} seconds")
    
    
    # Density grid places
    resultOSMTable = densityPlacesGridTemplate.format(area.lower(), osmSchema)
    resultOMFTable = densityPlacesGridTemplate.format(area.lower(), omfSchema)
    
    OSMValue = quality.getDensityPlaceGrid(connection, osmSchema, osmPlaceTable, area = area.capitalize(), boundingBoxTable = bounding_box_table, resultAsTable=resultOSMTable, schemaResult=schemaResult)
    OMFValue = quality.getDensityPlaceGrid(connection, omfSchema, omfPlaceTable, area = area.capitalize(), boundingBoxTable = bounding_box_table, resultAsTable=resultOMFTable, schemaResult=schemaResult)
    
    # Add two rows in the dataframe (one for the number and the other for percentage)
    data.append(["**10. Places density**", f"*{area}*", OSMValue, OMFValue])
    
    end = time.time()
    print(f"Density grid places: {end - start} seconds")
    
    
    end = time.time()
    print(f"{area}: {end - start} seconds")


# Sort data per Criterion / Area
data.sort(key= lambda a: (a[0], a[1]))

# Create dataframe to export as markdown in the end
columns = ['**Criterion**', '**Area**', '**OSM Value**', '**OMF Value**']
df = pd.DataFrame(data=data, columns=columns)

df['**Difference (abs)**'] = abs(df["**OSM Value**"] - df["**OMF Value**"])

print()
# Export to markdown table
generalResults = df.to_markdown(index=False, tablefmt="github")

# Create final markdown
exportMarkdown = f"""# Quality criterias result between OpenStreetMap and Overture Maps Foundation datasets

The test were run on {dateTimeMarkdown}, using the 2024-09-18.0 release of Overture Maps Foundation data and the OpenStreetMap data until 2024-08-31.

## General results

{generalResults}

## Specific results

{mappingResult}
"""

# Export the results to a markdown file
with open(pathSave, 'w') as f:
    f.writelines(exportMarkdown)

end = time.time()
print(f"Process ended in {end - start} seconds")