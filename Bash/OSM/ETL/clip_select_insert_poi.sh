#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")
city_labels=("Tokyo" "Tateyama" "Hamamatsu" "Higashi-hiroshima" "Kumamoto" "Morioka")

cnt=0
for city in "${cities[@]}"; do
	echo $city
	city_lable="$city_labels[$cnt]"

	sql="truncate poi_$city"
        psql -d shimazaki -U postgres -c "$sql"

	sql="
	with clipping_area as (
		select * from shape where name='${city_labels[$cnt]}'
	)
	insert into poi_$city (
		osm_type ,
		osm_id   ,
		name     ,
		class    ,
		subclass ,
		geom     
	)
	select
	        osm_type ,
                osm_id   ,
                pois.name,
                class    ,
                subclass ,
		ST_AsText(ST_Intersection(pois.geom, clipping_area.geom)) as geom
	from pois, clipping_area
	where ST_Intersects(pois.geom, clipping_area.geom)
	"
	psql -d shimazaki -U postgres -c "$sql"
	
	((cnt++))
done
