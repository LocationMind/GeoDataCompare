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
			class, subclass, count(*) as subclass_cnt 
		from osm.poi_$city 
		group by class, subclass 
		order by class, subclass_cnt desc
		)	to '$SCRIPT_DIR/tsv/osm_poi_cnt_$city.tsv' 
		with csv delimiter E'\t';
	"
	psql -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql"
done
