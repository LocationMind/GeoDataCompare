import duckdb
import os
import time

start = time.time()
# Read data
# path = os.path.join("Data", "okubo.parquet")
path_data = os.path.join("..", "Data", "OvertureMap", "locality", "*.parquet")

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

# Show all the tables in the database
table = duckdb.sql("SHOW ALL TABLES")
table.show()

# Show data
rel = duckdb.sql(f"SELECT * FROM '{path_data}';")
rel.show()

# Count number of rows
rel = duckdb.sql(f"SELECT count(*) as number_of_rows FROM '{path_data}';")
rel.show()

# Get all data without id
rel = duckdb.sql(f"SELECT * FROM '{path_data}' where admin_level = 1 and locality_type = 'country';")
rel.show()

# Get all data without id
rel = duckdb.sql(f"SELECT * FROM '{path_data}' where admin_level = 1;")
rel.show()

# Description of the parquets file
rel = duckdb.sql(f"DESCRIBE SELECT * FROM '{path_data}';")
rel.show()

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