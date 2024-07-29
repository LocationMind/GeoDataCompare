#!/bin/bash　-e

# Initialize the command in seconds.
SECONDS=0

echo $2
psql -U postgres -d $3 -c "drop table if exists public.pois;"

# import pbf file to database
/data/tool/osm2pgsql/1.9.2/osm2pgsql -d $3 -O flex -S ${0%/*}/pois.lua -E 4326 $1

mkdir ./osm_pois_$2/

# export table to files
pg_dump -U postgres -t public.pois $3 | gzip > ./osm_pois_$2/osm_pois_$2.sql.gz

psql -v ON_ERROR_STOP=1 -U postgres -d $3 -f ${0%/*}/pois2tsv.sql
mv ./pois.tsv ./osm_pois_$2/osm_pois_${2}.tsv
rm ./osm_pois_${2}/osm_pois_${2}.tsv.gz
gzip ./osm_pois_${2}/osm_pois_${2}.tsv

# export both tables to shp and compression them
mkdir ./osm_pois_${2}/osm_pois_${2}_shp/
pgsql2shp -u postgres -P postgres -f ./osm_pois_${2}/osm_pois_${2}_shp/osm_pois_${2}.shp $3 public.pois
zip ./osm_pois_${2}/osm_pois_${2}_shp.zip -r ./osm_pois_${2}/osm_pois_${2}_shp/
rm -r ./osm_pois_${2}/osm_pois_${2}_shp/

psql -U postgres -d $3 -c "drop table if exists public.pois;"

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"