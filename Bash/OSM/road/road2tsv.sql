copy (
    select
        groupno,
        osm_id,
        id,
        osm_source_id,
        osm_target_id,
        clazz,
        flags,
        source,
        target,
        km,
        kmh,
        cost,
        reverse_cost,
        x1,
        y1,
        x2,
        y2,
        osm_name,
        osm_meta,
        ST_asText(geom_way)
    from
        public.osm_road_available
    where
        osm_id is not null and geom_way is not null
    order by
        osm_id
) to STDOUT with csv header delimiter E'\t' \g 'road.tsv'