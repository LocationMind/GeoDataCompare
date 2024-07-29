#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")

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
		from poi_$city
	) to '~/tsv/osm_poi_$city.tsv' with csv delimiter E'\t';"
	psql -d shimazaki -U postgres -c "$sql"
done
