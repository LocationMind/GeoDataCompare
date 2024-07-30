#!/bin/bash

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# set config
source config.sh

cnt=0
for city in "${cities[@]}"; do
	echo $city
	sql="
	select
		count(height) as cnt_height
	from osm.building_$city
	"
	psql -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql"
	
	((cnt++))
done
