# Comparison betweem OpenStreetMap and OvertureMap Foundation data with PgRouting

- [Comparison betweem OpenStreetMap and OvertureMap Foundation data with PgRouting](#comparison-betweem-openstreetmap-and-overturemap-foundation-data-with-pgrouting)
- [Dataset creation](#dataset-creation)
- [Comparison process](#comparison-process)
	- [Tests zone](#tests-zone)
	- [Criteria for graph analysis](#criteria-for-graph-analysis)
		- [Number of nodes](#number-of-nodes)
		- [Number of ways](#number-of-ways)
		- [Number of kilometer (total / by class)](#number-of-kilometer-total--by-class)
- [Results](#results)
	- [General results](#general-results)
	- [Specific results](#specific-results)
		- [Total kilometer of roads by type (before mapping)](#total-kilometer-of-roads-by-type-before-mapping)
		- [Total kilometer of roads by type (after mapping)](#total-kilometer-of-roads-by-type-after-mapping)

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

<!-- ## Create vertices / nodes table

To have vertices that are well associated to the graph, we can use the `pgr_createVerticesTable` function of PgRouting.
To do so, just run the following SQL query in PostgreSQL, by replacing `edge` and `geom` respectively by the name of your edge table and the name of the geometry column:

```sql
SELECT pgr_createVerticesTable('edge', 'geom');
```

The vertices table will have the name of the edge table with `_vertices_pgr` at the end.
It is better to let the name like this, as some PgRouting function works with this vertices table without possibility to change the name of it in the function. -->

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

For OMF data, we need to keep only ways and nodes inside the bounding box (it is not necessary to do it with OSM data as it was constructed such as no vertices or edges are outside the bounding box).
Please be sure to have only one bounding box with the name that you will use, otherwise use the id of the bounding box it will be easier.

### Number of nodes

Without needing PgRouting functions, we can easily find the number of nodes in each dataset.
The SQL queries are the following:

**OSM**
```sql
SELECT
	(SELECT count(*) FROM node_tokyo) as vertice_number_tokyo,
	(SELECT count(*) FROM node_hamamatsu) as vertice_number_hamamatsu,
	(SELECT count(*) FROM node_tateyama) as vertice_number_tateyama;
```

**OMF**
```sql
SELECT
	(
		SELECT count(*)
		FROM vertice_tokyo AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
		WHERE b.name = 'tokyo'
	) as vertice_number_tokyo,
	(
		SELECT count(*)
		FROM vertice_hamamatsu AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
		WHERE b.name = 'hamamatsu'
	) as vertice_number_hamamatsu,
	(
		SELECT count(*)
		FROM vertice_tateyama AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
		WHERE b.name = 'tateyama'
	) as vertice_number_tateyama;
```

### Number of ways

Without needing PgRouting functions, we can easily find the number of ways in each dataset.
The SQL queries are the following:

**OSM**
```sql
SELECT
	(SELECT count(*) FROM tokyo_with_cost) as ways_number_tokyo,
	(SELECT count(*) FROM hamamatsu_with_cost) as ways_number_hamamatsu,
	(SELECT count(*) FROM tateyama_with_cost) as ways_number_tateyama;
```

**OMF**
```sql
SELECT
	(
		SELECT count(*)
		FROM edge_with_cost_tokyo AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.the_geom)
		WHERE b.name = 'tokyo'
	) as ways_number_tokyo,
	(
		SELECT count(*)
		FROM edge_with_cost_hamamatsu AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.the_geom)
		WHERE b.name = 'hamamatsu'
	) as ways_number_hamamatsu,
	(
		SELECT count(*)
		FROM edge_with_cost_tateyama AS e
		JOIN bounding_box AS b ON ST_Contains(b.geom, e.the_geom)
		WHERE b.name = 'tateyama'
	) as ways_number_tateyama;
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
Also, it is better to use the round function to truncate the result to two decimals here as there are many classes, so by letting `CEILING`, we lower down the result uncertainty.

The query to do so before mapping OSM classes to OMF classes are these one:

**OSM**
```sql
SELECT class,
round((SUM(ST_Length(geom::geography)) / 1000)::numeric, 2) as length_kilometer,
count(*) as nb_entity
FROM tokyo_with_cost
GROUP by class
ORDER by class ASC;
```

**OMF**
```sql
SELECT e.class,
round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2) as length_kilometer,
count(e.class) AS nb_entity
FROM edge_with_cost_tokyo AS e
JOIN bounding_box AS b ON ST_Contains(b.geom, e.geom)
WHERE b.name = 'tokyo'
GROUP BY class
ORDER by class ASC;
```


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
| **Number of edges** | *Tokyo* | 109922 | 101206 | 
| **Number of edges** | *Hamamatsu* | 44444 | 39579 |
| **Number of edges** | *Tateyama* | 8419 | 7821 |
|  |  |  |  |
| **Total Kilometer** | *Tokyo* | 3197 | 3153 | 
| **Total Kilometer** | *Hamamatsu* | 1770 | 1755 |
| **Total Kilometer** | *Tateyama* | 626 | 604 |
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

### Total kilometer of roads by type (before mapping)

Missing values correspond to no value in the dataset.

**For Tokyo**:

| class | OSM - Total length (km) | OSM - Number of entities | OMF - Total length (km) | OMF - Number of entities |
|---|---|---|---|---|
| alley | | | 143.63 | 3976 |
| bridleway | 0.02 | 1 | 0.02 | 1 |
| busway | 0.17 | 10 | | |
| corridor | 0.13 | 15 | | |
| crosswalk | | | 43.17 | 5968 |
| cycleway | 11.23 | 191 | 10.55 | 181 |
| driveway | | | 12.77 | 461 |
| elevator | 0.05 | 8 | | |
| footway | 1097.29 | 47834 | 686.37 | 25806 |
| living_street | 0.16 | 7 | 0.16 | 7 |
| motorway | 63.21 | 176 | 72.26 | 195 |
| motorway_link | 23.98 | 207 | | |
| parking_aisle | | | 15.17 | 566 |
| path | 34.48 | 1047 | 34.26 | 1026 |
| pedestrian | 27.75 | 799 | 27.64 | 762 |
| primary | 103.18 | 2647 | 104.20 | 2544 |
| primary_link | 2.56 | 62 | | |
| residential | 690.78 | 20806 | 689.98 | 20722 |
| road | 0.13 | 3 | | |
| secondary | 130.65 | 3521 | 131.70 | 3405 |
| secondary_link | 2.00 | 61 | | |
| service | 300.32 | 8778 | | |
| sidewalk | | | 348.45 | 8817 |
| steps | 20.17 | 2033 | 18.89 | 1833 |
| tertiary | 232.71 | 7553 | 233.89 | 7463 |
| tertiary_link | 2.29 | 74 | | |
| trunk | 57.57 | 1460 | 58.90 | 1439 |
| trunk_link | 1.89 | 50 | | |
| unclassified | 393.81 | 12579 | 392.86 | 12468 |
| unknown | | | 127.86 | 3566 |

**For Hamamatsu**:

| class | OSM - Total length (km) | OSM - Number of entities | OMF - Total length (km) | OMF - Number of entities |
|---|---|---|---|---|
| alley | | | 13.92 | 320 |
| crosswalk | | | 8.41 | 1254 |
| driveway | | | 19.34 | 578 |
| footway | 282.98 | 10348 | 236.26 | 5337 |
| motorway | 6.64 | 23 | 7.61 | 18 |
| motorway_link | 2.17 | 16 | | |
| parking_aisle | | | 107.45 | 4761 |
| path | 36.88 | 988 | 35.98 | 835 |
| pedestrian | 2.43 | 41 | 2.42 | 36 |
| primary | 39.00 | 874 | 38.71 | 840 |
| primary_link | 0.02 | 2 | | |
| residential | 586.21 | 12868 | 584.44 | 12630 |
| secondary | 23.59 | 661 | 23.55 | 640 |
| service | 202.42 | 7887 | | |
| sidewalk | | | 36.22 | 743 |
| steps | 4.19 | 396 | 4.21 | 390 |
| tertiary | 179.85 | 4207 | 178.60 | 4048 |
| tertiary_link | 0.02 | 4 | | |
| track | 66.54 | 735 | 65.91 | 660 |
| trunk | 24.47 | 507 | 26.32 | 522 |
| trunk_link | 2.10 | 23 | | |
| unclassified | 310.03 | 4864 | 308.61 | 4531 |
| unknown | | | 56.85 | 1436 |


**For Tateyama**: 

| class | OSM - Total length (km) | OSM - Number of entities | OMF - Total length (km) | OMF - Number of entities |
|---|---|---|---|---|
| alley | | | 33.34 | 501 |
| crosswalk | | | 2.66 | 528 |
| driveway | | | 3.59 | 70 |
| footway | 13.84 | 802 | 8.38 | 158 |
| parking_aisle | | | 6.11 | 132 |
| path | 62.75 | 291 | 51.71 | 235 |
| pedestrian | 0.84 | 6 | 0.84 | 6 |
| primary | 6.09 | 67 | 5.95 | 57 |
| residential | 264.28 | 3875 | 261.55 | 3664 |
| secondary | 24.72 | 473 | 24.59 | 441 |
| service | 58.89 | 1034 | | |
| sidewalk | | | 2.57 | 41 |
| steps | 0.30 | 13 | 0.30 | 13 |
| tertiary | 36.49 | 500 | 34.86 | 481 |
| track | 105.01 | 776 | 102.56 | 681 |
| trunk | 23.30 | 288 | 22.82 | 259 |
| unclassified | 28.56 | 294 | 25.98 | 273 |
| unknown | | | 15.55 | 281 |

### Total kilometer of roads by type (after mapping)

Missing values correspond to no value in the dataset.

**For Tokyo**: 

| class | OSM - Total length (km) | OSM - Number of entities | OMF - Total length (km) | OMF - Number of entities |
|---|---|---|---|---|
| alley | 145.24 | 4030 | 143.63 | 3976 |
| bridleway | 0.02 | 1 | 0.02 | 1 |
| crosswalk | 0 | 0 | 43.17 | 5968 |
| cycleway | 11.23 | 191 | 10.55 | 181 |
| driveway | 13.19 | 480 | 12.77 | 461 |
| footway | 413.18 | 26980 | 686.37 | 25806 |
| living_street | 0.16 | 7 | 0.16 | 7 |
| motorway | 87.19 | 383 | 72.26 | 195 |
| parking_aisle | 16.49 | 621 | 15.17 | 566 |
| path | 34.09 | 1038 | 34.26 | 1026 |
| pedestrian | 27.75 | 799 | 27.64 | 762 |
| primary | 105.74 | 2709 | 104.20 | 2544 |
| residential | 690.78 | 20806 | 689.98 | 20722 |
| secondary | 132.66 | 3582 | 131.70 | 3405 |
| sidewalk | 684.50 | 20863 | 348.45 | 8817 |
| steps | 20.17 | 2033 | 18.89 | 1833 |
| tertiary | 235.00 | 7627 | 233.89 | 7463 |
| track | 0 | 0 | 0 | 0 |
| trunk | 59.45 | 1510 | 58.90 | 1439 |
| unclassified | 393.81 | 12579 | 392.86 | 12468 |
| unknown | 125.88 | 3683 | 127.86 | 3566 |

**For Hamamatsu**:

| class | OSM - Total length (km) | OSM - Number of entities | OMF - Total length (km) | OMF - Number of entities |
|---|---|---|---|---|
| alley | 14.44 | 340 | 13.92 | 320 |
| bridleway | 0 | 0 | 0 | 0 |
| crosswalk | 0 | 0 | 8.41 | 1254 |
| cycleway | 0 | 0 | 0 | 0 |
| driveway | 19.46 | 604 | 19.34 | 578 |
| footway | 74.44 | 5735 | 236.26 | 5337 |
| living_street | 0 | 0 | 0 | 0 |
| motorway | 8.81 | 39 | 7.61 | 18 |
| parking_aisle | 108.87 | 5461 | 107.45 | 4761 |
| path | 36.88 | 988 | 35.98 | 835 |
| pedestrian | 2.43 | 41 | 2.42 | 36 |
| primary | 39.02 | 876 | 38.71 | 840 |
| residential | 586.21 | 12868 | 584.44 | 12630 |
| secondary | 23.59 | 661 | 23.55 | 640 |
| sidewalk | 208.54 | 4613 | 36.22 | 743 |
| steps | 4.19 | 396 | 4.21 | 390 |
| tertiary | 179.86 | 4211 | 178.60 | 4048 |
| track | 66.54 | 735 | 65.91 | 660 |
| trunk | 26.57 | 530 | 26.32 | 522 |
| unclassified | 310.03 | 4864 | 308.61 | 4531 |
| unknown | 59.65 | 1482 | 56.85 | 1436 |


**For Tateyama**: 

| class | OSM - Total length (km) | OSM - Number of entities | OMF - Total length (km) | OMF - Number of entities |
|---|---|---|---|---|
| alley | 33.64 | 527 | 33.34 | 501 |
| bridleway | 0 | 0 | 0 | 0 |
| crosswalk | 0 | 0 | 2.66 | 528 |
| cycleway | 0 | 0 | 0 | 0 |
| driveway | 3.70 | 75 | 3.59 | 70 |
| footway | 6.79 | 680 | 8.38 | 158 |
| living_street | 0 | 0 | 0 | 0 |
| motorway | 0 | 0 | 0 | 0 |
| parking_aisle | 6.79 | 141 | 6.11 | 132 |
| path | 62.75 | 291 | 51.71 | 235 |
| pedestrian | 0.84 | 6 | 0.84 | 6 |
| primary | 6.09 | 67 | 5.95 | 57 |
| residential | 264.28 | 3875 | 261.55 | 3664 |
| secondary | 24.72 | 473 | 24.59 | 441 |
| sidewalk | 7.05 | 122 | 2.57 | 41 |
| steps | 0.30 | 13 | 0.30 | 13 |
| tertiary | 36.49 | 500 | 34.86 | 481 |
| track | 105.01 | 776 | 102.56 | 681 |
| trunk | 23.30 | 288 | 22.82 | 259 |
| unclassified | 28.56 | 294 | 25.98 | 273 |
| unknown | 14.76 | 291 | 15.55 | 281 |