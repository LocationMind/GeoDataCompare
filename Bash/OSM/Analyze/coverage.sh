#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")
city_labels=("Tokyo" "Tateyama" "Hamamatsu" "Higashi-hiroshima" "Kumamoto" "Morioka")

cnt=0
for city in "${cities[@]}"; do
	echo $city
	city_lable="$city_labels[$cnt]"

	sql="select sum(ST_Area(building_$city.geom::geography)) / 1000000 from building_$city"
	building_area=$(psql -t -d shimazaki -U postgres -c "$sql")
	echo $building_area

        sql="select ST_Area(geom::geography) / 1000000 from shape where name='${city_labels[$cnt]}'"
	whole_area=$(psql -t -d shimazaki -U postgres -c "$sql")
	echo $whole_area

	echo "scale=5; $building_area / $whole_area * 100" | bc

	((cnt++))
done
