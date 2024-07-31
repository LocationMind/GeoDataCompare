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
output="./tsv/omf_source_in_place.tsv"
rm $output

for city in "${cities[@]}"; do
    echo $city
    psql -d postgres -c "\copy ( 
                        select 
                            dataset, cnt 
                        from (
                            select 'total' as dataset, count(*) as cnt from omf.${city}_place
                            union
                            select distinct source->>'dataset' as dataset, count(*) as cnt
                            from omf.${city}_place,
                            jsonb_array_elements(sources) as source
                            where source->>'dataset' is not null
                            group by source->>'dataset'
                        ) a
                        order by dataset desc
                    ) to 'omf_source_in_place.tmp'  
                    with csv delimiter E'\t';"
    echo "city  $city" >> "$output"
    cat omf_source_in_place.tmp >> "$output"
done

# rm tmp
rm omf_source_in_place.tmp

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"

exit 0