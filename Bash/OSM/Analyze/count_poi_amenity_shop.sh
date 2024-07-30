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
		name,
		cnt
	from (
	select
		'poi_cnt' as name,
		count(*) as cnt
	from osm.poi_$city

	union

	select
		'poi_amenity_cnt' as name,
    count(*) as cnt
	from osm.poi_$city
	where class='amenity'
        
	union

	select
		'poi_shop_cnt' as name,
    count(*) as cnt
	from osm.poi_$city
  where class='shop'
	) a
	order by name
	"
	psql -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql"

	((cnt++))
done
