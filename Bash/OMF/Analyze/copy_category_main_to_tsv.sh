#!/bin/bash

# Initialize the command in seconds.
SECONDS=0

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# make tsv dir
mkdir -p "${SCRIPT_DIR}/tsv"

# analyze
cities=("tokyo" "tateyama" "hamamatsu" "higashi_hiroshima" "kumamoto" "morioka")

for city in "${cities[@]}"; do
  echo $city
  psql -d postgres -c "select 
                        count(categories->>'main') as category_cnt
                      from omf.${city}_place 
                      where categories->>'main' is not null"
  psql -d postgres -c "\copy ( 
                          select 
                            distinct categories->>'main' as main_category, 
                            count(*) as category_cnt
                          from omf.${city}_place 
                          where categories->>'main' is not null
                          group by categories->>'main'
                          order by category_cnt desc
                      ) to './tsv/omf_place_category_main_$city.tsv'  
                      with csv delimiter E'\t';"
done

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"
