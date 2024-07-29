#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")

for city in "${cities[@]}"; do
	echo $city
	sql="\copy (select building, count(*) as cnt from building_tag_$city group by building order by cnt desc) to '~/buildings/tsv/building_tag_cnt_$city.tsv' with csv delimiter E'\t';"
	psql -d shimazaki -U postgres -c "$sql"
done
