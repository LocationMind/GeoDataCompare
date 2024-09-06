# How to use the application

The sidebar (available in every page) is used to control the layers and change their style.

The rest of the application is made to visualise layers and interact with the map.
The two maps views are connected, so whenever you move one map, the other one will be updated
with the same view within a second usually.

The two tables contains information about the number of edges and the total length in kilometer of the edge dataset for the selected area.
These tables will be loaded each time that a new area is selected and loaded, but it will remain constant if you only change the criterion.
You cannot select the table rows.

## Load layer

To load layer, you simply have to choose an area and the criterion that you want to display.

Each choice corresponds to one or several tables stored in the database, and for each layer, a criterion is calculated. In the following list, `<area>` is the name of the area (in lowercase), e.g. `tokyo`, and `<schema>` is the name of the schema corresponding to the map (either `osm` or `omf`):

- **Graph**:

    - *Original dataset*: Original graph dataset, where both edges (with cost) and nodes are represented.
    The total length of the dataset in kilometres is calculated, based on the edge with cost layer. The corresponding layers are `<schema>.node_<area>` for nodes and `<schema>.edge_with_cost_<area>` for edges.

    - *Connected components*: The connected components of a graph correspond to the different connected subgraphs (i.e. in this subgraph, it is possible to go from every node to another one) that are not part of a larger connected subgraph.
    Visit the <a href="https://en.wikipedia.org/wiki/Component_(graph_theory)" target="_blank" rel="noopener noreferrer">Wikipedia page</a> for more information about connected components of a graph.
    Edges of the graph are also represented for the connected components (you might want to increase the width of nodes to see them more clearly).
    The number of connected components of each graph is calculated.
    The corresponding layer is `results.connected_components_<area>_<schema>` for connected components and `<schema>.edge_with_cost_<area>` for edges.

    - *Strongly connected components*: The strongly connected components of a graph correspond to the different strongly connected subgraphs (i.e., in this subgraph, for every pair of vertices (u,v), there exists a path from u to v and another path from v to u) that are not part of a larger strongly connected subgraph.
    Visit the <a href="https://en.wikipedia.org/wiki/Strongly_connected_component" target="_blank" rel="noopener noreferrer">Wikipedia page</a> for more information about strongly connected components of a graph.
    Edges of the graph are also represented for the strongly connected components (you might want to increase the width of nodes to see the nodes more clearly).
    The number of strongly connected components of each graph is calculated.
    The corresponding layer is `results.strong_components_<area>_<schema>` for strongly connected components and `<schema>.edge_with_cost_<area>` for edges.

    - *Isolated nodes*: Isolated nodes are nodes that are not connected to the rest of the graph (i.e. there is no path coming from or to these nodes).
    The number of isolated nodes is calculated.
    The corresponding layer is `results.isolated_nodes_<area>_<schema>`.

    - *Overlap indicator*: For one dataset, the overlap indicator corresponds to the roads that are overlapping roads in the other dataset.
    Roads must be almost exactly the same to be considered overlapping (e.g. if there is a shift of 50 centimetres, roads will not be considered as overlapping).
    The percentage of overlapping roads for each dataset is calculated.
    The corresponding layer is `results.overlap_indicator_<area>_<schema>`.

    - *Corresponding nodes*: Corresponding nodes are nodes that can be found in both datasets (using an intersect condition).
    Both the number of corresponding nodes (same for each dataset) and the percentage of corresponding nodes per dataset (compared to the total number of nodes in the dataset) are calculated.
    The corresponding layer is `results.corresponding_nodes_<area>_<schema>`.

- **Buildings**:

    - *Buildings (coverage)*: Original building dataset.
    Buildings coverage in the area (percentage of building area in the test area) is calculated for this option.
    The corresponding layer is `<schema>.building_<area>`.

    - *Buildings (density)*: Original building dataset.
    Building density in the area (number of buildings per $km^2$) is calculated for this option.
    The corresponding layer is `<schema>.building_<area>`.

- **Places**:

    - *Places / Points of interest (density)*: Original places dataset.
    Place density in the area (number of places per $km^2$) is calculated for this option.
    The corresponding layer is `<schema>.place_<area>`.


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

## Change application theme

You can change the theme of the application between dark and light by clicking on the Moon or Sun logo, depending on your current theme.
By default, the view used for the application will be the default view of your device
<div class = "pb-3"></div>