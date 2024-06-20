import duckdb
import os
import time

start = time.time()
# Read data
path_data = os.path.join("..", "Data", "OvertureMap_Japan", "connector", "japan_connector_2024_06_13.parquet")

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

# Drop table
duckdb.execute(f"DROP TABLE IF EXISTS overturemap.{schema}.connector;")

# Create the connector table
duckdb.execute(f"""CREATE TABLE overturemap.{schema}.connector AS (SELECT
               id,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt,
               subtype,
               version,
               update_time,
               JSON(sources) AS sources,
               FROM '{path_data}');
               """)

end = time.time()

print(f"Table creation : {end - start} seconds")

duckdb.execute(f"CREATE INDEX connector_id_idx ON overturemap.{schema}.connector (id);")

end = time.time()

print(f"Index : {end - start} seconds")

rel = duckdb.sql(f"SELECT count(*) FROM overturemap.{schema}.connector;")
rel.show()

end = time.time()

print(f"Select : {end - start} seconds")

# Add a geometry column and change the WKT geom to a geometry
duckdb.execute(f"CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS {schema}.connector ADD COLUMN geom geometry;')")
duckdb.execute(f"CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS {schema}.connector ADD COLUMN theme character varying;')")
duckdb.execute(f"CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS {schema}.connector ADD COLUMN type character varying;')")

duckdb.execute(f"""CALL postgres_execute('overturemap', 'UPDATE {schema}.connector 
               SET geom = public.ST_GeomFromText(geom_wkt, 4326), theme = ''transportation'', type = ''connector'';')""")

end = time.time()

print(f"Alter + Update : {end - start} seconds")

# Create a geom index
duckdb.execute(f"""CALL postgres_execute('overturemap', 'CREATE INDEX connector_geom_idx
               ON {schema}.connector
               USING GIST (geom);')""")


end = time.time()

print(f"Update took {end - start} seconds")