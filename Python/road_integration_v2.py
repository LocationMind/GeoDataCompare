import duckdb
from duckdb.typing import *
import os
import time

start = time.time()

# Read data
path_data = os.path.join(".", "Data", "Test", "tokyo_segment_2024_06_13.parquet")

# Create and load the spatial extension
duckdb.install_extension("spatial")
duckdb.load_extension("spatial")

# Create and load the postgres extension
duckdb.install_extension("postgres")
duckdb.load_extension("postgres")

# Create environment variable for postgres connexion
dbname = 'pgrouting'
host = '127.0.0.1'
user = 'postgres'
password = 'postgres'
schema = 'omf'
duckdb.execute(f"ATTACH 'dbname={dbname} host={host} user={user} password={password}' AS overturemap (TYPE POSTGRES);")

# Show data description
rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data}';")
rel.show()

# # Drop table
duckdb.execute(f"DROP TABLE IF EXISTS overturemap.{schema}.road CASCADE;")

duckdb.execute(f"""CREATE TABLE overturemap.{schema}.road AS (SELECT
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
               FROM '{path_data}'
               WHERE subtype = 'road');""")

end = time.time()

print(f"Table creation : {end - start} seconds")

duckdb.execute(f"CREATE INDEX road_id_idx ON overturemap.{schema}.road (id);")

end = time.time()

print(f"Index : {end - start} seconds")

rel = duckdb.sql(f"SELECT count(*) FROM overturemap.{schema}.road;")
rel.show()

end = time.time()

print(f"Select : {end - start} seconds")

# Add a geometry column and change the WKT geom to a geometry
duckdb.execute(f"CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS {schema}.road ADD COLUMN geom geometry;')")
duckdb.execute(f"CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS {schema}.road ADD COLUMN theme character varying;')")
duckdb.execute(f"CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS {schema}.road ADD COLUMN type character varying;')")

duckdb.execute(f"""CALL postgres_execute('overturemap', 'UPDATE {schema}.road 
               SET geom = public.ST_GeomFromText(geom_wkt, 4326), theme = ''transportation'', type = ''road'';')""")

end = time.time()

print(f"Alter + Update : {end - start} seconds")

# Create a geom index
duckdb.execute(f"""CALL postgres_execute('overturemap', 'CREATE INDEX road_geom_idx
               ON {schema}.road
               USING GIST (geom);')""")

end = time.time()

print(f"Update took {end - start} seconds")