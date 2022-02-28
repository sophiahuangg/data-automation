#!/usr/bin/bash

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# Download the X-13 file from the census bureau website
curl -o x13as_html.tar.gz https://www2.census.gov/software/x-13arima-seats/x13as/unix-linux/program-archives/x13as_html-v1-1-b58.tar.gz

# Extract
tar -xzvf x13as_html.tar.gz

# Add file extension to x13 file
mv x13as/x13as_html x13as/x13as_html.exe

x13aspath=$(get_abs_filename x13as/x13as_html.exe)

export x13as=$x13aspath