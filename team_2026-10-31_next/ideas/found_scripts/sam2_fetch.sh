#!/bin/bash
# found, 31 Oct 2026: fetch Meta's sam2 python package (facebookresearch/sam2 @ 2b90b9f, Apache-2.0) file by file into a new,
# isolated source dir on gaint, verifying each file's git blob sha1. No pip, no build. Usage: bash sam2_fetch.sh LIST.tsv
set -u
SHA=2b90b9f5ceec907a1c18123530e92e794ad901a4
DST=/home/noob/work/venv_sam2_src/sam2_${SHA:0:7}
mkdir -p "$DST"; bad=0; n=0
while IFS=$'\t' read -r path sha size; do
  mkdir -p "$DST/$(dirname "$path")"
  curl -s -f -m 60 -o "$DST/$path" "https://raw.githubusercontent.com/facebookresearch/sam2/$SHA/$path" || { echo "FETCH FAIL $path"; bad=$((bad+1)); continue; }
  got=$( (printf 'blob %d\0' "$(stat -c %s "$DST/$path")"; cat "$DST/$path") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$sha" ] || { echo "SHA MISMATCH $path"; bad=$((bad+1)); }
  n=$((n+1))
done < "$1"
echo "fetched $n files, bad $bad, bytes $(du -sb "$DST" | cut -f1)"
