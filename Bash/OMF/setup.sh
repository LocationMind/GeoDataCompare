#!/bin/bash

# move to working directory
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd "${SCRIPT_DIR}"

# pip install
pip install -r "$SCRIPT_DIR/requirements.txt"

# get latest resource
OMF_DIR="$SCRIPT_DIR/overturemaps-py"
if [ -d "$OMF_DIR" ]; then
  cd "$OMF_DIR"
  git checkout .
  git pull origin main
  cd -
else
  git clone git@github.com:OvertureMaps/overturemaps-py.git
fi

exit 0