import utils
import os
import psycopg2

def getNumberElements(connection:psycopg2.extensions.connection,
                      schema:str,
                      tableName:str,
                      filter:bool = False,
                      joinTable:str = 'bounding_box',
                      areaName:str = "") -> int:
    """Get the number of elements for the designed table (ways or nodes).
    If filter is true, then only entity contains in the join table will be used.
    The ST_Contains method will be used for this.
    If so, the area name is necessary and an exception will be raised if not given.
    
    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the number of row
        filter (bool, optional): Choose to apply a filter or not. Defaults to False.
        joinTable (str, optional): Name of the join table, only necessary if the filter is on.
        This table must be in the public schema. Defaults to 'bounding_box'.
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to "".

    Raises:
        ValueError: If areaName is None or an empty string but the filter is on.
        An area name must be given.
        ValueError: If joinTable is None or an empty string but the filter is on.
        A join table must be given.
    
    Returns:
        int: Number of elements in the table.
    """
    # General query
    query = f"""SELECT COUNT(*) as cnt FROM {schema}.{tableName} AS e """
    
    # Join query if needed
    joinQuery = f"""JOIN public.{joinTable} AS b ON ST_Contains(b.geom, e.geom) WHERE b.name = '{areaName}';"""
    
    if filter:
        # Check for parameter exception
        if areaName == "" or areaName is None:
            raise ValueError("If filter is true, an area name must be given")
        if joinTable == "" or joinTable is None:
            raise ValueError("If filter is true, a join table must be given")
        query += joinQuery
    else:
        query += ";"
    
    # Execute query
    cursor = utils.executeSelectQuery(connection, query)
    
    # Get result
    row = cursor.fetchone()
    count = row[0]
    
    # close cursor
    return count


def getTotalLengthKilometer(connection:psycopg2.extensions.connection,
                            schema:str,
                            tableName:str,
                            filter:bool = False,
                            joinTable:str = 'bounding_box',
                            areaName:str = None) -> float:
    """Return the total length in kilometer of the table.
    If filter is true, then only entity contains in the join table will be used.
    The ST_Contains method will be used for this.
    The function used to calculate length is :
    `CEILING(SUM(ST_Length(geom::geography)) / 1000`.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to calculate the total length kilometer.
        filter (bool, optional): Choose to apply a filter or not. Defaults to False.
        joinTable (str, optional): Name of the join table, only necessary if the filter is on.
        This table must be in the public schema. Defaults to 'bounding_box'.
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to "".

    Raises:
        ValueError: If areaName is None or an empty string but the filter is on.
        An area name must be given.
        ValueError: If joinTable is None or an empty string but the filter is on.
        A join table must be given.

    Returns:
        float: Total length in kilometer of the table.
    """
    # General query
    query = f"""SELECT CEILING(SUM(public.ST_Length(e.geom::geography)) / 1000) as cnt FROM {schema}.{tableName} AS e """
    
    # Join query if needed
    joinQuery = f"""JOIN public.{joinTable} AS b ON ST_Contains(b.geom, e.geom) WHERE b.name = '{areaName}';"""
    
    if filter:
        # Check for parameter exception
        if areaName == "" or areaName is None:
            raise ValueError("If filter is true, an area name must be given")
        if joinTable == "" or joinTable is None:
            raise ValueError("If filter is true, a join table must be given")
        query += joinQuery
    else:
        query += ";"
    
    # Execute query
    cursor = utils.executeSelectQuery(connection, query)
    
    # Get result
    row = cursor.fetchone()
    count = row[0]
    
    # close cursor
    cursor.close()
    
    return count


def getLengthKilometerPerClass(connection:psycopg2.extensions.connection,
                               schema:str,
                               tableName:str,
                               filter:bool = False,
                               joinTable:str = 'bounding_box',
                               areaName:str = None) -> list[tuple[str, float, int]]:
    """Return the length in kilometer of the table per class, in a dict format.
    No mapping is made for each dataset.
    If filter is true, then only entity contains in the join table will be used.
    The ST_Contains method will be used for this.
    The function used to calculate length is :
    `round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2)`.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to calculate the length kilometer per class.
        filter (bool, optional): Choose to apply a filter or not. Defaults to False.
        joinTable (str, optional): Name of the join table, only necessary if the filter is on.
        This table must be in the public schema. Defaults to 'bounding_box'.
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to "".

    Raises:
        ValueError: If areaName is None or an empty string but the filter is on.
        An area name must be given.
        ValueError: If joinTable is None or an empty string but the filter is on.
        A join table must be given.

    Returns:
        list[tuple[str, float, int]]: List representing the total length per classes.
    """
    # General query
    query = f"""
    SELECT class,
    round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2) as length_kilometer,
    COUNT(*) as nb_entity
    FROM {schema}.{tableName} AS e """
    
    # Join query if needed
    joinQuery = f"""
    JOIN public.{joinTable} AS b ON ST_Contains(b.geom, e.geom)
    WHERE b.name = '{areaName}' """
    
    if filter:
        # Check for parameter exception
        if areaName == "" or areaName is None:
            raise ValueError("If filter is true, an area name must be given")
        if joinTable == "" or joinTable is None:
            raise ValueError("If filter is true, a join table must be given")
        query += joinQuery
    
    query += """
    GROUP by class
    ORDER by class ASC;"""
    
    # Execute query
    cursor = utils.executeSelectQuery(connection, query)
    
    listClasses = []
    # Get result
    for (newClass, length, number) in cursor:
        listClasses.append((newClass, float(length), number))
    
    listClasses.sort(key= lambda a: a[0].lower())
    
    # close cursor
    cursor.close()
    
    return listClasses


def getLengthKilometerByFinalClassOSM(connection:psycopg2.extensions.connection,
                                      schema:str,
                                      tableName:str) -> list[tuple[str, float, int]]:
    """Return the length in kilometer of the table per class, in a dict format for OSM data.
    Because it is only for OSM data, no filter is needed.
    The mapping is made from OSM Data to OMF classes.
    The function used to calculate length is :
    `round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2)`

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to calculate the length kilometer per class.

    Returns:
        list[tuple[str, float, int]]: List representing the total length per classes.
    """
    # General query
    query = f"""
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
        FROM {schema}.{tableName}
    ),
    final_classes AS (
        SELECT unnest(ARRAY[
            'alley', 'bridleway', 'cycleway', 'driveway', 'footway', 'living_street',
            'motorway', 'parking_aisle', 'path', 'pedestrian', 'primary', 'residential',
            'secondary', 'sidewalk', 'steps', 'tertiary', 'trunk', 'unclassified', 'unknown',
            'crosswalk', 'track'
        ]) AS new_class
    )
    SELECT 
        fin.new_class AS new_class,
        COALESCE(join_table.length_kilometer, 0) AS length_kilometer,
        COALESCE(join_table.nb_entity, 0) AS nb_entity
    FROM final_classes AS fin
    LEFT JOIN (
        SELECT new_class,	
        round((SUM(ST_Length(geom::geography)) / 1000)::numeric, 2) as length_kilometer,
        COUNT(*) as nb_entity
        FROM table_new_classes
        GROUP BY new_class
    ) join_table
    USING (new_class)
    ORDER BY fin.new_class ASC;
    """
    
    # Execute query
    cursor = utils.executeSelectQuery(connection, query)
    
    listClasses = []
    # Get result
    for (newClass, length, number) in cursor:
        listClasses.append((newClass, float(length), number))
    
    # Sort the list by alphabetic order
    listClasses.sort(key= lambda a: a[0].lower())
    
    # close cursor
    cursor.close()
    
    return listClasses


def getLengthKilometerByFinalClassOMF(connection:psycopg2.extensions.connection,
                                      schema:str,
                                      tableName:str,
                                      joinTable:str = 'bounding_box',
                                      areaName:str = None) -> dict[str, float]:
    """Return the length in kilometer of the table per class, in a dict format.
    This works only for OMF dataset, therefore a filter is used.
    Only entity contains in the join table will be used, and the ST_Contains method
    will be used for this.
    The function used to calculate length is :
    `round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2)`

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to calculate the length kilometer per class.
        joinTable (str, optional): Name of the join table, only necessary if the filter is on.
        This table must be in the public schema. Defaults to 'bounding_box'.
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to "".

    Raises:
        ValueError: If areaName is None or an empty string. An area name must be given.
        ValueError: If joinTable is None or an empty string. A join table must be given.

    Returns:
        dict[str, float]: Dictionnary representing the total length per final classes.
    """
    # General query
    query = f"""
    WITH final_classes AS (
        SELECT unnest(ARRAY[
            'alley', 'bridleway', 'cycleway', 'driveway', 'footway', 'living_street',
            'motorway', 'parking_aisle', 'path', 'pedestrian', 'primary', 'residential',
            'secondary', 'sidewalk', 'steps', 'tertiary', 'trunk', 'unclassified', 'unknown',
            'crosswalk', 'track'
        ]) AS new_class
    )
    SELECT 
        fin.new_class AS new_class,
        COALESCE(join_table.length_kilometer, 0) AS length_kilometer,
        COALESCE(join_table.nb_entity, 0) AS nb_entity
    FROM final_classes AS fin
    LEFT JOIN (
        SELECT e.class AS new_class,
        round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2) as length_kilometer,
        COUNT(e.class) AS nb_entity
        FROM {schema}.{tableName} AS e
        JOIN public.{joinTable} AS b ON ST_Contains(b.geom, e.geom)
        WHERE b.name = '{areaName}'
        GROUP BY class
    ) join_table
    USING (new_class)
    ORDER BY fin.new_class ASC;
    """
    
    # Check for execption
    if areaName == "" or areaName is None:
        raise ValueError("If filter is true, an area name must be given")
    if joinTable == "" or joinTable is None:
        raise ValueError("If filter is true, a join table must be given")
    
    # Execute query
    cursor = utils.executeSelectQuery(connection, query)
    
    listClasses = []
    # Get result
    for (newClass, length, number) in cursor:
        listClasses.append((newClass, float(length), number))
    
    # Sort the list by alphabetic order
    listClasses.sort(key= lambda a: a[0].lower())
    
    # close cursor
    cursor.close()
    
    return listClasses


def getConnectedComponents(connection:psycopg2.extensions.connection,
                           schema:str,
                           tableName:str) -> int:
    """Return the number of connected components of the graph using PgRouting algorithms.
    PgRouting must be installed otherwise it will not work.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the connected components.

    Returns:
        int: Number of connected components for the graph.
    """
    # General query
    query = f"""SELECT COUNT(*) FROM (
		SELECT COUNT(*)
		FROM public.pgr_connectedComponents('SELECT id, source, target, cost, reverse_cost FROM {schema}.{tableName}')
		GROUP BY DISTINCT component
	)"""
    
    # Execute query
    cursor = utils.executeSelectQuery(connection, query)
    
    # Get result
    row = cursor.fetchone()
    count = row[0]
    
    # close cursor
    cursor.close()
    
    return count
    
    
def getStrongConnectedComponents(connection:psycopg2.extensions.connection,
                                 schema:str,
                                 tableName:str) -> int:
    """Return the number of strong connected components
    of the graph using PgRouting algorithms.
    No filter is necessary as it would only 
    PgRouting must be installed otherwise it will not work.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the strong connected components.
    
    Returns:
        int: Number of strong connected components for the graph.
    """
    # General query
    query = f"""SELECT COUNT(*) FROM (
		SELECT COUNT(*)
		FROM public.pgr_strongComponents('SELECT id, source, target, cost, reverse_cost FROM {schema}.{tableName}')
		GROUP BY DISTINCT component
	)"""
    
    # Execute query
    cursor = utils.executeSelectQuery(connection, query)
    
    # Get result
    row = cursor.fetchone()
    count = row[0]
    
    # close cursor
    cursor.close()
    
    return count


def getOverlapIndicator(connection:psycopg2.extensions.connection,
                        schemaDatasetA:str,
                        tableNameDatasetA:str,
                        schemaDatasetB:str,
                        tableNameDatasetB:str,
                        resultAsTable:str = "",
                        schemaResult:str = "public") -> float:
    """Return the value of the overlap indicator for dataset A over dataset B.
    The result can be write as a table if resultAsTable parameter is not empty.
    If so, a DROP TABLE / CREATE TABLE statement will be added to the query.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database.
        schemaDatasetA (str): Name of the schema for the dataset A.
        tableNameDatasetA (str): Name of the table for the dataset A.
        schemaDatasetB (str): Name of the schema for the dataset B.
        tableNameDatasetB (str): Name of the table for the dataset B.
        resultAsTable (str, optional). If given, the result will be saved as a table.
        Otherwise, only the percentage will be shown. Defaults to "".
        schemaResult (str, optional): Name of the schema for the results.
        Not necessary if resultAsTable is empty. Defaults to "public".

    Returns:
        float: Overlap indicator in percentage.
    """
    query = ""
    # Add create table statement if the parameter is on
    if resultAsTable !="":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")
        
        # Add drop / create table statement
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;
        
        CREATE TABLE {schemaResult}.{resultAsTable} AS
        """
    
    # General query
    query = f"""
    WITH union_buffer AS (
        SELECT public.ST_Union(public.ST_Transform(public.ST_Buffer(geom::geography, 1)::geometry, 4326)) AS buffer,
        true as test
        FROM {schemaDatasetB}.{tableNameDatasetB}
    ),
    intersect_buffer AS (
        SELECT
            CASE
                WHEN b.test is true THEN true
                ELSE false
            END AS overlap,
            os.*
        FROM {schemaDatasetA}.{tableNameDatasetA} AS os
        LEFT JOIN union_buffer b ON public.ST_Contains(b.buffer, os.geom)
        ORDER BY id asc
    )
    """
    
    # Select query (either added to the general query or run in its own)
    selectPart = """
    SELECT
        overlap,
        round((SUM(public.ST_Length(geom::geography)) / 1000)::numeric, 2) AS length_kilometer
    FROM {}
    GROUP BY overlap
    ORDER BY overlap;
    """
    
    # If the table is created, we do not sum up the length directly, only after the table is created
    if resultAsTable !="":
        query+= " SELECT * FROM intersect_buffer;"
        
        # Execute the query to create the table
        utils.executeQueryWithTransaction(connection, query)
        
        print(f"Table {schemaResult}.{resultAsTable} created successfully.")
        
        # Select the overlap indicator
        selectQuery = selectPart.format(f"{schemaResult}.{resultAsTable}")
        cursor = utils.executeSelectQuery(connection, selectQuery)
    # Else, we do not put the result in another table and select only the overlap part
    else:
        query += selectPart.format("intersect_buffer")
        cursor = utils.executeSelectQuery(connection, query)
    
    totalLength = 0
    overlapLength = 0
    # Fetch result to calculate the indicator
    for (overlap, length) in cursor:
        # We take the overlap length from the result
        if overlap == True:
            overlapLength = length
        totalLength += length
    
    # Calculate indicator
    indicator = round((overlapLength / totalLength) * 100, 2)
    
    # Print info to user
    print(f"Total length is {totalLength} km")
    print(f"Overlap length is {overlapLength} km")
    print(f"Percentage of road from dataset {schemaDatasetA} in dataset {schemaDatasetB} is : {indicator} %")
    
    return indicator


def getCorrespondingNodes(connection:psycopg2.extensions.connection,
                          schemaDatasetA:str,
                          tableNameDatasetA:str,
                          schemaDatasetB:str,
                          tableNameDatasetB:str,
                          joinTable:str = 'bounding_box',
                          resultAsTable:str = "",
                          schemaResult:str = "public") -> tuple[int, float]:
    """Return the number of corresponding nodes in dataset A, comparing it to dataset B,
    and the percentage of nodes.
    Both tables are filtered using the join table.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database.
        schemaDatasetA (str): Name of the schema for the dataset A.
        tableNameDatasetA (str): Name of the table for the dataset A.
        schemaDatasetB (str): Name of the schema for the dataset B.
        tableNameDatasetB (str): Name of the table for the dataset B.
        joinTable (str, optional): Name of the join table, only necessary if the filter is on.
        This table must be in the public schema. Defaults to 'bounding_box'.
        resultAsTable (str, optional). If given, the result will be saved as a table.
        Otherwise, only the percentage will be shown. Defaults to "".
        schemaResult (str, optional): Name of the schema for the results.
        Not necessary if resultAsTable is empty. Defaults to "public".

    Returns:
        tuple[int, float]: First value is the number of nodes,
        second value is the percentage of nodes.
    """
    query = ""
    # Add create table statement if the parameter is on
    if resultAsTable !="":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")
        
        # Add drop / create table statement
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;
        
        CREATE TABLE {schemaResult}.{resultAsTable} AS
        """
    
    # General query
    query = f"""
    WITH vertices_dataset_a AS (
        SELECT n.*
        FROM {schemaDatasetA}.{tableNameDatasetA} AS n
        JOIN public.{joinTable} b ON public.ST_Intersects(b.geom, n.geom)
    ),
    vertices_dataset_b AS (
        SELECT n.*
        FROM {schemaDatasetB}.{tableNameDatasetB} AS n
        JOIN public.{joinTable} b ON public.ST_Intersects(b.geom, n.geom)
    ),
    vertices_intersect AS (
        SELECT
            va.*,
            CASE WHEN public.ST_Intersects(va.geom, vb.geom) THEN true
            ELSE false
            END AS intersects
        FROM vertices_dataset_a AS va
        LEFT JOIN vertices_dataset_b vb ON public.ST_Intersects(va.geom, vb.geom)
    )
    """
    
    # Select query (either added to the general query or run in its own)
    selectPart = """SELECT intersects, COUNT(*) as nb
    FROM {}
    GROUP BY intersects
    ORDER BY intersects;
    """
    
    # If the table is created, we do not sum up the length directly, only after the table is created
    if resultAsTable !="":
        query+= " SELECT * FROM vertices_intersect;"
        
        # Execute the query to create the table
        utils.executeQueryWithTransaction(connection, query)
        
        print(f"Table {schemaResult}.{resultAsTable} created successfully.")
        
        # Select the overlap indicator
        selectQuery = selectPart.format(f"{schemaResult}.{resultAsTable}")
        cursor = utils.executeSelectQuery(connection, selectQuery)
    # Else, we do not put the result in another table and select all elements group by intersects
    else:
        query += selectPart.format("vertices_intersect")
        cursor = utils.executeSelectQuery(connection, query)
    
    totalNodes = 0
    intersectNodes = 0
    # Fetch result to calculate the indicator
    for (intersects, nb) in cursor:
        # We take the overlap length from the result
        if intersects == True:
            intersectNodes = nb
        totalNodes += nb
    
    # Calculate indicator
    percentage = round((intersectNodes / totalNodes) * 100, 2)
    
    # Print info to user
    print(f"Total nodes: {totalNodes}")
    print(f"Intersects nodes: {intersectNodes}")
    print(f"Percentage of corresponding nodes from dataset {schemaDatasetA} in dataset {schemaDatasetB} is : {percentage} %")
    
    return intersectNodes, percentage

if __name__ == "__main__":
    import time
    import pandas as pd
    start = time.time()
    
    # Connect to the database and give table template for OSM and OMF dataset
    database = "pgrouting"
    connection = utils.getConnection(database)
    
    osmSchema = 'osm'
    osmEdgeTableTemplate = "edge_with_cost_{}"
    osmNodeTableTemplate = "node_{}"
    
    omfSchema = 'omf'
    omfEdgeTableTemplate = "edge_with_cost_{}"
    omfNodeTableTemplate = "node_{}"
    
    listArea = ['tokyo', 'tateyama']
    
    # Data to add to the dataFrame
    data = []
    
    for area in listArea:
        osmEdgeTable = osmEdgeTableTemplate.format(area)
        osmNodeTable = osmNodeTableTemplate.format(area)
        
        omfEdgeTable = omfEdgeTableTemplate.format(area)
        omfNodeTable = omfNodeTableTemplate.format(area)
        
        # Capitalize the area name to be able to filter with the bounding box
        area = area.capitalize()
        
        # Number of edges / nodes
        OSMValue = getNumberElements(connection, osmSchema, osmEdgeTable)
        print(f"Number of edges in OSM for {area} is : {OSMValue}")
        
        OMFValue = getNumberElements(connection, omfSchema, omfEdgeTable, filter = True, areaName = area)
        print(f"Number of edges in OMF for {area} is : {OMFValue}")
        
        # Add data to the data list
        data.append(["1. Number of nodes", area, OSMValue, OMFValue])
        
        OSMValue = getNumberElements(connection, osmSchema, osmNodeTable)
        print(f"Number of nodes in OSM for {area} is : {OSMValue}")
        
        OMFValue = getNumberElements(connection, omfSchema, omfNodeTable, filter = True, areaName = area)
        print(f"Number of nodes in OMF for {area} is : {OMFValue}")
        
        # Add data to the data list
        data.append(["2. Number of edges", area, OSMValue, OMFValue])
        
        
        # Total length kilometer
        OSMValue = getTotalLengthKilometer(connection, osmSchema, osmEdgeTable)
        print(f"Total length in km in OSM for {area} is : {OSMValue}")
        
        OMFValue = getTotalLengthKilometer(connection, omfSchema, omfEdgeTable, filter = True, areaName = area)
        print(f"Total length in km in OMF for {area} is : {OMFValue}")
        
        # Add data to the data list
        data.append(["3. Total length (km)", area, OSMValue, OMFValue])
        
        
        # Total length kilometer per class
        listClasses = getLengthKilometerPerClass(connection, osmSchema, osmEdgeTable)
        print(f"Total length in km per class OSM for {area} is : {listClasses}")
        
        listClasses = getLengthKilometerPerClass(connection, omfSchema, omfEdgeTable, filter = True, areaName = area)
        print(f"Total length in km per class OMF for {area} is : {listClasses}")
        
        
        # Total length kilometer per final class
        listClasses = getLengthKilometerByFinalClassOSM(connection, osmSchema, osmEdgeTable)
        print(f"Total length in km per final class OSM for {area} is : {listClasses}")
        
        listClasses = getLengthKilometerByFinalClassOMF(connection, omfSchema, omfEdgeTable, areaName = area)
        print(f"Total length in km per final class OMF for {area} is : {listClasses}")
        
        
        # Connected components
        OSMValue = getConnectedComponents(connection, osmSchema, osmEdgeTable)
        print(f"Number of connected components in OSM for {area} is : {OSMValue}")
        
        OMFValue = getConnectedComponents(connection, omfSchema, omfEdgeTable)
        print(f"Number of connected components in OMF for {area} is : {OMFValue}")
        
        # Add data to the data list
        data.append(["4. Number of connected components", area, OSMValue, OMFValue])
        
        
        # Strong connected components
        OSMValue = getStrongConnectedComponents(connection, osmSchema, osmEdgeTable)
        print(f"Number of strong connected components in OSM for {area} is : {OSMValue}")
        
        OMFValue = getStrongConnectedComponents(connection, omfSchema, omfEdgeTable)
        print(f"Number of strong connected components in OMF for {area} is : {OMFValue}")
        
        # Add data to the data list
        data.append(["5. Number of strong connected components", area, OSMValue, OMFValue])
        
        end = time.time()
        print(f"Criteria until now took {end - start} seconds")
        
        # Overlap indicator
        OSMValue = getOverlapIndicator(connection, osmSchema, osmEdgeTable, omfSchema, omfEdgeTable)
        print(f"OSM Overlap indicator (% of OSM roads in OMF dataset) for {area} is : {OSMValue}")
        
        end = time.time()
        print(f"Overlap indicator 1 took {end - start} seconds")
        
        OMFValue = getOverlapIndicator(connection, omfSchema, omfEdgeTable, osmSchema, osmEdgeTable)
        print(f"OMF Overlap indicator (% of OMF roads in OSM dataset) for {area} is : {OMFValue}")
        
        end = time.time()
        print(f"Overlap indicator 2 took {end - start} seconds")
        
        # Add data to the data list
        data.append(["7. Number of strong connected components", area, OSMValue, OMFValue])
        
        # Corresponding nodes
        OSMValue = getCorrespondingNodes(connection, osmSchema, osmEdgeTable, omfSchema, omfEdgeTable)
        print(f"Number of corresponding nodes in OSM for {area} is : {OSMValue[0]} ({OSMValue[0]} %)")
        
        end = time.time()
        print(f"Corresponding nodes for OSM took {end - start} seconds")
        
        OMFValue = getCorrespondingNodes(connection, omfSchema, omfEdgeTable, osmSchema, osmEdgeTable)
        print(f"Number of corresponding nodes in OMF for {area} is : {OMFValue[0]} ({OMFValue[1]} %)")
        
        end = time.time()
        print(f"Corresponding nodes for OMF took {end - start} seconds")
        
        # Add two rows in the dataframe (one for the number and the other for percentage)
        data.append(["8. Number of corresponding nodes", area, OSMValue[0], OMFValue[0]])
        
        # Add data to the data list
        data.append(["9. Percentage of corresponding nodes", area, f"{OSMValue[1]} %", f"{OMFValue[1]} %"])
    
    # Sort data per Criterion / Area
    data.sort(key= lambda a: (a[0], a[1]))
    
    # Create dataframe to export as markdown in the end
    columns = ['Criterion', 'Area', 'OSM Value', 'OMF Value']
    df = pd.DataFrame(data=data, columns=columns)
    
    print(df)
    
    end = time.time()
    print(f"It took {end - start} seconds")