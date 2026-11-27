#!/bin/bash
# c3x: checks before (and between) the launch steps (run by the LEAD on gaint) = the form of harness/c3lane/c3lane_check.sh.
# READ ONLY on both machines. Lines start with OK, FAIL, SKIP or INFO; the last line counts them.
# Env: X (full c3x commit, after the commit), XB (/tmp/noob_el/bench_<7 hex>, after the deploy), IO (default
#   /home/noob/work/bench_c3_io/c3x; its rendered.txt / render_cmp.out are used after `render`).
set -u
X=${X:-}; XB=${XB:-}; IO=${IO:-/home/noob/work/bench_c3_io/c3x}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
WT=/home/noob/work/bench_wt_c3s; RF=/home/noob/work/bench_wt_final; BQ=/tmp/noob_el/bench_q; B89=/tmp/noob_el/bench_89b9ea5
BASE=852ed5c411b967d7ea758ef2cd5dbe70ae4e50a1; TREE=c860f1bc243ff5262f8c23ffb1e551cfaea5ea79
P=/home/noob/work/el-fault-detection/.venv/bin/python
C(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$1"; }
NO=0; NFL=0; NS=0
ok(){ NO=$((NO+1)); echo "OK   $*"; }; bad(){ NFL=$((NFL+1)); echo "FAIL $*"; }; skip(){ NS=$((NS+1)); echo "SKIP $*"; }
ck(){ if eval "$2"; then ok "$1"; else bad "$1"; fi; }
echo "[$(date '+%F %T')] c3x check (X '${X:-none}', XB '${XB:-none}', IO $IO)"
echo "--- 1 code"
ck "bench_wt_final at 89b9ea5, no tracked change (training, dump and read code of every cv5v3 run)" '[ "$(git -C $RF rev-parse --short HEAD)" = 89b9ea5 ] && [ "$(git -C $RF status --porcelain -uno | wc -l)" = 0 ]'
ck "c3x.patch applies to a fresh archive of 852ed5c and gives the three pinned files; 7 card tests pass there" 'x=$(mktemp -d) && git -C $WT archive $BASE | tar -x -C $x && (cd $x && git apply $HERE/c3x.patch && echo "98f152de3ea7f8c88e892162e07b4450  bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
d7b207089f6cfeb484ca9ef96f734786  bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml
501a6f95f90a3186401814f769eadf89  tests/test_bench_c3x_card.py" | md5sum -c --quiet - && CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_c3x_card.py 2>&1 | tail -1 | grep -q "^7 passed"); rc=$?; rm -rf $x; [ $rc = 0 ]'
if [ -z "$X" ]; then skip "no X given: the c3x commit is not made yet"; ck "worktree $WT on bench_c3s at 852ed5c, no tracked change" '[ "$(git -C $WT rev-parse HEAD)" = $BASE ] && [ "$(git -C $WT status --porcelain -uno | wc -l)" = 0 ]'
else
  ck "X is one commit on 852ed5c with the tested tree $TREE; worktree $WT at X, no tracked change" '[ "$(git -C $WT rev-parse $X^)" = $BASE ] && [ "$(git -C $WT rev-parse $X^{tree})" = $TREE ] && [ "$(git -C $WT rev-parse HEAD)" = $X ] && [ "$(git -C $WT status --porcelain -uno | wc -l)" = 0 ]'
  ck "code proof (c3x_codeproof.sh): 0 FAIL" 'bash $HERE/c3x_codeproof.sh $X > /tmp/c3x_check_codeproof.$$ 2>&1; r=$?; tail -1 /tmp/c3x_check_codeproof.$$ | sed "s/^/     /"; rm -f /tmp/c3x_check_codeproof.$$; [ $r = 0 ]'
fi
if [ -z "$XB" ]; then skip "no XB given: the c3x commit is not deployed yet"
else q=$(C "cd $XB && echo \"\$(cat REVISION)\"; md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; md5sum < bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml | cut -c1-32; md5sum < bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml | cut -c1-32; md5sum < bench/q/cv02/cq.sh | cut -c1-32; diff <(grep -v '  REVISION\$' $B89/CODE.md5) <(grep -v '  REVISION\$' CODE.md5) | grep '^[<>]' | awk '{print \$1 \$3}' | LC_ALL=C sort | tr '\n' ' '") || q=""
  ck "XB $XB: REVISION = X, CODE.md5 OK, card 98f152de, cv02 variant d7b20708, cq.sh 14d33b80; against bench_89b9ea5 only the 9 paths" '[ "$(echo $q)" = "$X CODE_OK 98f152de3ea7f8c88e892162e07b4450 d7b207089f6cfeb484ca9ef96f734786 14d33b80b17b116ec68941f1b40c5951 <bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <bench/q/cv02/slim_ckpt.py >bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml >bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml >bench/methods_cv02/swad_const_pf_v11.yaml >bench/q/cv02/cq.sh >bench/q/cv02/cq_rescue.sh >bench/q/cv02/cq_setup.sh >bench/q/cv02/slim_ckpt.py >tests/test_bench_c3x_card.py >tests/test_bench_cq_readouts.py" ]'
  w=$(C "md5sum < /tmp/noob_el/cache/hf/hub/models--timm--hrnet_w18.ms_aug_in1k/snapshots/7e2c5583769f54514fd87e3ba9de408e33eaba0f/model.safetensors | cut -c1-32")
  ck "HRNet encoder weights file on cv02 = the card's md5 e6bb005d" '[ "$w" = e6bb005ddbe1b52bde05618fc6b4b8e3 ]'
fi
echo "--- 2 roots and names"
r=$(C "cd /tmp/noob_el/bench_data_v3b/roots && md5sum -c --quiet ROOTS_cv5v3_v11.md5 > /dev/null 2>&1 && echo ROOTS_OK; for k in 0 1 2 3 4; do d=cv5v3_v11_f\$k; (cd \$d && md5sum -c --quiet SPLITS.md5 > /dev/null 2>&1 && md5sum -c --quiet DATA_MANIFEST.md5 > /dev/null 2>&1 && cmp -s splits/val.txt splits/test.txt && echo \"\$d \$(grep -c . splits/train.txt)/\$(grep -c . splits/val.txt) \$(cat splits/train.txt splits/val.txt | md5sum | cut -c1-8)\"); done") || r=""
g=$(for k in 0 1 2 3 4; do d=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f$k; echo "cv5v3_v11_f$k $(grep -c . $d/splits/train.txt)/$(grep -c . $d/splits/val.txt) $(cat $d/splits/train.txt $d/splits/val.txt | md5sum | cut -c1-8)"; done)
ck "cv02 cv5v3 roots: ROOTS, SPLITS, DATA_MANIFEST check, test = val, 425/107 422/110 429/103 431/101 421/111, lists equal to gaint's" '[ "$(echo "$r" | head -1)" = ROOTS_OK ] && [ "$(echo "$r" | tail -n +2)" = "$g" ] && [ "$(echo "$g" | cut -d" " -f2 | tr "\n" " ")" = "425/107 422/110 429/103 431/101 421/111 " ]'
h=$(C "for k in 0 1 2 3 4; do for s in 5 6 7 8 9; do n=c3x_hrnet_swad_v11_f\${k}_s\$s; for b in /tmp/noob_el/bench_*/; do [ -e \$b/experiments/\$n ] || [ -e \$b/runs/\$n ] && echo \"\$n in \$b\"; done; done; done; ls -d $BQ/c3x 2>/dev/null; true")
ck "no c3x name on cv02 (any deploy's experiments or runs)$( [ -n "$(echo "$h" | grep "bench_q/c3x")" ] && echo "; queue dir c3x exists (placed)")" '[ -z "$(echo "$h" | grep -v "bench_q/c3x$")" ] || [ -n "$(C "test -s $BQ/c3x/launch.log && echo armed")" ]'
ck "no c3x run in a gaint relay dir other than bench_relay/c3x; relay patterns ^c3_, ^c3h_, ^c3s_ do not match c3x_" '[ -z "$(ls -d /home/noob/work/bench_relay/*/c3x_* 2>/dev/null | grep -v "/bench_relay/c3x/")" ] && ! echo c3x_hrnet_swad_v11_f0_s5 | grep -qE "^c3_|^c3h_|^c3s_|^r2_"'
if [ -s $IO/render_cmp.out ]; then ck "render (IO): $(tail -1 $IO/render_cmp.out)" 'grep -q "render compare: 0 FAIL" $IO/render_cmp.out'; else skip "no render in $IO yet"; fi
echo "--- 3 queues on cv02"
s=$(C "for q in $BQ/*/; do n=\$(basename \$q); p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; m=\$(cat \$q/MAXC 2>/dev/null); echo \"\$n MAXC \${m:-16} LPG \$(cat \$q/LPG 2>/dev/null) dispatched \$(grep -c 'cv02 q: all jobs dispatched' \$q/launch.log) fixture_only \$([ -s \$q/jobs.txt ] && [ \"\$(cut -d'|' -f9 \$q/jobs.txt | sort -u)\" = --fixture ] && echo 1 || echo 0) share \$(cat \$q/SHARE_TRAIN 2>/dev/null)/\$(cat \$q/SHARE_DUMP 2>/dev/null) started \$(ls \$q/pids/*.gpu 2>/dev/null | wc -l) of \$(grep -c . \$q/jobs.txt)\"; done; echo ---; for q in $BQ/*/; do for f in \$q/pids/*.gpu; do [ -e \$f ] || continue; n=\$(basename \$f .gpu); [ -e \$q/pids/\$n.end ] || [ -e \$q/pids/\$n.rc ] || case \$n in dump_*) ;; *) echo \"train \$(cat \$f) \$n\";; esac; done; done")
echo "$s" | sed 's/^/     /'
live=$(echo "$s" | sed '/^---$/,$d'); can=$(echo "$live" | awk '$3 != 0 && $7 == 0 && $9 == 0 {print $1}' | tr '\n' ' ')
ck "live queues that can still start training: '$can' (at most one)" '[ "$(echo $can | wc -w)" -le 1 ]'
if echo "$live" | grep -q "^c3all3 .* dispatched 1 "; then ok "c3all3 has dispatched all its jobs: c3x may be armed"; else echo "INFO c3all3 has NOT dispatched all its jobs: c3x must not be armed yet ($(echo "$live" | grep "^c3all3 " | grep -o "started.*"))"; fi
ck "c3all, c3all2, c3base, c3hrnet frozen (MAXC 0) where live" '[ -z "$(echo "$live" | awk "(\$1 == \"c3all\" || \$1 == \"c3all2\" || \$1 == \"c3base\" || \$1 == \"c3hrnet\") && \$3 != 0")" ]'
if echo "$live" | grep -q "^c3x "; then ck "c3x runs with MAXC 8, LPG 1, SHARE_TRAIN 20480 and SHARE_DUMP 10240" 'echo "$live" | grep -q "^c3x MAXC 8 LPG 1 .* share 20480/10240 "'; else skip "c3x is not armed yet"; fi
ck "no GPU holds two training runs of ours (open training lanes of all queues)" '[ -z "$(echo "$s" | sed -n "/^---$/,\$p" | awk "/^train /{print \$2}" | sort | uniq -d)" ]'
echo "--- 4 disk and guards"
t=$(C "df --output=avail -BG /tmp | tail -1 | tr -dc 0-9; echo; for g in bench_diskguard3 bench_diskguard4; do tmux has-session -t \"=\$g\" 2>/dev/null && echo \"\$g up\" || echo \"\$g down\"; done; { md5sum < $BQ/diskguard4.sh; } 2>/dev/null | cut -c1-32; ls $BQ/*/HOLD 2>/dev/null | wc -l")
cf=$(echo "$t" | sed -n 1p); echo "     cv02: free ${cf:-?} GB; $(echo "$t" | sed -n 2,3p | tr '\n' ' ')"
ck "cv02 disk guard 3 up (c3all3); no HOLD file" 'echo "$t" | grep -qx "bench_diskguard3 up" && [ "$(echo "$t" | tail -1)" = 0 ]'
if echo "$t" | grep -qx "bench_diskguard4 up"; then ck "cv02 disk guard 4 up with the reviewed script" '[ "$(echo "$t" | sed -n 4p)" = "$(md5sum < $HERE/diskguard4.sh | cut -c1-32)" ]'; else skip "disk guard 4 not started yet (step guard)"; fi
echo "INFO cv02 need for c3x (S): 25 runs x 1.03 GB that stay (latest 0.75 + best 0.08 + slim 0.17 + logs) + 3.3 GB of .swad dump dirs that stay + dumps in transit 8 x 0.27 + the 20 GB guard floor = 51 GB, plus about 1.2 GB per c3all3 run still training; free now ${cf:-?} GB. A disk guard HOLD stops new training starts and the dumps of finished runs"
gf=$(df --output=avail -BG /home/noob/work | tail -1 | tr -dc 0-9)
echo "INFO gaint need for c3x (S): 25 runs x 0.43 GB relayed (slim 2 sets 0.17 + two dumps without logp 0.26) = 11 GB, read cache < 1 GB; free now $gf GB"
ck "gaint free >= 25 GB (relay start floor)" '[ "$gf" -ge 25 ]'
for r in c3base c3hrnet c3swad c3x; do p=$(cat /home/noob/work/bench_relay/$r/relay.pid 2>/dev/null); if kill -0 "$p" 2>/dev/null; then ok "relay $r alive ($(ls /home/noob/work/bench_relay/$r/.ok | wc -l) runs relayed)"; else skip "relay $r is not running"; fi; done
tmux has-session -t "=bench_relayguard_c3x" 2>/dev/null && ok "gaint relay guard for c3x up" || skip "gaint relay guard for c3x not started yet"
echo "--- 5 files"
(cd $HERE && md5sum c3x.patch c3x_commit.sh c3x_codeproof.sh c3x_make_jobs.py c3x_rendercmp.py c3x_queue.sh diskguard4.sh c3x_relay.sh c3x_relayguard.sh c3x_check.sh run_read_c3x.sh c3x_verdict.py c3x_class_guard.py smoke/c3x_smoke.sh smoke/c3x_smoke_check.py smoke/smoke_c3x_hrnet_swad_path.yaml | sed 's/^/     /')
echo "[$(date '+%F %T')] C3X CHECK: $NO OK, $NFL FAIL, $NS SKIP"
[ $NFL = 0 ]
