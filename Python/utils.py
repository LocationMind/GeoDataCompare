import duckdb
import psycopg2
import sqlalchemy

def bboxCSVToBboxWKT(bboxCSV:str) -> str:
    """Transform a bounding box in CSV format to its equivalent in OGC WKT format.

    Args:
        bboxCSV (str): Bbox in the format 'W, S, E, N'.

    Returns:
        str: Bbox in OGC WKT format : 'POLYGON ((W S, E S, E N, W N, W S))'.
    """
    (W, S, E, N) = bboxCSV.split(',')
    bboxWKT = f"POLYGON (({W} {N}, {E} {N}, {E} {S}, {W} {S}, {W} {N}))"
    return bboxWKT


def bboxCSVToTuple(bboxCSV:str) -> tuple[float, float, float, float]:
    """Tranform a bbox in a CSV format to a tuple.
    The bbox is in format west, south, east, north
    The tuple will be as (north, south, east, west)

    Args:
        bboxCSV (str): Bbox in the format 'W, S, E, N'.

    Returns:
        (tuple(float, float, float, float)): bbox in the format (north, south, east, west)
    """
    (west, south, east, north) = bboxCSV.split(',')
    return (float(north), float(south), float(east), float(west))


def initialiseDuckDB(dbname: str,
                     host: str= '127.0.0.1',
                     user: str= 'postgres',
                     password: str= 'postgres'):
    """Initialise duckdb and connect it to a postgresql database.
    It also create postgis and pgrouting extension if not installed yet.
    
    To use the database, use "dbpostgresql" as the name of the database
    you will be connected to.

    Args:
        dbname (str): Name of the database.
        host (str, optional): Host of the database. Defaults to '127.0.0.1'.
        user (str, optional): Username for the database. Defaults to 'postgres'.
        password (str, optional): User password for the database. Defaults to 'postgres'.
    """
    # Create and load the spatial extension
    duckdb.install_extension("spatial")
    duckdb.load_extension("spatial")

    # Create and load the postgres extension
    duckdb.install_extension("postgres")
    duckdb.load_extension("postgres")

    duckdb.execute(f"ATTACH 'dbname={dbname} host={host} user={user} password={password}' AS dbpostgresql (TYPE POSTGRES);")
    
    # Create PostGIS extension if not exists
    duckdb.execute(
        """
        CALL postgres_execute(
            'dbpostgresql',
            'CREATE EXTENSION IF NOT EXISTS postgis;')""")
    
    # Create PgRouting extension if not exists
    duckdb.execute(
        """
        CALL postgres_execute(
            'dbpostgresql',
            'CREATE EXTENSION IF NOT EXISTS pgrouting;')""")


def getConnection(database:str,
                  host:str="127.0.0.1",
                  user:str="postgres",
                  password:str="postgres",
                  port:str="5432") -> psycopg2.extensions.connection:
    """
    Get connection token to the database.
    Only the host is required, other parameters can be ommited.

    Parameters
    ----------
    database (str): Database to connect to.
    host (str, optional): Ip address for the database connection. The default is "127.0.0.1"
    user (str, optional): Username for the database connection. The default is "postgres".
    password (str, optional): Password for the database connection. The default is "postgres".
    port (str, optional): Port for the connection. The default is "5432".

    Returns
    -------
        psycopg2.extensions.connection: Database connection token.

    """
    connection = psycopg2.connect(database=database,
                                  host=host,
                                  user=user,
                                  password=password,
                                  port=port)
    return connection


def getEngine(database:str,
              host:str="127.0.0.1",
              user:str="postgres",
              password:str="postgres",
              port:str="5432") -> sqlalchemy.engine.base.Engine:
    """Get sqlalchemy engine to connect to the database.
    
    Args:
        database (str): Database to connect to.
        host (str, optional): Ip address for the database connection. The default is "127.0.0.1"
        user (str, optional): Username for the database connection. The default is "postgres".
        password (str, optional): Password for the database connection. The default is "postgres".
        port (str, optional): Port for the connection. The default is "5432".

    Returns:
        sqlalchemy.engine.base.Engine: Engine with the database connection.
    """
    engine = sqlalchemy.create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    return engine

def initialisePostgreSQL(connection:psycopg2.extensions.connection):
    """Initialise postgreSQL by installing postgis and pgrouting extensions.
    If the extensions already exist, it skip the query.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
    """
    # Create PgRouting extension if not exists
    sqlInitPostgreSQL  = """
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS pgrouting;"""
    
    executeQueryWithTransaction(connection, sqlInitPostgreSQL)


def executeQueryWithTransaction(connection:psycopg2.extensions.connection,
                                query:str):
    """Execute a query safely by using a SQL transaction.
    It does not return anything, so this function should not be used
    for SELECT queries for instance.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        query (str): Insert query already formatted.
    """
    try:
        cursor = connection.cursor()
        # Execute and commit the query
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        # If there is an error, the transaction is canceled
        connection.rollback()
        print("The following error occured :", e)
        cursor.close()
        raise Exception(e)
    finally:
        # The transaction is closed anyway
        cursor.close()


def executeSelectQuery(connection:psycopg2.extensions.connection,
                       query:str) -> psycopg2.extensions.cursor:
    """Execute a select query and return the cursor.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        query (str): Insert query already formatted.
    
    Return:
        psycopg2.extensions.cursor: cursor for the query.
    """
    cursor = connection.cursor()
    # Execute and commit the query
    cursor.execute(query)

    return cursor

def isProcessAlreadyDone(connection:psycopg2.extensions.connection,
                         area:str,
                         schema:str) -> bool:
    """Return a boolean that indicates if the table is store in the database.
    To do so, check if edge_with_cost and node tables are created for the
    given schema.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        area (str): Name of the area.
        schema (str): Name of the schema.

    Returns:
        bool: True if the table is stored in the database.
    """
    # Create edge with cost and node table name
    edgeTable = f"edge_with_cost_{area}"
    nodeTable = f"node_{area}"
    
    # Create query
    query = f"""
    SELECT t.table_schema, t.table_name FROM information_schema.tables AS t
    WHERE ((t.table_name = '{edgeTable}') OR (t.table_name = '{nodeTable}'))
    AND (t.table_schema = '{schema}')
    ORDER BY t.table_schema, t.table_name ASC
    """
    
    # Execute query
    cursor = executeSelectQuery(connection, query)
    
    done = False
    # Exactly two rows are selected is the process has been done
    if cursor.rowcount == 2:
        # Result is already sorted, so the first row should be the edge one, the second the node
        edgeRow = cursor.fetchone()
        nodeRow = cursor.fetchone()
        if edgeRow == (schema, edgeTable) and nodeRow == (schema, nodeTable):
            done = True
    
    return done