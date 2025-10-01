#!/bin/bash

# Usage: ./count_crops.sh signs_40k_ocr_no_partial_order N 
# where N is out of the total of 118 
# To add for outputting to file instead of terminal: > counts.txt

# Counts files in the first N subfolders of parent_dir (natural order, non-recursive)

parent="$1"
N="$2"

if [[ -z "$parent" || -z "$N" ]]; then
  echo "Usage: $0 parent_dir N"
  exit 1
fi

if [[ ! -d "$parent" ]]; then
  echo "Error: $parent is not a directory"
  exit 1
fi

count=0
folders=($(ls -d "$parent"/*/ 2>/dev/null | sort -V | head -n "$N"))

for folder in "${folders[@]}"; do
  num=$(find "$folder" -maxdepth 1 -type f -iname "*.jpg" | wc -l)
  echo "$(basename "$folder"): $num files"
  ((count+=num))
done

echo "Total files in first $N folders (natural order): $count"
