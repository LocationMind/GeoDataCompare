# How to use the application

The sidebar (available in every page) is used to control the layers and change their style.

The rest of the application is made to visualise layers and interact with the map.
The two maps views are connected, so whenever you move one map, the other one will be updated
with the same view within a second usually.

The two tables contains information about the number of edges and the total length in kilometer of the edge dataset for the selected area.
These tables will be loaded each time that a new area is selected and loaded, but it will remain constant if you only change the criterion.
You can only check the rows, but select them will have no effect on the maps as it is currently not possible to filter easily layers with LonBoard 

## Necessary components

The application connects to a PostgreSQL Database to load the different layers.
It relies on a single layer table "bounding_box" that stores the information of the different test areas,
particularly with a unique key representing the name of the area (e.g. "Tokyo" or "Hiroshima").
There will be as many selects as rows in this table.

The layers displayed in the OSM (resp. OMF) map container must be saved in a schema named `osm`
(resp. `omf`) for the original dataset, or in a schema named `results` where the table has
"osm" (resp. `omf`) as a suffix (e.g. `osm.edge_with_cost_tokyo` or `results.overlap_indicator_tokyo_osm`)

If the database does not respect this architecture, then the application might not be working correctly.

## Load layer

To load layer, you simply have to choose an area and the criterion that you want to display.

If you choose the *Original dataset*, then both nodes and edges of the area will be loaded, respectively in tables `.

For the other criterion, the following tables will be loaded:

- 

# Hello 2
