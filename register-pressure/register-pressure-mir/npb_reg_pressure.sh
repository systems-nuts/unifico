#!/bin/bash

directory=$1

file_names=$(ls -1 "$directory")

for file in $file_names; do
  echo "$file"
  python parse_pressure_sets.py -i "$directory/$file"
done
