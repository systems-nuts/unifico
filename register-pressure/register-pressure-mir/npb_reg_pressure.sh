#!/bin/bash

directory="npb_mirs"

file_names=$(ls -1 "$directory")

for file in $file_names; do
  python parse_pressure_sets.py -i npb_mirs/"$file"
done
