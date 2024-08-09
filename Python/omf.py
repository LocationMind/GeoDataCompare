import duckdb
import psycopg2
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Python import utils

## Create tables statement

def describeData(pathData: str):
    """Describe the data in a file.

    Args:
        pathData (str): Path of files to describe.
    """
    # Show data description
    rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{pathData}';")
    rel.show()


def createRoadTable(pathSegmentData: str,
                    tableName: str = 'road',
                    dropTableIfExists:bool = True,
                    schema:str = 'public',
                    newVersion:bool = True):
    """Create the road table in postgis.
    Depending on the `newVersion` parameter, the schema used to
    integrate data will be different.
    New version schema correspond to the one used after
    the 2024-06-13-beta.0 release included.

    Args:
        pathSegmentData (str): Path of the road data.
        tableName (str, optional): Name of the table to create. Defaults to 'road'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        newVersion (bool, optional): If True, take the new schema to integrate data.
        Otherwise, take the old schema.
        Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")
    
    # Choose which version to chose
    if newVersion:
        # New version and new schema
        duckdb.execute(
            f"""
            CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
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
            FROM '{pathSegmentData}'
            WHERE subtype = 'road');""")
    else:
        # Old version with old schemas
        duckdb.execute(
            f"""
            CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
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
            ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
            FROM '{pathSegmentData}'
            WHERE subtype = 'road');""")
    
    # Create index id and geometry
    createIndexIdDuckDB(tableName, schema = schema)
    createGeometryDuckDB(tableName, schema = schema)


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
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathConnectorData}');
               """)
    
    # Create index id and geometry
    createIndexIdDuckDB(tableName, schema = schema)
    createGeometryDuckDB(tableName, schema = schema)


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
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathBuildingData}');
               """)
    
    # Create index id and geometry
    createIndexIdDuckDB(tableName, schema = schema)
    createGeometryDuckDB(tableName, schema = schema)


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
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathBuildingPartData}');
               """)
    
    # Create index id and geometry
    createIndexIdDuckDB(tableName, schema = schema)
    createGeometryDuckDB(tableName, schema = schema)


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
    createIndexIdDuckDB(tableName, schema = schema)
    createGeometryDuckDB(tableName, schema = schema)


def createPlaceTable(pathPlaceData: str,
                     tableName: str = 'place',
                     dropTableIfExists:bool = True,
                     schema:str = 'public'):
    """Create the place table in postgis.

    Args:
        pathPlaceData (str): Path of the place data.
        tableName (str, optional): Name of the table to create. Defaults to 'place'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.{schema}.{tableName} CASCADE;")
    
    # Create the place table with all the good attributes
    duckdb.execute(f"""CREATE TABLE dbpostgresql.{schema}.{tableName} AS (SELECT
               id,
               version,
               update_time,
               JSON(sources) AS sources,
               names.primary AS primary_name,
               JSON(categories) as categories,
               confidence,
               websites,
               emails,
               socials,
               phones,
               JSON(addresses) as addresses,
               JSON(brand) as brand,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt
               FROM '{pathPlaceData}');
               """)
    
    # Create index id and geometry
    createIndexIdDuckDB(tableName, schema = schema)
    createGeometryDuckDB(tableName, schema = schema)


def createIndexIdDuckDB(tableName: str,
                        idTableName:str = "id",
                        schema:str = 'public'):
    """Create an index on the id column of the table.
    The name of the index will be `<tableName>_id_idx`

    Args:
        tableName (str): Name of the table.
        idTableName (str, optional): Name of the id column. Defaults to "id".
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    duckdb.execute(f"DROP INDEX IF EXISTS dbpostgresql.{schema}.{tableName}_id_idx CASCADE")
    duckdb.execute(f"CREATE INDEX {tableName}_id_idx ON dbpostgresql.{schema}.{tableName} ({idTableName});")


def createGeometryDuckDB(tableName: str,
                         schema:str = 'public'):
    """Creates the geom column of the table from the geom_wkt column.
    It also removes the geom_wkt and create a geom index, which name will be
    `<tableName>_geom_idx`

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


## Graph

def getExtentTable(connection:psycopg2.extensions.connection,
                   tableName:str,
                   schema:str = 'public') -> str:
    """Get extent of a geometrical table with a geom column.
    Return the extent in a CSV format,

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableName (str): Name of the table.
        schema (str, optional): Name of the schema. Defaults to 'public'.

    Returns:
        str: Bbox in a CSV format: "xmin,ymin,xmax,ymax".
    """
    # Create the query
    query = f"""
    WITH extent AS (
        SELECT public.ST_Extent(geom) AS bbox FROM {schema}.{tableName}
    )
    SELECT
        public.ST_XMin(e.bbox) AS x_min,
        public.ST_YMin(e.bbox) AS y_min,
        public.ST_XMax(e.bbox) AS x_max,
        public.ST_YMax(e.bbox) AS y_max
    FROM extent AS e;
    """
    
    # Get the cursor and the first line
    cursor = utils.executeSelectQuery(connection, query)
    row = cursor.fetchone()
    
    # Create the dictionnary
    bbox = f"{row[0]},{row[1]},{row[2]},{row[3]}"
    
    # Close the cursor
    cursor.close()
    
    return bbox


def deleteConnectors(connection:psycopg2.extensions.connection,
                     roadTable:str,
                     connectorTable:str,
                     schemaConnector:str = 'public',
                     schemaRoad:str = 'public') -> int:
    """Delete from the connector table all entity that does not intersects
    the road table.
    Return the number of entity deleted.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        roadTable (str): Name of the road table.
        connectorTable (str): Name of the connector table.
        schemaConnector (str, optional): Name of the schema for the connector table.
        Defaults to 'public'.
        schemaRoad (str, optional): Name of the schema for the road table.
        Defaults to 'public'.

    Returns:
        int: Number of entity deleted
    """
    # Create query
    sqlDelete = f"""
    DELETE FROM {schemaConnector}.{connectorTable}
    WHERE id not in (
        SELECT DISTINCT ON (c.id)
        c.id
        FROM {schemaConnector}.{connectorTable} AS c
        JOIN {schemaRoad}.{roadTable} AS r ON (public.ST_Intersects(c.geom, r.geom))
    );
    """
    
    # Execute the query and commit it
    cursor = utils.executeSelectQuery(connection, sqlDelete)
    connection.commit()
    
    # Get number of deleted connector
    nbDeleted = cursor.rowcount
    
    # Close cursor
    cursor.close()
    
    return nbDeleted


def createTablesFromBbox(bbox: str,
                         savePathFolder: str,
                         roadTable:str,
                         connectorTable:str,
                         connection:psycopg2.extensions.connection,
                         schema:str = "public",
                         newVersion:bool = True,
                         deleteDataWhenFinish:bool = True):
    """Create road and connector tables from a bbox.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        aeraName (str): Name of the area.
        roadTable (str): Name of the road table to create.
        connectorTable (str): Name of the road table to create.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema for saving the tables.
        Defaults to "public".
        newVersion (bool, optional): If True, take the new schema to integrate data.
        Otherwise, take the old schema.
        Defaults to True.
        deleteDataWhenFinish (bool, optional): Delete downloaded at the end of the
        process if True. Defaults to True.
    """
    # Download segment data
    pathSegmentFile = utils.downloadOMFTypeBbox(bbox, savePathFolder, "segment")
    
    # Create the road table and get its extent
    createRoadTable(pathSegmentFile, roadTable, schema = schema, newVersion=newVersion)
    newBbox = getExtentTable(connection, roadTable, schema = schema)
    
    # Download connector data from this bbox 
    pathConnectorFile = utils.downloadOMFTypeBbox(newBbox, savePathFolder, "connector")
    
    # Create the connector table
    createConnectorTable(pathConnectorFile, connectorTable, schema = schema)
    
    # Delete connectors that do not intersects with the 
    nb = deleteConnectors(connection,
                          roadTable = roadTable,
                          connectorTable = connectorTable,
                          schemaConnector = schema,
                          schemaRoad = schema)
    
    print(f"Number of entity deleted: {nb} ")
    
    # Delete the downloaded data if user wants
    if deleteDataWhenFinish:
        # Segment file
        if os.path.isfile(pathSegmentFile):
            os.remove(pathSegmentFile)
            print(f"{pathSegmentFile} has been deleted")
        else:
            print(f"{pathSegmentFile} is not a file")
        
        # Connector file
        if os.path.isfile(pathConnectorFile):
            os.remove(pathConnectorFile)
            print(f"{pathConnectorFile} has been deleted")
        else:
            print(f"{pathConnectorFile} is not a file")


def createRoadsConnectorsTable(extractedRoadTable:str,
                               extractedConnectorTable:str,
                               connection:psycopg2.extensions.connection,
                               schema:str = 'public',
                               roadsConnectorsTable:str = 'roads_connectors',
                               dropTableIfExists:bool = True):
    """Create the roads_connectors table from the extracted data.

    Args:
        extractedRoadTable (str): Name of the extracted road table.
        extractedConnectorTable (str): Name of the extracted connector table.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        roadsConnectorsTable (str, optional): Name of the table to create. Defaults to 'roads_connectors'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        utils.dropTableCascade(connection, roadsConnectorsTable, schema)
    
    # Create roads_connectors table
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{roadsConnectorsTable} AS
    SELECT
        r.id AS road_id,
        cons.con_id AS connector_id,
        json_array_length(r.connector_ids) AS max_i,
        cons.i::integer AS i,
        c.geom AS geom,
        r.version,
        r.update_time,
        r.sources,
        r.primary_name,
        r.class,
        r.connector_ids,
        r.access_restrictions,
        r.level_rules,
        r.prohibited_transitions,
        r.road_surface,
        r.road_flags,
        r.speed_limits,
        r.width_rules
    FROM
        {schema}.{extractedRoadTable} AS r, json_array_elements_text(r.connector_ids) WITH ORDINALITY cons(con_id, i)
    LEFT JOIN
        {schema}.{extractedConnectorTable} AS c ON cons.con_id = c.id
    WHERE r.class IS NOT null;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)

    # Indexes creation
    sqlCreateIndexes = f"""
    DROP INDEX IF EXISTS {schema}.{roadsConnectorsTable}_connector_road_idx CASCADE;
    
    CREATE INDEX IF NOT EXISTS {roadsConnectorsTable}_connector_road_idx
    ON {schema}.{roadsConnectorsTable} USING btree
    (connector_id ASC NULLS LAST)
    INCLUDE(road_id);
    
    DROP INDEX IF EXISTS {schema}.{roadsConnectorsTable}_road_i_idx CASCADE;
    
    CREATE INDEX IF NOT EXISTS {roadsConnectorsTable}_road_i_idx
    ON {schema}.{roadsConnectorsTable} USING btree
    (road_id ASC NULLS LAST, i ASC NULLS LAST);"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateIndexes)


def createConnectorsRoadCountTable(connection:psycopg2.extensions.connection,
                                   schema:str = 'public',
                                   roadsConnectorsTable:str = 'roads_connectors',
                                   connectorsRoadCountTable:str = 'connectors_road_count',
                                   dropTableIfExists:bool = True):
    """Create the connectors_road_count table from the extracted data.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        roadsConnectorsTable (str): Name of the roads connectors table. Defaults to 'roads_connectors'.
        connectorsRoadCountTable (str, optional): Name of the table to create. Defaults to 'connectors_road_count'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        utils.dropTableCascade(connection, connectorsRoadCountTable, schema)
    
    # Create table
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{connectorsRoadCountTable} AS
    SELECT connector_id, array_agg(road_id) AS roads, count(*) AS cnt
    FROM {schema}.{roadsConnectorsTable}
    GROUP BY connector_id;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    # Add primary key
    sqlPrimaryKey = f"""ALTER TABLE {schema}.{connectorsRoadCountTable} ADD PRIMARY KEY (connector_id);"""
    
    utils.executeQueryWithTransaction(connection, sqlPrimaryKey)
    
    # Create index on connector id column
    utils.createIndex(connection, connectorsRoadCountTable, columnName='connector_id', schema=schema)


def createEdgeTable(extractedRoadTable:str,
                    connection:psycopg2.extensions.connection,
                    schema:str = 'public',
                    roadsConnectorsTable:str = 'roads_connectors',
                    connectorsRoadCountTable:str = 'connectors_road_count',
                    edgeTable:str = 'edge',
                    dropTableIfExists:bool = True):
    """Create the edge table from the extracted roads and tables constructed before.
    The cost are not yet saved into this table.

    Args:
        extractedRoadTable (str): Name of the extracted road table.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        roadsConnectorsTable (str, optional): Name of the roads connector table. Defaults to 'roads_connectors'.
        connectorsRoadCountTable (str, optional): Name of the connectors road count table. Defaults to 'connectors_road_count'.
        edgeTable (str, optional): Name of the edge table to create. Defaults to 'edge'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """    
    

    # Drop table if the user wants to
    if dropTableIfExists:
        utils.dropTableCascade(connection, edgeTable, schema)

    # Create edge table
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{edgeTable} AS
    SELECT
        road_id AS omfid,
        CASE
            WHEN n = 1 AND "end" = max_i THEN road_id
            ELSE road_id || '-' || CAST(n AS character varying)
        END AS "id",
        "source",
        target,
        -- GEOMETRY CREATION
		public.ST_SplitLineFromPoints(r.geom, t.first_geom, t.second_geom) as geom,
        public.ST_Length(public.ST_SplitLineFromPoints(r.geom, t.first_geom, t.second_geom)::geography) AS len,
		public.ST_LineLocatePoint(r.geom, t.first_geom) AS start_value,
    	public.ST_LineLocatePoint(r.geom, t.second_geom) AS end_value,
        t.version,
        t.update_time,
        t.sources,
        t.primary_name,
        t.class,
        t.connector_ids,
        t.access_restrictions,
        t.level_rules,
        t.prohibited_transitions,
        t.road_surface,
        t.road_flags,
        t.speed_limits,
        t.width_rules
    FROM (
        SELECT
            road_id,
            max_i,
            row_number() OVER cons -1 AS n,
            lag(connector_id) OVER cons AS "source",
            connector_id AS target,
            lag(geom) OVER cons AS first_geom,
            geom AS second_geom,
            lag(i) OVER cons AS "start",
            i AS "end",
            version,
            update_time,
            sources,
            primary_name,
            class,
            connector_ids,
            access_restrictions,
            level_rules,
            prohibited_transitions,
            road_surface,
            road_flags,
            speed_limits,
            width_rules
        FROM {schema}.{roadsConnectorsTable}
        LEFT JOIN {schema}.{connectorsRoadCountTable} USING (connector_id)
        WINDOW cons AS (PARTITION BY road_id ORDER BY i ASC ROWS 1 PRECEDING)
        ORDER BY road_id ASC
    ) t
    LEFT JOIN {schema}.{extractedRoadTable} as r ON road_id = id
    WHERE n>0;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    # Add primary key
    sqlPrimaryKey = f"""ALTER TABLE {schema}.{edgeTable} ADD CONSTRAINT {edgeTable}_pkey PRIMARY KEY (id);"""
    
    utils.executeQueryWithTransaction(connection, sqlPrimaryKey)
    
    # Create geom index
    utils.createGeomIndex(connection, edgeTable, schema = schema)

    # Create original id index
    sqlIndex = f"""
    DROP INDEX IF EXISTS {schema}.{edgeTable}_omfid_idx CASCADE;

    CREATE INDEX IF NOT EXISTS {edgeTable}_omfid_idx
    ON {schema}.{edgeTable} USING btree
    (omfid ASC NULLS LAST)
    TABLESPACE pg_default;"""
    
    utils.executeQueryWithTransaction(connection, sqlIndex)


def createJoinEdgeTable(connection:psycopg2.extensions.connection,
                        schema:str = 'public',
                        edgeTable:str = 'edge',
                        joinEdgeTable:str = 'join_edge_str_to_int',
                        dropTableIfExists:bool = True):
    """Create a join table for edges id (string) and integer id for pgr_djikstra algorithm.
    It also inserts the value from the edges.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        edgeTable (str, optional): Name of the edge table. Defaults to 'edge'.
        joinEdgeTable (str, optional): Name of the join edge table. Defaults to 'join_edge_str_to_int'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        utils.dropTableCascade(connection, joinEdgeTable, schema)

    # Create the table and the indexes
    sqlCreateTable = f"""
    CREATE TABLE IF NOT EXISTS {schema}.{joinEdgeTable}
    (
        id bigserial PRIMARY KEY,
        edge_id character varying NOT NULL,
        CONSTRAINT {joinEdgeTable}_unique_edge_id UNIQUE (edge_id)
    );

    ALTER TABLE IF EXISTS {schema}.{joinEdgeTable}
        OWNER to postgres;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    # Create the indexes
    utils.createIndex(connection, joinEdgeTable, columnName='id', schema=schema)
    
    utils.createIndex(connection, joinEdgeTable, columnName='edge_id', schema=schema)
        
    # Insert the values
    sqlInsert = f"""
        INSERT INTO {schema}.{joinEdgeTable}(edge_id)
        SELECT id FROM {schema}.{edgeTable}
        ORDER BY id ASC;"""
        
    utils.executeQueryWithTransaction(connection, sqlInsert)


def createJoinConnectorTable(extractedConnectorTable:str,
                             connection:psycopg2.extensions.connection,
                             schema:str = 'public',
                             joinConnectorTable:str = 'join_connector_str_to_int',
                             dropTableIfExists:bool = True):
    
    """Create a join table for connectors id (string) and integer id for pgr_djikstra algorithm.
    It does it only for the extracted connector table.

    Args:
        extractedConnectorTable (str): Name of the extracted connector table.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        utils.dropTableCascade(connection, joinConnectorTable, schema)

    # Create the table and the indexes
    sqlCreateTable = f"""
    CREATE TABLE IF NOT EXISTS {schema}.{joinConnectorTable}
    (
        id bigserial PRIMARY KEY,
        connector_id character varying NOT NULL,
        CONSTRAINT {joinConnectorTable}_unique_connector_id UNIQUE (connector_id)
    );

    ALTER TABLE IF EXISTS {schema}.{joinConnectorTable}
        OWNER to postgres;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    # Create the indexes
    utils.createIndex(connection, joinConnectorTable, columnName='id', schema=schema)
    
    utils.createIndex(connection, joinConnectorTable, columnName='connector_id', schema=schema)
    
    # Insert the values
    sqlInsert = f"""
    INSERT INTO {schema}.{joinConnectorTable} (connector_id)
    SELECT id FROM {schema}.{extractedConnectorTable}
    ORDER BY id ASC;"""
    
    utils.executeQueryWithTransaction(connection, sqlInsert)


def createEdgeWithCostTable(connection:psycopg2.extensions.connection,
                            schema:str = 'public',
                            edgeTable:str = 'edge',
                            joinEdgeTable:str = 'join_edge_str_to_int',
                            joinConnectorTable:str = 'join_connector_str_to_int',
                            edgeWithCostTable:str = 'edge_with_cost',
                            dropTableIfExists:bool = True):
    """Create a table for edges with associated cost and reversed cost.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        edgeTable (str, optional): Name of the edge table. Defaults to 'edge'.
        joinEdgeTable (str, optional): Name of the join edge table. Defaults to 'join_edge_str_to_int'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostTable (str, optional): Name of the edge with cost table to create. Defaults to 'edge_with_cost'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """    

    # Drop view if the user wants to
    if dropTableIfExists:
        utils.dropTableCascade(connection, edgeWithCostTable, schema)
    
    # Create the view
    sqlCreateTable = f"""
    CREATE TABLE IF NOT EXISTS {schema}.{edgeWithCostTable} AS
    SELECT
        j.id,
        s.id AS "source",
        t.id AS "target",
        e.start_value,
        e.end_value,
        public.get_edge_cost(e.len, e.access_restrictions, 'forward', e.start_value, e.end_value) AS cost,
        public.get_edge_cost(e.len, e.access_restrictions, 'backward', e.start_value, e.end_value) AS reverse_cost,
        e.class,
        e.access_restrictions,
        e.level_rules,
        e.prohibited_transitions,
        e.road_surface,
        e.road_flags,
        e.speed_limits,
        e.width_rules,
        e.update_time,
        e.omfid,
        e.sources,
        e.primary_name,
        e.geom
    FROM {schema}.{edgeTable} AS e

    LEFT JOIN {schema}.{joinConnectorTable} AS s ON source=s.connector_id
    LEFT JOIN {schema}.{joinConnectorTable} AS t ON target=t.connector_id
    LEFT JOIN {schema}.{joinEdgeTable} AS j ON e.id=j.edge_id;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    utils.createIndex(connection, edgeWithCostTable, columnName="id", schema=schema)
    
    utils.createGeomIndex(connection, edgeWithCostTable, schema=schema)


def createNodeTable(connection:psycopg2.extensions.connection,
                    schema:str = 'public',
                    nodeTable:str = 'node',
                    connectorsRoadCountTable:str = 'connectors_road_count',
                    extractedConnectorTable:str = 'connector',
                    joinConnectorTable:str = 'join_connector_str_to_int',
                    edgeWithCostTable:str = 'edge_with_cost',
                    dropTableIfExists:bool = True):
    """Create the node table by counting the number of edges in and out for each node.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        nodeTable (str, optional): Name of the node table to create. Defaults to 'node'.
        connectorsRoadCountTable (str, optional): Name of the connectors road count table. Defaults to 'connectors_road_count'.
        extractedConnectorTable (str, optional): Name of the extracted connector table.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostTable (str, optional): Name of the edge with cost table to create. Defaults to 'edge_with_cost'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """    
    
    # Drop table if the user wants to
    if dropTableIfExists:
        utils.dropTableCascade(connection, nodeTable, schema)
    
    # Create nodes table
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{nodeTable} AS
    SELECT 
        j.id AS id,
        in_edges,
        out_edges,
        c.id AS omfid,
        c.geom,
        c.version,
        c.update_time,
        c.sources
    FROM {schema}.{connectorsRoadCountTable} AS cnt
    LEFT JOIN {schema}.{extractedConnectorTable} c ON cnt.connector_id = c.id
    LEFT JOIN {schema}.{joinConnectorTable} AS j ON j.connector_id = cnt.connector_id
    LEFT JOIN (
        SELECT target, array_agg(id) AS in_edges
        FROM {schema}.{edgeWithCostTable}
        WHERE target IS NOT NULL GROUP BY target) ei ON j.id = target
    LEFT JOIN (
        SELECT "source", array_agg(id) AS out_edges
        FROM {schema}.{edgeWithCostTable}
        WHERE "source" IS NOT NULL GROUP BY "source") eo ON j.id = "source";"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    # Add primary key
    sqlPrimaryKey = f"""ALTER TABLE {schema}.{nodeTable} ADD CONSTRAINT {nodeTable}_pkey PRIMARY KEY (id);"""
    
    utils.executeQueryWithTransaction(connection, sqlPrimaryKey)
    
    # Create geom index
    utils.createGeomIndex(connection, nodeTable, schema = schema)


def keepDataOnlyInBbox(area:str,
                       connection:psycopg2.extensions.connection,
                       schema:str = 'public',
                       edgeWithCostTable:str = 'edge_with_cost',
                       nodeTable:str = 'node'):
    """Update nodes and edges with cost table to keep only those inside the bbox.
    It creates new nodes and new edges if needed, and change the graph topology too.

    Args:
        area (str): Name of the area.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        edgeWithCostTable (str, optional): Name of the edge table. Defaults to 'edge'.
        nodeTable (str, optional): Name of the node table. Defaults to 'node'.
    """
    # Delete features outside the bounding box
    deleteOutsideBbox = f"""
    -- Delete not contains
    DELETE FROM {schema}.{edgeWithCostTable}
    WHERE id NOT IN (
        SELECT e.id FROM {schema}.{edgeWithCostTable} AS e
        JOIN public.bounding_box AS b
        ON public.ST_Intersects(b.geom, e.geom)
        WHERE b.name = '{area.capitalize()}');
    """
    
    # Execute query
    utils.executeQueryWithTransaction(connection, deleteOutsideBbox)
    
    # Update geometry of features intersecting the border of the bounding box
    updateGeomBbox = f"""
    -- Update geom by clipping with the bounding box
    WITH edge_border AS (
        SELECT e.id AS edge_id,
        public.ST_Intersection(b.geom, e.geom) AS new_geom
        FROM {schema}.{edgeWithCostTable} AS e 
        JOIN public.bounding_box AS b
        ON public.ST_Intersects(public.ST_Boundary(b.geom), e.geom)
        WHERE b.name = '{area.capitalize()}'
    )
    UPDATE {schema}.{edgeWithCostTable} AS e
    SET geom = eb.new_geom
    FROM edge_border AS eb
    WHERE e.id = eb.edge_id;
    """
    
    # Execute query
    utils.executeQueryWithTransaction(connection, updateGeomBbox)
    
    # For multigeom edges, dump them in single geometry and save them in the database
    multiGeomQuery = f"""
    -- multigeom case
    WITH multigeom AS (
        SELECT * FROM {schema}.{edgeWithCostTable} AS e
        WHERE public.ST_NumGeometries(e.geom) != 1
    ),
    dumpgeom AS (
        SELECT (public.ST_Dump(m.geom)).geom AS line, * FROM multigeom AS m
    ),
    insert_edges AS (
        INSERT INTO {schema}.{edgeWithCostTable} (
            id, source, target, start_value, end_value, cost, reverse_cost, class,
            access_restrictions, level_rules, prohibited_transitions, road_surface,
            road_flags, speed_limits, width_rules, update_time, omfid, sources, primary_name, geom
        )
        -- Increment id to ensure the unicity of this column
        SELECT ((SELECT MAX(id) FROM {schema}.{edgeWithCostTable}) + row_number() OVER (order by d.id)),
        source, target, start_value, end_value, cost, reverse_cost, class,
        access_restrictions, level_rules, prohibited_transitions, road_surface,
        road_flags, speed_limits, width_rules, update_time, omfid, sources, primary_name, d.line
        FROM dumpgeom AS d
    )
    DELETE FROM {schema}.{edgeWithCostTable}
    WHERE id IN (SELECT id FROM multigeom);
    """
    
    # Execute query
    utils.executeQueryWithTransaction(connection, multiGeomQuery)
    
    # Create new nodes at the border of the bounding box
    nodesClipQuery = f"""
    -- nodes
    WITH edge_border AS (
        SELECT e.id, e.source, e.target, e.geom
        FROM {schema}.{edgeWithCostTable} AS e 
        JOIN public.bounding_box AS b
        ON public.ST_Intersects(public.ST_Boundary(b.geom), e.geom)
        WHERE b.name = '{area.capitalize()}'
    ),
    clip_point AS (
        SELECT (public.ST_Dump(public.ST_Intersection(public.ST_Boundary(b.geom), e.geom))).geom AS point
        FROM edge_border AS e
        JOIN public.bounding_box AS b
        ON public.ST_Intersects(public.ST_Boundary(b.geom), e.geom)
        WHERE b.name = '{area.capitalize()}'
    ),
    insert_nodes AS (
        INSERT INTO {schema}.{nodeTable} AS n (id, geom)
        -- Increment id to ensure the unicity of this column
        SELECT ((SELECT MAX(id) FROM {schema}.{nodeTable}) + row_number() OVER (order by cp.point)),
        cp.point
        FROM clip_point AS cp
    )
    DELETE FROM {schema}.{nodeTable} AS n
    WHERE id NOT IN (
        SELECT n.id FROM {schema}.{nodeTable} AS n
        JOIN {schema}.{edgeWithCostTable} AS e
        ON public.ST_Intersects(n.geom, e.geom)
    );
    """
    
    # Execute query
    utils.executeQueryWithTransaction(connection, nodesClipQuery)
    
    # Correct the topology by modifying the source, target and cost
    correctTopology = f"""
    -- Correct topology
    WITH edge_border AS (
        SELECT e.id, e.source, e.target, e.geom
        FROM {schema}.{edgeWithCostTable} AS e 
        JOIN public.bounding_box AS b
        ON public.ST_Intersects(public.ST_Boundary(b.geom), e.geom)
        WHERE b.name = '{area.capitalize()}'
    ),
    edge_nodes AS (
        SELECT e.id, e.source, e.target, array_agg(n.id) AS nodes
        FROM edge_border AS e
        JOIN {schema}.{nodeTable} AS n
        ON public.ST_Intersects(n.geom, e.geom)
        GROUP BY e.id, e.source, e.target
        ORDER BY e.id
    ),
    new_source_target AS (
        SELECT e.id,
        CASE 
            WHEN e.source IN (e.nodes[1], e.nodes[2]) THEN e.source
            WHEN e.target = e.nodes[1] THEN e.nodes[2]
            WHEN e.target = e.nodes[2] THEN e.nodes[1]
            ELSE e.nodes[1]
        END AS new_source,
        CASE 
            WHEN e.target IN (e.nodes[1], e.nodes[2]) THEN e.target
            WHEN e.source = e.nodes[1] THEN e.nodes[2]
            WHEN e.source = e.nodes[2] THEN e.nodes[1]
            ELSE e.nodes[2]
        END AS new_target
        FROM edge_nodes AS e
    )
    UPDATE {schema}.{edgeWithCostTable} AS e
    SET
        source = nst.new_source,
        target = nst.new_target,
        cost = CASE WHEN cost = -1 THEN -1 ELSE public.ST_Length(e.geom::geography) END,
        reverse_cost = CASE WHEN reverse_cost = -1 THEN -1 ELSE public.ST_Length(e.geom::geography) END
    FROM new_source_target AS nst
    WHERE e.id = nst.id;
    """
    
    # Execute query
    utils.executeQueryWithTransaction(connection, correctTopology)


def createGraph(bbox:str,
                savePathFolder:str,
                area:str,
                connection:psycopg2.extensions.connection,
                schema:str = 'public',
                newVersion:bool = True,
                dropTablesIfExist:bool = True,
                deleteDataWhenFinish:bool = True,
                deleteOtherTables:bool = True,
                printTime:bool = True):
    """Create graph from a bounding box.
    The name of the tables are created with a template name,
    depending on the name of the area.

    DuckDb must be initialised with PostgreSQL first.

    Args:
        bbox (str): Bbox to extract data in it. Must be in the format 'E, S, W, N'.
        savePathFolder (str): Path of the destination folder.
        area (str): Name of the area.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        newVersion (bool, optional): If True, take the new schema to integrate data.
        Otherwise, take the old schema.
        Defaults to True.
        dropTablesIfExist (bool, optional): Drop all tables if True. Defaults to True.
        deleteDataWhenFinish (bool, optional): Delete downloaded at the end of the
        process if True. Defaults to True.
        deleteOtherTables (bool, optional): Delete other tables if True. Defaults to True.
        printTime (bool, optional): If true, print the time taken to the user. Defaults to True.
    """
    start = time.time()
    
    # Check if we print to the user or not
    if printTime:
        log = print
    else:
        # Empty function
        log = lambda x : x
    
    # If the area is not null, we create the name of the table
    if area != "":
        extractedRoadTable = f"road_{area}"
        extractedConnectorTable = f"connector_{area}"
        
        roadsConnectorsTable = f'roads_connectors_{area}'
        connectorsRoadCountTable = f'connectors_road_count_{area}'
        edgeTable = f'edge_{area}'
        joinEdgeTable = f'join_edge_str_to_int_{area}'
        joinConnectorTable = f'join_connector_str_to_int_{area}'
        edgeWithCostTable = f'edge_with_cost_{area}'
        nodeTable = f'node_{area}'
    else:
        raise ValueError("Area must not be an empty string")
    
    # Download and create extract tables
    createTablesFromBbox(bbox = bbox,
                         savePathFolder = savePathFolder,
                         roadTable = extractedRoadTable,
                         connectorTable = extractedConnectorTable,
                         connection = connection,
                         schema = schema,
                         newVersion = newVersion,
                         deleteDataWhenFinish = deleteDataWhenFinish)
    
    end = time.time()
    log(f"createTablesFromBbox: {end - start} seconds")

    # Create roads connector table
    createRoadsConnectorsTable(extractedRoadTable = extractedRoadTable,
                               extractedConnectorTable = extractedConnectorTable,
                               connection = connection,
                               schema = schema,
                               roadsConnectorsTable = roadsConnectorsTable,
                               dropTableIfExists = dropTablesIfExist)
    end = time.time()
    log(f"createRoadsConnectorsTable: {end - start} seconds")

    # Create connectors road count table
    createConnectorsRoadCountTable(connection = connection,
                                   schema = schema,
                                   roadsConnectorsTable = roadsConnectorsTable,
                                   connectorsRoadCountTable = connectorsRoadCountTable,
                                   dropTableIfExists = dropTablesIfExist)
    end = time.time()
    log(f"createConnectorsRoadCountTable: {end - start} seconds")
    
    # Create edge table
    createEdgeTable(extractedRoadTable = extractedRoadTable ,
                    connection = connection,
                    schema = schema,
                    roadsConnectorsTable = roadsConnectorsTable,
                    connectorsRoadCountTable = connectorsRoadCountTable,
                    edgeTable = edgeTable,
                    dropTableIfExists = dropTablesIfExist)
    end = time.time()
    log(f"createEdgeTable: {end - start} seconds")

    # Create join edges and join connectors tables
    createJoinEdgeTable(connection = connection,
                        schema = schema,
                        edgeTable = edgeTable,
                        joinEdgeTable = joinEdgeTable,
                        dropTableIfExists = dropTablesIfExist)
    end = time.time()
    log(f"createJoinEdgeTable: {end - start} seconds")
    
    createJoinConnectorTable(extractedConnectorTable = extractedConnectorTable,
                             connection = connection,
                             schema = schema,
                             joinConnectorTable = joinConnectorTable,
                             dropTableIfExists = dropTablesIfExist)
    end = time.time()
    log(f"createJoinConnectorTable: {end - start} seconds")
    
    # Create edges with cost and nodes tables
    createEdgeWithCostTable(connection = connection,
                            schema = schema,
                            edgeTable = edgeTable,
                            joinEdgeTable = joinEdgeTable,
                            joinConnectorTable = joinConnectorTable,
                            edgeWithCostTable = edgeWithCostTable,
                            dropTableIfExists = dropTablesIfExist)
    end = time.time()
    log(f"createEdgeWithCostTable: {end - start} seconds")
    
    createNodeTable(connection = connection,
                    schema = schema,
                    nodeTable = nodeTable,
                    connectorsRoadCountTable = connectorsRoadCountTable,
                    extractedConnectorTable = extractedConnectorTable,
                    joinConnectorTable = joinConnectorTable,
                    edgeWithCostTable = edgeWithCostTable,
                    dropTableIfExists = dropTablesIfExist)
    end = time.time()
    log(f"createNodeTable: {end - start} seconds")
    
    # Update topology and graph to keep data only in the bbox
    keepDataOnlyInBbox(area = area,
                       connection = connection,
                       schema = schema,
                       edgeWithCostTable = edgeWithCostTable,
                       nodeTable = nodeTable)
    end = time.time()
    log(f"createNodeTable: {end - start} seconds")
    
    # Delete all useless tables if the user wants to
    if deleteOtherTables:
        utils.dropTableCascade(connection, extractedRoadTable, schema)
        utils.dropTableCascade(connection, extractedConnectorTable, schema)
        utils.dropTableCascade(connection, roadsConnectorsTable, schema)
        utils.dropTableCascade(connection, connectorsRoadCountTable, schema)
        utils.dropTableCascade(connection, edgeTable, schema)
        utils.dropTableCascade(connection, joinEdgeTable, schema)
        utils.dropTableCascade(connection, joinConnectorTable, schema)
        
        end = time.time()
        log(f"deleteOtherTables: {end - start} seconds")
    
    end = time.time()
    log(f"Graph download for {area.capitalize()}: {end - start} seconds")


## Buildings

def createBuildingFromBbox(bbox: str,
                           savePathFolder: str,
                           area:str,
                           schema:str = "public",
                           deleteDataWhenFinish:bool = True):
    """Create building table from a bbox using overturemaps.py tool.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        area (str): Name of the area.
        schema (str, optional): Schema to save the table. Defaults to "public".
        deleteDataWhenFinish (bool, optional): Delete downloaded at the end of the
        process if True. Defaults to True.
    """
    # Download building data
    pathBuildingFile = utils.downloadOMFTypeBbox(bbox, savePathFolder, "building")
    
    # Name of the table
    tableName = f"building_{area}"
    
    # Create the road table and get its extent
    createBuildingTable(pathBuildingFile, tableName, schema = schema)
    
    # Delete the downloaded data if user wants
    if deleteDataWhenFinish:
        # Segment file
        if os.path.isfile(pathBuildingFile):
            os.remove(pathBuildingFile)
            print(f"{pathBuildingFile} has been deleted")
        else:
            print(f"{pathBuildingFile} is not a file")


## Places

def createPlaceFromBbox(bbox: str,
                        savePathFolder: str,
                        area:str,
                        schema:str = "public",
                        deleteDataWhenFinish:bool = True):
    """Create place table from a bbox using overturemaps.py tool.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        area (str): Name of the area.
        schema (str, optional): Schema to save the table. Defaults to "public".
        deleteDataWhenFinish (bool, optional): Delete downloaded at the end of the
        process if True. Defaults to True.
    """
    # Download place data
    pathPlaceFile = utils.downloadOMFTypeBbox(bbox, savePathFolder, "place")
    
    # Name of the table
    tableName = f"place_{area}"
    
    # Create the road table and get its extent
    createPlaceTable(pathPlaceFile, tableName, schema = schema)
    
    # Delete the downloaded data if user wants
    if deleteDataWhenFinish:
        # Segment file
        if os.path.isfile(pathPlaceFile):
            os.remove(pathPlaceFile)
            print(f"{pathPlaceFile} has been deleted")
        else:
            print(f"{pathPlaceFile} is not a file")