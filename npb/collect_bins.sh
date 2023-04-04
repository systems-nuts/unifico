#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

src_dir="$1"
dest_dir="$2"

# Check if the source and destination directories exist
if [ ! -d "$src_dir" ]; then
    echo "Source directory does not exist: $src_dir"
    exit 1
fi

if [ ! -d "$dest_dir" ]; then
    echo "Destination directory does not exist: $dest_dir"
    exit 1
fi

rm "$dest_dir"/*

# Find and copy .out files to the destination directory
find "$src_dir" -type f -name "*.out" -exec cp {} "$dest_dir" \;

echo "All .out files have been copied to $dest_dir"
