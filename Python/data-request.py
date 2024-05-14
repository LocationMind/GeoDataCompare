import duckdb
import os
import time

start = time.time()

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

rel = duckdb.sql("SELECT * FROM overturemap.public.building WHERE id = '08b2f5a366998fff0200d893ee900152'")
rel.show()

end = time.time()

print(f"Update took {end - start} seconds")