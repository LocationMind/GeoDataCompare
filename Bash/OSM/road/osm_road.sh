#!/bin/bash　-e

# Initialize the command in seconds.
SECONDS=0

# remove output files generated previpusly
rm -r ./osm_road

# convert osm.pbf to sql.gz by using osm2po
sh ${0%/*}/osm2road/conv_osm_road.sh $1

psql -d postgres -c "drop table if exists public.osm_road_available;"
psql -d postgres -c "drop table if exists public.osm_road_assessment;"

# import the files into tables
gzip -cd ./osm_road/osm_road_available.sql.gz | psql -d postgres
gzip -cd ./osm_road/osm_road_assessment.sql.gz | psql -d postgres

# assess the network
psql -v ON_ERROR_STOP=1 -d postgres -f ${0%/*}/network_assessment.sql

# export the network to files
psql -d postgres -f ${0%/*}/road2tsv.sql
mv ./osm_road/road.tsv ./osm_road/osm_road_$2.tsv
pg_dump -d postgres -t osm_road_available | gzip > ./osm_road/osm_road_$2.sql.gz

mkdir ./osm_road/osm_road_${2}_shp/
pgsql2shp -P postgreses -f ./osm_road/osm_road_${2}_shp/osm_road_${2}.shp miyake public.road
zip ./osm_road/osm_road_${2}_shp.zip -r ./osm_road/osm_road_${2}_shp/
rm -r ./osm_road/osm_road_${2}_shp/

mv ./osm_road/ ./osm_road_${2}/

psql -d postgres -c "drop table if exists public.osm_road_available;"
psql -d postgres -c "drop table if exists public.osm_road_assessment;"

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"
