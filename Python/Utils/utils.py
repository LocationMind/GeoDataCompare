import psycopg2
import sqlalchemy
import duckdb
import os
import utm
import dotenv

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
    The bbox is in format west, south, east, north.
    The tuple will be as (north, south, east, west).

    Args:
        bboxCSV (str): Bbox in the format 'W, S, E, N'.

    Returns:
        (tuple(float, float, float, float)): bbox in the format (N, S, E, W)
    """
    (west, south, east, north) = bboxCSV.split(',')
    return (float(north), float(south), float(east), float(west))


def initialiseDuckDB(path:str = None):
    """Initialise duckdb and connect it to a postgresql database.
    It also create postgis and pgrouting extension if not installed yet.
    
    To use the database, use "dbpostgresql" as the name of the database
    you will be connected to.

    Args:
        path (str, optional): Path of the .env file.
        The default value correspond to the .env file being at the project root.
        Defaults to None.
    """
    # Check if the path is provided
    if path is None:
        path = os.path.join(os.getcwd(), '.env')
    
    # Read environnment variables
    dotenv.load_dotenv(path)
    
    database = os.getenv("POSTGRES_DATABASE")
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    port = os.getenv("POSTGRES_PORT")
    
    # Create and load the spatial extension
    duckdb.install_extension("spatial")
    duckdb.load_extension("spatial")

    # Create and load the postgres extension
    duckdb.install_extension("postgres")
    duckdb.load_extension("postgres")
    
    # Attach to the PostgreSQL database
    duckdb.execute(f"ATTACH 'postgresql://{user}:{password}@{host}:{port}/{database}' AS dbpostgresql (TYPE POSTGRES);")


def getConnection(path:str = None) -> psycopg2.extensions.connection:
    """Get connection token to the database from .env file.
    If no path is provided, consider that the file is at the project root.

    Args:
        path (str, optional): Path of the .env file.
        The default value correspond to the .env file being at the project root.
        Defaults to None.

    Returns:
        psycopg2.extensions.connection: Database connection token.
    """
    if path is None:
        path = os.path.join(os.getcwd(), '.env')
    
    # Read environnment variables
    dotenv.load_dotenv(path)
    
    database = os.getenv("POSTGRES_DATABASE")
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    port = os.getenv("POSTGRES_PORT")
    
    # Get connection token
    connection = psycopg2.connect(database=database,
                                  host=host,
                                  user=user,
                                  password=password,
                                  port=port)
    return connection


def getEngine(path:str = None) -> sqlalchemy.engine.base.Engine:
    """Get engine from .env file.
    If no path is provided, consider that the file is at the project root.
    
    Args:
        path (str, optional): Path of the .env file.
        The default value correspond to the .env file being at the project root.
        Defaults to None.

    Returns:
        sqlalchemy.engine.base.Engine:
        Engine used for (geo)pandas sql queries.
    """
    # Check if the path is provided
    if path is None:
        path = os.path.join(os.getcwd(), '.env')
    
    # Read environnment variables
    dotenv.load_dotenv(path)
    
    database = os.getenv("POSTGRES_DATABASE")
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    port = os.getenv("POSTGRES_PORT")
    
    # Create engine
    engine = sqlalchemy.create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    return engine


def executeQueryWithTransaction(connection:psycopg2.extensions.connection,
                                query:str):
    """Execute a query safely by using a SQL transaction.
    It does not return anything, so this function should not be used
    for SELECT queries for instance.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        query (str): Insert query already formatted.
    
    Raises:
        Exeption: If an exception occur.
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


def addSplitLineFromPointsFunction(connection):
    """Add a custom function named "ST_SplitLineFromPoints" to the public schema.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
    """
    # Create and add the function
    sqlAddFunction = """
    CREATE OR REPLACE FUNCTION public.ST_SplitLineFromPoints(
        line geometry,
        point_a geometry,
        point_b geometry
        )
        RETURNS geometry AS
        $BODY$
        WITH
            split AS (SELECT (public.ST_Split(
                line,
                public.ST_Multi( public.ST_Union( point_a, point_b)))
                            ) geom)
            SELECT (g.gdump).geom as geom FROM (
            SELECT public.ST_Dump(
                geom
            ) AS gdump from split) as g
            WHERE public.ST_Intersects((g.gdump).geom, point_a) AND public.ST_Intersects((g.gdump).geom, point_b)
        $BODY$
        LANGUAGE SQL;

    ALTER FUNCTION public.ST_SplitLineFromPoints(geometry, geometry, geometry)
        OWNER TO postgres;
    
    COMMENT ON FUNCTION public.ST_SplitLineFromPoints(geometry, geometry, geometry)
        IS 'args: line, point_a, point_b - Returns a collection of geometries created by splitting a line by two points. It only returns the line that intersects the two points.';"""
    
    executeQueryWithTransaction(connection, sqlAddFunction)


def addGetEdgeCostFunction(connection):
    """Add a custom function named "get_edge_cost" to the public schema.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
    """
    
    # Create and add the function
    sqlAddFunction = """
    CREATE OR REPLACE FUNCTION public.get_edge_cost(
        len double precision,
        access_restrictions json,
        direction character varying,
        start_fraction double precision,
        end_fraction double precision
    )
    RETURNS double precision AS
    $BODY$
    DECLARE
        access json;
    BEGIN
        FOR access IN SELECT json_array_elements(access_restrictions) AS restrictions
        LOOP

            IF access->>'access_type' = 'denied'
            AND access->'when'->>'heading' = direction
            AND(
                (start_fraction >= (access->'between'->>0)::double precision
                AND end_fraction <= (access->'between'->>1)::double precision)
                OR access->>'between' is null) THEN
                -- Access denied, no cost
                RETURN -1;
            END IF;
        END LOOP;
        
        -- Access granted, return length of the edge
        RETURN len;
    END
    $BODY$
    LANGUAGE plpgsql;

    ALTER FUNCTION public.get_edge_cost(double precision, json, character varying, double precision, double precision)
        OWNER TO postgres;

    COMMENT ON FUNCTION public.get_edge_cost(double precision, json, character varying, double precision, double precision)
        IS 'args: len, access_restrictions, direction, start_fraction, end_fraction -
        Return cost of the edge with the right direction and start and end of line fraction.';"""
    
    executeQueryWithTransaction(connection, sqlAddFunction)


def initialisePostgreSQL(connection:psycopg2.extensions.connection):
    """Initialise postgreSQL by installing postgis and pgrouting extensions.
    If the extensions already exist, it skip the query.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
    """
    # Create extensions and schemas if not exist
    sqlInitPostgreSQL  = """
    CREATE EXTENSION IF NOT EXISTS postgis SCHEMA public;

    CREATE EXTENSION IF NOT EXISTS pgrouting SCHEMA public;

    CREATE SCHEMA IF NOT EXISTS osm;

    CREATE SCHEMA IF NOT EXISTS omf;

    CREATE SCHEMA IF NOT EXISTS results;"""
    
    executeQueryWithTransaction(connection, sqlInitPostgreSQL)
    
    # Add functions to postgresql
    addSplitLineFromPointsFunction(connection)
    addGetEdgeCostFunction(connection)


def createIndex(connection:psycopg2.extensions.connection,
                tableName:str,
                columnName:str,
                schema:str = 'public'):
    """Create a non geometrical index on the column table.
    Drop the index if already exists.
    The name of the index will be `<table_name>_<column>_idx`.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableName (str, optional): Name of the table.
        columnName (str): Name of the column.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Create the query
    sqlQuery = f"""DROP INDEX IF EXISTS {schema}.{tableName}_{columnName}_idx CASCADE;
    
    CREATE INDEX IF NOT EXISTS {tableName}_{columnName}_idx ON {schema}.{tableName} USING btree ({columnName} ASC NULLS LAST);"""
    
    # And execute it
    executeQueryWithTransaction(connection, sqlQuery)


def createGeomIndex(connection:psycopg2.extensions.connection,
                    tableName:str,
                    geomColumnName:str = 'geom',
                    schema:str = 'public'):
    """Create a geometrical index on the geom column for the speciefied table.
    Drop the index if already exists.
    The name of the index will be `<table_name>_geom_idx`.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableName (str, optional): Name of the table.
        columnName (str): Name of the geometry column. Defaults to 'geom'.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Create the query
    sqlQuery = f"""DROP INDEX IF EXISTS {schema}.{tableName}_geom_idx CASCADE;
        
    CREATE INDEX IF NOT EXISTS {tableName}_geom_idx
    ON {schema}.{tableName} USING GIST ({geomColumnName});"""
    
    # And execute it
    executeQueryWithTransaction(connection, sqlQuery)


def dropTableCascade(connection:psycopg2.extensions.connection,
                     tableName:str,
                     schema:str):
    """Drop (cascade) a table for the given schema

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableName (str): Name of the table to drop.
        schema (str): Name of the schema the table belong to.
    """
    dropSQL = f"DROP TABLE IF EXISTS {schema}.{tableName} CASCADE;"
    executeQueryWithTransaction(connection, dropSQL)
    

def createBoundingboxTable(connection:psycopg2.extensions.connection,
                           tableName:str = 'bounding_box',
                           dropTableIfExists:bool = True):
    """Create the bounding box table in the public schema.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableName (str, optional): Name of the table to create. Defaults to 'bounding_box'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        dropTableCascade(connection, tableName, schema = "public")
    
    # Create bounding_box structure
    sqlBbox = f"""
    CREATE TABLE IF NOT EXISTS public.{tableName} (
        id serial NOT NULL,
        geom geometry,
        wkt_geom character varying COLLATE pg_catalog."default",
        name character varying COLLATE pg_catalog."default",
        CONSTRAINT {tableName}_pkey PRIMARY KEY (id))"""
    
    executeQueryWithTransaction(connection, sqlBbox)
    
    # Index creation
    createIndex(connection, tableName, 'id', schema='public')

    # Geometry index creation
    createGeomIndex(connection, tableName, geomColumnName='geom', schema='public')


def insertBoundingBox(connection:psycopg2.extensions.connection,
                      wktGeom:str,
                      aeraName:str,
                      tableName:str = 'bounding_box') -> int:
    """Insert a bounding box inside the table.
    The geometry is provided in the WKT format.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        wktGeom (str): Geometry in OGC WKT format.
        aeraName (str): Name of the area.
        tableName (str, optional): Name of the bounding box table.
        Defaults to 'bounding_box'.
    
    Return:
        int: Id of the inserted row
    """
    # Insert value and return id
    sqlInsert = f"""
    INSERT INTO public.{tableName} (geom, wkt_geom, name)
    VALUES (public.ST_GeomFromText('{wktGeom}', 4326), '{wktGeom}', '{aeraName}');"""
    
    executeQueryWithTransaction(connection, sqlInsert)
    # Select the entity with the greatest id among those that corresponds exactly to the one added before
    sqlId = f"""
    SELECT id
    FROM public.{tableName}
    WHERE wkt_geom = '{wktGeom}'
    AND name = '{aeraName}'
    ORDER BY id DESC
    LIMIT 1"""
    
    cursor = executeSelectQuery(connection, sqlId)
    
    # Get id of the inserted row
    id = cursor.fetchone()[0]
    
    # Close the cursor
    cursor.close()
    
    return id


def isProcessAlreadyDone(connection:psycopg2.extensions.connection,
                         tableName:str,
                         schema:str,
                         skipCheck:bool = False) -> bool:
    """Return a boolean that indicates if the table is stored in the database.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        area (str): Name of the area.
        schema (str): Name of the schema.
        skipCheck (boo, optional): If True, do not check if it exists and return False.

    Returns:
        bool: True if the table is stored in the database.
    """
    # If the user do not want to check if it exists, return False
    if skipCheck:
        return False
    
    # Otherwise, check if the table exists    
    # Create query
    query = f"""
    SELECT t.table_schema, t.table_name FROM information_schema.tables AS t
    WHERE t.table_name = '{tableName}' and t.table_schema = '{schema}'
    ORDER BY t.table_schema, t.table_name ASC
    """
    
    # Execute query
    cursor = executeSelectQuery(connection, query)
    
    done = False
    # There should be only one row in the cursor
    if cursor.rowcount == 1:
        # If it is the case, because of the query, we do not need to check more information
       done = True
    
    return done


def downloadOMFTypeBbox(bbox: str,
                        savePathFolder: str,
                        dataType:str,
                        fileName:str = "") -> str:
    """Download OvertureMap data of a certain type for the designated bbox.
    Return the path of the saved file.
    Overturemaps must be already install using pip command tool :
    "pip install overturemaps"

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        dataType (str): Subtype of OMF data.
        fileName(str, optional): Name of the file without the extension.
        If empty, the filename will be the provided type.
        Defaults to ''.
    
    Raises:
        ValueError: If an error occured while downloading the data.
    
    Returns:
        str: Path of the saved file.
    """
    # Create the command line
    cmd = "overturemaps download --bbox={0} -f geoparquet --type={1} -o {2}"
    
    if fileName == "":
        fileName = dataType
        
    # Download OvertureMap connector data
    path = os.path.join(savePathFolder, f"{fileName}.parquet")
    
    # Run command
    print("Run command: ", cmd.format(bbox, dataType, path))
    result = os.system(cmd.format(bbox, dataType, path))
    
    # Check if result is okay
    if result != 0:
        raise(ValueError("An error as ocured"))
    
    print(f"{dataType} data has been downloaded")
    
    return path


def getUTMProjFromArea(connection:psycopg2.extensions.connection,
                       aeraName:str,
                       tableName:str = 'bounding_box') -> int:
    """Get UTM projection for a specific point.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        aeraName (str): Name of the area.
        tableName (str, optional): Name of the bounding box table.
        Defaults to 'bounding_box'.

    Returns:
        int: UTM projection crs id
    """
    # Get centroid of the area
    sql = f"""
    WITH area_centroid AS (
        SELECT public.ST_Centroid(geom) as center FROM public.{tableName}
        WHERE name = '{aeraName.capitalize()}'
        LIMIT 1
    )
    SELECT public.ST_X(ac.center) AS lon, public.ST_Y(ac.center) AS lat
    FROM area_centroid AS ac;
    """
    
    # Execute query
    cursor = executeSelectQuery(connection, sql)
    
    # Get lat and lon from row
    (lon, lat) = cursor.fetchone()
    
    # Get zone number
    zone = utm.from_latlon(latitude = lat, longitude = lon)[2]
    
    # Return formatted string
    epsgCode = f"326{zone:02d}" if lat >= 0 else f"327{zone:02d}"
    
    return int(epsgCode)