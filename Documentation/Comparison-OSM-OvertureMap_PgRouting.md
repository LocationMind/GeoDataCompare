# Comparison betweem OpenStreetMap and OvertureMap Foundation data with PgRouting

- [Comparison betweem OpenStreetMap and OvertureMap Foundation data with PgRouting](#comparison-betweem-openstreetmap-and-overturemap-foundation-data-with-pgrouting)
- [Dataset creation](#dataset-creation)
- [Comparison process](#comparison-process)
	- [Tests zone](#tests-zone)
	- [Create vertices / nodes table](#create-vertices--nodes-table)
	- [Criteria for graph analysis](#criteria-for-graph-analysis)
		- [Number of nodes](#number-of-nodes)
		- [Number of kilometer (total / by class)](#number-of-kilometer-total--by-class)
- [Results](#results)
	- [General results](#general-results)
	- [Specific results](#specific-results)
		- [Total kilometer of roads by type](#total-kilometer-of-roads-by-type)

# Dataset creation

To create the two datasets, please refer to the documentation for each data type:

- OvertureMap : [OvertureMap_data.md (section Djikstra Algorithm)](./OvertureMap_data.md)

- OpenStreetMap : [OSM_PgRouting.md](./OSM_PgRouting.md)

# Comparison process

## Tests zone

3 different areas have been chosen for testing PgRouting algorithm:

- **Tokyo** (urban area) : bbox = `139.74609375, 35.67514743608467, 139.833984375, 35.7465122599185`

![Tokyo area](./Images/tokyo_area.png)

- **Hamamatsu** (sub-urban area) : bbox = `137.63671875, 34.66935854524544, 137.724609375, 34.74161249883172`

![Hamamatsu area](./Images/hamamatsu_area.png)

- **Tateyama** (rural area) : bbox = `139.833984375, 34.95799531086791, 139.921875, 35.02999636902566`

![Tateyama area](./Images/tateyama_area.png)

These areas are represented here too, in a global view:

![Test aresa](./Images/test_areas.png)

For **OpenStreetMap (OSM) dataset**, the names of the edge tables are :

- Tokyo : `tokyo_with_cost`
- Hamamatsu : `hamamatsu_with_cost`
- Tateyama : `tateyama_with_cost`

For **OvertureMap foundation (OMF) dataset**, the names of the edge tables are :

- Tokyo : `edge_with_cost_tokyo`
- Hamamatsu : `edge_with_cost_hamamatsu`
- Tateyama : `edge_with_cost_tateyama`



## Create vertices / nodes table

To have vertices that are well associated to the graph, we can use the `pgr_createVerticesTable` function of PgRouting.
To do so, just run the following SQL query in PostgreSQL, by replacing `edge` and `geom` respectively by the name of your edge table and the name of the geometry column:

```sql
SELECT pgr_createVerticesTable('edge', 'geom');
```

The vertices table will have the name of the edge table with `_vertices_pgr` at the end.
It is better to let the name like this, as some PgRouting function works with this vertices table without possibility to change the name of it in the function.

## Criteria for graph analysis

Two compare and assess the quality of those datasets, we can use different criteria, intrinsic and extrinsic ones too.
Here is a list of criteria that we used:

- Number of nodes;
- Number of roads entity (in total and by class);
- Number of roads kilometer (in total and by class);
- Number of connected components;
- Number of isolated nodes;
- Sort nodes by number of roads getting in / out of it.
- Spatial extent of one dataset comparing to the another for ways (i.e. pourcentage of dataset A overlaping dataset B and vice versa);
- Number of associated nodes in both dataset.

To calculate those criteria, we can use PgRouting functions, writing SQL request or using python and geopandas / networkx packages.

### Number of nodes

Without needing PgRouting functions, we can easily find the number of nodes in each dataset.
The SQL query is the following:

```sql
SELECT
	(SELECT count(*) FROM tokyo_with_cost_vertices_pgr) as vertice_number_tokyo,
	(SELECT count(*) FROM hamamatsu_with_cost_vertices_pgr) as vertice_number_hamamatsu,
	(SELECT count(*) FROM tateyama_with_cost_vertices_pgr) as vertice_number_tateyama;
```

For OMF data, we need to keep only thos inside the bounding box (it is not necessary to do it with OSM data as it was constructed such as no vertices or edges are outside the bounding box).
Please be sure to have only one bounding box with the name that you will use, otherwise use the id of the bounding box it will be easier.
Here is the SQL query:

```sql
SELECT
	(
		SELECT count(*)
		FROM edge_with_cost_tokyo_vertices_pgr AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.the_geom)
		WHERE b.name = 'tokyo'
	) as vertice_number_tokyo,
	(
		SELECT count(*)
		FROM edge_with_cost_hamamatsu_vertices_pgr AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.the_geom)
		WHERE b.name = 'hamamatsu'
	) as vertice_number_hamamatsu,
	(
		SELECT count(*)
		FROM edge_with_cost_tateyama_vertices_pgr AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.the_geom)
		WHERE b.name = 'tateyama'
	) as vertice_number_tateyama;
```

### Number of kilometer (total / by class)

To calculate the number of kilometer it is not more complicated than for the number of nodes.
The `CEILING` function is use to avoid a too large number of decimal.

Total kilometer query:

**OSM**
```sql
SELECT
	(SELECT CEILING(SUM(ST_Length(geom::geography)) / 1000) FROM tokyo_with_cost) as total_kilometer_tokyo,
	(SELECT CEILING(SUM(ST_Length(geom::geography)) / 1000) FROM hamamatsu_with_cost) as total_kilometer_hamamatsu,
	(SELECT CEILING(SUM(ST_Length(geom::geography)) / 1000) FROM tateyama_with_cost) as total_kilometer_tateyama;
```

**OMF**
```sql
SELECT
	(
		SELECT CEILING(SUM(ST_Length(e.geom::geography)) / 1000)
		FROM edge_with_cost_tokyo AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
		WHERE b.name = 'tokyo'
	) as total_kilometer_tokyo,
	(
		SELECT CEILING(SUM(ST_Length(e.geom::geography)) / 1000)
		FROM edge_with_cost_hamamatsu AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
		WHERE b.name = 'hamamatsu'
	) as total_kilometer_hamamatsu,
	(
		SELECT CEILING(SUM(ST_Length(e.geom::geography)) / 1000)
		FROM edge_with_cost_tateyama AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
		WHERE b.name = 'tateyama'
	) as total_kilometer_tateyama;
```

To have the result by class, we simply have to add a `GROUP BY class` clause in the request.
However, because the result will not be given in one line, each request must be run separately.
Also, it is better to use the round function to truncate the result to two decimals here as there are many classes, so by letting `CEILING`, we raise the risk of having bad values.

It is easier to transform OSM classes into OMF classes, as these classes have been created from OSM classes.
Also, we might want to have 21 rows in the results (ie one row per class), even though the class does not exist in the data.
To do so, we can change slightly the query to include all results.
For OSM data, the mapping has been done according to what is written in this document: [mapping_OSM_to_OMF](./mapping_OSM_to_OMF.md).

**OSM**
```sql
WITH table_new_classes AS
(
	SELECT id,
	geom,
	-- New class creations
	CASE
		WHEN class = 'motorway' OR class = 'motorway_link' THEN 'motorway'
		WHEN class = 'trunk' OR class = 'trunk_link' THEN 'trunk'
		WHEN class = 'primary' OR class = 'primary_link' THEN 'primary'
		WHEN class = 'secondary' OR class = 'secondary_link' THEN 'secondary'
		WHEN class = 'tertiary' OR class = 'tertiary_link' THEN 'tertiary'
		WHEN class = 'residential' OR (class = 'unclassified' AND abutters = 'residential') THEN 'residential'
		WHEN class = 'living_street' THEN 'living_street'
		WHEN class = 'service' AND service = 'parking_aisle' THEN 'parking_aisle'
		WHEN class = 'service' AND service = 'driveway' THEN 'driveway'
		WHEN class = 'service' AND service = 'alley' THEN 'alley'
		WHEN class = 'pedestrian' THEN 'pedestrian'
		WHEN (class = 'footway' OR class = 'path') AND footway = 'sidewalk' THEN 'sidewalk'
		WHEN (class = 'footway' OR class = 'path') AND footway = 'crosswalk' THEN 'crosswalk'
		WHEN class = 'footway' THEN 'footway'
		WHEN class = 'path' THEN 'path'
		WHEN class = 'steps' THEN 'steps'
		WHEN class = 'track' THEN 'track'
		WHEN class = 'cycleway' THEN 'cycleway'
		WHEN class = 'bridleway' THEN 'bridleway'
		WHEN class = 'unclassified' THEN 'unclassified'
		ELSE 'unknown'
	END AS new_class
	FROM public.tokyo_with_cost
),
OMF_classes AS (
    SELECT unnest(ARRAY[
        'alley', 'bridleway', 'cycleway', 'driveway', 'footway', 'living_street',
        'motorway', 'parking_aisle', 'path', 'pedestrian', 'primary', 'residential',
        'secondary', 'sidewalk', 'steps', 'tertiary', 'trunk', 'unclassified', 'unknown',
        'crosswalk', 'track'
    ]) AS new_class
)
SELECT 
    omf.new_class AS new_class,
    COALESCE(join_table.length_kilometer, 0) AS length_kilometer,
    COALESCE(join_table.nb_entity, 0) AS nb_entity
FROM OMF_classes AS omf
LEFT JOIN (
	SELECT new_class,	
	round((SUM(ST_Length(geom::geography)) / 1000)::numeric, 2) as length_kilometer,
	count(*) as nb_entity
	FROM table_new_classes
	GROUP BY new_class
) join_table
USING (new_class)
ORDER BY omf.new_class ASC;
```

**OMF**
```sql
WITH OMF_classes AS (
    SELECT unnest(ARRAY[
        'alley', 'bridleway', 'cycleway', 'driveway', 'footway', 'living_street',
        'motorway', 'parking_aisle', 'path', 'pedestrian', 'primary', 'residential',
        'secondary', 'sidewalk', 'steps', 'tertiary', 'trunk', 'unclassified', 'unknown',
        'crosswalk', 'track'
    ]) AS new_class
)
SELECT 
    omf.new_class AS new_class,
    COALESCE(join_table.length_kilometer, 0) AS length_kilometer,
    COALESCE(join_table.nb_entity, 0) AS nb_entity
FROM OMF_classes AS omf
LEFT JOIN (
	SELECT e.class AS new_class,
	round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2) as length_kilometer,
	count(e.class) AS nb_entity
	FROM edge_with_cost_tokyo AS e
	JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
	WHERE b.name = 'tokyo'
	GROUP BY class
) join_table
USING (new_class)
ORDER BY omf.new_class ASC;
```

# Results

## General results

| **Criterion** | **Area** | **OSM Value** | **OMF Value** |
| --- | --- | --- | --- |
| **Number of nodes** | *Tokyo* | 62613 | 66230 | 
| **Number of nodes** | *Hamamatsu* | 26409 | 27858 |
| **Number of nodes** | *Tateyama* | 5962 | 6143 |
|  |  |  |  |
| **Total Kilometer** | *Tokyo* | 3176 | 3153 | 
| **Total Kilometer** | *Hamamatsu* | 1756 | 1755 |
| **Total Kilometer** | *Tateyama* | 604 | 604 |
|  |  |  |  |
| **Criterion** | *Tokyo* | xxx | yyy | 
| **Criterion** | *Hamamatsu* | xxx | xxx |
| **Criterion** | *Tateyama* | xxx | xxx |
|  |  |  |  |
| **Criterion** | *Tokyo* | xxx | yyy | 
| **Criterion** | *Hamamatsu* | xxx | xxx |
| **Criterion** | *Tateyama* | xxx | xxx |
|  |  |  |  |
| **Criterion** | *Tokyo* | xxx | yyy | 
| **Criterion** | *Hamamatsu* | xxx | xxx |
| **Criterion** | *Tateyama* | xxx | xxx |
|  |  |  |  |
| **Criterion** | *Tokyo* | xxx | yyy | 
| **Criterion** | *Hamamatsu* | xxx | xxx |
| **Criterion** | *Tateyama* | xxx | xxx |
|  |  |  |  |

## Specific results

### Total kilometer of roads by type

Missing values correspond to no value in the dataset.

**For Tokyo**: 

| class          | OSM   | OMF   |
|----------------|-------|-------|
| alley          |       | 143.63|
| bridleway      |       | 0.02  |
| busway         | 0.17  |       |
| corridor       | 0.11  |       |
| crosswalk      |       | 43.17 |
| cycleway       | 10.22 | 10.55 |
| driveway       |       | 12.77 |
| elevator       | 0.05  |       |
| footway        | 1090.40| 686.37|
| living_street  | 0.14  | 0.16  |
| motorway       | 48.79 | 72.26 |
| motorway_link  | 24.36 |       |
| parking_aisle  |       | 15.17 |
| path           | 34.43 | 34.26 |
| pedestrian     | 27.20 | 27.64 |
| primary        | 101.69| 104.20|
| primary_link   | 2.56  |       |
| residential    | 691.48| 689.98|
| road           | 0.13  |       |
| secondary      | 129.83| 131.70|
| secondary_link | 1.93  |       |
| service        | 298.75|       |
| sidewalk       |       | 348.45|
| steps          | 28.30 | 18.89 |
| tertiary       | 231.61| 233.89|
| tertiary_link  | 2.14  |       |
| trunk          | 57.02 | 58.90 |
| trunk_link     | 1.89  |       |
| unclassified   | 392.26| 392.86|
| unknown        |       | 127.86|


**For Hamamatsu**:

| class          | OSM    | OMF    |
|----------------|--------|--------|
| alley          |        | 13.92  |
| crosswalk      |        | 8.41   |
| driveway       |        | 19.34  |
| footway        | 280.68 | 236.26 |
| motorway       | 5.44   | 7.61   |
| motorway_link  | 2.17   |        |
| parking_aisle  |        | 107.45 |
| path           | 35.02  | 35.98  |
| pedestrian     | 2.45   | 2.42   |
| primary        | 38.69  | 38.71  |
| primary_link   | 0.02   |        |
| residential    | 583.74 | 584.44 |
| secondary      | 23.55  | 23.55  |
| service        | 197.71 |        |
| sidewalk       |        | 36.22  |
| steps          | 7.70   | 4.21   |
| tertiary       | 178.51 | 178.60 |
| tertiary_link  | 0.02   |        |
| track          | 62.82  | 65.91  |
| trunk          | 24.22  | 26.32  |
| trunk_link     | 2.10   |        |
| unclassified   | 310.43 | 308.61 |
| unknown        |        | 56.85  |


**For Tateyama**: 

| class          | OSM    | OMF    |
|----------------|--------|--------|
| alley          |        | 33.34  |
| crosswalk      |        | 2.66   |
| driveway       |        | 3.59   |
| footway        | 12.78  | 8.38   |
| parking_aisle  |        | 6.11   |
| path           | 53.26  | 51.71  |
| pedestrian     | 0.05   | 0.84   |
| primary        | 5.95   | 5.95   |
| residential    | 261.91 | 261.55 |
| secondary      | 24.59  | 24.59  |
| service        | 59.48  |        |
| sidewalk       |        | 2.57   |
| steps          | 0.50   | 0.30   |
| tertiary       | 35.12  | 34.86  |
| track          | 102.00 | 102.56 |
| trunk          | 22.82  | 22.82  |
| unclassified   | 25.43  | 25.98  |
| unknown        |        | 15.55  |
