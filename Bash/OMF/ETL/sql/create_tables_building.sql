-- drop table
drop table if exists omf.tokyo_building;
drop table if exists omf.hamamatsu_building;
drop table if exists omf.tateyama_building;
drop table if exists omf.kumamoto_building;
drop table if exists omf.higashi_hiroshima_building;
drop table if exists omf.morioka_building;
drop table if exists omf.building;

-- create table
create table omf.building (
    ogc_fid             integer,
    wkb_geometry        geometry(MULTIPOLYGON, 4326),
    id                  varchar,
    version             integer,
    update_time         timestamp with time zone,
    sources             json,
    subtype             varchar,
    names               json,
    class               varchar,
    level               integer,
    has_parts           boolean,
    height              double precision,
    min_height          double precision,
    num_floors          integer,
    facade_color        varchar,
    facade_material     varchar,
    min_floor           integer,
    roof_material       varchar,
    roof_shape          varchar,
    roof_direction      double precision,
    roof_orientation    varchar,
    roof_color          varchar,
    area_name           char(50)
)
;

create table
    omf.tokyo_building (like omf.building including all);

create table
    omf.hamamatsu_building (like omf.building including all);

create table
    omf.tateyama_building (like omf.building including all);

create table
    omf.kumamoto_building (like omf.building including all);

create table
    omf.higashi_hiroshima_building (like omf.building including all);

create table
    omf.morioka_building (like omf.building including all);
