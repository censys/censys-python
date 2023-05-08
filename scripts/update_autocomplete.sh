#!/usr/bin/env bash

update_autocomplete() {
    echo "Updating autocomplete data for $1..."
    # Write a temporary file to avoid corrupting the original if the download fails
    tmp_file=$(mktemp)
    curl "https://search.censys.io/static/data/autocomplete-$1.json" -s -o "$tmp_file" && echo "" >> "$tmp_file"
    mv "$tmp_file" "censys/cli/data/$1_autocomplete.json"
}

update_autocomplete hosts
update_autocomplete certificates
