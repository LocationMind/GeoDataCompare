# How to use the application

The sidebar (available on every page) is used to control the layers and change their style.

The rest of the application is made to visualise layers and interact with the map.
The two map views are connected, so whenever you move one map, the other will be updated
with the same view within a second, usually.

The two tables contain information about the number of edges and the total length in kilometres of the edge dataset for the selected area.
These tables will be loaded each time a new area is selected and loaded, but they will remain constant if you only change the criterion.
You cannot select the table rows.

## Load layer

To load a layer, you simply have to choose an area and the criterion that you want to display.

Each choice corresponds to one or several tables stored in the database, and for each layer, a criterion is calculated.
In the following list, `<area>` is the name of the area (in lowercase), e.g. `tokyo`, and `<schema>` is the name of the schema corresponding to the map (either `osm` or `omf`):


- **Graph**:

    - *Original dataset*: Original graph dataset, where both edges (with cost) and nodes are represented.
    The total length of the dataset in kilometres is calculated, based on the edge with cost layer.
    The corresponding layers are `<schema>.node_<area>` for nodes and `<schema>.edge_with_cost_<area>` for edges.

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
    Building coverage in the area (percentage of building area in the test area) is calculated for this option.
    The corresponding layer is `<schema>.building_<area>`.

    - *Buildings (density)*: Original building dataset.
    Building density in the area (number of buildings per km&sup2;) is calculated for this option.
    The corresponding layer is `<schema>.building_<area>`.

- **Places**:

    - *Places / Points of interest (density)*: Original places dataset.
    Place density in the area (number of places per km&sup2;) is calculated for this option.
    The corresponding layer is `<schema>.place_<area>`.

    - *Places grid density*: Grid of 100 * 100 metres over the area with the number of places per grid.
    Place density in the area (number of places per km&sup2;) is calculated for this option.
    The corresponding layer is `results.density_places_grid_<area>_<schema>`.

## Change layer style

In the sidebar, you have options to change the style of the layer.
Depending on the current criterion displayed, the modification made might not work.
The values of `Radius min pixel`, `Width min pixel`, and `Line min pixel` are common to all layers and are respectively for point layers, line layers, and polygon layers.
Otherwise, each criterion has its own style, with the `Connected components`, `Strongly connected components` and `Places grid density` sharing the same one.

For the `Style range` part, it is not possible to add more classes to the dataframe, nor to remove any.
The first minimum value must be `0`, and the last maximum value must be `max`; you cannot change them.
You can sort the dataframe, but it is not recommended, as whenever the dataframe is sorted, it will not be possible to change any value of the dataframe, and the sorting will be reset every time you try to change a value.
For the colours, you can choose one with the colour picker above the dataframe to help you select the colour you want.
You can either enter a hex value (with the `#` before, otherwise it will not work) or directly enter the name of a colour (such as `black`, `red`, or `purple`) in the cell to apply your modification, or in the colour picker input to see what the colour might look like.
If the input is not compatible with a colour, nothing will happen, and the value will not be changed in the dataframe.

You can also choose to reset the value by setting the **Style adapted to places (grid)** switch to true or false.
If it is true, the colours and numbers will be adapted to the grid for the places, while if it is false, they will be adapted for the (strongly) connected components.

## Change application theme

You can change the theme of the application between dark and light by clicking on the Moon or Sun logo, depending on your current theme.
By default, the view used for the application is the light view.
<div class="pb-3"></div>

# User and developer documentation

Please refer to the <a href="https://github.com/LocationMind/OSM_Overture_Works" target="_blank" rel="noopener noreferrer">GitHub project</a> for more information about the user and developer documentation.
The user documentation can be found <a href="https://github.com/LocationMind/OSM_Overture_Works/blob/main/Documentation/user-doc.md" target="_blank" rel="noopener noreferrer">here</a>, while the developer documentation is located <a href="https://github.com/LocationMind/OSM_Overture_Works/blob/main/Documentation/dev-doc.md" target="_blank" rel="noopener noreferrer">here</a>.