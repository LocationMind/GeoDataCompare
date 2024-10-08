import os
import pandas as pd
import psycopg2
import sys
from src.Utils import utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def getListAreas(
    connection: psycopg2.extensions.connection,
    tableName: str = "bounding_box",
    schema: str = "public",
    columnName: str = "name",
) -> list[str]:
    """Get all areas names in the bounding box table.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database.
        tableName (str): Name of the bounding box table. Defaults to 'bounding_box'.
        schema (str): Schema where the bounding box table is stored. Defaults to 'public'.
        columnName (str, optional): Name of the column to select. Defaults to 'name'.

    Returns:
        list[str]: List of all areas, sorted by names
    """
    # Get all the entity from bounding box table, order by name
    query = f"""SELECT {columnName} FROM {schema}.{tableName}
    ORDER BY {columnName} ASC;"""

    # Execute query
    cursor = utils.executeSelectQuery(connection, query)

    listArea = []
    # Put result to a list
    for row in cursor:
        listArea.append(row[0])

    return listArea


def getNumberElements(
    connection: psycopg2.extensions.connection,
    schema: str,
    tableName: str,
    filter: bool = False,
    joinTable: str = "bounding_box",
    areaName: str = "",
) -> int:
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


def getTotalLengthKilometer(
    connection: psycopg2.extensions.connection,
    schema: str,
    edgeTableName: str,
    filter: bool = False,
    joinTable: str = "bounding_box",
    areaName: str = None,
) -> float:
    """Return the total length in kilometer of the table.
    If filter is true, then only entity contains in the join table will be used.
    The ST_Contains method will be used for this.
    The function used to calculate length is:
    `CEILING(SUM(ST_Length(geom::geography)) / 1000`.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        edgeTableName (str): Name of the edge table to calculate the total length kilometer.
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
    query = f"""SELECT CEILING(SUM(public.ST_Length(e.geom::geography)) / 1000) as cnt FROM {schema}.{edgeTableName} AS e """

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


def getLengthKilometerPerClass(
    connection: psycopg2.extensions.connection,
    schema: str,
    edgeTableName: str,
    filter: bool = False,
    joinTable: str = "bounding_box",
    areaName: str = None,
) -> list[tuple[str, float, int]]:
    """Return the length in kilometer of the table per class, in a dict format.
    No mapping is made for each dataset.
    If filter is true, then only entity contains in the join table will be used.
    The ST_Contains method will be used for this.
    The function used to calculate length is:
    `round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2)`.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        edgeTableName (str): Name of the edge table to calculate the length kilometer per class.
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
    FROM {schema}.{edgeTableName} AS e """

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
    for newClass, length, number in cursor:
        # None case
        if newClass is None:
            newClass = "None"
        listClasses.append((newClass, float(length), number))

    listClasses.sort(key=lambda a: a[0].lower())

    # close cursor
    cursor.close()

    return listClasses


def getConnectedComponents(
    connection: psycopg2.extensions.connection,
    schema: str,
    edgeTableName: str,
    resultAsTable: str = "",
    nodeTableName: str = "",
    schemaResult: str = "public",
    idColumnName: str = "id",
) -> int:
    """Return the number of connected components of the graph using PgRouting algorithms.
    PgRouting must be installed otherwise it will not work.
    If you want to save the result as table, two queries will be run.
    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        edgeTableName (str): Name of the edge table to count the connected components.
        resultAsTable (str, optional). If given, the result will be saved as a table.
        Otherwise, only the percentage will be shown. Defaults to "".
        nodeTableName (str): Name of the node table.
        Only necessary if one wants to save the result as table. Defaults to "".
        schemaResult (str, optional): Name of the schema for the results.
        Not necessary if resultAsTable is empty. Defaults to "public".
        idColumnName (str, optional): Name of the node id column.
        Not necessary if resultAsTable is empty. Defaults to "id".

    Raises:
        ValueError: If no result schema is given when saving the result as table.

    Returns:
        int: Number of connected components for the graph.
    """
    # General query
    query = f"""SELECT COUNT(*) FROM (
        SELECT COUNT(*)
        FROM public.pgr_connectedComponents('SELECT id, source, target, cost, reverse_cost FROM {schema}.{edgeTableName}')
        GROUP BY DISTINCT component
    ) AS sub;"""

    # Execute query
    cursor = utils.executeSelectQuery(connection, query)

    # Get result
    row = cursor.fetchone()
    count = row[0]

    # close cursor
    cursor.close()

    # Add create table statement if the parameter is on
    if resultAsTable != "":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")
        if nodeTableName == "":
            raise ValueError("The node table must be given for the result output")

        # Add drop / create table statement
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;

        CREATE TABLE {schemaResult}.{resultAsTable} AS
        SELECT *, COUNT(*) OVER (PARTITION BY component) AS cardinality
        FROM pgr_connectedComponents('SELECT id, source, target, cost, reverse_cost FROM {schema}.{edgeTableName}') pgr
        JOIN {schema}.{nodeTableName} AS v ON pgr.node = v.{idColumnName}
        ORDER by COUNT(*) OVER (PARTITION BY component) ASC;
        """

        # Execute query
        utils.executeQueryWithTransaction(connection, query)

    return count


def getStrongConnectedComponents(
    connection: psycopg2.extensions.connection,
    schema: str,
    edgeTableName: str,
    resultAsTable: str = "",
    nodeTableName: str = "",
    schemaResult: str = "public",
    idColumnName: str = "id",
) -> int:
    """Return the number of strong connected components of the graph using PgRouting algorithms.
    PgRouting must be installed otherwise it will not work.
    If you want to save the result as table, two queries will be run.
    The node table is necessary for this.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        edgeTableName (str): Name of the edge table to count the strong connected components.
        resultAsTable (str, optional). If given, the result will be saved as a table.
        Otherwise, only the percentage will be shown. Defaults to "".
        nodeTableName (str): Name of the node table.
        Only necessary if one wants to save the result as table. Defaults to "".
        schemaResult (str, optional): Name of the schema for the results.
        Not necessary if resultAsTable is empty. Defaults to "public".
        idColumnName (str, optional): Name of the node id column.
        Not necessary if resultAsTable is empty. Defaults to "id".

    Raises:
        ValueError: If no result schema is given when saving the result as table.
        ValueError: If no node table is given when saving the result as table.

    Returns:
        int: Number of strong connected components for the graph.
    """
    # General query
    query = f"""SELECT COUNT(*) FROM (
        SELECT COUNT(*)
        FROM public.pgr_strongComponents('SELECT id, source, target, cost, reverse_cost FROM {schema}.{edgeTableName}')
        GROUP BY DISTINCT component
    ) AS sub;"""

    # Execute query
    cursor = utils.executeSelectQuery(connection, query)

    # Get result
    row = cursor.fetchone()
    count = row[0]

    # close cursor
    cursor.close()

    # Add create table statement if the parameter is on
    if resultAsTable != "":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")
        if nodeTableName == "":
            raise ValueError("The node table must be given for the result output")

        # Create table query
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;

        CREATE TABLE {schemaResult}.{resultAsTable} AS
        SELECT *, COUNT(*) OVER (PARTITION BY component) AS cardinality
        FROM pgr_strongComponents('SELECT id, source, target, cost, reverse_cost FROM {schema}.{edgeTableName}') pgr
        JOIN {schema}.{nodeTableName} AS v ON pgr.node = v.{idColumnName}
        ORDER by COUNT(*) OVER (PARTITION BY component) ASC;
        """

        # Execute query
        utils.executeQueryWithTransaction(connection, query)

    return count


def getIsolatedNodes(
    connection: psycopg2.extensions.connection,
    schema: str,
    edgeTableName: str,
    nodeTableName: str,
    resultAsTable: str = "",
    schemaResult: str = "public",
) -> int:
    """Return the number of isolated nodes in the graph, by counting
    the number of nodes that do not intersect any roads

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        edgeTableName (str): Name of the edge table.
        nodeTableName (str): Name of the node table.
        resultAsTable (str, optional). If given, the result will be saved as a table.
        Otherwise, only the percentage will be shown. Defaults to "".
        schemaResult (str, optional): Name of the schema for the results.
        Not necessary if resultAsTable is empty. Defaults to "public".

    Raises:
        ValueError: If no result schema is given when saving the result as table.

    Returns:
        int: Number of strong connected components for the graph.
    """
    query = ""
    # Add create table statement if the parameter is on
    if resultAsTable != "":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")

        # Add drop / create table statement
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;

        CREATE TABLE {schemaResult}.{resultAsTable} AS
        """

    # General query
    query += f"""
    WITH isolated_nodes AS (
        SELECT DISTINCT ON (n.geom)
            n.*,
            CASE WHEN public.ST_Intersects(e.geom, n.geom)THEN true
            ELSE false
            END AS intersects
        FROM {schema}.{nodeTableName} AS n
        LEFT JOIN {schema}.{edgeTableName} e ON public.ST_Intersects(e.geom, n.geom)
    )
    """

    # Select query (either added to the general query or run on its own)
    selectPart = """ SELECT intersects, COUNT(*) as nb
    FROM {}
    GROUP BY intersects
    ORDER BY intersects;
    """

    # If the table is created, we do not sum up the length directly, only after the table is created
    if resultAsTable != "":
        query += " SELECT * FROM isolated_nodes;"

        # Execute the query to create the table
        utils.executeQueryWithTransaction(connection, query)

        # Select the overlap indicator
        selectQuery = selectPart.format(f"{schemaResult}.{resultAsTable}")
        cursor = utils.executeSelectQuery(connection, selectQuery)
    # Else, we do not put the result in another table and select all elements group by intersects
    else:
        query += selectPart.format("isolated_nodes")
        cursor = utils.executeSelectQuery(connection, query)

    isolatedNodes = 0
    # Fetch result to calculate the indicator
    for intersects, nb in cursor:
        # We take the overlap length from the result
        if not intersects:
            isolatedNodes = nb

    return isolatedNodes


def getOverlapIndicator(
    connection: psycopg2.extensions.connection,
    schemaDatasetA: str,
    tableNameDatasetA: str,
    schemaDatasetB: str,
    tableNameDatasetB: str,
    resultAsTable: str = "",
    schemaResult: str = "public",
) -> float:
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

    Raises:
        ValueError: If no result schema is given when saving the result as table.

    Returns:
        float: Overlap indicator in percentage.
    """
    query = ""
    # Add create table statement if the parameter is on
    if resultAsTable != "":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")

        # Add drop / create table statement
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;

        CREATE TABLE {schemaResult}.{resultAsTable} AS
        """

    # General query
    query += f"""
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
    if resultAsTable != "":
        query += " SELECT * FROM intersect_buffer;"

        # Execute the query to create the table
        utils.executeQueryWithTransaction(connection, query)

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
    for overlap, length in cursor:
        # We take the overlap length from the result
        if overlap:
            overlapLength = length
        totalLength += length

    # Calculate indicator
    indicator = round((overlapLength / totalLength) * 100, 2)

    return indicator


def getCorrespondingNodes(
    connection: psycopg2.extensions.connection,
    schemaDatasetA: str,
    tableNameDatasetA: str,
    schemaDatasetB: str,
    tableNameDatasetB: str,
    joinTable: str = "bounding_box",
    resultAsTable: str = "",
    schemaResult: str = "public",
) -> tuple[int, float]:
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

    Raises:
        ValueError: If no result schema is given when saving the result as table.

    Returns:
        tuple[int, float]: First value is the number of nodes,
        second value is the percentage of nodes.
    """
    query = ""
    # Add create table statement if the parameter is on
    if resultAsTable != "":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")

        # Add drop / create table statement
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;

        CREATE TABLE {schemaResult}.{resultAsTable} AS
        """

    # General query
    query += f"""
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
        SELECT DISTINCT ON (va.geom)
            va.*,
            CASE WHEN public.ST_Intersects(va.geom, vb.geom) THEN true
            ELSE false
            END AS intersects
        FROM vertices_dataset_a AS va
        LEFT JOIN vertices_dataset_b vb ON public.ST_Intersects(va.geom, vb.geom)
    )
    """

    # Select query (either added to the general query or run on its own)
    selectPart = """SELECT intersects, COUNT(*) as nb
    FROM {}
    GROUP BY intersects
    ORDER BY intersects;
    """

    # If the table is created, we do not sum up the length directly, only after the table is created
    if resultAsTable != "":
        query += " SELECT * FROM vertices_intersect;"

        # Execute the query to create the table
        utils.executeQueryWithTransaction(connection, query)

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
    for intersects, nb in cursor:
        # We take the number of intersected nodes
        if intersects:
            intersectNodes = nb
        totalNodes += nb

    # Calculate indicator
    percentage = round((intersectNodes / totalNodes) * 100, 2)

    return intersectNodes, percentage


def listsToMardownTable(
    listOSM: list,
    listOMF: list,
) -> str:
    """Merge two list with the same first column into a markdown table.
    The lists must be list of tuples or list of list, and within each tuples or
    list, the same number of value is expected.
    Otherwise, an exception will be raised.
    Same way if the column do not correspond to the number of column in the list.

    Args:
        listOSM (list): List of OSM results.
        listOMF (list): List of OMF results.
        columnsOSM (list, optional): Name of the OSM list columns.
        Defaults to ["class", "OMF - Total length (km)", "OMF - Number of entities"].
        columnsOSM (list, optional): Name of the OMF list columns.
        Defaults to ["class", "OMF - Total length (km)", "OMF - Number of entities"].

    Raises:
        ValueError: If the listOSM parameter is empty.
        ValueError: If the listOSM parameter is empty.
        ValueError: If the first entry of both list does not have the same number of columns.

    Returns:
        str: Mardown table corresponding to the two lists merged.
    """
    ## Exceptions
    # Len of the two lists
    if len(listOSM) == 0:
        raise ValueError("The OSM list parameter must not be empty")
    if len(listOMF) == 0:
        raise ValueError("The OMF list parameter must not be empty")

    # Test if the list have the same number of column in the first entry
    lenOSM = len(listOSM[0])
    lenOMF = len(listOMF[0])

    if lenOSM != lenOMF:
        raise ValueError(
            f"The two lists does not have the same number of columns in the first entry: len(listOSM[0]) = {lenOSM}, len(listOMF[0]) = {lenOMF})"
        )

    # Transform list in dataframe
    columnsOSM = ["class", "length", "entity"]
    columnsOMF = ["class", "length", "entity"]
    dfOSM = pd.DataFrame(listOSM, columns=columnsOSM)
    dfOMF = pd.DataFrame(listOMF, columns=columnsOMF)

    finalList = []
    # Iterate over OSM rows first
    for _, (classDf, lengthOSM, entityOSM) in dfOSM.iterrows():
        # Check if the value is also in OMF dataframe
        valueInOMF = dfOMF.loc[dfOMF["class"] == classDf]

        # If no value is found, we put 0 as a value
        if valueInOMF.empty:
            lengthOMF, entityOMF = 0, 0
        # Otherwise, we take the value and remove the line from the OMF dataframe
        else:
            id = valueInOMF.index
            lengthOMF = valueInOMF.iloc[0]["length"]
            entityOMF = valueInOMF.iloc[0]["entity"]
            # Remove line from the dataFrame
            dfOMF = dfOMF.drop(id)

        # Add the value to the final list
        finalList.append([classDf, lengthOSM, entityOSM, lengthOMF, entityOMF])

    # Iterate over the rest of OMF rows
    for _, (classDf, lengthOMF, entityOMF) in dfOMF.iterrows():
        # We already check OSM values so the total number is 0 for OSM dataset
        lengthOSM, entityOSM = 0, 0
        # Add the value to the final list
        finalList.append([classDf, lengthOSM, entityOSM, lengthOMF, entityOMF])

    # Sort the list by class
    finalList.sort(key=lambda a: a[0])

    # Create the dataframe
    finalColumns = [
        "class",
        "OSM - Total length (km)",
        "OSM - Number of entities",
        "OMF - Total length (km)",
        "OMF - Number of entities",
    ]
    finalDataFrame = pd.DataFrame(finalList, columns=finalColumns)

    # Export to markdown
    markdown = finalDataFrame.to_markdown(index=False, tablefmt="github")

    return markdown


def getDensityPlaceGrid(
    connection: psycopg2.extensions.connection,
    schema: str,
    placeTable: str,
    area: str,
    boundingBoxTable: str = "bounding_box",
    resultAsTable: str = "",
    schemaResult: str = "public",
) -> int:
    """Return the density of places in the bounding box.
    If the result is save as a table then the density is calculated on
    100 x 100 meters square.
    Uses the geometry from the bounding box table for a density.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database.
        schema (str): Name of the schema.
        placeTable (str): Name of the place table.
        area (str): Name of the bounding box area.
        boundingBoxTable (str, optional): Name of the bounding box table.
        Defaults to 'bounding_box'.
        resultAsTable (str, optional). If given, the result will be saved as a table.
        Defaults to "".
        schemaResult (str, optional): Name of the schema for the results.
        Not necessary if resultAsTable is empty. Defaults to "public".

    Raises:
        ValueError: If no result schema is given when saving the result as table.

    Returns:
        int: Density of places per kilometer square.
    """
    # Get density value
    queryDensity = f"""
    WITH area_bbox AS (
        SELECT ST_Area(geom::geography) / 1000000 AS area
        FROM public.{boundingBoxTable}
        WHERE name = '{area}'
    ),
    nb_places AS (
        SELECT count(*) AS nb FROM {schema}.{placeTable}
    )
    SELECT nb_places.nb / area_bbox.area AS density FROM nb_places, area_bbox
    """

    cursor = utils.executeSelectQuery(connection, queryDensity)
    value = cursor.fetchone()[0]

    # Create table if needed
    if resultAsTable != "":
        if schemaResult == "":
            raise ValueError("A schema must be given for the result output")

        # Add drop / create table statement
        query = f"""
        DROP TABLE IF EXISTS {schemaResult}.{resultAsTable} CASCADE;

        CREATE TABLE {schemaResult}.{resultAsTable} AS
        WITH grid AS (
            SELECT (ST_SquareGrid(0.001, geom)).*
            FROM public.{boundingBoxTable} WHERE name = '{area}'
        ),
        grid_intersects AS (
            SELECT count(*) as nb, g.geom, g.i, g.j
            FROM grid AS g
            JOIN {schema}.{placeTable} AS p ON ST_Intersects(g.geom, p.geom)
            GROUP BY (g.geom, g.i, g.j)
        ),
        grid_not_intersects AS (
            SELECT 0 as nb, g.geom, g.i, g.j
            FROM grid AS g
            WHERE (g.i, g.j) NOT IN (
                SELECT i, j FROM grid_intersects
            )
            GROUP BY (g.geom, g.i, g.j)
        )
        SELECT * FROM grid_not_intersects
        UNION
        SELECT * FROM grid_intersects
        ORDER by i, j ASC;

        ALTER TABLE {schemaResult}.{resultAsTable}
        ADD COLUMN id serial;
        """

        # Create table
        utils.executeQueryWithTransaction(connection, query)

    return value
