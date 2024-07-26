#!/bin/bash

# Initialize the command in seconds.
SECONDS=0

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# get command line arguments
if [ -z "$1" ]; then
  echo -e "Write Type in first argument.\n e.g. [building, place]"
  exit 1
fi
if [ -z "$2" ]; then
  echo -e "Write Release Version in second argument.\nYou could check list of versions:"
  aws s3 ls s3://overturemaps-us-west-2/release/ --region us-west-2 --no-sign-request
  exit 1
fi
TYPE=$1 # e.g. [building, place]
RELEASE_VERSION=$2 # e.g. [2024-07-22.0, 2024-06-13-beta.1]

# define data dir
DATA_DIR="$SCRIPT_DIR/data/$RELEASE_VERSION/overturemaps/"

# create schema
psql -U postgres -d postgres -c "create schema omf;"

# create table
psql -U postgres -d postgres -f ./create_tables_$TYPE.sql

# Tokyo
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln omf.tokyo_$TYPE -nlt multipolygon $DATA_DIR/tokyo_$TYPE.geojson

# Hamamatsu
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln omf.hamamatsu_$TYPE -nlt multipolygon $DATA_DIR/hamamatsu_$TYPE.geojson

# Tateyama
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln omf.tateyama_$TYPE -nlt multipolygon $DATA_DIR/tateyama_$TYPE.geojson

# Kumamoto
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln omf.kumamoto_$TYPE -nlt multipolygon $DATA_DIR/kumamoto_$TYPE.geojson

# Higashi_hiroshima
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln omf.higashi_hiroshima_$TYPE -nlt multipolygon $DATA_DIR/higashi_hiroshima_$TYPE.geojson

# Morioka
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres dbname=postgres" -nln omf.morioka_$TYPE -nlt multipolygon $DATA_DIR/morioka_$TYPE.geojson


# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"
