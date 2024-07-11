import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import geopandas as gpd
import math
import utils



# Set up your PostGIS connection
db_config = {
    'dbname': 'pgrouting',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Connect to the database
connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
connection = utils.getConnection('pgrouting')
engine = create_engine(connection_string)

layer = gpd.read_postgis(sql="select * from omf.edge_with_cost_tokyo", con=engine);

# The purpose of this function is to calculate the x and y tile coordinates for a given latitude, longitude, and zoom level, using the Web Mercator projection.
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)



Session = sessionmaker(bind=engine)
session = Session()

# Define the extent
min_x, min_y, max_x, max_y = layer.total_bounds # Example extent covering the world

# extent_query = 'SELECT ST_XMin(ST_Extent(geom)) as min_x, ST_YMin(ST_Extent(geom)) as min_y, ST_XMax(ST_Extent(geom)) as max_x, ST_YMax(ST_Extent(geom)) as max_y  from osm.multipolygons_layer'
# min_x, min_y, max_x, max_y = session.execute(extent_query).all()[0]

# Define the zoom levels
zoom_levels = list(range(19, 20))  # Example zoom levels from 0 to 17

# Define the SQL query template to fetch geometries for each zoom level
sql_template = '''
    SELECT
        ST_AsMVT(q, 'edge_with_cost_tokyo', 4096, 'geom') as mvt
    FROM (
        SELECT
            ST_AsMVTGeom(
                ST_Transform(geom, 3857),
                ST_TileEnvelope({z}, {x}, {y}),
                4096,
                0,
                true
            ) AS geom,
            *
        FROM
            omf.edge_with_cost_tokyo
        WHERE
            geom && ST_Transform(ST_TileEnvelope({z}, {x}, {y}), 4326)
    ) q;
'''

# Generate vector tiles for the specified extent and zoom levels and locally store them
for z in zoom_levels:
    min_tile_x, max_tile_y = deg2num(min_y, min_x, z)
    max_tile_x, min_tile_y = deg2num(max_y, max_x, z)
    for x in range(min_tile_x, max_tile_x + 1):
        for y in range(min_tile_y, max_tile_y + 1):
            print(z, x, y)
            sql = sql_template.format(z=z, x=x, y=y)
            result = session.execute(text(sql)).scalar()
            
            if result:
                tile_path = f"tiles/{z}/{x}"
                os.makedirs(tile_path, exist_ok=True)
                with open(f"{tile_path}/{y}.mvt", "wb") as tile_file:
                    tile_file.write(result)