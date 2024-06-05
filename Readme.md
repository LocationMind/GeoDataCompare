# OSM_Overture_Works

|   |   |
|:---:|:---:|
| Main  | [![Test](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml/badge.svg?branch=main)](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml?query=branch%3Amain)  |
| Dev  | [![Test](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml/badge.svg?branch=dev)](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml?query=branch%3Adev)  |
| Last commit | [![Test](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml/badge.svg)](https://github.com/LocationMind/OSM_Overture_Works/actions/workflows/action.yml) |

## Bounding box used to test algorithms:

- urban area --> 12/3638/1612 (tokyo)
  - `139.74609375, 35.67514743608467, 139.833984375, 35.7465122599185`

- sub-urban area --> 12/3614/1626 (hamamatsu)
  - `137.63671875, 34.66935854524544, 137.724609375, 34.74161249883172`

- rural --> 12/3639/1622 (tateyama)
  - `139.833984375, 34.95799531086791, 139.921875, 35.02999636902566`


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

