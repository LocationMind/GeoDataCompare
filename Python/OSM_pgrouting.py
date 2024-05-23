import networkx as nx
import osmnx as ox
import numpy as np
from sqlalchemy import create_engine
import time

start = time.time()

def bboxCsvToTuple(bbox):
    """Tranform a bbox in a CSV format to a tuple.
    The bbox is in format west, south, east, north
    The tuple will be as (north, south, east, west)

    Args:
        bbox (str): bbox of an area, given in a CSV format

    Returns:
        (tuple(float, float, float, float)): bbox in the format (north, south, east, west)
    """
    (west, south, east, north) = bbox.split(',')
    return (float(north), float(south), float(east), float(west))

# Get network data for driving cars only in Tokyo center
bbox = bboxCsvToTuple("139.69779,35.603791,139.838965,35.723621")
graph = ox.graph_from_bbox(bbox=bbox, network_type="drive")

end = time.time()
print(f"Create graph : {end - start} seconds")

# Transform the graph in a directed graph

# Transform the graph to geodataframe for the edges and nodes
node, edge = ox.graph_to_gdfs(graph)

end = time.time()
print(f"Load graph : {end - start} seconds")

# Create an engine to save into postgresql
engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/osm-pgrouting") 

# Save nodes to postgresql
node.to_postgis("node_bbox", engine, if_exists="replace", index=True)

end = time.time()
print(f"Save node to postgis : {end - start} seconds")

# Save edges to postgresql
edge.to_postgis("edge_bbox", engine, if_exists="replace", index=True)

end = time.time()
print(f"Save edge to postgis : {end - start} seconds")