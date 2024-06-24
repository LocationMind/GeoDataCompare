import duckdb
import psycopg2
import sqlalchemy

def bboxCSVTobboxWKT(bboxCSV:str) -> str:
    """Transform a bounding box in CSV format to its equivalent in OGC WKT format.

    Args:
        bboxCSV (str): Bbox in the format 'E, S, W, N'.

    Returns:
        str: Bbox in OGC WKT format : 'POLYGON ((W S, E S, E N, W N, W S))'.
    """
    (W, S, E, N) = bboxCSV.split(',')
    bboxWKT = f"POLYGON (({W} {N}, {E} {N}, {E} {S}, {W} {S}, {W} {N}))"
    return bboxWKT


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
    It does not return anything, so this function should not be used for SELECT queries for instance.

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
    """Execute a select auery and return the cursor.

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