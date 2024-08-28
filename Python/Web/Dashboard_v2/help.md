# How to use the application

The sidebar (available in every page) is used to control the layers and change their style.

The rest of the application is made to visualise layers and interact with the map.
The two maps views are connected, so whenever you move one map, the other one will be updated
with the same view within a second usually.

The two tables contains information about the number of edges and the total length in kilometer of the edge dataset for the selected area.
These tables will be loaded each time that a new area is selected and loaded, but it will remain constant if you only change the criterion.
You can only check the rows, but select them will have no effect on the maps as it is currently not possible to filter easily layers with LonBoard 

## Necessary components

The application connects to a **PostgreSQL Database** to load the different layers.
It relies on a single layer table "bounding_box" that stores the information of the different test areas,
particularly with a unique key representing the name of the area (e.g. `Tokyo` or `Hiroshima`).
There will be as many selects as rows in this table.

The layers displayed in the OSM (resp. OMF) map container must be saved in a schema named `osm`
(resp. `omf`) for the original dataset, or in a schema named `results` where the table has
"osm" (resp. `omf`) as a suffix (e.g. `osm.edge_with_cost_tokyo` or `results.overlap_indicator_tokyo_osm`)

If the database does not respect this architecture, then the application might not be working correctly.

## Load layer

To load layer, you simply have to choose an area and the criterion that you want to display.

Each choice correspond to one or several tables stored in the database:

- *Road network* : `<schema>.edge_with_cost_<area>` for nodes and `<schema>.edge_with_cost_<area>` for edges.

- *Buildings* : `<schema>.building_<area>`.

- *Places / Points of interest* : `<schema>.place_<area>`.

- *Connected components* : `results.connected_components_<area>_<schema>`.

- *Strongly connected components* : `results.strong_components_<area>_<schema>`.

- *Isolated nodes* : `results.isolated_nodes_<area>_<schema>`.

- *Overlap indicator* : `results.overlap_indicator_<area>_<schema>`.

- *Corresponding nodes* : `results.corresponding_nodes_<area>_<schema>`.

Where `<area>` is the name of the area (in lowercase), e.g. `tokyo` and `<schema>` the name of the schema corresponding to the map (either `osm` or `omf`).

## Change layer style

In the sidebar, you have options to change the style of the layer.
Depending on the current criterion displayed, the modification made might not be working.
The value of `Radius min pixel`, `Width min pixel`, and `Line min pixel` are common to all layer and are respectively forpoint layers, line layers, and polygon layers.
Otherwise, each criterion has its own style, the `Connected components` and `Strongly connected components` sharing the same one.

For the `Style components` part, it is not possible to add more classes to the dataframe, nor to remove some.
The first minimun value has to be `1` and the last maximum value has to be `max`, you cannot change them.
You can sort the dataframe but it is not recommended, as whenever the dataframe is sorted, it will not be possible to any value of the dataframe, and the sorting will be reset every time you will try to change a value.
For the colors, you can choose one with the color picker above the dataframe to help you choosing the color you want.
You can either enter an hex value (with the `#` before, otherwise it will not work) or directly the name of a color (such as `black`, `red` or `purple`) directly in the cell to apply your modification, or in the color picker input to see what the color might look like.
If the input is not compatible with a color, nothing will happen and the value will not be changed in the dataframe.

## Change theme

You can change the theme of the application between dark and light by clicking on the Moon or Sun logo, depending on your current theme.
By default, the view used for the application will be the default view of your device.