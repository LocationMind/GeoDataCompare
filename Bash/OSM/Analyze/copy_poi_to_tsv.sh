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
			osm_type ,
			osm_id   ,
			name     ,
			class    ,
			subclass ,
			ST_AsText(geom)
		from osm.poi_$city
	) to '$SCRIPT_DIR/tsv/osm_poi_$city.tsv' with csv delimiter E'\t';"
	psql -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql"
done
