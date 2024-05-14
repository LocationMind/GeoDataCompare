# Internship : Open data quality assessment (OpenStreetMap and Overture Map)

### Useful command

pip install gdal
pip install overturemaps
pip install duckdb
pip install shapely

add ogr2ogr to the environnment variable : 

then adding 2 new entries : 

GDAL_DATA

With path:

C:\OSGeo4W\share\gdal

One for:

PROJ_LIB

With path:

C:\OSGeo4W64\share\proj
This is not useful if you have already install postgresal and postgis I think

From : https://gisforthought.com/setting-up-your-gdal-and-ogr-environmental-variables/

### Log / Notes / Thoughts

The insertion of overturemap data using duckdb is quite long : more than an hour for the buildings, and almost 3 hours for the roads!

