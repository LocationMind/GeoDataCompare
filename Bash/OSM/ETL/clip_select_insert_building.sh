#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")
city_labels=("Tokyo" "Tateyama" "Hamamatsu" "Higashi-hiroshima" "Kumamoto" "Morioka")

cnt=0
for city in "${cities[@]}"; do
	echo $city
	city_lable="$city_labels[$cnt]"

	sql="truncate building_$city"
        psql -d shimazaki -U postgres -c "$sql"

	sql="
	with clipping_area as (
		select * from shape where name='${city_labels[$cnt]}'
	)
	insert into building_$city (
		area_id,
		id,
		geom
	)
	select
   		area_id,
		id,	
		ST_AsText(ST_Intersection(building.geom, clipping_area.geom)) as geom
	from building, clipping_area
	where ST_Intersects(building.geom, clipping_area.geom)
	"
	psql -d shimazaki -U postgres -c "$sql"
	
	((cnt++))
done
