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
output="./tsv/omf_place_cnt.tsv"
rm $output

# export header
psql -d postgres -c "\copy ( 
    select
        '$city' as city,
        count(ogc_fid) as ogc_fid_cnt,
        count(wkb_geometry) as wkb_geometry_cnt,
        count(id) as id_cnt,
        count(version) as version_cnt,
        count(update_time) as update_time_cnt,
        count(sources) as sources_cnt,
        count(names) as names_cnt,
        count(categories) as categories_cnt,
        count(confidence) as confidence_cnt,
        count(websites) as websites_cnt,
        count(emails) as emails_cnt,
        count(socials) as socials_cnt,
        count(phones) as phones_cnt,
        count(addresses) as addresses_cnt,
        count(brand) as brand_cnt
    from 
        omf.${city}_place
    where id is null
    ) to 'omf.tmp'  
    with csv header delimiter E'\t';"
cat omf.tmp >> "$output"

# export data
for city in "${cities[@]}"; do
    echo $city
    psql -d postgres -c "\copy ( 
        select
            '$city' as city,
            count(ogc_fid) as ogc_fid_cnt,
            count(wkb_geometry) as wkb_geometry_cnt,
            count(id) as id_cnt,
            count(version) as version_cnt,
            count(update_time) as update_time_cnt,
            count(sources) as sources_cnt,
            count(names) as names_cnt,
            count(categories) as categories_cnt,
            count(confidence) as confidence_cnt,
            count(websites) as websites_cnt,
            count(emails) as emails_cnt,
            count(socials) as socials_cnt,
            count(phones) as phones_cnt,
            count(addresses) as addresses_cnt,
            count(brand) as brand_cnt
        from 
            omf.${city}_place
        ) to 'omf.tmp'  
        with csv delimiter E'\t';"
    cat omf.tmp >> "$output"
done

# rm tmp
rm omf.tmp

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"