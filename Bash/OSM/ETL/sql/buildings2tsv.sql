copy (
    select
        area_id,
        id,
        ST_asText(geom)
    from
        public.buildings
    where
        area_id is not null and geom is not null
    order by
        area_id
) to STDOUT with csv header delimiter E'\t' \g 'buildings.tsv'