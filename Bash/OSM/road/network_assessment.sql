alter table public.osm_road_available add column groupno integer;

update public.osm_road_available
set groupno = val.groupno
from (
    select
        oras.groupno as groupno,
        orav.id as id
    from
        public.osm_road_assessment oras,
        public.osm_road_available orav
    where ST_Intersects(orav.geom_way, oras.geom)
) as val where public.osm_road_available.id = val.id ;

