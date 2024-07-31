#!/bin/bash　-e

# Initialize the command in seconds.
SECONDS=0

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# get current date
CURRENT_DATE=$(date +"%Y%m%d")

# define data dir
DATA_DIR="$SCRIPT_DIR/data/$CURRENT_DATE"
mkdir -p "$DATA_DIR"

### Main ###

# download
curl -o "$DATA_DIR/japan-latest.osm.pbf" https://download.geofabrik.de/asia/japan-latest.osm.pbf

### Postprocessing ###

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"