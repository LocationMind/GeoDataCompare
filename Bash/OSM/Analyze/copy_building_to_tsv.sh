#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")

for city in "${cities[@]}"; do
	echo $city
	sql="\copy (select area_id, id,  ST_AsText(geom)from building_$city) to '~/tsv/osm_building_$city.tsv' with csv delimiter E'\t';"
	psql -d shimazaki -U postgres -c "$sql"
done
