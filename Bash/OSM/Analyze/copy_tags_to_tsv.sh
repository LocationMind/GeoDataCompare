#!/bin/bash

sql="\copy (select distinct building from building_tag order by building) to '~/buildings/tsv/building_distinct_tag.tsv' with csv delimiter E'\t';"
psql -d shimazaki -U postgres -c "$sql"
