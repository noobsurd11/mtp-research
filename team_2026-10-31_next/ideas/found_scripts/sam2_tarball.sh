#!/bin/bash
# found, 31 Oct 2026: Meta sam2 @ 2b90b9f via one codeload tarball into a NEW isolated dir; keep only sam2/, LICENSE*, setup.py,
# pyproject.toml; verify every kept file's git blob sha1 against the GitHub tree list (LIST.tsv). Nothing is executed from it here.
set -u
SHA=2b90b9f5ceec907a1c18123530e92e794ad901a4
DL=/home/noob/work/venv_sam2_src/dl_$SHA; DST=/home/noob/work/venv_sam2_src/sam2_${SHA:0:7}
rm -rf "$DST" "$DL"; mkdir -p "$DL" "$DST"
curl -L -f -s -S -m 600 -o "$DL/sam2.tar.gz" "https://codeload.github.com/facebookresearch/sam2/tar.gz/$SHA" || { echo "DOWNLOAD FAIL"; exit 1; }
echo "tarball bytes $(stat -c %s "$DL/sam2.tar.gz") sha256 $(sha256sum "$DL/sam2.tar.gz" | cut -d' ' -f1)"
tar -xzf "$DL/sam2.tar.gz" -C "$DL" --wildcards "sam2-$SHA/sam2/*" "sam2-$SHA/LICENSE" "sam2-$SHA/LICENSE_cctorch" "sam2-$SHA/setup.py" "sam2-$SHA/pyproject.toml"
cp -r "$DL/sam2-$SHA/." "$DST/"
bad=0; n=0
while IFS=$'\t' read -r path sha size; do
  f="$DST/$path"; [ -f "$f" ] || { echo "MISSING $path"; bad=$((bad+1)); continue; }
  got=$( (printf 'blob %d\0' "$(stat -c %s "$f")"; cat "$f") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$sha" ] || { echo "SHA MISMATCH $path"; bad=$((bad+1)); }
  n=$((n+1))
done < "$1"
extra=$(find "$DST" -type f | wc -l)
echo "verified $n files, bad $bad, files in dst $extra, bytes $(du -sb "$DST" | cut -f1)"
rm -rf "$DL"
