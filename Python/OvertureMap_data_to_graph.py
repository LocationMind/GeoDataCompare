import duckdb
import psycopg2
import sqlalchemy
import os
import utils
import data_integration as di


def downloadSegmentBbox(bbox: str,
                        savePathFolder: str,
                        fileName:str = "segment") -> str:
    """Download OvertureMap data of a certain type for the designated bbox.
    Overturemaps must be already install using pip command tool :
    "pip install overturemaps"

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        fileName(str, optional): Name of the file without the extension. Defaults to 'segment'.
    
    Returns:
        str: Path of the saved file.
    """
    # Create the command line
    cmd = "overturemaps download --bbox={0} -f geoparquet --type={1} -o {2}"

    # Download OvertureMap segment data
    pathSegment = os.path.join(savePathFolder, f"{fileName}.parquet")
    try:
        print("Run command : ", cmd.format(bbox, "segment", pathSegment))
        os.system(cmd.format(bbox, "segment", pathSegment))
        print("Segment data has been downloaded")
    except Exception as e:
        print(e)
    
    return pathSegment


def downloadConnectorBbox(bbox: str,
                          savePathFolder: str,
                          fileName:str = "connector") -> str:
    """Download OvertureMap data of a certain type for the designated bbox.
    Overturemaps must be already install using pip command tool :
    "pip install overturemaps"

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        fileName(str, optional): Name of the file without the extension. Defaults to 'segment'.
    
    Returns:
        str: Path of the saved file.
    """
    # Create the command line
    cmd = "overturemaps download --bbox={0} -f geoparquet --type={1} -o {2}"

    # Download OvertureMap connector data
    pathConnector = os.path.join(savePathFolder, f"{fileName}.parquet")
    try:
        print("Run command : ", cmd.format(bbox, "connector", pathConnector))
        os.system(cmd.format(bbox, "connector", pathConnector))
        print("Connector data has been downloaded")
    except Exception as e:
        print(e)
    
    return pathConnector


def getExtentTable(connection:psycopg2.extensions.connection,
                   tableName:str,
                   schema:str = 'public') -> dict[str, float]:
    """Get extent of a geometrical table with a geom column for

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableName (str): Name of the table.
        schema (str, optional): Name of the schema. Defaults to 'public'.

    Returns:
        dict[str, float]: Bbox in a CSV format: "xmin,ymin,xmax,ymax".
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
                     tableNameConnector:str,
                     tableNameRoad,
                     schemaConnector:str = 'public',
                     schemaRoad:str = 'public') -> int:
    """Delete from the connector table all entity that does not intersects
    the road table.
    Return the number of entity deleted.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableNameConnector (str): Name of the connector table.
        tableNameRoad (_type_): Name of the road table.
        schemaConnector (str, optional): Name of the schema for the connector table.
        Defaults to 'public'.
        schemaRoad (str, optional): Name of the schema for the road table.
        Defaults to 'public'.

    Returns:
        int: Number of entity deleted
    """
    # Create query
    sqlDelete = f"""
    DELETE FROM {schemaConnector}.{tableNameConnector}
    WHERE id not in (
        SELECT DISTINCT ON (c.id)
        c.id
        FROM {schemaConnector}.{tableNameConnector} AS c
        JOIN {schemaRoad}.{tableNameRoad} AS r ON (public.ST_Intersects(c.geom, r.geom))
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
                         area:str,
                         roadTable:str,
                         connectorTable:str,
                         schema:str = "public",
                         deleteDataWhenFinish:bool = True):
    """Create road and connector tables from a bbox.

    Args:
        bbox (str): Bbox in the format 'east, south, west, north'.
        savePathFolder (str): Path of the destination folder.
        aeraName (str): Name of the area.
        roadTable (str): Name of the road table to create.
        connectorTable (str): Name of the road table to create
        schema (str, optional): Name of the schema for saving the tables.
        Defaults to "public".
        deleteDataWhenFinish (bool, optional): Delete downloaded at the end of the
        process if True. Defaults to True.
    """
    # Create files names
    segmentFile = f"segment_{area}"
    connectorFile = f"connector_{area}"
    
    # Download segment data
    pathSegmentFile = downloadSegmentBbox(bbox, savePathFolder, segmentFile)
    
    # Create the road table and get its extent
    di.createRoadTableV2(pathSegmentFile, roadTable, schema = schema)
    newBbox = getExtentTable(connection, roadTable, schema = schema)
    
    # Download connector data from this bbox 
    pathConnectorFile = downloadConnectorBbox(newBbox, savePathFolder, connectorFile)
    
    # Create the connector table
    di.createConnectorTable(pathConnectorFile, connectorTable, schema = schema)
    
    # Delete connectors that do not intersects with the 
    nb = deleteConnectors(connection,
                          tableNameConnector = connectorTable,
                          tableNameRoad = roadTable,
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
    

def createIndex(connection:psycopg2.extensions.connection,
                tableName:str,
                columnName:str,
                schema:str = 'public'):
    """Create a non geometrical index on the column table.
    Drop the index if already exists.
    The name of the index will be <table_name>_<column>_idx.

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
    utils.executeQueryWithTransaction(connection, sqlQuery)


def createGeomIndex(connection:psycopg2.extensions.connection,
                    tableName:str,
                    geomColumnName:str = 'geom',
                    schema:str = 'public'):
    """Create a geometrical index on the geom column for the speciefied table.
    Drop the index if already exists.
    The name of the index will be <table_name>_geom_idx.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        tableName (str, optional): Name of the table.
        columnName (str): Name of the geometry column. Defaults to 'geom'.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Create the query
    sqlQuery = f"""DROP INDEX IF EXISTS {schema}.{tableName}_geom_idx CASCADE;
        
    CREATE INDEX IF NOT EXISTS {tableName}_geom_idx ON {schema}.{tableName} USING GIST ({geomColumnName});"""
    
    # And execute it
    utils.executeQueryWithTransaction(connection, sqlQuery)


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
        dropSQL = f"DROP TABLE IF EXISTS public.{tableName} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)
    
    # Create bounding_box structure
    sqlBbox = f"""
    CREATE TABLE IF NOT EXISTS public.{tableName} (
        id serial NOT NULL,
        geom geometry,
        wkt_geom character varying COLLATE pg_catalog."default",
        name character varying COLLATE pg_catalog."default",
        CONSTRAINT {tableName}_pkey PRIMARY KEY (id))"""
    
    utils.executeQueryWithTransaction(connection, sqlBbox)
    
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
        tableName (str, optional): Name of the table to create. Defaults to 'bounding_box'.
    
    Return:
        int: Id of the inserted row
    """
    # Insert value and return id
    sqlInsert = f"""
    INSERT INTO public.{tableName} (geom, wkt_geom, name)
    VALUES (public.ST_GeomFromText('{wktGeom}', 4326), '{wktGeom}', '{aeraName}');"""
    
    utils.executeQueryWithTransaction(connection, sqlInsert)
    # Select the entity with the greatest id among those that corresponds exactly to the one added before
    sqlId = f"""
    SELECT id
    FROM public.{tableName}
    WHERE wkt_geom = '{wktGeom}'
    AND name = '{aeraName}'
    ORDER BY id DESC
    LIMIT 1"""
    
    cursor = utils.executeSelectQuery(connection, sqlId)
    
    # Get id of the inserted row
    id = cursor.fetchone()[0]
    
    # Close the cursor
    cursor.close()
    
    return id


def extractRoads(extractedRoadTable:str,
                 boundingBoxId:int,
                 connection:psycopg2.extensions.connection,
                 schema:str = 'public',
                 roadTable:str = 'road',
                 boundingBoxTable:str = 'bounding_box',
                 dropTableIfExists:bool = True):
    """Extract roads from the bbox. The road table must have been created
    by functions in data_integration script.

    Args:
        extractedRoadTable (str): Name of the extracted road table.
        boundingBoxId (int): Id of the bounding box.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        roadTable (str, optional): Name of the initial road table. Defaults to 'road'.
        boundingBoxTable (str, optional): Name of the bounding box table. Defaults to 'bounding_box'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{extractedRoadTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)
    
    # Extract roads from the bounding box
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{extractedRoadTable} AS
    SELECT
        r.id,
        r.geom,
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
    FROM {schema}.{roadTable} r
        JOIN public.{boundingBoxTable} AS box ON public.ST_Intersects(r.geom, box.geom)
    WHERE box.id = {boundingBoxId};"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    # Create geom index
    createGeomIndex(connection, extractedRoadTable, schema=schema)
    
    # Create another index
    sqlOtherIndex = f"""
    DROP INDEX IF EXISTS {schema}.{extractedRoadTable}_id_idx CASCADE;

    CREATE INDEX IF NOT EXISTS {extractedRoadTable}_id_idx
    ON {schema}.{extractedRoadTable} USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default;"""
    
    utils.executeQueryWithTransaction(connection, sqlOtherIndex)
    

def extractConnectors(extractedConnectorTable:str,
                      extractedRoadTable:str,
                      connection:psycopg2.extensions.connection,
                      schema:str = 'public',
                      connectorTable:str = 'connector',
                      dropTableIfExists:bool = True):
    """Extract connectors that intersects the extracted roads.
    Connectors might be outside of the bbox if extracted roads are outside the bbox too.

    Args:
        extractedConnectorTable (str): Name of the extracted connector table.
        extractedRoadTable (str): Name of the extracted road table.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        connectorTable (str, optional): Name of the initial connector table. Defaults to 'connector'
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{extractedConnectorTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)

    # Extract connectors from the bounding box
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{extractedConnectorTable} AS
    SELECT DISTINCT ON (c.id)
        c.id,
		c.geom,
        c.version,
        c.update_time,
        c.sources
    FROM {schema}.{connectorTable} AS c
    JOIN {schema}.{extractedRoadTable} AS r ON public.ST_Intersects(c.geom, r.geom)
	ORDER BY c.id;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    # Create index if exists
    sqlOtherIndex = f"""
    DROP INDEX IF EXISTS {schema}.{extractedConnectorTable}_id_idx CASCADE;

    CREATE INDEX IF NOT EXISTS {extractedConnectorTable}_id_idx
    ON {schema}.{extractedConnectorTable} USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default;"""
    
    utils.executeQueryWithTransaction(connection, sqlOtherIndex)


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
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{roadsConnectorsTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)
    
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
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{connectorsRoadCountTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)
    
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
    createIndex(connection, connectorsRoadCountTable, columnName='connector_id', schema=schema)


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
    
    utils.executeQueryWithTransaction(connection, sqlAddFunction)


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
    
    utils.executeQueryWithTransaction(connection, sqlAddFunction)


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
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{edgeTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)

    # Create edge table
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{edgeTable} AS
    SELECT
        road_id AS original_id,
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
    createGeomIndex(connection, edgeTable, schema = schema)

    # Create original id index
    sqlIndex = f"""
    DROP INDEX IF EXISTS {schema}.{edgeTable}_original_id_idx CASCADE;

    CREATE INDEX IF NOT EXISTS {edgeTable}_original_id_idx
    ON {schema}.{edgeTable} USING btree
    (original_id ASC NULLS LAST)
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
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{joinEdgeTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)

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
    createIndex(connection, joinEdgeTable, columnName='id', schema=schema)
    
    createIndex(connection, joinEdgeTable, columnName='edge_id', schema=schema)
        
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
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{joinConnectorTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)

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
    createIndex(connection, joinConnectorTable, columnName='id', schema=schema)
    
    createIndex(connection, joinConnectorTable, columnName='connector_id', schema=schema)
    
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
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{edgeWithCostTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)
    
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
        e.sources,
        e.primary_name,
        e.geom
    FROM {schema}.{edgeTable} AS e

    LEFT JOIN {schema}.{joinConnectorTable} AS s ON source=s.connector_id
    LEFT JOIN {schema}.{joinConnectorTable} AS t ON target=t.connector_id
    LEFT JOIN {schema}.{joinEdgeTable} AS j ON e.id=j.edge_id;"""
    
    utils.executeQueryWithTransaction(connection, sqlCreateTable)
    
    createIndex(connection, edgeWithCostTable, columnName="id", schema=schema)
    
    createGeomIndex(connection, edgeWithCostTable, schema=schema)


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
        dropSQL = f"DROP TABLE IF EXISTS {schema}.{nodeTable} CASCADE;"
        utils.executeQueryWithTransaction(connection, dropSQL)
    
    # Create nodes table
    sqlCreateTable = f"""
    CREATE TABLE {schema}.{nodeTable} AS
    SELECT j.id AS id, in_edges, out_edges, c.geom
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
    createGeomIndex(connection, nodeTable, schema = schema)
    

def getClosestPointIntId(lat:float,
                         lon:float,
                         extractedConnectorTable:str,
                         connection:psycopg2.extensions.connection,
                         schema:str = 'public',
                         joinConnectorTable:str = 'join_connector_str_to_int') -> int:
    """Return the closest point id of the graph from the point in parameter.
    The coordinantes must be given in WGS84, SRID:4326

    Args:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        extractedConnectorTable (str, optional): Name of the extracted connector table.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.

    Returns:
        int: Id of the closest point, compatible with pgr_djikstra algorithm.
    """
    # Select the closest point
    sqlSelect = f"""
    SELECT j.id, public.ST_Transform(public.ST_GeomFromText('POINT({lon} {lat})', 4326), 6691)  <-> public.ST_Transform(c.geom, 6691) AS dist
    FROM {schema}.{extractedConnectorTable} AS c
    JOIN {schema}.{joinConnectorTable} AS j on j.connector_id = c.id
    ORDER by dist
    LIMIT 1;"""
    
    cursor = utils.executeSelectQuery(connection, sqlSelect)
    
    # Get first line
    result= cursor.fetchone()
    id = result[0]
    
    # Close cursor
    cursor.close()
    return id


def djikstra(startLat:float,
             startLon:float,
             endLat:float,
             endLon:float,
             saveGeoJSONPath:str,
             extractedConnectorTable:str,
             schema:str = 'public',
             joinConnectorTable:str = 'join_connector_str_to_int',
             edgeWithCostTable:str = 'edge_with_cost'
             ):
    """Execute the pgr_djikstra algorithm and save the result into a GeoJSON file.
    The graph is always consider to be oriented.
    The points must be given in WGS84, SRID:4326.
    
    DuckDb is used for this query, especially for the export in GeoJSON

    Args:
        startLat (float): Latitude of the starting point.
        startLon (float): Longitude of the starting point.
        endLat (float): Latitude of the ending point.
        endLon (float): Longitude of the ending point.
        saveGeoJSONPath (str): Save path for the GeoJSON file.
        extractedConnectorTable (str,): Name of the extracted connector table.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostTable (str, optional): Name of the edge with cost table. Defaults to 'edge_with_cost'.
    """

    # Get ids of start and end points
    startId = getClosestPointIntId(startLat, startLon, extractedConnectorTable, joinConnectorTable)
    endId = getClosestPointIntId(endLat, endLon, extractedConnectorTable, joinConnectorTable)

    # Run pgr_djikstra algorithm between those points    
    rel = duckdb.sql(f"""
    SELECT * FROM postgres_query(
        'dbpostgresql',
        'SELECT seq, edge, dij."cost", public.ST_AsGeoJSON(geom) as geojson
        FROM pgr_dijkstra(
            ''SELECT id, source, target, cost, reverse_cost
            FROM {schema}.{edgeWithCostTable}''::text,
            {startId},
            {endId},
            directed := true) dij
        JOIN {schema}.{edgeWithCostTable} AS e ON edge = e.id;')""")
    
    rel.show()

    rel.to_table("djikstra")
    
    # Add a geometry column to djikstra table
    duckdb.execute("ALTER TABLE djikstra ADD COLUMN geometry GEOMETRY;")
    
    # Change geometry so it can be read by DuckDB
    duckdb.execute("UPDATE djikstra SET geometry = public.ST_GeomFromGeoJSON(geojson);")
    
    # Remove geojson column
    duckdb.execute("ALTER TABLE djikstra DROP geojson;")
    
    rel = duckdb.sql("SELECT * FROM djikstra;")
    rel.show()

    duckdb.execute(f"""COPY djikstra TO '{saveGeoJSONPath}'
                   WITH (FORMAT GDAL, DRIVER 'GeoJSON');""")
    
    print(f"File has been saved to {saveGeoJSONPath}")


def createPgRoutingTables(bboxCSV:str,
                          areaNameBoundingBox:str,
                          extractedRoadTable:str,
                          extractedConnectorTable:str,
                          connection:psycopg2.extensions.connection,
                          schema:str = 'public',
                          dropTablesIfExist:bool = True,
                          boundingBoxTable:str = 'bounding_box',
                          roadsConnectorsTable:str = 'roads_connectors',
                          connectorsRoadCountTable:str = 'connectors_road_count',
                          edgeTable:str = 'edge',
                          joinEdgeTable:str = 'join_edge_str_to_int',
                          joinConnectorTable:str = 'join_connector_str_to_int',
                          edgeWithCostTable:str = 'edge_with_cost',
                          nodeTable:str = 'node',
                          start:float = None):
    """Create all the tables from a provided bbox.
    The road and connector data must have already been registered into the database.
    The name of the the extracted tables must be user inputs.
    Other tables names are not mandatory.

    DuckDb must be initialised with PostgreSQL first.

    Args:
        bboxCSV (str): bbox to extract data in it. Must be in the format 'E, S, W, N'.
        areaNameBoundingBox (str): Name of the bounding box area.
        extractedRoadTable (str): Name of the extracted road table.
        extractedConnectorTable (str): Name of the extracted connector table.
        connection (psycopg2.extensions.connection): Database connection token.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        dropTablesIfExist (bool, optional): Drop all tables if True. Defaults to True.
        boundingBoxTable (str, optional): Name of the bounding box table. Defaults to 'bounding_box'.
        roadsConnectorsTable (str, optional): Name of the roads connectors table. Defaults to 'roads_connectors'.
        connectorsRoadCountTable (str, optional): Name of the connectors road count table. Defaults to 'connectors_road_count'.
        edgeTable (str, optional): Name of the edge table. Defaults to 'edge'.
        joinEdgeTable (str, optional): Name of the join edge table. Defaults to 'join_edge_str_to_int'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostTable (str, optional): Name of the edge with cost table. Defaults to 'edge_with_cost'.
        nodeTable (str, optional): Name of the node table. Defaults to 'node'.
        start (float, optional): Start time of the process. If None, it is initialise with time.time(). Defaults to None,
    """
    if start is None or type(start) != float:
        start = time.time()
    # Tranform bbox to OGC WKT format and create bounding box table 
    wktGeom = utils.bboxCSVToBboxWKT(bboxCSV)

    # Insert bbox in it and get bbox id
    id = insertBoundingBox(connection = connection,
                           wktGeom = wktGeom,
                           aeraName = areaNameBoundingBox,
                           tableName = boundingBoxTable)
    end = time.time()
    print(f"insertBoundingBox : {end - start} seconds")

    # Create roads connector table
    createRoadsConnectorsTable(extractedRoadTable = extractedRoadTable,
                               extractedConnectorTable = extractedConnectorTable,
                               connection = connection,
                               schema = schema,
                               roadsConnectorsTable = roadsConnectorsTable,
                               dropTableIfExists = dropTablesIfExist)
    end = time.time()
    print(f"createRoadsConnectorsTable : {end - start} seconds")

    # Create connectors road count table
    createConnectorsRoadCountTable(connection = connection,
                                   schema = schema,
                                   roadsConnectorsTable = roadsConnectorsTable,
                                   connectorsRoadCountTable = connectorsRoadCountTable,
                                   dropTableIfExists = dropTablesIfExist)
    end = time.time()
    print(f"createConnectorsRoadCountTable : {end - start} seconds")
    
    # Create edge table
    createEdgeTable(extractedRoadTable = extractedRoadTable ,
                    connection = connection,
                    schema = schema,
                    roadsConnectorsTable = roadsConnectorsTable,
                    connectorsRoadCountTable = connectorsRoadCountTable,
                    edgeTable = edgeTable,
                    dropTableIfExists = dropTablesIfExist)
    end = time.time()
    print(f"createEdgeTable : {end - start} seconds")

    # Create join edges and join connectors tables
    createJoinEdgeTable(connection = connection,
                        schema = schema,
                        edgeTable = edgeTable,
                        joinEdgeTable = joinEdgeTable,
                        dropTableIfExists = dropTablesIfExist)
    end = time.time()
    print(f"createJoinEdgeTable : {end - start} seconds")
    
    createJoinConnectorTable(extractedConnectorTable = extractedConnectorTable,
                             connection = connection,
                             schema = schema,
                             joinConnectorTable = joinConnectorTable,
                             dropTableIfExists = dropTablesIfExist)
    end = time.time()
    print(f"createJoinConnectorTable : {end - start} seconds")
    
    # Finally, create edges with cost and nodes tables
    createEdgeWithCostTable(connection = connection,
                            schema = schema,
                            edgeTable = edgeTable,
                            joinEdgeTable = joinEdgeTable,
                            joinConnectorTable = joinConnectorTable,
                            edgeWithCostTable = edgeWithCostTable,
                            dropTableIfExists = dropTablesIfExist)
    end = time.time()
    print(f"createEdgeWithCostTable : {end - start} seconds")
    
    createNodeTable(connection = connection,
                    schema = schema,
                    nodeTable = nodeTable,
                    connectorsRoadCountTable = connectorsRoadCountTable,
                    extractedConnectorTable = extractedConnectorTable,
                    joinConnectorTable = joinConnectorTable,
                    edgeWithCostTable = edgeWithCostTable,
                    dropTableIfExists = dropTablesIfExist)
    end = time.time()
    print(f"createnodeTable : {end - start} seconds")


if __name__ == "__main__":
    import time
    import json
    start = time.time()
    
    # Database and schema names
    database = "pgrouting"
    schema = "omf"
    createBboxTable = True
    
    # Get connection initialise DuckDB and postgreSQL
    connection = utils.getConnection(database)    
    utils.initialisePostgreSQL(connection)
    utils.initialiseDuckDB(database)
    
    if createBboxTable:
        # Create bbox table
        createBoundingboxTable(connection)
        end = time.time()
        print(f"createBoundingboxTable : {end - start} seconds")
        
    # # Add functions to postres
    addSplitLineFromPointsFunction(connection)
    end = time.time()
    print(f"addSplitLineFromPointsFunction : {end - start} seconds")
    
    addGetEdgeCostFunction(connection)
    end = time.time()
    print(f"addGetEdgeCostFunction : {end - start} seconds")
    
    
    # Load the 3 bbox that we will use from the json file
    pathJson = os.path.join(".", "Data", "Bbox", "bboxs.json")
    folderSave = os.path.join(".", "Data", ".temp")
    
    with open(pathJson, "r") as f:
        bboxJson = json.load(f)
    
    # Create tables for each bbox
    for elem in bboxJson["bboxs"]:
        # Get the element we need from the json
        bbox = elem["bbox"]
        areaBbox = elem["area"]
        area = elem["area"].lower()
        
        print(f"Start process {areaBbox}")
        # Check if the process has already been done
        if utils.isProcessAlreadyDone(connection, area, 'omf'):
            
            print(f"{areaBbox} has already been calculated yet")
            
            # If the bounding box table has been recreated, we insert a row in it
            if createBboxTable:
                # Tranform bbox to OGC WKT format and create bounding box table 
                wktGeom = utils.bboxCSVToBboxWKT(bbox)

                # Insert bbox in it and get bbox id
                id = insertBoundingBox(connection = connection,
                                    wktGeom = wktGeom,
                                    aeraName = areaBbox)
                end = time.time()
                print(f"insertBoundingBox : {end - start} seconds")
        else:
            
            print(f"{areaBbox} has not been calculated yet")
        
            # Create names of the other tables
            extractRoad = f"road_{area}"
            extractConnector = f"connector_{area}"
            
            roadsConnectorsTable = f'roads_connectors_{area}'
            connectorsRoadCountTable = f'connectors_road_count_{area}'
            edgeTable = f'edge_{area}'
            joinEdgeTable = f'join_edge_str_to_int_{area}'
            joinConnectorTable = f'join_connector_str_to_int_{area}'
            edgeWithCostTable = f'edge_with_cost_{area}'
            nodeTable = f'node_{area}'
            
            # Download and create connector and road tables from bbox
            createTablesFromBbox(bbox = bbox,
                                    savePathFolder = folderSave,
                                    area = area,
                                    roadTable = extractRoad,
                                    connectorTable = extractConnector,
                                    schema = schema,
                                    deleteDataWhenFinish = True)
            
            end = time.time()
            print(f"createTablesFromBbox : {end - start} seconds")
            
            # Create all tables for each
            createPgRoutingTables(bboxCSV = bbox,
                                    areaNameBoundingBox = areaBbox,
                                    extractedRoadTable = extractRoad,
                                    extractedConnectorTable = extractConnector,
                                    connection = connection,
                                    schema = schema,
                                    roadsConnectorsTable = roadsConnectorsTable,
                                    connectorsRoadCountTable = connectorsRoadCountTable,
                                    edgeTable = edgeTable,
                                    joinEdgeTable = joinEdgeTable,
                                    joinConnectorTable = joinConnectorTable,
                                    edgeWithCostTable = edgeWithCostTable,
                                    nodeTable = nodeTable,
                                    start = start)
            