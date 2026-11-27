#!/usr/bin/env bash
# gput.sh: copy local files or directories to gaint through the tunnel, with retries and an md5 check.
# usage: gput.sh <local path> <remote path>      (a directory is sent as a tar stream and unpacked INTO <remote path>)
# Refuses remote paths outside /home/noob/work/el_bench, /home/noob/work/bq, /home/noob/work/bench_*, /home/noob/work/s2c/open .
set -u
src=$1; dst=$2
case "$dst" in
  /home/noob/work/el_bench|/home/noob/work/el_bench/*|/home/noob/work/bq|/home/noob/work/bq/*|/home/noob/work/bench_*|/home/noob/work/s2c/open|/home/noob/work/s2c/open/*) ;;
  *) echo "gput: refused remote path $dst" >&2; exit 2;;
esac
# On gaint itself (hostname giant) this is a local copy with the same path rule and an md5 check.
if [ "$(hostname)" = giant ]; then
  if [ -d "$src" ]; then
    mkdir -p "$dst" && tar -C "$src" -cf - . | tar -C "$dst" -xf - && { echo "gput ok local-dir $dst"; exit 0; }
  else
    mkdir -p "$(dirname "$dst")" && cp "$src" "$dst" && [ "$(md5sum < "$src")" = "$(md5sum < "$dst")" ] && { echo "gput ok $(md5sum "$dst" | cut -d' ' -f1) $dst"; exit 0; }
  fi
  echo "gput: local copy failed ($src -> $dst)" >&2; exit 255
fi
tries=${GSSH_TRIES:-6}
hosts=("noob@172.18.22.20" "ssh.noobsurd.info")
for i in $(seq 1 "$tries"); do
  host=${hosts[$(( (i - 1) % 2 ))]}
  ct=25; [ "$host" = "noob@172.18.22.20" ] && ct=6
  if [ -d "$src" ]; then
    lsum=$(tar -C "$src" -cf - . | md5sum | cut -d' ' -f1)
    rsum=$(tar -C "$src" -cf - . | ssh -o BatchMode=yes -o ConnectTimeout=$ct "$host" "mkdir -p '$dst' && tee /tmp/gput_\$\$.tar | md5sum | cut -d' ' -f1; tar -C '$dst' -xf /tmp/gput_\$\$.tar; rm -f /tmp/gput_\$\$.tar" 2>/dev/null | tail -1)
  else
    lsum=$(md5sum "$src" | cut -d' ' -f1)
    rsum=$(ssh -o BatchMode=yes -o ConnectTimeout=$ct "$host" "mkdir -p \"\$(dirname '$dst')\" && cat > '$dst' && md5sum '$dst' | cut -d' ' -f1" < "$src" 2>/dev/null | tail -1)
  fi
  if [ -n "$rsum" ] && [ "$lsum" = "$rsum" ]; then echo "gput ok $lsum $dst"; exit 0; fi
  sleep $((i * 3))
done
echo "gput: failed after $tries attempts ($src -> $dst)" >&2; exit 255
