# It will takes 25 minutes to process 5 areas
# Initialize the command in seconds.
SECONDS=0

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

mkdir ./data/202405/overturemaps/

psql -U postgres -d postgres -c "create schema ovt;"

psql -U postgres -d postgres -c "drop table if exists ovt.hamamatsu_bld;"
psql -U postgres -d postgres -c "drop table if exists ovt.tokyo_bld;"
psql -U postgres -d postgres -c "drop table if exists ovt.tateyama_bld;"
psql -U postgres -d postgres -c "drop table if exists ovt.kumamoto_bld;"
psql -U postgres -d postgres -c "drop table if exists ovt.higashi_hiroshima_bld;"
psql -U postgres -d postgres -c "drop table if exists ovt.morioka_bld;"

psql -U postgres -d postgres -f ./create_tables.sql

# Tokyo
overturemaps download --bbox=139.74609375,35.67514744,139.83398438,35.74651226 -f geojson --type=building -o ./data/202405/overturemaps/tokyo.geojson
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln ovt.tokyo_bld -nlt multipolygon ./data/202405/overturemaps/tokyo.geojson

# Hamamatsu
overturemaps download --bbox=137.63671875,34.66935855,137.72460938,34.7416125 -f geojson --type=building -o ./data/202405/overturemaps/hamamatsu.geojson
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln ovt.hamamatsu_bld -nlt multipolygon ./data/202405/overturemaps/hamamatsu.geojson

# Tateyama
overturemaps download --bbox=139.83398438,34.95799531,139.921875,35.02999637 -f geojson --type=building -o ./data/202405/overturemaps/tateyama.geojson
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln ovt.tateyama_bld -nlt multipolygon ./data/202405/overturemaps/tateyama.geojson

# Kumamoto
overturemaps download --bbox=130.68726409,32.72948989,130.77515472,32.80174385 -f geojson --type=building -o ./data/202405/overturemaps/kumamoto.geojson
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln ovt.kumamoto_bld -nlt multipolygon ./data/202405/overturemaps/kumamoto.geojson

# Higashi_hiroshima
overturemaps download --bbox=132.69418348,34.38622724,132.7820741,34.45848119 -f geojson --type=building -o ./data/202405/overturemaps/higashi_hiroshima.geojson
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln ovt.higashi_hiroshima_bld -nlt multipolygon ./data/202405/overturemaps/higashi_hiroshima.geojson

# Morioka
overturemaps download --bbox=141.07765453,39.6823863,141.16554516,39.75375112 -f geojson --type=building -o ./data/202405/overturemaps/morioka.geojson
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln ovt.morioka_bld -nlt multipolygon ./data/202405/overturemaps/morioka.geojson


# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"
