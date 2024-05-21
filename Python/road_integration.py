import duckdb
from duckdb.typing import *
import os
import time
import json

def extract_information(data, field) -> str:
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

start = time.time()

# Read data
path_data = os.path.join("..", "Data", "OvertureMap_Japan", "segment", "*.parquet")

# Create and load the spatial extension
duckdb.install_extension("spatial")
duckdb.load_extension("spatial")

# Create and load the postgres extension
duckdb.install_extension("postgres")
duckdb.load_extension("postgres")

# Add the function to duck_db
duckdb.create_function("extract_info", extract_information, [VARCHAR, VARCHAR], VARCHAR)

# Create environment variable for postgres connexion
dbname = 'overturemap'
host = '127.0.0.1'
user = 'postgres'
password = 'postgres'
duckdb.execute(f"ATTACH 'dbname={dbname} host={host} user={user} password={password}' AS overturemap (TYPE POSTGRES);")

# # Show data description
# rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data}';")
# rel.show()

# # Drop table
# duckdb.execute("DROP TABLE IF EXISTS overturemap.public.road CASCADE;")

# duckdb.execute(f"""CREATE TABLE overturemap.public.road AS (SELECT
#                id,
#                ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt,
#                version,
#                update_time,
#                JSON(sources) AS sources,
#                names.primary AS primary_name,
#                class,
#                JSON(connector_ids) AS connector_ids,
#                JSON(extract_info(road, 'surface')) AS surface,
#                JSON(extract_info(road, 'width')) AS width,
#                JSON(extract_info(road, 'lanes')) AS lanes,
#                JSON(extract_info(road, 'restrictions')) AS restrictions,
#                FROM '{path_data}');""")

end = time.time()

print(f"Table creation : {end - start} seconds")

duckdb.execute("CREATE INDEX road_id_idx ON overturemap.public.road (id);")

end = time.time()

print(f"Index : {end - start} seconds")

rel = duckdb.sql("SELECT count(*) FROM overturemap.public.road;")
rel.show()

end = time.time()

print(f"Select : {end - start} seconds")

# Add a geometry column and change the WKT geom to a geometry
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.road ADD COLUMN geom geometry;')")
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.road ADD COLUMN theme character varying;')")
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.road ADD COLUMN type character varying;')")

duckdb.execute("""CALL postgres_execute('overturemap', 'UPDATE public.road 
               SET geom = public.ST_GeomFromText(geom_wkt, 4326), theme = ''transportation'', type = ''road'';')""")

end = time.time()

print(f"Alter + Update : {end - start} seconds")

# Create a geom index
duckdb.execute("""CALL postgres_execute('overturemap', 'CREATE INDEX road_geom_idx
               ON public.road
               USING GIST (geom);')""")

end = time.time()

print(f"Update took {end - start} seconds")