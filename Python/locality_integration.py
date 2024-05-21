import duckdb
import os
import time

start = time.time()
# Read data
path_data_locality_area = os.path.join("..", "Data", "OvertureMap_Japan", "locality_area", "*.parquet")
path_data_locality = os.path.join("..", "Data", "OvertureMap_Japan", "locality", "*.parquet")

# Create and load the spatial extension
duckdb.install_extension("spatial")
duckdb.load_extension("spatial")
# duckdb.execute("INSTALL spatial; LOAD spatial;")

# Create and load the postgres extension
duckdb.install_extension("postgres")
duckdb.load_extension("postgres")
# duckdb.execute("INSTALL postgres; LOAD postgres;")

# Create environment variable for postgres connexion
dbname = 'overturemap'
host = '127.0.0.1'
user = 'postgres'
password = 'postgres'
duckdb.execute(f"ATTACH 'dbname={dbname} host={host} user={user} password={password}' AS overturemap (TYPE POSTGRES);")

# Show data description
rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data_locality_area}';")
rel.show()

# Show data description
rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data_locality}';")
rel.show()

# Create table for the locality and for the locality area
duckdb.execute(f"""CREATE TABLE locality AS (SELECT 
               id ,
               ST_GeomFromWKB(geometry) AS geometry,
               JSON(bbox) AS bbox,
               admin_level,
               is_maritime  ,
               geopol_display   ,
               version ,
               update_time  ,
               JSON(sources) AS sources,
               subtype  ,
               locality_type    ,
               wikidata ,
               context_id   ,
               population  ,
               iso_country_code_alpha_2 ,
               iso_sub_country_code ,
               default_language ,
               driving_side ,
               JSON(names) AS names,
               locality_id
               FROM '{path_data_locality}'
               WHERE admin_level = 1);""")

duckdb.execute("CREATE UNIQUE INDEX locality_id_idx ON locality (id);")

rel = duckdb.sql("SELECT * FROM locality;")
rel.show()

duckdb.execute(f"""CREATE TABLE locality_area AS (SELECT 
               id ,
               ST_GeomFromWKB(geometry) AS geometry,
               JSON(bbox) AS bbox,
               admin_level,
               is_maritime  ,
               geopol_display   ,
               version ,
               update_time  ,
               JSON(sources) AS sources,
               subtype  ,
               locality_type    ,
               wikidata ,
               context_id   ,
               population  ,
               iso_country_code_alpha_2 ,
               iso_sub_country_code ,
               default_language ,
               driving_side ,
               JSON(names) AS names,
               locality_id
               FROM '{path_data_locality_area}');
               """)

duckdb.execute("CREATE UNIQUE INDEX locality_area_id_idx ON locality_area (id);")

rel = duckdb.sql("SELECT * FROM locality_area;")
rel.show()

# Join the two tables
duckdb.execute(f"CREATE TABLE join_table_locality AS (SELECT l.* EXCLUDE (geometry), la.geometry FROM locality l JOIN locality_area la ON l.id = la.locality_id);")

rel = duckdb.sql("SELECT * FROM join_table_locality;")
rel.show()

# Drop table
duckdb.execute("DROP TABLE IF EXISTS overturemap.public.locality;")

# Load data in a postgresql table
duckdb.execute(f"""CREATE TABLE overturemap.public.locality AS (SELECT 
               id ,
               ST_AsText(geometry) AS geom_wkt,
               JSON(bbox) AS bbox,
               admin_level,
               is_maritime  ,
               geopol_display   ,
               version ,
               update_time  ,
               JSON(sources) AS sources,
               subtype  ,
               locality_type    ,
               wikidata ,
               context_id   ,
               population  ,
               iso_country_code_alpha_2 ,
               iso_sub_country_code ,
               default_language ,
               driving_side ,
               JSON(names) AS names,
               locality_id
               FROM join_table_locality
               );
               """)

duckdb.execute("CREATE UNIQUE INDEX locality_id_idx ON overturemap.public.locality (id);")

# Add a geometry column and change the WKT geom to a geometry
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.locality ADD COLUMN geom geometry;')")

duckdb.execute("CALL postgres_execute('overturemap', 'UPDATE public.locality SET geom = public.ST_GeomFromText(geom_wkt, 4326);')")


# Create a geom index
duckdb.execute("""CALL postgres_execute('overturemap', 'CREATE INDEX locality_geom_idx
               ON public.locality
               USING GIST (geom);')""")

end = time.time()

print(f"Update took {end - start} seconds")