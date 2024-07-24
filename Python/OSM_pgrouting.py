import osmnx as ox
from osmnx import convert as con
import geopandas as gpd
import pandas as pd
import sqlalchemy
import psycopg2
import utils

def downloadOSMData(bbox:str) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Download data using osmnx and return two geodataframes.
    Also simplify the graph but do not merge them via their osmid.
    Both edges and nodes have their geometry column rename to 'geom'.

    Args:
        bbox (str): Bbox in a CSV format

    Returns:
        tuple[geopandas.GeoDataFrame, geopandas.GeoDataFrame]: First element is the nodea.
        Second element is the edges
    """
    # Get network data for a specific bbox
    bboxTuple = utils.bboxCSVToTuple(bbox)
    graph = ox.graph_from_bbox(bbox=bboxTuple, simplify=False, retain_all=True)
    
    # Simplify the graph by using the simplify_graph function but without aggregating edges
    graph = ox.simplify_graph(graph, edge_attrs_differ=['osmid'])

    # Transform the graph to geodataframe for the edges and nodes
    node = con.graph_to_gdfs(graph, nodes=True, edges=False, node_geometry=True)
    edge = con.graph_to_gdfs(graph, nodes=False, edges=True, fill_edge_geometry=True)
    
    # Rename geometry column to geom
    node = node.rename(columns={'geometry':'geom'})
    node = node.set_geometry("geom")
    
    edge = edge.rename(columns={'geometry':'geom'})
    edge = edge.set_geometry("geom")
    return node, edge


def addMissingColumns(connection:psycopg2.extensions.connection,
                      edgeTable:str,
                      schema:str = 'public'):
    """Add missing columns to the edge table.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        edgeTable (str): Name of the edge table.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """    
    # Add missing columns if not exists
    sqlMissingColumns = f"""
    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS osmid text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS oneway boolean;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS lanes text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS highway text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS reversed text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS length double precision;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS ref text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS maxspeed text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS maxspeed text; 

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS name text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS service text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS access text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS tunnel text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS bridge text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS footway text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS abutters text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS width text;

    ALTER TABLE {schema}.{edgeTable} ADD COLUMN IF NOT EXISTS junction text;"""

    # Execute the query
    utils.executeQueryWithTransaction(connection, sqlMissingColumns)


def createTableToAggregateEdges(connection:psycopg2.extensions.connection, 
                                edgeTable:str,
                                area:str,
                                schema:str = 'public'):
    """Create a table to join parallel edges.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        edgeTable (str): Name of the edge table.
        area (str): Name of the area.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    sql = f"""
    -- Add id column to edge table
    ALTER TABLE {schema}.{edgeTable} ADD COLUMN id serial;
    
    -- Drop table if exists
    DROP TABLE IF EXISTS {schema}.{area} CASCADE;
    
    -- Create table with a self join
    CREATE TABLE IF NOT EXISTS {schema}.{area} AS
    SELECT
        e1.id AS id1,
        e1.u AS u1,
        e1.v AS v1,
        e1.key AS key1,
        e2.id AS id2,
        e2.u AS u2,
        e2.v AS v2,
        e2.key AS key2,
        e1.osmid AS osmid1,
        e1.oneway AS oneway1,
        e1.ref AS ref1,
        e1.name AS name1,
        e1.highway AS highway1,
        e1.reversed AS reversed1,
        e1.length AS length1,
        e1.lanes AS lanes1,
        e1.maxspeed AS maxspeed1,
        e1.geom AS geom1,
        e1.access AS access1,
        e1.bridge AS bridge1,
        e1.tunnel AS tunnel1,
        e1.service AS service1,
        e1.footway AS footway1,
        e1.abutters AS abutters1,
        e1.width AS width1,
        e1.junction AS junction1,
        e2.osmid AS osmid2,
        e2.oneway AS oneway2,
        e2.ref AS ref2,
        e2.name AS name2,
        e2.highway AS highway2,
        e2.reversed AS reversed2,
        e2.length AS length2,
        e2.lanes AS lanes2,
        e2.maxspeed AS maxspeed2,
        e2.geom AS geom2,
        e2.access AS access2,
        e2.bridge AS bridge2,
        e2.tunnel AS tunnel2,
        e2.service AS service2,
        e2.footway AS footway2,
        e2.abutters AS abutters2,
        e2.width AS width2,
        e2.junction AS junction2
    FROM {schema}.{edgeTable} AS e1
    LEFT JOIN {schema}.{edgeTable} AS e2 ON e1.u = e2.v AND e1.v = e2.u
    AND e1.id != e2.id AND e1.highway = e2.highway
    AND ST_Contains(ST_Buffer(ST_Transform(e1.geom, 6691), 0.5), ST_Transform(e2.geom, 6691))
    AND ST_Contains(ST_Buffer(ST_Transform(e2.geom, 6691), 0.5), ST_Transform(e1.geom, 6691))
    ORDER BY e1.id;
    
    -- Add cost and reverse cost columns
    ALTER TABLE {schema}.{area} DROP COLUMN IF EXISTS cost;
    ALTER TABLE {schema}.{area} DROP COLUMN IF EXISTS reverse_cost;

    ALTER TABLE {schema}.{area} ADD COLUMN cost double precision DEFAULT -1;
    ALTER TABLE {schema}.{area} ADD COLUMN reverse_cost double precision DEFAULT -1;

    -- Set cost to length of the road
    UPDATE {schema}.{area} 
    SET cost = ST_Length(geom1::geography);

    -- Set reverse cost for parallel roads 
    UPDATE {schema}.{area}
    SET reverse_cost = ST_Length(geom1::geography)
    WHERE u1 = v2 AND v1 = u2 AND highway1 = highway2 AND id1 != id2
    AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
    AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691));
    
    CREATE INDEX {area}_geom1_idx
    ON {schema}.{area} USING gist (geom1);
    
    CREATE INDEX {area}_geom2_idx
    ON {schema}.{area} USING gist (geom2);
    
    CREATE INDEX {area}_id1_idx
    ON {schema}.{area} USING btree (id1);"""
    
    # Execute the query
    utils.executeQueryWithTransaction(connection, sql)


def getBidirectionalRoads(engine:sqlalchemy.engine.base.Engine,
                           area:str,
                           schema:str = 'public',
                           geomColumn:str = 'geom1') -> gpd.GeoDataFrame:
    """Get only bidirectional roads from the parallel edge table.

    Args:
        engine (sqlalchemy.engine.base.Engine): Engine with the database connection.
        area (str): Name of the area.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        geomColumn (str, optional): Name of the geomColumn to use. Defaults to 'geom1'.
    
    Return:
        geopandas.GeoDataFrame: Geodataframe of bidirectional roads.
    """
    # Select bidirectional roads
    sql_bi_roads = f"""
    SELECT * FROM {schema}.{area}
    WHERE u1 = v2 AND v1 = u2 AND highway1 = highway2
    AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
    AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691));"""

    bi = gpd.read_postgis(sql_bi_roads, engine, geom_col=geomColumn)
    
    return bi


def getUnidirectionalRoads(engine:sqlalchemy.engine.base.Engine,
                            area:str,
                            schema:str = 'public',
                            geomColumn:str = 'geom1') -> gpd.GeoDataFrame:
    """Get only unidirectional roads from the parallel edge table.

    Args:
        engine (sqlalchemy.engine.base.Engine): Engine with the database connection.
        area (str): Name of the area.
        schema (str, optional): Name of the schema. Defaults to 'public'.
        geomColumn (str, optional): Name of the geomColumn to use. Defaults to 'geom1'.
    
    Return:
        geopandas.GeoDataFrame: Geodataframe of unidirectional roads.
    """
    # Select all the other roads
    sql_uni_road = f"""
    SELECT * FROM {schema}.{area}
    WHERE id1 not in (
        SELECT id1 FROM {schema}.{area}
        WHERE u1 = v2 AND v1 = u2 AND highway1 = highway2
        AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
        AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691)));"""
    
    uni = gpd.read_postgis(sql_uni_road, engine, geom_col=geomColumn)
    
    return uni


def aggregateBiRoads(bi:gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Aggregate bidirectional roads to keep only one occurence of each.

    Args:
        bi (gpd.GeoDataFrame): Bidirectional roads with parallel.

    Returns:
        gpd.GeoDataFrame: Bidirectional roads without parallel.
    """
    # Dictionnary for mapping id1 and id2
    dict = {}

    # To do so, we first have to parse each row and check what are the rows corresponding to each couple (id1, id2)
    for index, row in bi.iterrows():
        id1, id2 = row["id1"], row["id2"]
        # If this couple is not inside the dictionnary, we add it with a count of one
        if (id1, id2) not in dict:
            # Check if (id2, id1) is in it
            if (id2, id1) not in dict:
                dict[(id1, id2)] = [index]
            # Else, we add one to this tuple
            else:
                dict[(id2, id1)].append(index)
        else:
            dict[(id1, id2)].append(index)

    end = time.time()
    print(f"Dictionnary creation took {end - start} seconds")

    # When we have all the pair in the dictionnary, we verify that we only have two value per key
    listNot2Count = []
    for key in dict:
        if len(dict[key]) != 2:
            # If there are not exactly two occurences of the pair, we remove it but keep a track of it
            listNot2Count.append(dict.pop(key))
    
    # If there are elements, we print them
    for elem in listNot2Count:
        print(f"These ids do not have exactly 2 occurences : {elem}")

    # Create an empty geodataframe with the same columns than the existing
    bi_without_parallel = gpd.GeoDataFrame().reindex_like(bi)

    listIndex = []
    # Then, for each pair, we remove the second occurence to keep only one road per key
    for key in dict:
        index = dict[key][1]
        listIndex.append(index)

    # Take only the row with the index on the list
    bi_without_parallel = bi.loc[listIndex]
    
    return bi_without_parallel


def createGeomIndex(connection:psycopg2.extensions.connection,
                    area:str,
                    schema:str = "public"):
    """Create geometry index on the edge with cost table.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        area (str): Name of the area.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Create a geon index on the table
    sql_create_index = f"""
    CREATE INDEX edge_with_cost_{area}_geom_idx
    ON {schema}.edge_with_cost_{area} USING gist (geom);
    """
    
    utils.executeQueryWithTransaction(connection, sql_create_index)


def createMappedClasses(connection:psycopg2.extensions.connection,
                        area:str,
                        schema:str = "public"):
    """Create the mapped class as a new attribute class.
    The mapping is made from OSM classes to OMF classes.

    Args:
        connection (psycopg2.extensions.connection): Database connection token.
        area (str): Name of the area.
        schema (str, optional): Name of the schema. Defaults to 'public'.
    """
    # Create class column
    sql_create_class_column = f"""
    ALTER TABLE IF EXISTS {schema}.edge_with_cost_{area}
    ADD COLUMN class character varying;
    """
    
    utils.executeQueryWithTransaction(connection, sql_create_class_column)
    
    # Update the table
    sql_class_omf = f"""
    UPDATE {schema}.edge_with_cost_{area}
    SET "class" =
    CASE
        WHEN highway = 'motorway' OR highway = 'motorway_link' THEN 'motorway'
        WHEN highway = 'trunk' OR highway = 'trunk_link' THEN 'trunk'
        WHEN highway = 'primary' OR highway = 'primary_link' THEN 'primary'
        WHEN highway = 'secondary' OR highway = 'secondary_link' THEN 'secondary'
        WHEN highway = 'tertiary' OR highway = 'tertiary_link' THEN 'tertiary'
        WHEN highway = 'residential' OR (highway = 'unclassified' AND abutters = 'residential') THEN 'residential'
        WHEN highway = 'living_street' THEN 'living_street'
        WHEN highway = 'service' AND service = 'parking_aisle' THEN 'parking_aisle'
        WHEN highway = 'service' AND service = 'driveway' THEN 'driveway'
        WHEN highway = 'service' AND service = 'alley' THEN 'alley'
        WHEN highway = 'pedestrian' THEN 'pedestrian'
        WHEN (highway = 'footway' OR highway = 'path') AND footway = 'sidewalk' THEN 'sidewalk'
        WHEN (highway = 'footway' OR highway = 'path') AND footway = 'crosswalk' THEN 'crosswalk'
        WHEN highway = 'footway' THEN 'footway'
        WHEN highway = 'path' THEN 'path'
        WHEN highway = 'steps' THEN 'steps'
        WHEN highway = 'track' THEN 'track'
        WHEN highway = 'cycleway' THEN 'cycleway'
        WHEN highway = 'bridleway' THEN 'bridleway'
        WHEN highway = 'unclassified' THEN 'unclassified'
        ELSE 'unknown'
    END
    """
    
    utils.executeQueryWithTransaction(connection, sql_class_omf)


if __name__ == "__main__":
    import json
    import os
    import time
    start = time.time()
    
    # Create connections to the database
    database = "pgrouting"
    schema = 'osm'
    
    engine = utils.getEngine(database)
    connection = utils.getConnection(database)
    
    ## OSMnx settings
    # Add footway and abutters tags to ways
    ox.settings.useful_tags_way += ["footway"]
    ox.settings.useful_tags_way += ["abutters"]
    
    # Download data until the 8th April only, up to date data from OMF 2024-06-13-beta.0 release
    ox.settings.overpass_settings = '[out:json][timeout:{timeout}]{maxsize}[date:"2024-06-07T00:00:00Z"]'
    
    # Load the 3 bbox that we will use from the json file
    path_json = os.path.join(".", "Data", "Bbox", "bboxs.json")
    with open(path_json, "r") as f:
        bboxJson = json.load(f)
    
    # Create tables for each bbox
    for elem in bboxJson["bboxs"]:
        
        # Get and create the element we need from the json
        bbox = elem["bbox"]
        area = elem["area"].lower()
        
        # Check if the area is already done
        if not utils.isProcessAlreadyDone(connection, area, schema):
        
            edgeTable = f"edge_{area}"
            nodeTable = f"node_{area}"
            
            end = time.time()
            print(f"Start download {area} :  {end - start} seconds")
    
            ## Download data with OSMnx
            # Get network data for a specific bbox
            node, edge = downloadOSMData(bbox)
            
            end = time.time()
            print(f"Load graph : {end - start} seconds")

            # Save nodes to postgresql by renaming the osmid column
            node.to_postgis(nodeTable, engine, if_exists="replace", schema=schema, index=True, index_label="id")

            end = time.time()
            print(f"Save node to postgis : {end - start} seconds")

            # Save edges to postgresql
            edge.to_postgis(edgeTable, engine, if_exists="replace", schema=schema, index=True)

            end = time.time()
            print(f"Save edge to postgis : {end - start} seconds")
            
            # Add missing columns if needed to the edge table
            addMissingColumns(connection, edgeTable, schema=schema)
            
            end = time.time()
            print(f"Add missing columns took {end - start} seconds")
            
            # Create table to aggregate parallel edges
            createTableToAggregateEdges(connection, edgeTable, area, schema)
            
            end = time.time()
            print(f"Execute query took {end - start} seconds")
            
            # Get bidirectional and unidirectional roads
            bi = getBidirectionalRoads(engine, area, schema)
            
            end = time.time()
            print(f"Bidirectional roads took {end - start} seconds")
            
            uni = getUnidirectionalRoads(engine, area, schema)

            end = time.time()
            print(f"Unidirectional roads took {end - start} seconds")
            
            # Agregate bidirectional roads into one
            bi_without_parallel = aggregateBiRoads(bi)

            end = time.time()
            print(f"Removing parallel edges took {end - start} seconds")

            # We concatenate the two dataframes to recreate the whole road network
            edge_with_cost = pd.concat([bi_without_parallel, uni])

            end = time.time()
            print(f"Concat dataframes took {end - start} seconds")

            # Rename useful columns
            edge_with_cost = edge_with_cost.rename(
                columns= {"id1":"original_id",
                        "u1":"source",
                        "v1":"target",
                        "geom1":"geom",
                        "osmid1":"osmid",
                        "oneway1":"oneway",
                        "ref1":"ref",
                        "name1":"name",
                        "highway1":"highway",
                        "lanes1":"lanes",
                        "maxspeed1":"maxspeed",
                        "access1":"access",
                        "bridge1":"bridge",
                        "tunnel1":"tunnel",
                        "service1":"service",
                        "footway1":"footway",
                        "abutters1":"abutters",
                        "width1":"width",
                        "junction1":"junction"})
            
            # Keep only these columns
            edge_with_cost = edge_with_cost[[
                "original_id",
                "source",
                "target",
                "cost",
                "reverse_cost",
                "geom",
                "osmid",
                "oneway",
                "ref",
                "name",
                "highway",
                "lanes",
                "maxspeed",
                "access",
                "bridge",
                "tunnel",
                "service",
                "footway",
                "abutters",
                "width",
                "junction"]]

            # Set the geometry to the geom column
            edge_with_cost = edge_with_cost.set_geometry("geom")
            
            # Load dataframe into postgis table
            edge_with_cost.to_postgis(f"edge_with_cost_{area}", engine, if_exists="replace", index=True, index_label = 'id', schema = schema)
            
            end = time.time()
            print(f"Edge with cost to postgis took {end - start} seconds")
            
            # Create geom index
            createGeomIndex(connection, area, schema)
            
            end = time.time()
            print(f"Geom index with cost to postgis took {end - start} seconds")
            
            # Create mapped classes
            createMappedClasses(connection, area, schema)
            
            end = time.time()
            print(f"Create mapped classes took {end - start} seconds")
            
            end = time.time()
            print(f"Download {area} took {end - start} seconds")
            
        else:
            print(f"{area} has already been downloaded")