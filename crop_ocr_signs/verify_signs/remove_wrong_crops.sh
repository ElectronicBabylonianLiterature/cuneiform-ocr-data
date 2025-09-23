#!/bin/bash


folderA="$1"
folderB="$2"

for file in "$folderA"/*; do
  filename=$(basename "$file")
  if [[ ! -e "$folderB/$filename" ]]; then
    echo "Removing $file (not in $folderB)"
    rm -rf "$file"
  fi
done