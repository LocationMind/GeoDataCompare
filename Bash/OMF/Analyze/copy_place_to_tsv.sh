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
  psql -d postgres -c "\copy ( 
    select
        ogc_fid,
        ST_AsText(wkb_geometry) as wkb_geometry,
        id,
        version,
        update_time,
        sources::text,
        names::text,
        categories::text,
        confidence,
        websites,
        emails,
        socials,
        phones,
        addresses::text,
        brand::text
    from
        omf.${city}_place
    ) to './tsv/omf_place_$city.tsv'  
    with csv delimiter E'\t';"
done

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"

exit 0