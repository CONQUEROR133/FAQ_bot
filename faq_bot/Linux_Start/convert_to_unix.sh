#!/bin/bash

# Script to convert line endings to Unix format (LF)
# This is useful when preparing files on Windows for upload to Linux VPS

echo "Converting line endings to Unix format..."

# Convert all .sh files in the current directory
for file in *.sh; do
    if [ -f "$file" ]; then
        echo "Converting $file..."
        sed -i 's/\r$//' "$file"
    fi
done

echo "Line ending conversion completed!"
echo "All .sh files are now in Unix format and ready for VPS deployment."