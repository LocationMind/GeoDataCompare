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
    If filter is true, then the elements will be joined with the given join table using
    the ST_Contains method (usually with a bounding box).
    If so, the area name is necessary and an exception will be raised if not given.
    
    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the number of row
        filter (bool, optional): Choose to apply a filter or not. Defaults to False
        joinTable (str, optional): Name of the join table, only necessary if the filter is on. Defaults to False
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to ""
    
    Returns:
        int: Number of elements in the table.
    """
    query = f"""SELECT COUNT(*) as cnt FROM {schema}.{tableName} AS e """
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
    The function used is `CEILING(SUM(ST_Length(geom::geography)) / 1000`

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the number of row
        filter (bool, optional): Choose to apply a filter or not. Defaults to False
        joinTable (str, optional): Name of the join table, only necessary if the filter is on. Defaults to False
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to ""

    Returns:
        float: Total length in kilometer of the table
    """
    # TODO: Write the function
    
    
def getLengthKilometerByClass(connection:psycopg2.extensions.connection,
                              schema:str,
                              tableName:str,
                              filter:bool = False,
                              joinTable:str = 'bounding_box',
                              areaName:str = None) -> dict[str, float]:
    """Return the length in kilometer of the table per class, in a dict format.
    The function used is `round((SUM(ST_Length(e.geom::geography)) / 1000)::numeric, 2)`

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the number of row
        filter (bool, optional): Choose to apply a filter or not. Defaults to False
        joinTable (str, optional): Name of the join table, only necessary if the filter is on. Defaults to False
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to ""

    Returns:
        dict[str, float]: Dictionnary representing the total length per classes
    """
    # TODO: Write the function
    
    
def getConnectedComponents(connection:psycopg2.extensions.connection,
                           schema:str,
                           tableName:str,
                           filter:bool = False,
                           joinTable:str = 'bounding_box',
                           areaName:str = None) -> int:
    """Return the number of connected components of the graph using PgRouting algorithms.
    PgRouting must be installed otherwise it will not work.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the number of row
        filter (bool, optional): Choose to apply a filter or not. Defaults to False
        joinTable (str, optional): Name of the join table, only necessary if the filter is on. Defaults to False
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to ""

    Returns:
        int: Number of connected components for the graph.
    """
    # TODO: Write the function
    
    
def getStrongConnectedComponents(connection:psycopg2.extensions.connection,
                                 schema:str,
                                 tableName:str,
                                 filter:bool = False,
                                 joinTable:str = 'bounding_box',
                                 areaName:str = None) -> int:
    """Return the number of strong connected components
    of the graph using PgRouting algorithms.
    PgRouting must be installed otherwise it will not work.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database
        schema (str): Name of the schema.
        tableName (str): Name of the table to count the number of row
        filter (bool, optional): Choose to apply a filter or not. Defaults to False
        joinTable (str, optional): Name of the join table, only necessary if the filter is on. Defaults to False
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to ""
    
    Returns:
        int: Number of strong connected components for the graph.
    """
    # TODO: Write the function
    
    
def getOverlapIndicator(connection:psycopg2.extensions.connection,
                        schemaDatasetA:str,
                        tableNameDatasetA:str,
                        schemaDatasetB:str,
                        tableNameDatasetB:str,
                        filter:bool = False,
                        joinTable:str = 'bounding_box',
                        areaName:str = None) -> float:
    """Return the value of the overlap indicator for dataset A over dataset B.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database.
        schemaDatasetA (str): Name of the schema for the dataset A.
        tableNameDatasetA (str): Name of the table for the dataset A.
        schemaDatasetB (str): Name of the schema for the dataset B.
        tableNameDatasetB (str): Name of the table for the dataset B.
        filter (bool, optional): Choose to apply a filter or not. Defaults to False.
        joinTable (str, optional): Name of the join table, only necessary if the filter is on. Defaults to False.
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to "".

    Returns:
        float: Overlap indicator in percentage.
    """
    # TODO: Write the function
    
    
def getCorrespondingNodes(connection:psycopg2.extensions.connection,
                          schemaDatasetA:str,
                          tableNameDatasetA:str,
                          schemaDatasetB:str,
                          tableNameDatasetB:str,
                          filter:bool = False,
                          joinTable:str = 'bounding_box',
                          areaName:str = None) -> tuple[int, float]:
    """Return the number of corresponding nodes in dataset A, comparing it to dataset B,
    and the percentage of nodes.

    Args:
        connection (psycopg2.extensions.connection): Connection token for the database.
        schemaDatasetA (str): Name of the schema for the dataset A.
        tableNameDatasetA (str): Name of the table for the dataset A.
        schemaDatasetB (str): Name of the schema for the dataset B.
        tableNameDatasetB (str): Name of the table for the dataset B.
        filter (bool, optional): Choose to apply a filter or not. Defaults to False.
        joinTable (str, optional): Name of the join table, only necessary if the filter is on. Defaults to False.
        areaName (str, optional): Name of the area for the filer, only necessary if the filter is on. Defaults to "".

    Returns:
        tuple[int, float]: First value is the number of nodes,
        second value is the percentage of nodes.
    """
    # TODO: Write the function

if __name__ == "__main__":
    import time
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
    
    listArea = ['tateyama']
    
    for area in listArea:
        osmEdgeTable = osmEdgeTableTemplate.format(area)
        osmNodeTable = osmNodeTableTemplate.format(area)
        
        omfEdgeTable = omfEdgeTableTemplate.format(area)
        omfNodeTable = omfNodeTableTemplate.format(area)
        
        count = getNumberElements(connection, osmSchema, osmEdgeTable)
        print(f"Number of edges in OSM for {area} is : {count}")
        
        count = getNumberElements(connection, omfSchema, omfEdgeTable, filter = True, areaName = area.capitalize())
        print(f"Number of edges in OMF for {area} is : {count}")
        
        count = getNumberElements(connection, osmSchema, osmNodeTable)
        print(f"Number of nodes in OSM for {area} is : {count}")
        
        count = getNumberElements(connection, omfSchema, omfNodeTable, filter = True, areaName = area.capitalize())
        print(f"Number of nodes in OMF for {area} is : {count}")
    
    end = time.time()
    print(f"It took {end - start} seconds")