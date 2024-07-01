import duckdb
from duckdb.typing import *
import os
import time
import json

def downloadConnectorAndSegmentBbox(bbox: str,
                                    savePathFolder: str):
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
        data (str): Original data in string format.
        field (str): Name of the field to extract.

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
        pathData (str): Path of files to describe.
    """
    # Show data description
    rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{pathData}';")
    rel.show()


def createRoadTable(pathSegmentData: str,
                    tableName: str = 'road',
                    dropTableIfExists:bool = True,
                    schema:str = 'public'):
    """Create the road table in postgis. This function is not compatible with segment data
    released after the 2024/06/13 release, only before.

    Args:
        pathSegmentData (str): Path of the road data.
        tableName (str, optional): Name of the table to create. Defaults to 'road'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")

    # Create the road table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
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
                -- 'transportation' AS theme,
                -- 'road' AS type,
                ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
                FROM '{pathSegmentData}'
                WHERE subtype = 'road');""")
    
    # Create index id and geometry
    createIndexId(tableName, schema = schema)
    createGeometry(tableName, schema = schema)


def createRoadTableV2(pathSegmentData: str,
                      tableName: str = 'road',
                      dropTableIfExists:bool = True,
                      schema:str = 'public'):
    """Create the road table in postgis. This function is compatible with segment data
    released after the 2024/06/13 release.

    Args:
        pathSegmentData (str): Path of the road data.
        tableName (str, optional): Name of the table to create. Defaults to 'road'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")

    # Create the road table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
               id,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt,
               version,
               update_time,
               JSON(sources) AS sources,
               names.primary AS primary_name,
               class,
               JSON(connector_ids) AS connector_ids,
               JSON(access_restrictions) AS access_restrictions,
               JSON(level_rules) AS level_rules,
               JSON(prohibited_transitions) AS prohibited_transitions,
               JSON(road_surface) AS road_surface,
               JSON(road_flags) AS road_flags,
               JSON(speed_limits) AS speed_limits,
               JSON(width_rules) AS width_rules
                -- 'transportation' AS theme,
                -- 'road' AS type,
               FROM '{pathSegmentData}'
               WHERE subtype = 'road');""")
    
    # Create index id and geometry
    createIndexId(tableName, schema = schema)
    createGeometry(tableName, schema = schema)


def createConnectorTable(pathConnectorData: str,
                         tableName: str = 'connector',
                         dropTableIfExists:bool = True,
                         schema:str = 'public'):
    """Create the connector table in postgis.

    Args:
        pathConnectorData (str): Path of the connector data.
        tableName (str, optional): Name of the table to create. Defaults to 'connector'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")

    # Create the building table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
               id,
               version,
               update_time,
               JSON(sources) AS sources,
               -- 'transportation' AS theme,
               -- 'connector' AS type,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathConnectorData}');
               """)
    
    # Create index id and geometry
    createIndexId(tableName, schema = schema)
    createGeometry(tableName, schema = schema)


def createBuildingTable(pathBuildingData: str,
                        tableName: str = 'building',
                        dropTableIfExists:bool = True,
                        schema:str = 'public'):
    """Create the building table in postgis.

    Args:
        pathBuildingData (str): Path of the building data.
        tableName (str, optional): Name of the table to create. Defaults to 'building'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")

    # Create the building table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
               id,
               version,
               update_time,
               JSON(sources) AS sources,
               names.primary AS primary_name,
               class,
               level,
               height,
               has_parts,
               -- 'buildings' AS theme,
               -- 'building' AS type,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathBuildingData}');
               """)
    
    # Create index id and geometry
    createIndexId(tableName, schema = schema)
    createGeometry(tableName, schema = schema)


def createBuildingPartTable(pathBuildingPartData: str,
                            tableName: str = 'building_part',
                            dropTableIfExists:bool = True,
                            schema:str = 'public'):
    """Create the building_part table in postgis.

    Args:
        pathBuildingPartData (str): Path of the building_part data.
        tableName (str, optional): Name of the table to create. Defaults to 'building_part'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")

    # Create the building table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
               id,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt,
               version,
               update_time,
               JSON(sources) AS sources,
               names.primary AS primary_name,
               level,
               height,
               building_id,
               -- 'buildings' AS theme,
               -- 'building_part' AS type,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathBuildingPartData}');
               """)
    
    # Create index id and geometry
    createIndexId(tableName, schema = schema)
    createGeometry(tableName, schema = schema)


def createLocalityTable(pathLocality:str,
                        pathLocalityArea:str,
                        tableName:str = 'locality',
                        dropTableIfExists:bool = True,
                        schema:str = 'public'):
    """Create the locality table in postgis. Both localities and locality areas

    Args:
        pathLocality (str): Path of the locality data.
        pathLocalityArea (str): Path of the locality area data.
        tableName (str, optional): Name of the table to create. Defaults to 'road'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")
    
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
    duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName};")

    # Load data in a postgresql table
    duckdb.execute(f"""CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT 
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
    createIndexId(tableName, schema = schema)
    createGeometry(tableName, schema = schema)


def createIndexId(tableName: str,
                  idTableName:str = "id",
                  schema:str = 'public'):
    """Create an index on the id column of the table.
    The name of the index will be "<tableName>_id_idx"

    Args:
        tableName (str): Name of the table.
        idTableName (str, optional): Name of the id column. Defaults to "id".
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    duckdb.execute(f"DROP INDEX IF EXISTS dbpostgresql.{schema}.{tableName}_id_idx CASCADE")
    duckdb.execute(f"CREATE INDEX {tableName}_id_idx ON dbpostgresql.{schema}.{tableName} ({idTableName});")


def createGeometry(tableName: str,
                   schema:str = 'public'):
    """Creates the geom column of the table from the geom_wkt column.
    It also removes the geom_wkt and create a geom index, which name will be
    "<tableName>_geom_idx"

    Args:
        tableName (str): Name of the table.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Add a geometry column
    duckdb.execute(f"""CALL postgres_execute('dbpostgresql', 'ALTER TABLE IF EXISTS {schema}.{tableName} ADD COLUMN geom geometry;')""")

    # Create the geometry from the wkt one
    duckdb.execute(f"""CALL postgres_execute('dbpostgresql',
                'UPDATE {schema}.{tableName} 
                SET geom = public.ST_GeomFromText(geom_wkt, 4326)')""")
    
    # Remove the geom_wkt column
    duckdb.execute(f"""CALL postgres_execute('dbpostgresql',
                'ALTER TABLE {schema}.{tableName} 
                DROP COLUMN geom_wkt CASCADE;')""")
    
    # Create a geom index
    duckdb.execute(f"DROP INDEX IF EXISTS dbpostgresql.{schema}.{tableName}_geom_idx CASCADE;")
    
    duckdb.execute(
        f"""CALL postgres_execute(
            'dbpostgresql',
            'CREATE INDEX {tableName}_geom_idx
                ON {schema}.{tableName}
                USING GIST (geom);')""")


if __name__ == "__main__":
    import time
    start = time.time()
    # Path to data
    pathConnector = os.path.join("..", "Data", "OvertureMap_Japan", "connector", "japan_connector_2024_06_13.parquet")
    pathSegment = os.path.join("..", "Data", "OvertureMap_Japan", "segment", "japan_segment_2024_06_13.parquet")
    
    # Init duck db for postgres connection
    initDuckDb('pgrouting')

    # Create connector table (June release)
    describeData(pathConnector)
    createConnectorTable(pathConnector, schema = 'omf', dropTableIfExists=True)
    
    end = time.time()
    print(f"Connector table created in {end - start} seconds")
    
    # Create road table (June release)
    describeData(pathSegment)
    createRoadTableV2(pathSegment, schema = 'omf', dropTableIfExists=True)
    
    end = time.time()
    print(f"Road table created in {end - start} seconds")