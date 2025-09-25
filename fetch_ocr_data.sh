#!/bin/bash

set -e

# Configuration
MONGODB_URI="${MONGODB_URI:-Your MongoDB connection string}"
DATA_PATH="${DATA_PATH:-./data}"

# Set up data directories
DATA_PATH=$(realpath "$DATA_PATH") # convert to absolute paths
mkdir -p "$DATA_PATH"
CURR_DIR=$(pwd)


# Set up the ebl-api submodule
if [ ! -d "ebl-api" ] || [ ! -f ".gitmodules" ] || ! grep -q "ebl-api" ".gitmodules"; then
    git submodule add https://github.com/ElectronicBabylonianLiterature/ebl-api.git
fi

git submodule update --init --recursive
git submodule set-branch --branch re-train-ocr-model ebl-api
git submodule update --remote


# Fetch all annotations and images from EBL-API
OUTPUT_ANNOTATIONS="$DATA_PATH/annotations/annotations"
OUTPUT_IMAGES="$DATA_PATH/annotations/imgs"
mkdir -p "$OUTPUT_ANNOTATIONS"
mkdir -p "$OUTPUT_IMAGES"
EBL_PATH="./ebl-api"

cmd=(python -m ebl.fragmentarium.retrieve_annotations)

cmd+=(--output_annotations "$OUTPUT_ANNOTATIONS")
cmd+=(--output_imgs "$OUTPUT_IMAGES")

export MONGODB_URI
export MONGODB_DB="ebl"

echo "Starting to fetch all annotations and images from EBL-API"
echo "command: ${cmd[*]}"
cd "$EBL_PATH"
"${cmd[@]}"

# Run filtering
cd "$CURR_DIR"
export MONGODB_CONNECTION="$MONGODB_URI"
export ANNOTATIONS_DIRECTORY="$OUTPUT_ANNOTATIONS"
echo "=== Starting to filter annotations ==="
rm -f valid_fragments.json
python -m cuneiform_ocr_data.filter_annotations

# Verify that valid_fragments.json was created and is not empty
if [ ! -f "valid_fragments.json" ]; then
    echo "Error: valid_fragments.json was not created by filter_annotations"
    exit 1
fi

if [ ! -s "valid_fragments.json" ]; then
    echo "Error: valid_fragments.json is empty"
    exit 1
fi

echo "Successfully created valid_fragments.json with $(wc -l < valid_fragments.json) lines"

# Fetch with filtered list
echo "=== Copy valid_fragments.json to EBL annotations ==="
VALID_ANNO_PATH="$EBL_PATH/ebl/fragmentarium/annotations.json"
# Create new annotations.json with valid_fragments list under "finished" key
echo '{"finished":' > "$VALID_ANNO_PATH"
cat valid_fragments.json >> "$VALID_ANNO_PATH"
echo '}' >> "$VALID_ANNO_PATH"
OUTPUT_ANNOTATIONS_FILTERED="$DATA_PATH/filtered_annotations/annotations"
OUTPUT_IMAGES_FILTERED="$DATA_PATH/filtered_annotations/imgs"
mkdir -p "$OUTPUT_ANNOTATIONS_FILTERED"
mkdir -p "$OUTPUT_IMAGES_FILTERED"

echo "=== Starting to fetch filtered annotations and images from EBL-API ==="
cd "$EBL_PATH"
export MONGODB_URI
export MONGODB_DB="ebl"
python -m ebl.fragmentarium.retrieve_annotations --output_annotations "$OUTPUT_ANNOTATIONS_FILTERED" --output_imgs "$OUTPUT_IMAGES_FILTERED" --filter "finished"


# Clean submodule changes
echo "=== Cleaning up ==="
git checkout -- .
cd "$CURR_DIR"
rm valid_fragments.json