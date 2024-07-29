#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")
city_labels=("Tokyo" "Tateyama" "Hamamatsu" "Higashi-hiroshima" "Kumamoto" "Morioka")

cnt=0
for city in "${cities[@]}"; do
	echo $city
	city_lable="$city_labels[$cnt]"

	sql="truncate building_tag_$city"
        psql -d shimazaki -U postgres -c "$sql"

	sql="
	with clipping_area as (
		select * from shape where name='${city_labels[$cnt]}'
	)
	insert into building_tag_$city (
		area_id,
		id,
		geom,
		building,
		height
	)
	select
   		area_id,
		id,	
		ST_AsText(ST_Intersection(building_tag.geom, clipping_area.geom)) as geom,
		building,
		height
	from building_tag, clipping_area
	where ST_Intersects(building_tag.geom, clipping_area.geom)
	"
	psql -d shimazaki -U postgres -c "$sql"
	
	((cnt++))
done
