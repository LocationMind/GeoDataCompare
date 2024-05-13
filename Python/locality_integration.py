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
duckdb.execute("INSTALL spatial; LOAD spatial;")

# Create and load the postgres extension
duckdb.install_extension("postgres")
duckdb.load_extension("postgres")
duckdb.execute("INSTALL postgres; LOAD postgres;")

# Create environment variable for postgres connexion
dbname = 'overturemap'
host = '127.0.0.1'
user = 'postgres'
password = 'postgres'
duckdb.execute(f"ATTACH 'dbname={dbname} host={host} user={user} password={password}' AS overturemap (TYPE POSTGRES);")

'''
# Show all the tables in the database
table = duckdb.sql("SHOW ALL TABLES")
table.show()


# Count number of rows
rel = duckdb.sql(f"SELECT count(*) as number_of_rows FROM '{path_data_locality_area}';")
rel.show()

# Show data
rel = duckdb.sql(f"SELECT * FROM '{path_data_locality_area}';")
rel.show()

# Get all data without id
rel = duckdb.sql(f"SELECT * FROM '{path_data_locality_area}' where admin_level = 1;")
rel.show()
'''
# Show data description
rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data_locality_area}';")
rel.show()

# Show data description
rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data_locality_area}';")
rel.show()

# Create table for the locality and for the locality area
duckdb.execute(f"""CREATE TABLE locality AS (SELECT 
               id,
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

rel = duckdb.sql("SELECT * FROM locality;")
rel.show()

duckdb.execute(f"""CREATE TABLE locality_area AS (SELECT 
               id,
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

rel = duckdb.sql("SELECT * FROM locality_area;")
rel.show()

duckdb.execute(f"CREATE TABLE join_table_locality AS (SELECT l.* EXCLUDE (geometry), la.geometry FROM locality l JOIN locality_area la ON l.id = la.locality_id);")

rel = duckdb.sql("SELECT * FROM join_table_locality;")
rel.show()

# Drop table
duckdb.execute("DROP TABLE IF EXISTS overturemap.public.locality;")

# Load data in a postgresql table
duckdb.execute(f"""CREATE TABLE overturemap.public.locality AS (SELECT 
               id,
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

# Add a geometry column and change the WKT geom to a geometry
duckdb.execute("CALL postgres_execute('overturemap', 'ALTER TABLE IF EXISTS public.locality ADD COLUMN geom geometry;')")

duckdb.execute("CALL postgres_execute('overturemap', 'UPDATE public.locality SET geom = public.ST_GeomFromText(geom_wkt, 4326);')")

# Load data in a geopackage file table
# duckdb.execute(f"""COPY(
#                 SELECT
#                     id,
#                     ST_GeomFromWKB(geometry) AS geom,
#                     JSON(bbox) AS bbox,
#                     admin_level,
#                     is_maritime  ,
#                     geopol_display   ,
#                     version ,
#                     update_time  ,
#                     JSON(sources) AS sources,
#                     subtype  ,
#                     locality_type    ,
#                     wikidata ,
#                     context_id   ,
#                     population  ,
#                     iso_country_code_alpha_2 ,
#                     iso_sub_country_code ,
#                     default_language ,
#                     driving_side ,
#                     JSON(names) AS names,
#                     locality_id
#                     FROM '{path_data_locality_area}'
#                 ) 
#                 TO 'locality_area.gpkg'
#                 WITH (FORMAT GDAL, DRIVER 'GPKG');
#                """)


# # Get all data without id
# rel = duckdb.sql(f"SELECT * FROM '{path_data}' where admin_level = 1 and locality_type = 'country';")
# rel.show()




# Load parquets file into a table in a database
# duckdb.execute(f"""CREATE TABLE overturemap.segment AS (
#                 SELECT
#                     id,
#                     ST_GeomFromWkb(geometry) AS geom,
#                     version,




               
#                * FROM '{path_data}';""")

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
- 
"""

# rel = con.sql(f"SELECT count(*) as nb_entity FROM '{path_data}';")
# rel.show()


end = time.time()

print(f"Update took {end - start} seconds")