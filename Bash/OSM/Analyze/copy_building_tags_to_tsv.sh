#!/bin/bash

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# set config
source config.sh

sql="\copy (
  select 
    distinct building 
  from osm.building 
  order by building
  ) to '$SCRIPT_DIR/tsv/osm_building_distinct_tag.tsv' 
  with csv delimiter E'\t';"
psql -d $POSTGRES_DATABASE -U $POSTGRES_USER -c "$sql"
