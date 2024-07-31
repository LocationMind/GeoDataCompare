copy (
    select
        area_id,
        id,
        ST_asText (geom),
        building,
        height
    from
        osm.building
    where
        area_id is not null
        and geom is not null
    order by
        area_id
)
to STDOUT with csv header delimiter E'\t' \g '../tsv/building.tsv'