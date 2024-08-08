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
	osm.poi_tokyo (osm_type, osm_id, name, class, subclass, geom)
select
	osm_type,
	osm_id,
	poi.name,
	class,
	subclass,
	ST_AsText (ST_Intersection (poi.geom, clipping_area.geom)) as geom
from
	osm.poi,
	clipping_area
where
	ST_Intersects (poi.geom, clipping_area.geom);

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
	osm.poi_tateyama (osm_type, osm_id, name, class, subclass, geom)
select
	osm_type,
	osm_id,
	poi.name,
	class,
	subclass,
	ST_AsText (ST_Intersection (poi.geom, clipping_area.geom)) as geom
from
	osm.poi,
	clipping_area
where
	ST_Intersects (poi.geom, clipping_area.geom);

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
	osm.poi_hamamatsu (osm_type, osm_id, name, class, subclass, geom)
select
	osm_type,
	osm_id,
	poi.name,
	class,
	subclass,
	ST_AsText (ST_Intersection (poi.geom, clipping_area.geom)) as geom
from
	osm.poi,
	clipping_area
where
	ST_Intersects (poi.geom, clipping_area.geom);

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
	osm.poi_higashi_hiroshima (osm_type, osm_id, name, class, subclass, geom)
select
	osm_type,
	osm_id,
	poi.name,
	class,
	subclass,
	ST_AsText (ST_Intersection (poi.geom, clipping_area.geom)) as geom
from
	osm.poi,
	clipping_area
where
	ST_Intersects (poi.geom, clipping_area.geom);

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
	osm.poi_kumamoto (osm_type, osm_id, name, class, subclass, geom)
select
	osm_type,
	osm_id,
	poi.name,
	class,
	subclass,
	ST_AsText (ST_Intersection (poi.geom, clipping_area.geom)) as geom
from
	osm.poi,
	clipping_area
where
	ST_Intersects (poi.geom, clipping_area.geom);

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
	osm.poi_morioka (osm_type, osm_id, name, class, subclass, geom)
select
	osm_type,
	osm_id,
	poi.name,
	class,
	subclass,
	ST_AsText (ST_Intersection (poi.geom, clipping_area.geom)) as geom
from
	osm.poi,
	clipping_area
where
	ST_Intersects (poi.geom, clipping_area.geom);