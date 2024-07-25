drop table ovt.tokyo_bld;
create table ovt.tokyo_bld (
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

drop table ovt.hamamatsu_bld;
create table ovt.hamamatsu_bld (
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

drop table ovt.tateyama_bld;
create table ovt.tateyama_bld (
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

drop table ovt.kumamoto_bld;
create table ovt.kumamoto_bld (
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

drop table ovt.higashi_hiroshima_bld;
create table ovt.higashi_hiroshima_bld (
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

drop table ovt.morioka_bld;
create table ovt.morioka_bld (
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
