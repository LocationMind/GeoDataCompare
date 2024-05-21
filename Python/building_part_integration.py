import duckdb
import os
import time

start = time.time()
# Read data
path_data = os.path.join("..", "Data", "OvertureMap_Japan", "building_part", "*.parquet")

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
duckdb.execute("DROP TABLE IF EXISTS overturemap.public.building_part CASCADE;")

# Create the building_part table
duckdb.execute(f"""CREATE TABLE overturemap.public.building_part AS (SELECT
               id,
               ST_AsText(ST_GeomFromWKB(geometry)) AS geom_wkt,
               version,
               update_time,
               JSON(sources) AS sources,
               names.primary AS primary_name,
               level,
               height,
               building_id
               FROM '{path_data}');
               """)

end = time.time()

print(f"Table creation : {end - start} seconds")

duckdb.execute("CREATE INDEX building_part_id_idx ON overturemap.public.building_part (id);")

end = time.time()

print(f"Index : {end - start} seconds")

rel = duckdb.sql("SELECT count(*) FROM overturemap.public.building_part;")
rel.show()

end = time.time()

print(f"Select : {end - start} seconds")

# Add a geometry column and change the WKT geom to a geometry
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.building_part ADD COLUMN geom geometry;')")
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.building_part ADD COLUMN theme character varying;')")
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.building_part ADD COLUMN type character varying;')")

duckdb.execute("""CALL postgres_execute('overturemap', 'UPDATE public.building_part 
               SET geom = public.ST_GeomFromText(geom_wkt, 4326), theme = ''buildings'', type = ''building_part'';')""")

end = time.time()

print(f"Alter + Update : {end - start} seconds")

# Create a geom index
duckdb.execute("""CALL postgres_execute('overturemap', 'CREATE INDEX building_part_geom_idx
               ON public.building_part
               USING GIST (geom);')""")


end = time.time()

print(f"Update took {end - start} seconds")