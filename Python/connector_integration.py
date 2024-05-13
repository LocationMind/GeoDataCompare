import duckdb
import os
import time

start = time.time()
# Read data
path_data = os.path.join("..", "Data", "OvertureMap_Japan", "connector", "*.parquet")

# Create and load the spatial extension
duckdb.install_extension("spatial")
duckdb.load_extension("spatial")

# Create and load the postgres extension
duckdb.install_extension("postgres")
duckdb.load_extension("postgres")

# Create environment variable for postgres connexion
dbname = 'overturemap'
host = '127.0.0.1'
user = 'postgres'
password = 'postgres'
duckdb.execute(f"ATTACH 'dbname={dbname} host={host} user={user} password={password}' AS overturemap (TYPE POSTGRES);")

# Show data description
rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data}';")
rel.show()

# Drop table
duckdb.execute("DROP TABLE IF EXISTS overturemap.public.connector;")

# Create the connector table
duckdb.execute(f"""CREATE TABLE overturemap.public.connector AS (SELECT
               id,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt,
               version,
               update_time,
               JSON(sources) AS sources,
               FROM '{path_data}');
               """)

end = time.time()

print(f"Table creation : {end - start} seconds")

duckdb.execute("CREATE INDEX connector_id_idx ON overturemap.public.connector (id);")

end = time.time()

print(f"Index : {end - start} seconds")

rel = duckdb.sql("SELECT * FROM overturemap.public.connector;")
rel.show()

end = time.time()

print(f"Select : {end - start} seconds")

# Add a geometry column and change the WKT geom to a geometry
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.connector ADD COLUMN geom geometry;')")
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.connector ADD COLUMN theme character varying;')")
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.connector ADD COLUMN type character varying;')")

duckdb.execute("""CALL postgres_execute('overturemap', 'UPDATE public.connector 
               SET geom = public.ST_GeomFromText(geom_wkt, 4326), theme = ''transportation'', type = ''connector'';')""")

end = time.time()

print(f"Alter + Update : {end - start} seconds")

""" TODO : 
- Rethink the road and building model, as it may not be useful to add the theme and type in the data model (it is kind of in the name of the table already).
- Create SQL function to extract information within the data, such as :
    - primary_name in names
    - surface in road
    - width in road
    - lanes in road
    - restriction in road
- download data for connector, road and building part using overturemaps tool and the bbox of japan : 122.7141754,20.2145811,154.205541,45.7112046
- do the same for the administrtive boundaries, by keeping only important information for country only (admin_level = 1), like iso code and primary name.
"""

end = time.time()

print(f"Update took {end - start} seconds")