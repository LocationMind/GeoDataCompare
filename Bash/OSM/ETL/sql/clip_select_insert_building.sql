-- tokyo
with
	clipping_area as (
		select
			*
		from
			osm.shape
		where
			name = 'Tokyo'
	)
insert into
	osm.building_tokyo (area_id, id, geom, building, height)
select
	area_id,
	id,
	ST_Intersection (building.geom, clipping_area.geom) as geom,
	building,
	height
from
	osm.building,
	clipping_area
where
	ST_Intersects (building.geom, clipping_area.geom);

-- tateyama
with
	clipping_area as (
		select
			*
		from
			osm.shape
		where
			name = 'Tateyama'
	)
insert into
	osm.building_tateyama (area_id, id, geom, building, height)
select
	area_id,
	id,
	ST_Intersection (building.geom, clipping_area.geom) as geom,
	building,
	height
from
	osm.building,
	clipping_area
where
	ST_Intersects (building.geom, clipping_area.geom);

-- hamamatsu
with
	clipping_area as (
		select
			*
		from
			osm.shape
		where
			name = 'Hmaamatsu' -- becase of shape file
	)
insert into
	osm.building_hamamatsu (area_id, id, geom, building, height)
select
	area_id,
	id,
	ST_Intersection (building.geom, clipping_area.geom) as geom,
	building,
	height
from
	osm.building,
	clipping_area
where
	ST_Intersects (building.geom, clipping_area.geom);

-- higashi_hiroshima
with
	clipping_area as (
		select
			*
		from
			osm.shape
		where
			name = 'Higashi-hiroshima'
	)
insert into
	osm.building_higashi_hiroshima (area_id, id, geom, building, height)
select
	area_id,
	id,
	ST_Intersection (building.geom, clipping_area.geom) as geom,
	building,
	height
from
	osm.building,
	clipping_area
where
	ST_Intersects (building.geom, clipping_area.geom);

-- kumamoto
with
	clipping_area as (
		select
			*
		from
			osm.shape
		where
			name = 'Kumamoto'
	)
insert into
	osm.building_kumamoto (area_id, id, geom, building, height)
select
	area_id,
	id,
	ST_Intersection (building.geom, clipping_area.geom) as geom,
	building,
	height
from
	osm.building,
	clipping_area
where
	ST_Intersects (building.geom, clipping_area.geom);

-- morioka
with
	clipping_area as (
		select
			*
		from
			osm.shape
		where
			name = 'Morioka'
	)
insert into
	osm.building_morioka (area_id, id, geom, building, height)
select
	area_id,
	id,
	ST_Intersection (building.geom, clipping_area.geom) as geom,
	building,
	height
from
	osm.building,
	clipping_area
where
	ST_Intersects (building.geom, clipping_area.geom);