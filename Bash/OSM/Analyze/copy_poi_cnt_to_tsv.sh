#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")

for city in "${cities[@]}"; do
	echo $city
	sql="\copy (
		select 
			class, subclass, count(*) as subclass_cnt 
		from poi_$city 
		group by class, subclass 
		order by class, subclass_cnt desc) 
		to '~/osm/tsv/poi_cnt_$city.tsv' 
	with csv delimiter E'\t';
	"
	psql -d shimazaki -U postgres -c "$sql"
done
