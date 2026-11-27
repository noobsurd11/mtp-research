#!/usr/bin/env bash
# gget.sh: copy one remote file from gaint to a local path, with retries and an md5 check.
# usage: gget.sh <remote file> <local path>
set -u
src=$1; dst=$2
# On gaint itself (hostname giant) this is a local copy.
if [ "$(hostname)" = giant ]; then
  cp "$src" "$dst.part" && mv "$dst.part" "$dst" && { echo "gget ok $(md5sum "$dst" | cut -d' ' -f1) $dst"; exit 0; }
  echo "gget: local copy failed ($src)" >&2; exit 255
fi
tries=${GSSH_TRIES:-6}
hosts=("noob@172.18.22.20" "ssh.noobsurd.info")
for i in $(seq 1 "$tries"); do
  host=${hosts[$(( (i - 1) % 2 ))]}
  ct=25; [ "$host" = "noob@172.18.22.20" ] && ct=6
  rsum=$(ssh -n -o BatchMode=yes -o ConnectTimeout=$ct "$host" "md5sum '$src' | cut -d' ' -f1" 2>/dev/null | tail -1)
  if [ -n "$rsum" ] && ssh -n -o BatchMode=yes -o ConnectTimeout=$ct "$host" "cat '$src'" > "$dst.part" 2>/dev/null; then
    lsum=$(md5sum "$dst.part" | cut -d' ' -f1)
    if [ "$lsum" = "$rsum" ]; then mv "$dst.part" "$dst"; echo "gget ok $lsum $dst"; exit 0; fi
  fi
  sleep $((i * 3))
done
rm -f "$dst.part"; echo "gget: failed after $tries attempts ($src)" >&2; exit 255
