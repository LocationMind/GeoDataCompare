#!/bin/bash

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# set config
source config.sh

for city in "${cities[@]}"; do
	echo $city
	sql="\copy (
		select 
			area_id, 
			id,  
			ST_AsText(geom),
			building,
			height
		from osm.building_$city
		) to '$SCRIPT_DIR/tsv/osm_building_$city.tsv' 
		with csv delimiter E'\t';"
	psql -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql"
done
