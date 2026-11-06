#!/bin/bash
# usage: write_manifest.sh <set_dir>   -> <set_dir>/MANIFEST.md5 (md5sum format, paths relative to set_dir), run from outside the data dir
set -euo pipefail
d="$1"; out="$d/MANIFEST.md5"; tmp=$(mktemp)
find "$d" -type f ! -name MANIFEST.md5 ! -name '*.part' -print0 | sort -z | xargs -0 md5sum | sed "s#  $d/#  #" > "$tmp"
mv "$tmp" "$out"; echo "$(wc -l < "$out") files in $out"
