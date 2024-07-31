-- drop table
drop table if exists osm.poi_tokyo;

drop table if exists osm.poi_hamamatsu;

drop table if exists osm.poi_tateyama;

drop table if exists osm.poi_kumamoto;

drop table if exists osm.poi_higashi_hiroshima;

drop table if exists osm.poi_morioka;

-- create table
create table
  osm.poi_tokyo (like osm.poi including all);

create table
  osm.poi_hamamatsu (like osm.poi including all);

create table
  osm.poi_tateyama (like osm.poi including all);

create table
  osm.poi_kumamoto (like osm.poi including all);

create table
  osm.poi_higashi_hiroshima (like osm.poi including all);

create table
  osm.poi_morioka (like osm.poi including all);