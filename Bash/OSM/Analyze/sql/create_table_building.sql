drop table if exists building;
create table building (
	area_id bigint,
	id bigint,
	geom geometry(multipolygon,4326)
);
drop table if exists building_tokyo;
create table building_tokyo (
	area_id bigint,
	id bigint,
	geom geometry(multipolygon,4326)
);
drop table if exists building_hamamatsu;
create table building_hamamatsu (
	area_id bigint,
	id bigint,
	geom geometry(multipolygon,4326)
);
drop table if exists building_tateyama;
create table building_tateyama (
	area_id bigint,
	id bigint,
	geom geometry(multipolygon,4326)
);
drop table if exists building_morioka;
create table building_morioka (
        area_id bigint,
        id bigint,
        geom geometry(multipolygon,4326)
);
drop table if exists building_higashi_hiroshima;
create table building_higashi_hiroshima (
        area_id bigint,
        id bigint,
        geom geometry(multipolygon,4326)
);
drop table if exists building_kumamoto;
create table building_kumamoto (
        area_id bigint,
        id bigint,
        geom geometry(multipolygon,4326)
);
