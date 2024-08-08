-- drop table
drop table if exists omf.tokyo_place;
drop table if exists omf.hamamatsu_place;
drop table if exists omf.tateyama_place;
drop table if exists omf.kumamoto_place;
drop table if exists omf.higashi_hiroshima_place;
drop table if exists omf.morioka_place;
drop table if exists omf.place;

-- create table
create table
    omf.place (
        ogc_fid serial primary key,
        wkb_geometry geometry (point, 4326),
        id varchar,
        version integer,
        update_time timestamp with time zone,
        sources jsonb,
        names jsonb,
        categories jsonb,
        confidence double precision,
        websites text,
        emails text,
        socials text,
        phones text,
        addresses jsonb,
        brand jsonb
    );

create table
    omf.tokyo_place (like omf.place including all);

create table
    omf.hamamatsu_place (like omf.place including all);

create table
    omf.tateyama_place (like omf.place including all);

create table
    omf.kumamoto_place (like omf.place including all);

create table
    omf.higashi_hiroshima_place (like omf.place including all);

create table
    omf.morioka_place (like omf.place including all);