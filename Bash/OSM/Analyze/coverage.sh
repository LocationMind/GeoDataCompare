#!/bin/bash

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# set config
source config.sh

cnt=0
for city in "${cities[@]}"; do
	echo $city

	sql="select sum(ST_Area(building_$city.geom::geography)) / 1000000 from osm.building_$city"
	building_area=$(psql -t -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql")
	echo $building_area

	sql="select ST_Area(geom::geography) / 1000000 from osm.shape where name='${city_labels[$cnt]}'"
	whole_area=$(psql -t -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql")
	echo $whole_area

	echo "scale=5; $building_area / $whole_area * 100" | bc

	((cnt++))
done
