drop table omf.tokyo_bld;
create table omf.tokyo_bld (
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

drop table omf.hamamatsu_bld;
create table omf.hamamatsu_bld (
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
    area_name           char(50))
;

drop table omf.tateyama_bld;
create table omf.tateyama_bld (
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

drop table omf.kumamoto_bld;
create table omf.kumamoto_bld (
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

drop table omf.higashi_hiroshima_bld;
create table omf.higashi_hiroshima_bld (
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

drop table omf.morioka_bld;
create table omf.morioka_bld (
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
