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

# create data directory
DATA_DIR="$SCRIPT_DIR/data/$RELEASE_VERSION/overturemaps/"
mkdir -p $DATA_DIR

# change resource in "git@github.com:OvertureMaps/overturemaps-py.git" to change 
cd "${SCRIPT_DIR}/overturemaps-py"
before="overturemaps-us-west-2/release/.*/theme"
after="overturemaps-us-west-2/release/$RELEASE_VERSION/theme"
sed -i '' "s|$before|$after|g" "${SCRIPT_DIR}/overturemaps-py/overturemaps/core.py"

# Tokyo
poetry run overturemaps download --bbox=139.74609375,35.67514744,139.83398438,35.74651226 -f geojson --type=$TYPE -o "$DATA_DIR/tokyo_$TYPE.geojson"

# Hamamatsu
poetry run overturemaps download --bbox=137.63671875,34.66935855,137.72460938,34.7416125 -f geojson --type=$TYPE -o "$DATA_DIR/hamamatsu_$TYPE.geojson"

# Tateyama
poetry run overturemaps download --bbox=139.83398438,34.95799531,139.921875,35.02999637 -f geojson --type=$TYPE -o "$DATA_DIR/tateyama_$TYPE.geojson"

# Kumamoto
poetry run overturemaps download --bbox=130.68726409,32.72948989,130.77515472,32.80174385 -f geojson --type=$TYPE -o "$DATA_DIR/kumamoto_$TYPE.geojson"

# Higashi_hiroshima
poetry run overturemaps download --bbox=132.69418348,34.38622724,132.7820741,34.45848119 -f geojson --type=$TYPE -o "$DATA_DIR/higashi_hiroshima_$TYPE.geojson"

# Morioka
poetry run overturemaps download --bbox=141.07765453,39.6823863,141.16554516,39.75375112 -f geojson --type=$TYPE -o "$DATA_DIR/morioka_$TYPE.geojson"

# Display the measurement time.
time=$SECONDS
((sec=time%60, min=(time%3600)/60, hrs=time/3600))
timestamp=$(printf "%d:%02d:%02d" "$hrs" "$min" "$sec")
echo "Processing time is $timestamp"

exit 0