-- drop table
drop table if exists osm.building_tokyo;

drop table if exists osm.building_hamamatsu;

drop table if exists osm.building_tateyama;

drop table if exists osm.building_kumamoto;

drop table if exists osm.building_higashi_hiroshima;

drop table if exists osm.building_morioka;

-- create table
create table
        osm.building_tokyo (like osm.building including all);

create table
        osm.building_hamamatsu (like osm.building including all);

create table
        osm.building_tateyama (like osm.building including all);

create table
        osm.building_kumamoto (like osm.building including all);

create table
        osm.building_higashi_hiroshima (like osm.building including all);

create table
        osm.building_morioka (like osm.building including all);