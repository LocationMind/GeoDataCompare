import duckdb
import os
import data_integration as di

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


def createBoundingboxTable(tableName:str = 'bounding_box', dropTableIfExists:bool = True):
    """Create the bounding box table.

    Args:
        tableName (str, optional): Name of the table to create. Defaults to 'bounding_box'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{tableName} CASCADE;")
    
    # Create bounding_box structure
    duckdb.execute(
        """
        CALL postgres_execute(
            'dbpostgresql',
            'CREATE TABLE IF NOT EXISTS public.bounding_box
            (
                id serial NOT NULL,
                geom geometry,
                wkt_geom character varying COLLATE pg_catalog."default",
                name character varying COLLATE pg_catalog."default",
                CONSTRAINT bounding_box_pkey PRIMARY KEY (id)
            );')""")
    
    # Index creation
    duckdb.execute(
        f"""DROP INDEX IF EXISTS dbpostgresql.public.{tableName}_id_idx CASCADE;
        
        CREATE INDEX IF NOT EXISTS {tableName}_id_idx ON dbpostgresql.public.{tableName} (id);""")

    # Geometry index creation
    duckdb.execute(
        f"""DROP INDEX IF EXISTS dbpostgresql.public.{tableName}_geom_idx CASCADE;
        
        CREATE INDEX IF NOT EXISTS {tableName}_geom_idx ON dbpostgresql.public.{tableName} USING GIST (geom);""")


def insertBoundingBox(wktGeom:str, aeraName:str, tableName:str = 'bounding_box') -> int:
    """Insert a bounding box inside the table.
    The geometry is provided in the WKT format.

    Args:
        wktGeom (str): Geometry in OGC WKT format.
        aeraName (str): Name of the area.
    
    Return:
        int: Id of the inserted row
    """
    # Insert value and return id
    duckdb.execute(
        f"""
        CALL postgres_execute(
            'dbpostgresql',
            'INSERT INTO public.{tableName} (geom, wkt_geom, name)
            VALUES (ST_GeomFromText(''{wktGeom}'', 4326), ''{wktGeom}'', ''{aeraName}'');')""")
    
    # Select the entity with the greatest id among those that corresponds exactly to the one added before
    rel = duckdb.execute(
        f"""
        SELECT id
        FROM dbpostgresql.public.{tableName}
        WHERE wkt_geom = '{wktGeom}'
        AND name = '{aeraName}'
        ORDER BY id DESC
        LIMIT 1""")
    
    # Get id of the inserted row
    id = rel.fetchone()[0]
    print(id)
    return id


def extractRoads(extractedRoadTable:str,
                 boundingBoxId:int,
                 roadTable:str = 'road',
                 boundingBoxTable:str = 'bounding_box',
                 dropTableIfExists:bool = True
                 ):
    """Extract roads from the bbox. The road table must have been created
    by functions in data_integration script.

    Args:
        extractedRoadTable (str): Name of the extracted road table.
        boundingBoxId (int): Id of the bounding box.
        roadTable (str, optional): Name of the initial road table. Defaults to 'road'.
        boundingBoxTable (str, optional): Name of the bounding box table. Defaults to 'bounding_box'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{extractedRoadTable} CASCADE;")
    
    # Extract roads from the bounding box
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'CREATE TABLE public.{extractedRoadTable} AS
        SELECT
            r.id,
            r.geom,
            r.version,
            r.update_time,
            r.sources,
            r.primary_name,
            r.class,
            r.connector_ids,
            r.surface,
            r.width,
            r.lanes,
            r.restrictions
        FROM public.{roadTable} r
            JOIN public.{boundingBoxTable} AS box ON ST_Intersects(r.geom, box.geom)
        WHERE box.id = {boundingBoxId};')
        """)
    
    # Create index if exists
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'DROP INDEX IF EXISTS public.{extractedRoadTable}_geom_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {extractedRoadTable}_geom_idx
        ON public.{extractedRoadTable} USING gist (geom);

        DROP INDEX IF EXISTS public.{extractedRoadTable}_id_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {extractedRoadTable}_id_idx
        ON public.{extractedRoadTable} USING btree
        (id ASC NULLS LAST)
        TABLESPACE pg_default;')""")
    

def extractConnectors(extractedConnectorTable:str,
                      extractRoadTable:str,
                      connectorTable:str = 'connector',
                      dropTableIfExists:bool = True):
    """Extract connectors that intersects the extracted roads.
    Connectors might be outside of the bbox if extracted roads are outside the bbox too.

    Args:
        extractedConnectorTable (str): Name of the extracted connector table.
        extractedRoadTable (str): Name of the extracted road table.
        connetorTable (str, optional): Name of the initial connector table. Defaults to 'connector'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{extractedConnectorTable} CASCADE;")

    # Extract connectors from the bounding box
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'CREATE TABLE public.{extractedConnectorTable} AS
        SELECT
            c.id,
            c.geom,
            c.version,
            c.update_time,
            c.sources
        FROM public.{connectorTable} AS c
        JOIN public.{extractRoadTable} AS r ON ST_Intersects(c.geom, r.geom);')""")
    
    # Create index if exists
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'DROP INDEX IF EXISTS public.{extractedConnectorTable}_geom_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {extractedConnectorTable}_geom_idx
        ON public.{extractedConnectorTable} USING gist (geom);

        DROP INDEX IF EXISTS public.{extractedConnectorTable}_id_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {extractedConnectorTable}_id_idx
        ON public.{extractedConnectorTable} USING btree
        (id ASC NULLS LAST)
        TABLESPACE pg_default;')""")


def createRoadsConnectorsTable(extractedRoadTable:str,
                               initialConnectorTable:str,
                               roadsConnectorsTable:str = 'roads_connectors',
                               dropTableIfExists:bool = True):
    """Create the roads_connectors table from the extracted data.
    To avoid errors, the initial connector table (not extracted) is used.

    Args:
        extractedRoadTable (str): Name of the extracted road table.
        initialConnectorTable (str): Name of the initial connector table.
        roadsConnectorsTable (str, optional): Name of the table to create. Defaults to 'roads_connectors'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{roadsConnectorsTable} CASCADE;")
    
    # Create roads_connectors table
    duckdb.execute(
        f"""CALL postgres_execute(
        'dbpostgresql',
        'CREATE TABLE public.{roadsConnectorsTable} AS
        SELECT
            r.id AS road_id,
            cons.con_id AS connector_id,
            json_array_length(r.connector_ids) AS max_i,
            cons.i::integer AS i,
            r.class,
            c.geom AS geom,
            r.connector_ids,
            r.version,
            r.update_time,
            r.sources,
            r.primary_name,
            r.surface,
            r.width,
            r.lanes,
            r.restrictions
        FROM
            public.{extractedRoadTable} AS r, json_array_elements_text(r.connector_ids) WITH ORDINALITY cons(con_id, i)
        LEFT JOIN
            public.{initialConnectorTable} AS c ON cons.con_id = c.id
        WHERE r.class IS NOT null;')""")

    # Indexes creation
    duckdb.execute(f"""DROP INDEX IF EXISTS dbpostgresql.public.{roadsConnectorsTable}_connector_road_idx CASCADE;""")
    
    duckdb.execute(f"""CALL postgres_execute(
        'dbpostgresql',
        'CREATE INDEX IF NOT EXISTS {roadsConnectorsTable}_connector_road_idx
            ON public.{roadsConnectorsTable} USING btree
            (connector_id ASC NULLS LAST)
            INCLUDE(road_id);')""")
    
    duckdb.execute(f"""DROP INDEX IF EXISTS dbpostgresql.public.{roadsConnectorsTable}_road_i_idx CASCADE;""")   
    
    duckdb.execute(f"""CALL postgres_execute(
        'dbpostgresql',
        'CREATE INDEX IF NOT EXISTS {roadsConnectorsTable}_road_i_idx
            ON public.{roadsConnectorsTable} USING btree
            (road_id ASC NULLS LAST, i ASC NULLS LAST);')""")


def createConnectorsRoadCountTable(roadsConnectorsTable:str = 'roads_connectors',
                                   connectorsRoadCountTable:str = 'connectors_road_count',
                                   dropTableIfExists:bool = True):
    """Create the connectors_road_count table from the extracted data.

    Args:
        roadsConnectorsTable (str): Name of the roads connectors table. Defaults to 'roads_connectors'.
        connectorsRoadCountTable (str, optional): Name of the table to create. Defaults to 'connectors_road_count'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{connectorsRoadCountTable} CASCADE;")
    
    # Create table
    duckdb.execute(
        f"""
        CREATE TABLE dbpostgresql.public.{connectorsRoadCountTable} AS
        SELECT connector_id, array_agg(road_id) AS roads, count(*) AS cnt
        FROM dbpostgresql.public.{roadsConnectorsTable}
        GROUP BY connector_id;""")
    
    # Add primary key
    duckdb.execute(f"""CALL postgres_execute(
        'dbpostgresql',
        'ALTER TABLE public.{connectorsRoadCountTable} ADD PRIMARY KEY (connector_id);')""")


def addSplitLineFromPointsFunction():
    """Add a custom function name "ST_SplitLineFromPoints" to postgresql.
    """
    # Create and add the function
    duckdb.execute(
        """CALL postgres_execute(
        'dbpostgresql',
        'CREATE OR REPLACE FUNCTION public.ST_SplitLineFromPoints(
            line geometry,
            point_a geometry,
            point_b geometry
            )
            RETURNS geometry AS
            $BODY$
            WITH
                split AS (SELECT (ST_Split(
                    line,
                    ST_Multi( ST_Union( point_a, point_b)))
                                ) geom)
                SELECT (g.gdump).geom as geom FROM (
                SELECT ST_Dump(
                    geom
                ) AS gdump from split) as g
                WHERE ST_Intersects((g.gdump).geom, point_a) AND ST_Intersects((g.gdump).geom, point_b)
            $BODY$
            LANGUAGE SQL;

        ALTER FUNCTION public.ST_SplitLineFromPoints(geometry, geometry, geometry)
                   OWNER TO postgres;
        
        COMMENT ON FUNCTION public.ST_SplitLineFromPoints(geometry, geometry, geometry)
                   IS ''args: line, point_a, point_b - Returns a collection of geometries created by splitting a line by two points. It only returns the line that intersects the two points.'';')""")


def createEdgeTable(extractedRoadTable:str,
                    roadsConnectorsTable:str = 'roads_connectors',
                    connectorsRoadCountTable:str = 'connectors_road_count',
                    edgeTable:str = 'edge',
                    dropTableIfExists:bool = True):
    """Create the edge table from the extracted roads and tables constructed before.
    The cost are not yet saved into this table.

    Args:
        extractedRoadTable (str): Name of the extracted road table.
        roadsConnectorsTable (str, optional): Name of the roads connector table. Defaults to 'roads_connectors'.
        connectorsRoadCountTable (str, optional): Name of the connectors road count table. Defaults to 'connectors_road_count'.
        edgeTable (str, optional): Name of the edge table to create. Defaults to 'edge'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """    
    

    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{edgeTable} CASCADE;")

    # Create edge table
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'CREATE TABLE public.{edgeTable} AS
        SELECT
            road_id AS original_id,
            CASE
                WHEN n = 1 AND "end" = max_i THEN road_id
                ELSE road_id || ''-'' || CAST(n AS character varying)
            END AS "id",
            "source",
            target,
            -- GEOMETRY CREATION
            ST_AsText(ST_SplitLineFromPoints(r.geom, t.first_geom, t.second_geom)) AS wkt,
            ST_SplitLineFromPoints(r.geom, t.first_geom, t.second_geom) AS geom,
            ST_Length(ST_SplitLineFromPoints(r.geom, t.first_geom, t.second_geom)::geography) AS len,
            t."class",
            t."version",
            t.update_time,
            t.sources,
            t.primary_name,
            t.surface,
            t.width,
            t.lanes,
            t.restrictions
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
                "class",
                "version",
                update_time,
                sources,
                primary_name,
                surface,
                width,
                lanes,
                restrictions
            FROM public.{roadsConnectorsTable}
            LEFT JOIN public.{connectorsRoadCountTable} USING (connector_id)
            WINDOW cons AS (PARTITION BY road_id ORDER BY i ASC ROWS 1 PRECEDING)
            ORDER BY road_id ASC
        ) t
        LEFT JOIN public.{extractedRoadTable} as r ON road_id = id
        WHERE n>0;')""")
    
    # Add primary key
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'ALTER TABLE public.{edgeTable} ADD CONSTRAINT {edgeTable}_pkey PRIMARY KEY (id);')""")

    # Create index if not exists
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'DROP INDEX IF EXISTS public.{edgeTable}_geom_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {edgeTable}_geom_idx
        ON public.{edgeTable} USING gist (geom);

        DROP INDEX IF EXISTS public.{edgeTable}_original_id_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {edgeTable}_original_id_idx
        ON public.{edgeTable} USING btree
        (original_id ASC NULLS LAST)
        TABLESPACE pg_default;')""")


def createJoinEdgeTable(edgeTable:str = 'edge',
                        joinEdgeTable:str = 'join_edge_str_to_int',
                        dropTableIfExists:bool = True):
    """Create a join table for edges id (string) and integer id for pgr_djikstra algorithm.
    It also inserts the value from the edges.

    Args:
        edgeTable (str, optional): Name of the edge table. Defaults to 'edge'.
        joinEdgeTable (str, optional): Name of the join edge table. Defaults to 'join_edge_str_to_int'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{joinEdgeTable} CASCADE;")

    # Create the table and the indexes
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'CREATE TABLE IF NOT EXISTS public.{joinEdgeTable}
        (
            id bigserial PRIMARY KEY,
            edge_id character varying NOT NULL,
            CONSTRAINT {joinEdgeTable}_unique_edge_id UNIQUE (edge_id)
        );

        ALTER TABLE IF EXISTS public.{joinEdgeTable}
            OWNER to postgres;')""")
    
    print("Join edge created")
    
    # Create the indexes
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'DROP INDEX IF EXISTS public.{joinEdgeTable}_id_idx_edge_table CASCADE;

        CREATE INDEX IF NOT EXISTS {joinEdgeTable}_id_idx_edge_table
            ON public.{joinEdgeTable} USING btree
            (id ASC NULLS LAST);

        DROP INDEX IF EXISTS public.{joinEdgeTable}_edge_id_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {joinEdgeTable}_edge_id_idx
            ON public.{joinEdgeTable} USING btree
            (edge_id ASC NULLS LAST);')""")
    
    print("Index created")
    
    print("Start insert created")
    
    # Insert the values
    duckdb.execute(
        f"""
        INSERT INTO dbpostgresql.public.{joinEdgeTable}(edge_id)
        SELECT id FROM dbpostgresql.public.{edgeTable}
        ORDER BY id ASC;""")
    print("end insert created")


def createJoinConnectorTable(extractedConnectorTable:str,
                             joinConnectorTable:str = 'join_connector_str_to_int',
                             dropTableIfExists:bool = True):
    
    """Create a join table for connectors id (string) and integer id for pgr_djikstra algorithm.
    It does it only for the extracted connector table.

    Args:
        extractedConnectorTable (str): Name of the extracted connector table.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{joinConnectorTable} CASCADE;")

    # Create the table and the indexes
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'CREATE TABLE IF NOT EXISTS public.{joinConnectorTable}
        (
            id bigserial PRIMARY KEY,
            connector_id character varying NOT NULL,
            CONSTRAINT {joinConnectorTable}_unique_connector_id UNIQUE (connector_id)
        );

        ALTER TABLE IF EXISTS public.{joinConnectorTable}
            OWNER to postgres;')""")
    
    print("Join connector created")
    
    # Create the indexes
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'DROP INDEX IF EXISTS public.{joinConnectorTable}_id_idx_connector_table CASCADE;

        CREATE INDEX IF NOT EXISTS {joinConnectorTable}_id_idx_connector_table
            ON public.{joinConnectorTable} USING btree
            (id ASC NULLS LAST);
        
        DROP INDEX IF EXISTS public.{joinConnectorTable}_connector_id_idx CASCADE;

        CREATE INDEX IF NOT EXISTS {joinConnectorTable}_connector_id_idx
            ON public.{joinConnectorTable} USING btree
            (connector_id ASC NULLS LAST);')""")
    
    print("Index created")
    
    print("Start insert created")
    # Insert the values
    duckdb.execute(
        f"""
        INSERT INTO dbpostgresql.public.{joinConnectorTable} (connector_id)
        SELECT id FROM dbpostgresql.public.{extractedConnectorTable}
        ORDER BY id ASC;""")
    print("end insert created")


def createEdgeWithCostView(edgeTable:str = 'edge',
                           joinEdgeTable:str = 'join_edge_str_to_int',
                           joinConnectorTable:str = 'join_connector_str_to_int',
                           edgeWithCostView:str = 'edge_with_cost',
                           dropTableIfExists:bool = True):
    """Create a view for edges with associated cost and reversed cost.

    Args:
        edgeTable (str, optional): Name of the edge table. Defaults to 'edge'.
        joinEdgeTable (str, optional): Name of the join edge table. Defaults to 'join_edge_str_to_int'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostView (str, optional): Name of the edge view with cost to create. Defaults to 'edge_with_cost'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """    

    # Drop view if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP VIEW IF EXISTS dbpostgresql.public.{edgeWithCostView} CASCADE;")
    
    # Create the view
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'CREATE OR REPLACE VIEW public.{edgeWithCostView} AS
        SELECT
            j.id,
            s.id AS "source",
            t.id AS "target",
            CASE
                WHEN restrictions -> ''access'' -> 0 ->> ''access_type'' = ''denied''
                AND restrictions -> ''access'' -> 0 -> ''when'' ->> ''heading'' = ''forward''
                THEN ''-1''
                ELSE len
            END AS cost,
            CASE
                WHEN restrictions -> ''access'' -> 0 ->> ''access_type'' = ''denied''
                AND restrictions -> ''access'' -> 0 -> ''when'' ->> ''heading'' = ''backward''
                THEN ''-1''
                ELSE len
            END AS reverse_cost,
            class,
            e.geom
        FROM public.{edgeTable} AS e

        LEFT JOIN public.{joinConnectorTable} AS s ON source=s.connector_id
        LEFT JOIN public.{joinConnectorTable} AS t ON target=t.connector_id
        LEFT JOIN public.{joinEdgeTable} AS j ON e.id=j.edge_id;')""")


def createVerticeTable(verticeTable:str = 'vertice',
                       connectorsRoadCountTable:str = 'connectors_road_count',
                       connectorTable:str = 'connector',
                       joinConnectorTable:str = 'join_connector_str_to_int',
                       edgeWithCostView:str = 'edge_with_cost',
                       dropTableIfExists:bool = True):
    """_summary_

    Args:
        verticeTable (str, optional): Name of the vertice table to create. Defaults to 'vertice'.
        connectorsRoadCountTable (str, optional): Name of the connectors road count table. Defaults to 'connectors_road_count'.
        connectorTable (str, optional): Name of the initial connector table. Defaults to 'connector'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostView (str, optional): Name of the edge view with cost to create. Defaults to 'edge_with_cost'.
        dropTableIfExists (bool, optional): Drop table if True. Defaults to True.
    """    
    
    # Drop table if the user wants to
    if dropTableIfExists:
        duckdb.execute(f"DROP TABLE IF EXISTS dbpostgresql.public.{verticeTable} CASCADE;")
    
    # Create vertices table
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'CREATE TABLE public.{verticeTable} AS
        SELECT j.id AS id, in_edges, out_edges, c.geom
        FROM public.{connectorsRoadCountTable} AS cnt
        LEFT JOIN public.{connectorTable} c ON cnt.connector_id = c.id
        LEFT JOIN public.{joinConnectorTable} AS j ON j.connector_id = cnt.connector_id
        LEFT JOIN (
            SELECT target, array_agg(id) AS in_edges
            FROM public.{edgeWithCostView}
            WHERE target IS NOT NULL GROUP BY target) ei ON j.id = target
        LEFT JOIN (
            SELECT "source", array_agg(id) AS out_edges
            FROM public.{edgeWithCostView}
            WHERE "source" IS NOT NULL GROUP BY "source") eo ON j.id = "source";')""")
    
    # Add primary key
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'ALTER TABLE public.{verticeTable} ADD CONSTRAINT {verticeTable}_pkey PRIMARY KEY (id);')""")

    # Create geom index
    duckdb.execute(
        f"""
        CALL postgres_execute(
        'dbpostgresql',
        'DROP INDEX IF EXISTS public.{verticeTable}_geom_idx CASCADE;
        
        CREATE INDEX IF NOT EXISTS {verticeTable}_geom_idx ON public.{verticeTable} USING gist (geom);')""")


def initialisePgRouting():
    """Initialise pg routing. If the extension already exists, it skip the query
    """
    # Create PgRouting extension if not exists
    duckdb.execute(
        """
        CALL postgres_execute(
            'dbpostgresql',
            'CREATE EXTENSION IF NOT EXISTS pgrouting;')""")


def getClosestPointIntId(lat:float,
                         lon:float,
                         connectorTable:str = 'connector',
                         joinConnectorTable:str = 'join_connector_str_to_int') -> int:
    """Return the closest point id of the graph from the point in parameter.
    The coordinantes must be given in WGS84, SRID:4326

    Args:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        connectorTable (str, optional): Name of the initial connector table. Defaults to 'connector'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.

    Returns:
        int: Id of the closest point, compatible with pgr_djikstra algorithm.
    """
    # Select the closest point
    result = duckdb.sql(
        f"""
        SELECT * FROM postgres_query(
        'dbpostgresql',
        'SELECT j.id, ST_Transform(ST_GeomFromText(''POINT({lon} {lat})'', 4326), 6691)  <-> ST_Transform(c.geom, 6691) AS dist
        FROM public.{connectorTable} AS c
        JOIN public.{joinConnectorTable} AS j on j.connector_id = c.id
        ORDER by dist
        LIMIT 1;')""").fetchone()
    
    id = result[0]
    return id


def djikstra(startLat:float,
             startLon:float,
             endLat:float,
             endLon:float,
             saveGeoJSONPath:str,
             connectorTable:str = 'connector',
             joinConnectorTable:str = 'join_connector_str_to_int',
             edgeWithCostView:str = 'edge_with_cost'
             ):
    """Execute the pgr_djikstra algorithm and save the result into a GeoJSON file.
    The graph is always consider to be oriented.
    The points must be given in WGS84, SRID:4326

    Args:
        startLat (float): Latitude of the starting point.
        startLon (float): Longitude of the starting point.
        endLat (float): Latitude of the ending point.
        endLon (float): Longitude of the ending point.
        saveGeoJSONPath (str): Save path for the GeoJSON file.
        connectorTable (str, optional): Name of the initial connector table. Defaults to 'connector'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostView (str, optional): Name of the edge view with cost. Defaults to 'edge_with_cost'.
    """    

    # Get ids of start and end points
    startId = getClosestPointIntId(startLat, startLon, connectorTable, joinConnectorTable)
    endId = getClosestPointIntId(endLat, endLon, connectorTable, joinConnectorTable)

    # Run pgr_djikstra algorithm between those points
    rel = duckdb.sql(
        f"""
        SELECT * FROM postgres_query(
            'dbpostgresql',
            'SELECT seq, edge, dij."cost", ST_AsGeoJSON(geom) as geojson
            FROM pgr_dijkstra(
                ''SELECT id, source, target, cost, reverse_cost
                FROM public.{edgeWithCostView}''::text,
                {startId},
                {endId},
                directed := true) dij
            JOIN public.{edgeWithCostView} AS e ON edge = e.id;')""")
    
    rel.show()
    
    rel.to_table("djikstra")
    
    # Add a geometry column to djikstra table
    duckdb.execute("ALTER TABLE djikstra ADD COLUMN geometry GEOMETRY;")
    
    # Change geometry so it can be read by DuckDB
    duckdb.execute("UPDATE djikstra SET geometry = ST_GeomFromGeoJSON(geojson);")
    
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
                          dropTablesIfExist:bool = True,
                          boundingBoxTable:str = 'bounding_box',
                          roadTable:str = 'road',
                          connectorTable:str = 'connector',
                          roadsConnectorsTable:str = 'roads_connectors',
                          connectorsRoadCountTable:str = 'connectors_road_count',
                          edgeTable:str = 'edge',
                          joinEdgeTable:str = 'join_edge_str_to_int',
                          joinConnectorTable:str = 'join_connector_str_to_int',
                          edgeWithCostView:str = 'edge_with_cost',
                          verticeTable:str = 'vertice'):
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
        dropTablesIfExist (bool, optional): Drop all tables if True. Defaults to True.
        boundingBoxTable (str, optional): Name of the bounding box table. Defaults to 'bounding_box'.
        roadTable (str, optional): Name of the initial road table. Defaults to 'road'.
        connectorTable (str, optional): Name of the initial connector table. Defaults to 'connector'.
        roadsConnectorsTable (str, optional): Name of the roads connectors table. Defaults to 'roads_connectors'.
        connectorsRoadCountTable (str, optional): Name of the connectors road count table. Defaults to 'connectors_road_count'.
        edgeTable (str, optional): Name of the edge table. Defaults to 'edge'.
        joinEdgeTable (str, optional): Name of the join edge table. Defaults to 'join_edge_str_to_int'.
        joinConnectorTable (str, optional): Name of the join connector table. Defaults to 'join_connector_str_to_int'.
        edgeWithCostView (str, optional): Name of the edge view with cost. Defaults to 'edge_with_cost'.
        verticeTable (str, optional): Name of the vertice table. Defaults to 'vertice'.
    """
    start = time.time()
    # Tranform bbox to OGC WKT format and create bounding box table 
    wktGeom = bboxCSVTobboxWKT(bboxCSV)

    # Insert bbox in it and get bbox id
    id = insertBoundingBox(wktGeom, areaNameBoundingBox, boundingBoxTable)
    end = time.time()
    print(f"insertBoundingBox : {end - start} seconds")

    # Extract roads and connectors
    extractRoads(extractedRoadTable, id, roadTable, boundingBoxTable, dropTablesIfExist)
    end = time.time()
    print(f"extractRoads : {end - start} seconds")
    extractConnectors(extractedConnectorTable, extractedRoadTable, connectorTable, dropTablesIfExist)
    end = time.time()
    print(f"extractConnectors : {end - start} seconds")

    # Create roads connector table
    createRoadsConnectorsTable(extractedRoadTable, connectorTable, roadsConnectorsTable, dropTablesIfExist)
    end = time.time()
    print(f"createRoadsConnectorsTable : {end - start} seconds")

    # Create connectors road count table
    createConnectorsRoadCountTable(roadsConnectorsTable, connectorsRoadCountTable, dropTablesIfExist)
    end = time.time()
    print(f"createConnectorsRoadCountTable : {end - start} seconds")

    # Add a function to postres and create edge table
    addSplitLineFromPointsFunction()
    end = time.time()
    print(f"addSplitLineFromPointsFunction : {end - start} seconds")

    createEdgeTable(extractedRoadTable, roadsConnectorsTable, connectorsRoadCountTable,edgeTable, dropTablesIfExist)
    end = time.time()
    print(f"createEdgeTable : {end - start} seconds")

    # Create join edges and join connectors tables
    createJoinEdgeTable(edgeTable, joinEdgeTable, dropTablesIfExist)
    end = time.time()
    print(f"createJoinEdgeTable : {end - start} seconds")
    createJoinConnectorTable(connectorTable, joinConnectorTable, dropTablesIfExist)
    end = time.time()
    print(f"createJoinConnectorTable : {end - start} seconds")
    
    # Finally, create edges with cost view and vertice table
    createEdgeWithCostView(edgeTable, joinEdgeTable, joinConnectorTable, edgeWithCostView, dropTablesIfExist)
    end = time.time()
    print(f"createEdgeWithCostView : {end - start} seconds")
    createVerticeTable(verticeTable, connectorsRoadCountTable, connectorTable, joinConnectorTable, edgeWithCostView, dropTablesIfExist)
    end = time.time()
    print(f"createVerticeTable : {end - start} seconds")


if __name__ == "__main__":
    import time
    import json
    start = time.time()
    
    # Initialise duckdb
    di.initDuckDb('overturemap-pgrouting')
    
    # Create bbox table
    createBoundingboxTable()
    
    end = time.time()
    print(f"createBoundingboxTable : {end - start} seconds")
    
    # Load the 3 bbox that we will use from the json file
    path_json = os.path.join(".", "Data", "bboxs.json")
    with open(path_json, "r") as f:
        bboxJson = json.load(f)
    
    # Create tables for each bbox
    for elem in bboxJson["bboxs"]:
        # Get the element we need from the json
        bbox = elem["bbox"]
        area = elem["final_table"]
        extractRoad = elem["extractRoad"]
        extractConnector = elem["extractConnector"]
        
        # Create names of the other tables
        roadsConnectorsTable = f'roads_connectors_{area}'
        connectorsRoadCountTable = f'connectors_road_count_{area}'
        edgeTable = f'edge_{area}'
        joinEdgeTable = f'join_edge_str_to_int_{area}'
        joinConnectorTable = f'join_connector_str_to_int_{area}'
        edgeWithCostView = f'edge_with_cost_{area}'
        verticeTable = f'vertice_{area}'
        
        print(f"Start process {area}")
        
        # Create all tables for each
        createPgRoutingTables(bboxCSV = bbox,
                              areaNameBoundingBox = area,
                              extractedRoadTable = extractRoad, 
                              extractedConnectorTable = extractConnector,
                              roadsConnectorsTable = roadsConnectorsTable,
                              connectorsRoadCountTable = connectorsRoadCountTable,
                              edgeTable = edgeTable,
                              joinEdgeTable = joinEdgeTable,
                              joinConnectorTable = joinConnectorTable,
                              edgeWithCostView = edgeWithCostView,
                              verticeTable = verticeTable)
        
        # Djikstra algorithm
        # savePath = os.path.join(".", "Data", "Test", "result.geojson")
        # djikstra(35.699579, 139.696734, 35.701291, 139.700234, savePath)
        
        # end = time.time()
        # print(f"Djikstra : {end - start} seconds")