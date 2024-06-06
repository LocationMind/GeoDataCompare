import duckdb
from duckdb.typing import *
import os
import time
import json

def downloadConnectorAndSegmentBbox(bbox: str, savePathFolder: str):
    """Download OvertureMap data of a certain type for the designated bbox.
    Overturemaps must be already install using pip command tool :
    "pip install overturemaps"

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
    """
    # Create the command line
    cmd = "overturemaps download --bbox={0} -f geoparquet --type={1} -o {2}"

    # Download OvertureMap segment data
    pathSegment = os.path.join(savePathFolder, "segment.parquet")
    try:
        print("Run command : ", cmd.format(bbox, "segment", pathSegment))
        os.system(cmd.format(bbox, "segment", pathSegment))
        print("Segment data has been downloaded")
    except Exception as e:
        print(e)
    
    # Download OvertureMap connector data
    pathConnector = os.path.join(savePathFolder, "connector.parquet")
    try:
        print("Run command : ", cmd.format(bbox, "connector", pathConnector))
        os.system(cmd.format(bbox, "connector", pathConnector))
        print("Connector data has been downloaded")
    except Exception as e:
        print(e)


def extract_information(data:str,
                        field:str) -> str:
    """Extract information of the field in the data.
    Return none if no information were found.
    The data must be in a JSON format

    Args:
        data (str): Original data in string format
        field (str): Name of the field to extract

    Returns:
        str: Value of the field, None if there are no value
    """
    # If data is None, it returns None too
    if data is None:
        return None
    value = None
    # Convert string into a json
    try:
        json_data = json.loads(data)
        # If the value is in the dictionnary, we take it
        if field in json_data:
            value = json_data[field]
    except Exception as e:
        print(e)
    finally:
        return json.dumps(value)


def initDuckDb(dbname: str,
               host: str= '127.0.0.1',
               user: str= 'postgres',
               password: str= 'postgres'):
    """Initialise duckdb and connect it to a postgresql database
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

    duckdb.create_function("extract_info", extract_information, [VARCHAR, VARCHAR], VARCHAR)

    duckdb.execute(f"ATTACH 'dbname={dbname} host={host} user={user} password={password}' AS dbpostgresql (TYPE POSTGRES);")


def describeData(pathData: str):
    """Describe the data in one or serveal files

    Args:
        pathData (str): Path of files to describe
    """
    # Show data description
    rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{pathData}';")
    rel.show()


def initRoadTable(pathSegmentData: str, tableName: str = 'road', dropTableIfExists:bool = True):
    """Create the road table in postgis, without geometry

    Args:
        pathSegmentData (str): Path of the road data
        tableName (str, optional): Name of the table to create. Defaults to 'road'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{tableName} CASCADE;")

    # Create the road table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.public.{tableName} AS (SELECT
                id,
                version,
                update_time,
                JSON(sources) AS sources,
                names.primary AS primary_name,
                class,
                JSON(connector_ids) AS connector_ids,
                JSON(extract_info(road, 'surface')) AS surface,
                JSON(extract_info(road, 'width')) AS width,
                JSON(extract_info(road, 'lanes')) AS lanes,
                JSON(extract_info(road, 'restrictions')) AS restrictions,
                'transportation' AS theme,
                'road' AS type,
                ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
                FROM '{pathSegmentData}'
                WHERE subtype = 'road');""")


def initConnectorTable(pathConnectorData: str, tableName: str = 'connector', dropTableIfExists:bool = True):
    """Create the connector table in postgis, without geometry

    Args:
        pathConnectorData (str): Path of the connector data
        tableName (str, optional): Name of the table to create. Defaults to 'connector'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{tableName} CASCADE;")

    # Create the building table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.public.connector AS (SELECT
               id,
               version,
               update_time,
               JSON(sources) AS sources,
               'transportation' AS theme,
               'connector' AS type,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathConnectorData}');
               """)


def initBuildingTable(pathBuildingData: str, tableName: str = 'building', dropTableIfExists:bool = True):
    """Create the building table in postgis, without geometry

    Args:
        pathBuildingData (str): Path of the building data
        tableName (str, optional): Name of the table to create. Defaults to 'building'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{tableName} CASCADE;")

    # Create the building table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.public.building AS (SELECT
               id,
               version,
               update_time,
               JSON(sources) AS sources,
               names.primary AS primary_name,
               class,
               level,
               height,
               has_parts,
               'buildings' AS theme,
               'building' AS type,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathBuildingData}');
               """)


def initBuildingPartTable(pathBuildingPartData: str, tableName: str = 'building_part', dropTableIfExists:bool = True):
    """Create the building_part table in postgis, without geometry

    Args:
        pathBuildingPartData (str): Path of the building_part data
        tableName (str, optional): Name of the table to create. Defaults to 'building_part'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{tableName} CASCADE;")

    # Create the building table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.public.building_part AS (SELECT
               id,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt,
               version,
               update_time,
               JSON(sources) AS sources,
               names.primary AS primary_name,
               level,
               height,
               building_id,
               'buildings' AS theme,
               'building_part' AS type,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathBuildingPartData}');
               """)

def createLocalityTable(pathLocality:str, pathLocalityArea:str, tableName:str = 'locality', dropTableIfExists:bool = True):
    """Create the locality table in postgis, with everything.
    This function is different from the init functions as it creates everything directly.

    Args:
        pathLocality (str): Path of the locality data
        pathLocalityArea (str): Path of the locality area data
        tableName (str, optional): Name of the table to create. Defaults to 'road'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{tableName} CASCADE;")
    
    # Create table for the locality and for the locality area
    duckdb.execute(f"""CREATE TABLE locality AS (SELECT 
                id,
                ST_GeomFromWKB(geometry) AS geometry,
                JSON(bbox) AS bbox,
                admin_level,
                is_maritime,
                geopol_display,
                version,
                update_time,
                JSON(sources) AS sources,
                subtype,
                locality_type,
                wikidata,
                context_id,
                population,
                iso_country_code_alpha_2,
                iso_sub_country_code,
                default_language,
                driving_side,
                JSON(names) AS names,
                locality_id
                FROM '{pathLocality}'
                WHERE admin_level = 1);""")

    duckdb.execute("CREATE UNIQUE INDEX locality_id_idx ON locality (id);")

    duckdb.execute(f"""CREATE TABLE locality_area AS (SELECT 
                id,
                ST_GeomFromWKB(geometry) AS geometry,
                JSON(bbox) AS bbox,
                admin_level,
                is_maritime,
                geopol_display,
                version,
                update_time,
                JSON(sources) AS sources,
                subtype,
                locality_type,
                wikidata,
                context_id,
                population,
                iso_country_code_alpha_2,
                iso_sub_country_code,
                default_language,
                driving_side,
                JSON(names) AS names,
                locality_id
                FROM '{pathLocalityArea}');
                """)

    duckdb.execute("CREATE UNIQUE INDEX locality_area_id_idx ON locality_area (id);")

    # Join the two tables
    duckdb.execute(f"CREATE TABLE join_table_locality AS (SELECT l.* EXCLUDE (geometry), la.geometry FROM locality l JOIN locality_area la ON l.id = la.locality_id);")

    # Drop table
    duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{tableName};")

    # Load data in a postgresql table
    duckdb.execute(f"""CREATE TABLE dbpostgresql.public.{tableName} AS (SELECT 
                id,
                names.primary AS name,
                JSON(bbox) AS bbox,
                admin_level,
                is_maritime,
                geopol_display,
                version,
                update_time,
                JSON(sources) AS sources,
                subtype,
                locality_type,
                wikidata,
                context_id,
                population,
                iso_country_code_alpha_2,
                iso_sub_country_code,
                default_language,
                driving_side,
                locality_id,
                ST_AsText(geometry) AS geom_wkt
                FROM join_table_locality
                );
                """)
    
    # Create index id and geometry
    createIndexId(tableName)
    createGeometry(tableName)


def createIndexId(tableName: str, idTableName:str = "id"):
    """Create an index on the id column of the table.
    The name of the index will be "<tableName>_id_idx"

    Args:
        tableName (str): Name of the table
        idTableName (str, optional): Name of the id column. Defaults to "id".
    """
    duckdb.execute(f"DROP INDEX IF EXISTS dbpostgresql.public.{tableName}_id_idx CASCADE")
    duckdb.execute(f"CREATE INDEX {tableName}_id_idx ON dbpostgresql.public.{tableName} ({idTableName});")


def createGeometry(tableName: str):
    """Creates the geom column of the table from the geom_wkt column.
    It also removes the geom_wkt and create a geom index, which name will be
    "<tableName>_geom_idx"

    Args:
        tableName (str): Name of the table
    """
    # Add a geometry column
    duckdb.execute(f"""CALL postgres_execute('dbpostgresql', 'ALTER TABLE IF EXISTS public.{tableName} ADD COLUMN geom geometry;')""")

    # Create the geometry from the wkt one
    duckdb.execute(f"""CALL postgres_execute('dbpostgresql',
                'UPDATE public.{tableName} 
                SET geom = public.ST_GeomFromText(geom_wkt, 4326)')""")
    
    # Remove the geom_wkt column
    duckdb.execute(f"""CALL postgres_execute('dbpostgresql',
                'ALTER TABLE public.{tableName} 
                DROP COLUMN geom_wkt CASCADE;')""")
    
    # Create a geom index
    duckdb.execute(f"DROP INDEX IF EXISTS dbpostgresql.public.{tableName}_geom_idx CASCADE;")
    
    duckdb.execute(
        f"""CALL postgres_execute(
            'dbpostgresql',
            'CREATE INDEX {tableName}_geom_idx
                ON public.{tableName}
                USING GIST (geom);')""")


if __name__ == "__main__":

    # Create road table
    pathSave = os.path.join(".", "Data", "Test", "road_test.parquet")
    
    pathData = os.path.join("..", "Data", "OvertureMap_Japan", "connector", "*.parquet")
    
    initDuckDb('overturemap-pgrouting')

    initConnectorTable(pathData)

    createIndexId('connector')
    createGeometry('connector')