#!/bin/bash　-e

# Initialize the command in seconds.
SECONDS=0

psql -U postgres -d postgres -c "create schema osm;"

psql -U postgres -d postgres -c "drop table if exists osm.tokyo_bld;"
psql -U postgres -d postgres -c "drop table if exists osm.tateyama_bld;"
psql -U postgres -d postgres -c "drop table if exists osm.hamamatsu_bld;"
psql -U postgres -d postgres -c "drop table if exists osm.kumamoto_bld;"
psql -U postgres -d postgres -c "drop table if exists osm.higashi_hiroshima_bld;"
psql -U postgres -d postgres -c "drop table if exists osm.morioka_bld;"

psql -U postgres -d postgres -c "create table osm.tokyo_bld(area_id bigint, id bigint, geom geometry(MultiPolygon,4326));"
psql -U postgres -d postgres -c "create table osm.tateyama_bld(area_id bigint, id bigint, geom geometry(MultiPolygon,4326));"
psql -U postgres -d postgres -c "create table osm.hamamatsu_bld(area_id bigint, id bigint, geom geometry(MultiPolygon,4326));"
psql -U postgres -d postgres -c "create table osm.kumamoto_bld(area_id bigint, id bigint, geom geometry(MultiPolygon,4326));"
psql -U postgres -d postgres -c "create table osm.higashi_hiroshima_bld(area_id bigint, id bigint, geom geometry(MultiPolygon,4326));"
psql -U postgres -d postgres -c "create table osm.morioka_bld(area_id bigint, id bigint, geom geometry(MultiPolygon,4326));"

psql -U postgres -d postgres -c "\copy osm.tokyo_bld from './data/202405/osm/osm_building_tokyo.tsv' delimiter E'\t' csv;"
psql -U postgres -d postgres -c "\copy osm.tateyama_bld from './data/202405/osm/osm_building_tateyama.tsv' delimiter E'\t' csv;"
psql -U postgres -d postgres -c "\copy osm.hamamatsu_bld from './data/202405/osm/osm_building_hamamatsu.tsv' delimiter E'\t' csv;"
psql -U postgres -d postgres -c "\copy osm.kumamoto_bld from './data/202405/osm/osm_building_kumamoto.tsv' delimiter E'\t' csv;"
psql -U postgres -d postgres -c "\copy osm.higashi_hiroshima_bld from './data/202405/osm/osm_building_higashi_hiroshima.tsv' delimiter E'\t' csv;"
psql -U postgres -d postgres -c "\copy osm.morioka_bld from './data/202405/osm/osm_building_morioka.tsv' delimiter E'\t' csv;"

