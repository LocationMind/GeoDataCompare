#!/bin/bash

### Preprocessing ###

# Initialize the command in seconds.
SECONDS=0

# postgres
POSTGRES_USER=postgres
POSTGRES_DATABASE=postgres

# get current date
CURRENT_DATE=$(date +"%Y%m%d")

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# get command line arguments
if [ -z "$1" ]; then
  echo -e "Write Type in first argument.\n e.g. [building, poi]"
  exit 1
fi
if [ -z "$2" ]; then
  $2 = $CURRENT_DATE
  exit 1
fi
TYPE=$1 # e.g. [building, poi]
YYYYMMDD=$2 # e.g. [20240729]

# define data dir
DATA_DIR="$SCRIPT_DIR/data/$YYYYMMDD"
if [ ! -d "$DATA_DIR" ] ; then
  echo -e "DATA_DIR was empty: $DATA_DIR"
  echo -e "Write Type in second argument.\n e.g. [YYYYMMDD]"
fi

# pbf file
PBF_FILE="$DATA_DIR/japan-latest.osm.pbf"
if [ ! -f "$PBF_FILE" ] ; then
  echo -e "There is no pbf file. Dowload at first!"
  exit 1
fi

# shp file
SHP_FILE="$SCRIPT_DIR/shape/bbox_list.shp"

### Main ###

# create database, and drop $TYPE table made by osm2pgsql
psql -U $POSTGRES_USER -d $POSTGRES_DATABASE -c "create schema osm;"
psql -U $POSTGRES_USER -d $POSTGRES_DATABASE -c "drop table if exists osm.$TYPE;"

# import shape to database
shp2pgsql -I -s 4326 $SHP_FILE osm.shape | psql -d $POSTGRES_DATABASE -U $POSTGRES_USER

# import pbf file to database
osm2pgsql -d $POSTGRES_DATABASE --schema osm -O flex -S "$SCRIPT_DIR/lua/$TYPE.lua" -E 4326 "$PBF_FILE"

# create table in each cities
psql -U postgres -d postgres -f "$SCRIPT_DIR/sql/create_tables_$TYPE.sql"

# insert data about each cities
psql -U postgres -d postgres -f "$SCRIPT_DIR/sql/clip_select_insert_$TYPE.sql"

### Postprocessing ###

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"