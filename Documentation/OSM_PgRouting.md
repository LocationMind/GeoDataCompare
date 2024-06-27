# Using PgRouting with OSM data integrated with OSMnx

- [Using PgRouting with OSM data integrated with OSMnx](#using-pgrouting-with-osm-data-integrated-with-osmnx)
- [Import data into the database](#import-data-into-the-database)
  - [Download OSMnx](#download-osmnx)
  - [Import data with OSMnx](#import-data-with-osmnx)
- [Data modification for PgRouting](#data-modification-for-pgrouting)
  - [Initial data model](#initial-data-model)
  - [Data needed for pgr\_djikstra algorithm](#data-needed-for-pgr_djikstra-algorithm)
  - [pgr\_djikstra with initial graph provided by OSMnx](#pgr_djikstra-with-initial-graph-provided-by-osmnx)


# Import data into the database

## Download OSMnx

The best way to download OSMnx and all necessary dependecies is to create a python virtual environment and to download all the packages describe in the requirement.in file.
Of course, it is necessary to have python installed on your computer.
You can also see [this website](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for Linux command to install the virtual environment.

To do so, please run the following command in the folder you want to work in :

**Installing a virtual environment**
```console
py -m venv .venv
```

**Activate a virtual environment**
```console
.venv\Scripts\activate
```

Once activate, you can **deactivate** it by running the following command :
```console
.venv\Scripts\deactivate.bat
```

**Installing the dependencies**

```console
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

Once it is done, all the necessary dependencies should be installed.

## Import data with OSMnx

Using OSMnx, importing modified data almost compatible with pgrouting is quite easy.
The best way to do it is probably to download data using a bounding box (bbox).
Make sure that the bbox is not too large because OSMnx uses memory for the data download and integration.

Then, you can use the python script to download and integrate data into PostgreSQL : [OSM_pgrouting.py](../Python/OSM_pgrouting.py)

Be careful about these points :

- Change `bbox` by your own bbox. The function `bboxCsvToTuple` is used to transform the bbox provided by [this tool](https://boundingbox.klokantech.com/) developped by [Klokantech](https://www.klokantech.com/) when copying in CSV format.
If you use an other format, the function will not be working anymore, so please ensure to either use this tool or change your bbox in the good format (north, south, east, west).

- `engine` is used to create a connection with the postgres database. Information is already registered in it, but you can change the URL connection if you need. The URL format is `postgresql://myusername:mypassword@myhost:5432/mydatabase`, where 5432 is the port of the database.

- If you want to change the name of the node or edge table, please change the first variable of the `to_postgis` function.

This way, the data are registered into the database, and almost ready to use with PgRouting.

# Data modification for PgRouting

## Initial data model

Using OSMnx, it is possible to choose which type of road one want to download.
In the python script mentionned before, only driving road are downloaded.
OSMnx tranform OSM data into a multi directional graph (MultiDiGraph type of NetworkX, see [here](https://networkx.org/documentation/stable/reference/classes/multidigraph.html) for more details).
Each edge is connected between exactly 2 nodes.
When there are no restrictions about road access (i.e. it is possible to go in the two directions), then 2 edges will be created.
The difference between these two edges is that the source and target are reversed (`e1.u = e2.v AND e1.v = e2.u`).
Most of the time, one has the reverse attribute as `False` and the other has it as `True`.
The geometry are also similar, but not exactly the same (so it is not possible to join two entitys by their geometry just by doing `e1.geometry=e2.geometry` for instance).
Here is an example of two roads in reversed direction.

![2 similar roads on a map](./Images/similar-road-OSM-data.png)

If you check their attributes, they share the same osmid (meaning that the same road in OSM have been used to create these roads), but they have reversed u and v values.
Also, the "reversed" attribute is False for one and True for the other.
The "id" attribute was created in PostgreSQL as an easy way to identify a road.
Initial primary key on the edge table is the tuple (u, v , key).

![Attributes of these 2 roads](./Images/attributes-similar-road-OSM-data.png)

## Data needed for pgr_djikstra algorithm

For pgr_djikstra, we need an edge table with the following attributes :

| Name | *id* | *source* | *target* | *cost* | *reverse_cost* | *geometry* |
| - | - | - | - | - | - | - |
| **Signification** | Id of the road| Source node| Target node| Cost to go from source to target (`-1` if not possible)| cost to go from target to source (`-1` if not possible)| Geometry of the road|

It seems possible to map the edge table provided by OSMnx to the edge table necessary for pgr_djikstra algorithm.
However, I still have not succeeded to do so.
I think that we should probably first create the table(empty) and insert data according to multiple scenarios :

1. If `u = v`, that means that it is a loop. We should see if it is on only one way (max(key) = 0) or not (max(key)>0). But even if max(key)>0, it is still possible that it is just two different road, so maybe we should do another verification such as seeing if one entity is inside the buffer of another one (buffer contains the road, not only intersects).
2. If `u1 = v2 AND u2 = v1`, then it is possible that the road is two directions (forward and backward). To verify this, we can check for each roads that validate this condition (with a group by or window function it may be possible to verify for each road verifying this condition) if the buffer of one road contains the other road and vice versa. If so, it is the same road and we can make a row in the table, with `cost = reverse_cost = length(geometry)`. If it is not, then we check if other roads verifying `u1 = v2 AND u2 = v1` exists and we do the same tests. If no roads verify this condition, then we insert a row in the table with `length(geometry)` as the `cost` (or `reverse_cost`, depending on the value of `reversed`).
3. For other roads that do not verify the two conditions above, we insert a row in the table with `length(geometry)` as the `cost` (or `reverse_cost`, depending on the value of `reversed`).

It is possible to do this using GeoPandas: see the [OSM_pgrouting.py](../Python/OSM_pgrouting.py) file for more information.

## pgr_djikstra with initial graph provided by OSMnx

It is possible to keep the initial graphed (Multi directed graph) provided by OSMnx for pgr_djikstra algorithm, by setting the cost value to the length of the road and setting -1 to each segment.
Indeed, two geometry for one road is not a problem because when it happensm the source and target are reversed, and by putting a cost of -1 to the reverse cost, we ensure that the graph is well constructed.

To launch the `pgr_djikstra` algorithm with OSM data, run the following SQL requets to add `cost` and `reverse_cost` column to the edge table :

```SQL
ALTER TABLE edge_tokyo
	ADD COLUMN cost double precision;

ALTER TABLE edge_tokyo
	ADD COLUMN reverse_cost double precision DEFAULT(-1);

UPDATE edge_tokyo
	SET cost = length; -- length is an attribute already calculated by OSMnx
    -- We could also do SET cost = ST_Length(ST_Tranform(geometry, 6691))
```

Then, by choosing two nodes in the graph, you can run the following SQL request :

```SQL
SELECT seq, edge, dij."cost", geometry
FROM pgr_dijkstra(
    'SELECT id, u AS source, v AS target, cost, reverse_cost
FROM edge_tokyo'::text,
    256677064,
	254360859,
	directed := false) dij
JOIN edge_tokyo AS e ON edge = e.id
ORDER BY seq
```

Be sure to write `u AS source` and `v AS target` otherwise the algorithm will not work.

The result is : 

![Result for pg_routing test with OSM data](./Images/result_OSM_pgrouting_test.png)