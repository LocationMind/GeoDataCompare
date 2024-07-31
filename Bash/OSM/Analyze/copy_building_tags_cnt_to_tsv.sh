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
			building, 
			count(*) as cnt 
		from osm.building_$city 
		group by 
			building 
		order by 
			cnt desc
		) to '$SCRIPT_DIR/tsv/osm_building_cnt_$city.tsv'
		 with csv delimiter E'\t';"
	psql -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql"
done
