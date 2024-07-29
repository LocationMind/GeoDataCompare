drop table if exists building_tag_tokyo;
create table building_tag_tokyo (
	area_id bigint,
	id bigint,
        geom geometry(multipolygon,4326),
        building text,
        height text
);
drop table if exists building_tag_hamamatsu;
create table building_tag_hamamatsu (
	area_id bigint,
	id bigint,
        geom geometry(multipolygon,4326),
        building text,
        height text
);
drop table if exists building_tag_tateyama;
create table building_tag_tateyama (
	area_id bigint,
	id bigint,
        geom geometry(multipolygon,4326),
        building text,
        height text
);
drop table if exists building_tag_morioka;
create table building_tag_morioka (
        area_id bigint,
        id bigint,
        geom geometry(multipolygon,4326),
        building text,
        height text
);
drop table if exists building_tag_higashi_hiroshima;
create table building_tag_higashi_hiroshima (
        area_id bigint,
        id bigint,
        geom geometry(multipolygon,4326),
        building text,
        height text
);
drop table if exists building_tag_kumamoto;
create table building_tag_kumamoto (
        area_id bigint,
        id bigint,
        geom geometry(multipolygon,4326),
        building text,
        height text
);
