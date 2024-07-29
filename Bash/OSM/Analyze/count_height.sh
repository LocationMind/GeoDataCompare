#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")
city_labels=("Tokyo" "Tateyama" "Hamamatsu" "Higashi-hiroshima" "Kumamoto" "Morioka")

cnt=0
for city in "${cities[@]}"; do
	echo $city
	city_lable="$city_labels[$cnt]"

	sql="
	select
		count(height) as cnt_height
	from building_tag_$city
	"
	psql -d shimazaki -U postgres -c "$sql"
	
	((cnt++))
done
