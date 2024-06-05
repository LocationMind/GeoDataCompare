import osmnx as ox
from osmnx import convert as con
from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

log = print

def bboxCsvToTuple(bbox):
    """Tranform a bbox in a CSV format to a tuple.
    The bbox is in format west, south, east, north
    The tuple will be as (north, south, east, west)

    Args:
        bbox (str): bbox of an area, given in a CSV format

    Returns:
        (tuple(float, float, float, float)): bbox in the format (north, south, east, west)
    """
    (west, south, east, north) = bbox.split(',')
    return (float(north), float(south), float(east), float(west))

def getConnection(host,
                  user="postgres",
                  password="postgres",
                  port="5432",
                  database="osm-pgrouting"):
    """
    Get connection token to the database.
    Only the host is required, other parameters can be ommited.

    Parameters
    ----------
    host : str
       Ip address for the database connection.
    user : str, optional
        Username for the database connection. The default is "postgres".
    password : str, optional
        Password for the database connection. The default is "postgres".
    port : str, optional
        Port for the connection. The default is "5432".
    database : str, optional
        Database to connect to. The default is "panoramax".

    Returns
    -------
    connection : psycopg2.extensions.connection
        Database connection token.

    """
    connection = psycopg2.connect(host=host,
                                  user=user,
                                  password=password,
                                  port=port,
                                  database=database)
    return connection

def executeQueryWithTransaction(connection, query):
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
        linesNumber = cursor.rowcount
    except Exception as e:
        # If there is an error, the transaction is canceled
        connection.rollback()
        log("The following error occured :", e)
    finally:
        # The transaction is closed anyway
        cursor.close()

if __name__ == "__main__":
    import time
    start = time.time()
    
    ## Download data with OSMnx
    # Get network data for a specific bbox
    bbox = bboxCsvToTuple("139.74609375, 35.67514743608467, 139.833984375, 35.7465122599185")
    
    graph = ox.graph_from_bbox(bbox=bbox, retain_all=True)

    end = time.time()
    print(f"Create graph : {end - start} seconds")

    # Transform the graph to geodataframe for the edges and nodes
    node = con.graph_to_gdfs(graph, nodes=True, edges=False, node_geometry=True)
    edge = con.graph_to_gdfs(graph, nodes=False, edges=True, fill_edge_geometry=True)

    end = time.time()
    print(f"Load graph : {end - start} seconds")

    # Create an engine to save into postgresql
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/osm-pgrouting") 

    # Save nodes to postgresql
    node.to_postgis("node_bbox", engine, if_exists="replace", index=True)

    end = time.time()
    print(f"Save node to postgis : {end - start} seconds")

    # Save edges to postgresql
    edge.to_postgis("edge_bbox", engine, if_exists="replace", index=True)

    end = time.time()
    print(f"Save edge to postgis : {end - start} seconds")
    
    # Create a table to join parallel edges using psycopg2
    
    connection = getConnection("127.0.0.1")
    
    table_name = "edge_bbox_test"
    
    # SQL query to create the table with everything needed
    sql = f"""
    -- Drop table if exists
    DROP TABLE IF EXISTS {table_name} CASCADE;

    -- Create table with a self join
    CREATE TABLE IF NOT EXISTS {table_name} AS
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
        e1.geometry AS geom1,
        e1.access AS access1,
        e1.bridge AS bridge1,
        e1.tunnel AS tunnel1,
        e1.service AS service1,
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
        e2.geometry AS geom2,
        e2.access AS access2,
        e2.bridge AS bridge2,
        e2.tunnel AS tunnel2,
        e2.service AS service2,
        e2.width AS width2,
        e2.junction AS junction2
    FROM edge_bbox AS e1
    LEFT JOIN edge_bbox AS e2 ON e1.u = e2.v AND e1.v = e2.u
    WHERE e1.id != e2.id AND ST_Contains(ST_Buffer(ST_Transform(e1.geometry, 6691), 0.5), ST_Transform(e2.geometry, 6691))
    AND ST_Contains(ST_Buffer(ST_Transform(e2.geometry, 6691), 0.5), ST_Transform(e1.geometry, 6691))
    ORDER BY e1.id;

    -- Add cost and reverse cost columns
    ALTER TABLE {table_name} DROP COLUMN IF EXISTS cost;
    ALTER TABLE {table_name} DROP COLUMN IF EXISTS reverse_cost;

    ALTER TABLE {table_name} ADD COLUMN cost double precision;
    ALTER TABLE {table_name} ADD COLUMN reverse_cost double precision;

    -- Set cost to length of the road
    UPDATE {table_name}
    SET cost = ST_Length(geom1);

    -- Set reverse cost for parallel roads 
    UPDATE {table_name}
    SET reverse_cost = ST_Length(geom1)
    WHERE u1 = v2 AND v1 = u2
    AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
    AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691));
    
    CREATE INDEX {table_name}_geom1_idx
    ON public.{table_name} USING gist (geom1);
    
    CREATE INDEX {table_name}_geom2_idx
    ON public.{table_name} USING gist (geom2);
    
    CREATE INDEX {table_name}_id1_idx
    ON public.{table_name} USING btree (id1)"""
    
    # Execute the query
    executeQueryWithTransaction(connection, sql)
    
    end = time.time()
    print(f"Execute query took {end - start} seconds")

    # Select bidirectional roads
    sql_bi_roads = f"""
    SELECT * FROM {table_name}
    WHERE u1 = v2 AND v1 = u2
    AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
    AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691));"""

    bi = gpd.read_postgis(sql_bi_roads, engine, geom_col="geom1" )

    print(bi)

    print(bi.shape)

    end = time.time()
    print(f"Bidirectional roads took {end - start} seconds")

    # Select all the other roads
    sql_uni_road = f"""
    SELECT * FROM {table_name}
    WHERE id1 not in (
        SELECT id1 FROM {table_name}
        WHERE u1 = v2 AND v1 = u2
        AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
        AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691)));"""
    
    uni = gpd.read_postgis(sql_uni_road, engine, geom_col="geom1" )

    print(uni)

    print(uni.shape)

    end = time.time()
    print(f"Unidirectional roads took {end - start} seconds")
    
    ## For bidirectionnal roads, agregate them into one.
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

    print(listNot2Count)
    
    end = time.time()
    print(f"Remove not exactly 2 occurences took {end - start} seconds")

    # Create an empty geodataframe with the same columns than the existing
    bi_without_parallel = gpd.GeoDataFrame().reindex_like(bi)

    listIndex = []
    # Then, for each pair, we remove the second occurence to keep only one road per key
    for key in dict:
        index = dict[key][1]
        listIndex.append(index)

    # Take only the row with the index on the list
    bi_without_parallel = bi.loc[listIndex]

    print(bi_without_parallel)

    end = time.time()
    print(f"Removing parallel edges took {end - start} seconds")

    # We concatenate the two dataframes to recreate the whole road network
    edge_with_cost = pd.concat([bi_without_parallel, uni])

    print(edge_with_cost)

    end = time.time()
    print(f"Concat dataframes took {end - start} seconds")

    # Rename useful columns
    edge_with_cost = edge_with_cost.rename(
        columns= {"id1":"id",
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
                  "width1":"width",
                  "junction1":"junction"})
    
    # Keep only these columns
    edge_with_cost = edge_with_cost[[
        "id",
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
        "width",
        "junction"]]

    # Set the geometry to the geom column
    edge_with_cost = edge_with_cost.set_geometry("geom") 

    edge_with_cost.to_postgis("edge_bbox_with_cost", engine, if_exists="replace", index=True)
    
    sql_create_index = f"""
    CREATE INDEX {table_name}_with_cost_geom_idx
    ON public.{table_name}_with_cost USING gist (geom);
    """

    end = time.time()
    print(f"It took {end - start} seconds")

    # exec(open('c:/Users/Mathis.Rouillard/Documents/OSM_Overture_Works/Python/OSM_to_network.py').read())