import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
from shapely import wkt
import time

log = print

start = time.time()

engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/osm-pgrouting")

# Select all roads
sql = """SELECT * FROM edge_bbox_test;"""

df = gpd.read_postgis(sql, engine, geom_col="geom1" )

print(df)

print(df.shape)

end = time.time()
print(f"It took {end - start} seconds")

# Select bidirectional roads
sql_bi_roads = """
SELECT * FROM edge_bbox_test
WHERE u1 = v2 AND v1 = u2
AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691));"""

bi = gpd.read_postgis(sql_bi_roads, engine, geom_col="geom1" )

print(bi)

print(bi.shape)

end = time.time()
print(f"It took {end - start} seconds")

# Select all the other roads
sql_uni_road = """
SELECT * FROM edge_bbox_test
WHERE id1 not in (
    SELECT id1 FROM edge_bbox_test
    WHERE u1 = v2 AND v1 = u2
    AND ST_Contains(ST_Buffer(ST_Transform(geom1, 6691), 0.5), ST_Transform(geom2, 6691))
    AND ST_Contains(ST_Buffer(ST_Transform(geom2, 6691), 0.5), ST_Transform(geom1, 6691)));"""
    
uni = gpd.read_postgis(sql_uni_road, engine, geom_col="geom1" )

print(uni)

print(uni.shape)

end = time.time()
print(f"It took {end - start} seconds")

# Check if all roads have been selected
print(df.shape[0])
print(bi.shape[0] + uni.shape[0])

# For bidirectionnal roads, agregate them into one.
# Dictionnary for the mapping id1 / id2
dict = {}

# To do so, we first have to parse each row and check what are the 
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
print(f"It took {end - start} seconds")

# When we have all the pair in the dictionnary, we verify that we only have two value per key
listNot2Count = []
for key in dict:
    if len(dict[key]) != 2:
        # If there are not exactly two occurences of the pair, we remove it but keep a track of it
        listNot2Count.append(dict.pop(key))

print(listNot2Count)

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
print(f"It took {end - start} seconds")

# We concatenate the two dataframes to recreate the whole road network
edge_with_cost = pd.concat([bi_without_parallel, uni])

print(edge_with_cost)

end = time.time()
print(f"It took {end - start} seconds")

# Drop useless columns and rename the other columns
edge_with_cost = edge_with_cost.drop(columns=["key1", "id2", "u2", "v2", "key2", "geom2"])

edge_with_cost = edge_with_cost.rename(columns={"id1":"id", "u1":"source", "v1":"target", "geom1":"geom"})

# Set the geometry to the geom column
edge_with_cost = edge_with_cost.set_geometry("geom") 

edge_with_cost.to_postgis("edge_bbox_without_parallel", engine, if_exists="replace", index=True)

end = time.time()
print(f"It took {end - start} seconds")

# exec(open('c:/Users/Mathis.Rouillard/Documents/OSM_Overture_Works/Python/OSM_to_network.py').read())