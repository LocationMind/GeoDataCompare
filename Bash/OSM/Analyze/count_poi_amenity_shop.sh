#!/bin/bash

cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")
city_labels=("Tokyo" "Tateyama" "Hamamatsu" "Higashi-hiroshima" "Kumamoto" "Morioka")

cnt=0
for city in "${cities[@]}"; do
	echo $city
	city_lable="$city_labels[$cnt]"
	
	sql="
	select 
		name,
		cnt
	from (
	select
		'poi_cnt' as name,
		count(*) as cnt
	from poi_$city

	union

        select
		'poi_amenity_cnt' as name,
                count(*) as cnt
        from poi_$city
	where class='amenity'
        
	union

	select
		'poi_shop_cnt' as name,
                count(*) as cnt
        from poi_$city
        where class='shop'
	) a
	order by name
	"
        psql -d shimazaki -U postgres -c "$sql"

	((cnt++))
done
