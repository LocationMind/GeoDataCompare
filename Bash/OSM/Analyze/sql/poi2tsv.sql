copy (
    select
        osm_id,
        osm_type,
        name,
        class,
        subclass,
        ST_asText(geom)
    from
        osm.poi
    where
        osm_id is not null and geom is not null
    order by
        osm_id
) to STDOUT with csv header delimiter E'\t' \g '../tsv/poi.tsv'