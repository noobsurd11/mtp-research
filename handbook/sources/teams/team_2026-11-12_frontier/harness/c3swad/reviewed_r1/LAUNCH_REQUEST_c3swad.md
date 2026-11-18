# Launch request c3swad: swad_const on cv5v3, 5 seeds x 5 folds = 25 runs + 50 dumps, cv02 (builder c3swad, 17 Nov 2026; first version 09:27 IST, md5 b207c499; second version f92728fd after the lead's rulings of 09:30; this version: ruling time corrected from 09:35 to 09:30, no other change)

Status: files built and tested on gaint CPU. **Nothing launched, nothing written on cv02, no commit, no worktree changed, nothing deleted.** E = measured by my own command today, S = judgement. Changed against b207c499 (section 11): default order (Q4), the carry rule (Q5), the GPU list of the cv02 dump test (Q10); the patch `cq_c3swad.patch` is unchanged (524a70e6).
Notation: G = run on gaint (noob). T = /home/yugma/mtp/research/team_2026-11-12_frontier, H = T/harness/c3swad (every file there; md5 in section 13). W = /home/noob/work/bench_wt_final (89b9ea5). B = cv02 /tmp/noob_el/bench_89b9ea5 (the live deploy, where PF trains). QC = cv02 deploy dir of the patched queue code (does not exist yet). cv02 was read only with `ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 '<read-only command>'`.

## 0. Three findings that change the brief (E)
1. **New queue code is needed. The patch is small and touches no training, dump or read code.** Two reasons:
   - `cq.sh` l.106-107 needs `bench/methods_cv02/<card>.yaml` for every job. The file for `swad_const_pf_v11` is not in 89b9ea5 (`ls W/bench/methods_cv02`, and the same `ls` on cv02 B: 12 files, none for swad). Arming a list with a swad line fails at once.
   - `cq.sh` dumps one readout per run: the card's `weights_key` (swad_bn), run id = name (l.117, no `--weights-key`). The second readout `swad` needs a second dump step.
2. **The read does not use `--logp`.** `grep -n logp W/scripts/bench_read_w1.py W/bench/w1read.py W/bench/crossfit_op.py` gives 0 lines; the read uses pred, oth, m_crack, p_crack, p_inact. `bench_infer.py` l.195 adds logp as one more array and changes nothing else. The screen itself was read from dumps without logp (0 of 161 lines in bq/w2a2/dump/jobs.txt carry `--logp`). A swad dump without logp is 133 MB, with it 937 MB. Both swad dumps are made with logp 0 (lead's ruling Q2).
3. **Names under `^c3_` would end the c3base relay early.** It runs with N 50 (`head -1 bench_relay/c3base/relay.log`) and stops when 50 `.ok` files exist (relay_w1c.sh l.46-47). 25 swad runs under `^c3_` would count, and the relay would stop with 25 runs missing. So the swad names start with `c3s_` and get a third relay.

## 1. Runs (recommendation)
- 25 runs: folds 0 to 4, seeds 5 to 9, card `bench/methods/swad_const_pf_v11.yaml` unchanged (md5 46fb5b02 in W, in bench_wt_w2 and on cv02 B; E). Roots `/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<k>`. Same machine, same deploy dir B and same training code as PF.
- Names `c3s_swad_v11_f<k>_s<s>`. Dump run ids: `<name>` (swad_bn, the card's weights_key) and `<name>.swad` (swad). Method dir `swad_const_pf_v11`.
- Job line (cq.sh format + the new 10th field): `c3s_swad_v11_f0_s5|bench/methods/swad_const_pf_v11.yaml|5|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0|0|11000|5262|0||swad`.
- No mixing with PF (E): PF arm = regex `c3_pf_v11_f[0-4]_s[5-9]` in method dir `house_r34_unetpp_pf_v11` (full match; other dir, other prefix). `^c3_` and `^c3h_` do not match `c3s_` (relays, `c3_f81_list.sh` removal lists). c3swad_check.sh section 5: no `c3s_*` name and no `swad_const_pf_v11` dump folder exists on cv02 or in a gaint relay.
- Training code (E): `git -C /home/noob/work/el_bench merge-base --is-ancestor c57508e 89b9ea5` true. `git -C /home/noob/work/el_bench diff --stat c57508e 89b9ea5 -- configs/base.yaml configs/supervised.yaml src/trainers/trainer.py src/trainers/weight_avg.py src/trainers/enc_probe.py scripts/bn_recalibration.py scripts/train.py bench/cards.py bench/methods/swad_const_pf_v11.yaml` is empty: constant scheduler, weight_avg (swad, ema_9998), bn_recal, enc_probe and the card are byte-equal. The only training file that differs between the two commits is `src/models/bench_models.py` (1 hunk: a pooling swap inside `build_bench_smp` for deeplab decoders; the card uses `model.name=smp_unetpp`). The card renders the same options at both commits for all 25 jobs (c3swad_check.sh: 25 of 25).

## 2. How the runs enter cv02 with one training queue (recommendation: way c)
- (a) Append to c3all's jobs file: **does not work.** `cq.sh` l.87 checks the jobs md5 and l.94 reads the list once (`mapfile`) at arming (E).
- (b) A successor armed after c3all's end line: works, but c3all keeps its own order (HOUSE s7 before PF s8) and swad would start only after all carried jobs. Not proposed.
- (c) **Freeze c3all (MAXC 0) and arm one merged successor `c3all2`**: its not-started lines, byte for byte, plus the 25 swad lines. As c3base and c3hrnet on 16 Nov.
- Where the merged queue runs (S): **B stays the live deploy. Only the queue scripts and `bench/methods_cv02` come from the new deploy QC** (`QC` variable of the patch). Reasons: PF, HOUSE and HRNet keep their deploy dir, their relays (`^c3_`, `^c3h_` read B/runs) and the skip of existing names (`cq.sh` l.184, `cq_setup.sh` l.22 refuse or skip a name that exists in B/experiments); swad trains in the same dir and from the same files as PF (manifest `train_code_revision` 89b9ea5 for both). Running everything from the new deploy would move the comparator rows to another dir and need new relays (not proposed).
- Never two queues that can start training: `c3swad_handover.sh arm` refuses unless every other live queue has MAXC 0 or has dispatched all its jobs (E dry test today: `CAN_START c3all` -> REFUSED; rows2 passes as `all dispatched`). In-flight runs of c3all finish under c3all; the new queue sees them as another user above 4 GB and never shares their GPU. One known case stays (accepted on 16 Nov): a c3all dump that waits for its GPU can lose it to the next start of the new queue for one cycle.
- Commands as files (section 9): `c3swad_handover.sh` steps freeze, build, render, place, guard, arm, status. `DRY=1` prints every cv02 write instead of running it.

## 3. Order and expected finish times (order = lead's ruling Q4)
- Order built by `c3swad_make_jobs.py` from what has not started at the freeze: **PF s8, s9; then swad s5 to s9; then HRNet s7 (rest), s8, s9; then HOUSE s7, s8, s9** (inside each arm seed, then fold, ascending). Reason (lead): the registered HRNet read needs HOUSE s7 to s9, which end last in both orders, so swad first moves the swad verdict earlier and nothing later. Preview at 09:36 (E, `evidence/preview_jobs_default_20261117_0936.txt`, md5 29388346): 62 lines = PF 10, swad 25, HRNet 12, HOUSE 15; the 37 carried lines are byte-identical to c3all's (c3all had started 33 of 70).
- Run times (E, cv02 c3all launch.log, start to "trained"): PF 64.0 min (n 13, 59 to 82), HOUSE 65.4 (n 10), HRNet 117.5 (n 7, 108 to 166); dump 1.7 min; wait from "trained" to dump start 3.3 min mean.
- swad run time on cv02 (S, scaled): gaint, same queue and two lanes: swad 99.3 min (n 5, seed 6), PF-recipe arms beside it 97.6 (jml_hard), 98.1 (rcs), 99.8 (ema) (E, bq/w2a2 and bq/w2a launch.log). Ratio 1.00 to 1.02. So about 65 min on cv02, range as PF. One lane cycle: PF or HOUSE 70 min, HRNet 124, swad 75 (two dumps and one more start gap).
- Work left with 37 carried lines: 85.5 lane-hours. Hours after arming (S; simple division, the last jobs of a block end up to one run later; lanes depend on the other users):

| Usable GPUs | PF s5-9 complete (leakage read) | swad complete (this read) | HRNet complete | all complete |
|---|---|---|---|---|
| 1 | 11.7 h | 42.9 h | 67.7 h | 85.5 h |
| 2 | 5.8 h | 21.5 h | 33.9 h | 42.7 h |
| 3 | 3.9 h | 14.3 h | 22.6 h | 28.5 h |

  If armed 17 Nov 14:00 IST (S): swad complete 19 Nov 08:55 (1 GPU), 18 Nov 11:30 (2), 18 Nov 04:20 (3); all complete 21 Nov 03:30, 19 Nov 08:40, 18 Nov 18:30.
- Other order, built but not the default (`BUILD_OPTS=--alternate`): swad and HRNet in turn by seed. swad complete after 67.7 / 33.9 / 22.6 h, HRNet after 55.2 / 27.6 / 18.4 h. Same line set as the default (E: `evidence/preview_jobs_20261117_0910.txt`, 9fa16c46, is this order for the 09:10 state).
- Until the handover c3all keeps its own order (next: HRNet s7 rest, HOUSE s7, then PF s8). Lead's ruling Q9: no reorder today; one handover only, after the review PASS. `MODE=reorder` (a successor without swad lines, unpatched queue code) stays in the script and is not used unless the lead says so.

## 4. Dumps and readouts: the patch (`H/cq_c3swad.patch`, md5 524a70e6, on 89b9ea5)
What it adds: a 10th jobs.txt field with further weights keys. After the usual dump, each key is dumped the same way (same GPU, same gate, same waits and live check) with `--run-id <name>.<key> --weights-key <key> --bench-run dump_<name>.<key>`. All dumps must end rc 0, else no slim and no RUN.md5. The slim checkpoint then keeps only the dumped keys. RUN.md5 also lists the further dump folders and `enc_probe.jsonl`, so the relay carries them with checksums. `QC` lets the queue code and the cv02 card variants come from another deploy dir while training and dumps run in B. A line without the field, and a queue without QC, behave as before.
Every changed line (old line numbers of 89b9ea5; the patch file is the exact text):

| File | Old lines | Change |
|---|---|---|
| bench/q/cv02/cq.sh (02d5ba5f -> 5222150b) | after 17 | +7 comment lines (the field, QC) |
| | 36 | `QC=${QC:-$B}; HERE=$QC/bench/q/cv02` (was `HERE=$B/...`) |
| | 49 | `deploy_ok` also checks QC/CODE.md5 when QC != B; new helper `dcmd2` (the further dump command, made from the job's own dump command) |
| | 88 | text of the deploy failure line |
| | 95 | `R2=()` (list of further dump lines) |
| | 97, 182 | `read` takes the 10th field `ro` |
| | 106 | cv02 variant path `$QC/bench/methods_cv02/...` (was relative to B) |
| | after 113 | +10: checks of `ro` (not with a smoke extra; key syntax; not the card's weights_key; not twice; in the card's readouts) |
| | after 118 | +3: render and check the further dump commands |
| | 120 | further dump lines go into jobs_rendered.txt |
| | 122 | armed line: names QC when QC != B |
| | 138 | comment + three new locals |
| | after 146, 158, 167-168 | the dump block (old 147-166) runs once per dump name; `$DC` -> `$dc`; after the loop `if [ $dok = 1 ]` replaces the old rc test; slim gets `--keys <weights_key>,<readouts>` only when the field is set |
| | 173 | RUN.md5 list: + enc_probe.jsonl and the further dump folders, only when the field is set |
| | 199, 205 | pass `RO` and `PK` to the chain |
| bench/q/cv02/cq_setup.sh (8aa2f32f -> 630b1307) | 4, after 18, 23, 26 | comment; QC/CODE.md5 check; `H=${QC:-$B}/bench/q/cv02`; pass `QC` to cq.sh |
| bench/q/cv02/slim_ckpt.py (3a77b783 -> 20712dd3) | 6, after 28, 39-40, 44-45, 50 | `--keys K1,K2`: keep only these models keys, record `keys` and `all_keys` in `slim_of`; without it the written file is byte-equal to the old script's |
| bench/methods_cv02/swad_const_pf_v11.yaml (new, 618cea2f) | | the card with the weights path line of the cv02 PF variant (1 line differs; `cvcard.py` rc 0) |
| tests/test_bench_cq_readouts.py (new, 0216a2cf) | | 14 tests |

Not changed: lane rule, gap, HOLD, MAXC, start and stop code, train and dump command text, bench_lib.sh, relay, every file outside the five above.
- raw_bn: not free. One more dump (133 MB, about 3.5 min of lane per run = 1.5 lane-hours in all) and 100 MB more slim per run (5.8 GB on each machine). Left out. The full latest.pth (all six weight sets) stays on cv02, so any readout can be dumped later on the same GPU model.
- The existing removal list tool (`c3_f81_list.sh`) handles a swad run without change (code read, not run): it lists and removes the usual dump folder `<name>` only; `<name>.swad` (0.13 GB) stays on cv02.

## 5. Disk (E sizes; totals S)
One swad run:
| Part | Size | Source |
|---|---|---|
| latest.pth (6 weight sets + optimizer) | 897 MiB | `du` gaint w2a_swad_* (10 of 10) |
| best.pth | 100 MiB | same |
| slim, all 6 sets (unpatched) | 598 MiB | `evidence/realtest.log` |
| slim, swad_bn + swad (`--keys`) | 199 MiB | same |
| dump without logp, per readout | 133 MiB (107 cells) | same; gaint GPU dumps equal |
| dump with logp, per readout | 937 MB | lead, c3 relays |
- **Relayed to gaint: 0.47 GB per run = 12 GB for 25** (slim 2 sets, two dumps without logp, enc_probe.jsonl). With a 6-set slim 21 GB. With logp on both dumps 52 GB.
- **Stays on cv02: 1.17 GB per run = 29 GB for 25** (latest, best, slim), plus the two dumps 0.26 GB per run until removed.
- gaint: 70 GB free at 09:22 (`df`). Still to come about 44 GB of c3all relays and about 15 GB LOSO-2 (lead's numbers), then 12 GB swad and about 0.3 GB of read cache: 71 GB in all. **So gaint is about 2 GB short with nothing freed, and would end near 0.** With the ruled order PF and swad are relayed first: the swad runs and the swad read fit without freeing (S: about 28 GB free when swad is complete, at 2 GPUs). The shortage comes with the HRNet and HOUSE relays (28 GB). What must be freed: **at least 20 GB on gaint before the HOUSE runs are relayed (S: within about 34 hours of arming at 2 GPUs; 19 Nov 00:00 if armed at 14:00).** The rows 1 `--logp` dumps (49 GB, the lead's option i) cover it.
- If nothing is freed on gaint: the relay script has no disk guard (code read). `c3swad_relay.sh` refuses to start below 25 GB free. Tick rule (S): below 15 GB free on gaint the lead stops relays by their STOP files (swad: `touch /home/noob/work/bench_relay/c3swad/STOP`). Runs not relayed stay on cv02 and their read waits; nothing is lost. If a relay hits a full disk its tar fails, the run is retried, and after 3 failures it is left until the relay is restarted (relay_w1c.sh l.43-44).
- cv02: 82 GB free at 09:22, shared. Carried runs to come: 0.6 GB (PF, HOUSE) or 0.5 GB (HRNet) each stay = 21 GB; their `--logp` dumps (0.94 GB each) are in transit until the lead's tick removes them. With swad: 50 GB stay, so about 30 GB free at the end **if relayed dumps keep being removed at every tick**, 10 GB above the guard floor. `arm` prints the need (83 GB for the 09:10 list) beside the free space and refuses below 45 GB.
- If relayed dumps are not removed on cv02, or other users fill the disk: below 20 GB free, `bench_diskguard3` (new, `diskguard3.sh`, covers c3all2 and c3all3) touches HOLD in the merged queue dir. HOLD = no new training start and no dump start; running trainings finish (a checkpoint is overwritten in place, so they add little). `bench_diskguard` does the same in c3base, c3hrnet, rows2 and `bench_diskguard2` in c3all (their waiting dumps then wait too). A HOLD is removed by hand after space is freed. The jobs not started then are the last in the list (HOUSE).
- Nothing must be freed on cv02 for the swad runs alone. Room if wanted (user's call; S): full checkpoints of finished, relayed runs in our older deploy dirs: rows 1 19.8 GB, W1-C 17.5 GB, rows 2 10.7 GB (`ls -l .../latest.pth`, E; that every one has its slim copy on gaint was checked by the lead for rows 1 only).

## 6. GPU memory gate
- Measured peak of the gaint swad runs: **7,154 MiB in 10 of 10 runs** (bq/w2a/gpumem.log and bq/w2a2/gpumem.log; PF-recipe arms in the same logs 6,830, ema 7,068). So swad holds 324 MiB more than PF.
- cv02 PF peak 5,740 MiB (c3all gpumem.log), so swad on cv02 about 6,060 MiB (S).
- Gate rule peak + 2,048: 9,202 from the gaint peak. `cq.sh` l.109 refuses a gate below the card's 11,000. **Gate 11,000 is right**: it is the lowest value the queue accepts and it is above the rule's value. On a lane that qualifies (no other user above 4,096 MiB) a 48 GB A6000 has more than 40 GB free, so the gate never blocks such a lane; worst case on the GPU is 4,096 + 7,154 = 11.3 GB.
- Dump gate 5,262 = the reviewed PF lines' (same network and dump code; cv02 PF dump peak 3,212 MiB; on gaint the swad dumps peak at 4,102 against PF's 4,098).

## 7. Read (pre-registered 17 Nov 2026, before any cv5v3 swad run exists)
Tool: `W/scripts/bench_read_w1.py` (fdb56b78, 89b9ea5), run by `H/run_read_c3swad.sh`; rule applied by `H/c3swad_verdict.py`. One run gives the 532 cells and the 416 clean cells (`--score-exclude T/benchmark/splits/score_exclude_v3.txt`, 6d48dfbd), with `--groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv` (d880a769).
- **Arms** (cv02 runs only, relayed, checksums equal): PF = `c3_pf_v11_f[0-4]_s[5-9]`; SWADBN = `c3s_swad_v11_f[0-4]_s[5-9]` (readout swad_bn); SWAD = `c3s_swad_v11_f[0-4]_s[5-9]\.swad` (readout swad).
- **Pairs:** PF=SWADBN (primary), PF=SWAD (declared secondary). No other swad contrast decides anything; none is read.
- **Margin M:** `--aa PF:5,6:7,8` on the same PF dumps in the same read. The tool draws the A/A of PF seeds {5, 6} against {7, 8} with the same two-stage bootstrap as the contrasts and sets M(metric) = max(0.010, 2 x SE) at argmax; it does so once for the 532 cells and once for the 416 cells, and each cell set uses its own M at both operating points. Seed 9 is not in the A/A. Why this split (S): it is the tool's default and the split of every earlier margin (W1-G4, wave 2a), so there is no choice among splits; the bootstrap draws one seed per fold and arm, so the SE does not depend on how many seeds each side has.
- **Headline:** crack relF1@2. A gain counts only if delta >= M and the interval's lower end is above 0 at OP-A and at OP-W, on the 532 cells and on the 416 clean cells (four values, all four).
- **Guards**, each on both cell sets and at OP-A and OP-W:
  - width ratio (arm / PF) inside 0.85 to 1.15, pooled;
  - the same per source with at least 40 cells (ARTS 182 / 131, BMRK 50 / 50, CFVS 169 / 132, CSIR 114 / 103 on 532 / 416 cells; SDLE 17 / 0 is not judged);
  - false crack px on crack-free cells at most 1.5 x PF (the share of crack-free cells with 50 px or more is printed beside);
  - inactive IoU: delta >= -M(inactive IoU); mIoU-R13: delta >= -M(mIoU-R13).
- **The carry rule (lead's ruling of 17 Nov 2026, 09:30, verbatim):** "Confirmed if the primary (swad_bn) passes the headline at both operating points and every guard. If the primary passes the headline and every failing guard item of the primary is a per-source width (either operating point, either cell set), the confirmed claim is carried by the declared secondary readout swad, provided swad itself passes the headline at both operating points and every guard on both cell sets. If the primary fails the headline: not confirmed (no confirmed gain). In every other case: not confirmed, reported as a gain with the failing guards named."
  - This text replaces the lead's first wording of 08:43 (carry only when the one failing guard is a per-source width at OP-A). It was ruled at 09:30 on 17 Nov, before any cv5v3 swad run exists (E 09:40: no `c3s_*` run and no `swad_const_pf_v11` dump folder on cv02; c3all not frozen). Reason given by the lead: the screen value 1.147 (ARTS, OP-W, clean cells) sits at the band edge 1.15.
  - How the script applies it: a guard item = one guard at one operating point on one cell set (for the per-source width also one source). Kinds: width_pooled, width_source, false_alarm, inactive, miou. Only width_source items allow the carry. The verdict line names every failing item of swad_bn and, when the carry fails, what swad did not pass.
- **Reported beside the verdict** (same script, `verdict.txt`): per-seed differences (arm minus PF of the same seed, relF1@2, strict crack IoU, mIoU-R13, both operating points, both cell sets); the A/A difference, SE and M; layer3 and layer4 cosine to init at step 20000 for each of the 25 runs from the relayed `enc_probe.jsonl`. Per-class table: `H/c3swad_class_guard.py` = the reviewed `w2a_class_guard.py` with one line changed (imports from bench_wt_final instead of bench_wt_b; `bench/score_ext.py` and `bench/atlas.py` are byte-equal in both trees, E: git diff b5bf0ae 89b9ea5).
- **Read script:** refuses unless W is at 89b9ea5 with no tracked change, the tool is fdb56b78, the output folder `/home/noob/work/bench_reads/c3swad` is new, all 25 PF and all 25 swad runs are relayed with their dump folders (75) and enc_probe.jsonl, and every manifest names the expected run id, fold, seed, weights key, step 20000, set, fp32, train code revision 89b9ea5 and one single GPU model. CPU, nice 19, 8 workers. `SHOW=1` prints the command only. Test (E): `SHOW=1 bash H/run_read_c3swad.sh` prints
  `scripts/bench_read_w1.py --arm PF=<L>/house_r34_unetpp_pf_v11:c3_pf_v11_f[0-4]_s[5-9] --arm SWADBN=<L>/swad_const_pf_v11:c3s_swad_v11_f[0-4]_s[5-9] --arm SWAD=<L>/swad_const_pf_v11:c3s_swad_v11_f[0-4]_s[5-9]\.swad --pair PF=SWADBN --pair PF=SWAD --labels v11 --workers 8 --cache <O>/cache_c --baseline PF --aa PF:5,6:7,8 --groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv --score-exclude T/benchmark/splits/score_exclude_v3.txt --out <O>/read` (L = <O>/links/elbench1, O = /home/noob/work/bench_reads/c3swad). Without SHOW it refuses today (`36 of 50 runs not relayed`) and writes nothing.

## 8. Checks before launch
`bash H/c3swad_check.sh` (G, read only on both machines; with `QC=<dir>` after the deploy and `IO=<handover folder>` after the render). Today (E, `evidence/check_20261117.out`): **23 OK, 0 FAIL, 2 SKIP** (the two skips: QC not deployed, disk guard 3 not started). It checks:
1. card md5 equal in W, in bench_wt_w2 and on cv02 B; cv02 REVISION and CODE.md5; swad code byte-equal c57508e to 89b9ea5; the card renders the same options at both commits for the 25 jobs;
2. QC: CODE.md5, pinned cq.sh, the cv02 variant = card except the weights path line, weights file md5 on cv02;
3. roots on cv02 for all five folds (ROOTS, SPLITS, DATA_MANIFEST, test = val, 425/107, 422/110, 429/103, 431/101, 421/111) and lists equal to gaint's;
4. rendered jobs against the card: the 25 train lines of the cv02 render equal the card as rendered in W, both dump lines per job on the run's own fold, no `--logp` (tested on my gaint render and on a tampered copy: 2 FAIL as intended). At each start `cq.sh` itself logs `config OK (= card)` or HOLDs;
5. names unique on cv02 (experiments, runs, queue dirs, dumps) and in the gaint relays; relay patterns;
6. MAXC and LPG of every live queue, at most one queue that can start, no GPU with two of our training runs;
7. free space on both machines, the three cv02 disk guards, the two running relays;
8. patch applies to 89b9ea5, read script command, no read folder yet, md5 of the harness files.

## 9. Launch steps, in order (all G; nothing before the review PASS)
1. Review of this request and of `cq_c3swad.patch`.
2. `PATCH_MD5=524a70e64d2f8950ba98398f2f1423c6 bash H/c3swad_commit.sh` : new worktree /home/noob/work/bench_wt_c3s, branch bench_c3s, one commit on 89b9ea5 (W is not touched). Prints the commit X. Tested on a scratch repository (E).
3. `bash T/harness/c3base/c3_deploy.sh <X>` : the reviewed deploy script, unchanged. Gives QC = /tmp/noob_el/bench_<X7>.
4. cv02 dump dry test (lead's ruling Q10: yes, after the review PASS, before the handover): `QC=<QC> bash H/c3swad_dumptest.sh place`, then `arm`, then `look`. The two-readout chain on one cv02 GPU with the finished gaint run w2a_swad_f0_s5 as fixture, no training; expected lines are in the script header. **Lane rule of the test** (only a GPU where no other user holds more than 4,096 MiB and none of our training runs sits), where it is enforced:
   - `c3swad_dumptest.sh arm` (added after the ruling): reads every queue dir of ours on cv02 and passes `GPUS` = only the GPUs with no open lane of any of our queues (`pids/<name>.gpu` without `<name>.end`: a training run from its first second, or a run that waits for its dump). It refuses if no GPU is left. E dry run 09:38: open lanes on GPUs 7, 5, 0 (c3all) and 2 (rows2), so `GPUS='1 3 4 6'`. `cq_setup.sh` hands `GPUS` to `cq.sh` (unchanged code; chain test T6).
   - `cq.sh` lane rule, unchanged by the patch (the whole lane section is byte-equal; reviewed test `test_other_on.sh` 13 of 13 on the patched file): `other_on` (patched file l.69) and `lane_ok` (l.85), checked live at the fixture's lane pick (l.219) and again before each of the two dump starts (l.176, inside the loop over the dumps, l.171). A GPU qualifies only if no other user holds more than 4,096 MiB there. Processes of our other queues are not in the test queue's pid files, so they count as another user: a training run of ours (5,740 MiB or more, E) blocks the GPU.
   - Not covered (S): the training queue starts a run on the test's GPU after `arm`, and the dump's live check falls into the first seconds of that run (memory still below 4,096 MiB). The dump (3.2 GB, twice about 2 minutes) would then run beside it, the case seen on 16 Nov 17:40. To exclude it fully the test has to run inside the freeze window (after `freeze` and `build`, before `arm` of the handover), when no queue can start a training run; then a failed test leaves c3all frozen (way out: `MODE=reorder`). Lead's call; the ruled place is before the handover.
5. `QC=<QC> bash H/c3swad_check.sh`.
6. `bash H/c3swad_handover.sh freeze` ; wait 180 s ; `bash H/c3swad_handover.sh build` (default order of section 3).
7. `QC=<QC> bash H/c3swad_handover.sh render` : render-only on cv02 in a scratch dir; carried lines must be byte-equal to c3all's own jobs_rendered.txt.
8. `bash H/c3swad_handover.sh place` ; `bash H/c3swad_handover.sh guard` ; `QC=<QC> IO=/home/noob/work/bench_c3_io/c3swad bash H/c3swad_check.sh`.
9. `QC=<QC> bash H/c3swad_handover.sh arm` (lead's ruling Q8: right after freeze, settle and build). Must print `cq_setup: bench_q_c3all2 armed: gpumem <pid> queue <pid>`; the armed line in /tmp/noob_el/bench_q/c3all2/launch.log names `cq 5222150b` and `queue code QC <QC>`. At the first swad start: `c3s_swad_v11_f0_s5 config OK (= card)` and `startup line OK: Labelled: 425 (/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107`; after it `dumped dump_c3s_swad_v11_f0_s5 rc=0`, `dumped dump_c3s_swad_v11_f0_s5.swad rc=0`, `RUN.md5 c3s_swad_v11_f0_s5 rc=0: 220 files`.
10. `bash H/c3swad_relay.sh` (third relay, `^c3s_`, N 25; `SHOW=1` prints the command).
11. Ticks: `bash H/c3swad_handover.sh status`; HOLD and disk as now. Stop: `touch /tmp/noob_el/bench_q/c3all2/HOLD`; relay `touch /home/noob/work/bench_relay/c3swad/STOP`.
12. When all 50 runs are relayed: `bash H/run_read_c3swad.sh` in tmux.
Steps 6 to 9 take about 10 minutes; c3all starts nothing new in that time.

## 10. Tests (E; CPU only, nice 19; outputs in H/evidence)
- pytest on the patched tree: `tests/test_bench_cq_readouts.py` + `tests/test_bench_cq_cv5v3.py`: **20 passed**. The new file on the unpatched script: 13 of 14 fail (the one that passes is "a line without the field renders the pre-patch commands").
- `c3swad_chain_test.sh` (old and patched `cq.sh` run to their end line in a sandbox with stub python, stub nvidia-smi, stub tmux): **34 of 34** (`chain_test.out`; 32 checks of the first version + 2 on the `GPUS` list). Plain job: RUN.md5, rendered lines, stub calls and log lines equal between old and patched script. swad job: dumps `<name>` (key auto, no logp) then `<name>.swad` on the training GPU, slim `--keys swad_bn,swad`, RUN.md5 with enc_probe.jsonl and both dump folders. A failing second dump: no slim, no RUN.md5, lane released. QC != B: cvcard.py, slim_ckpt.py and the cv02 variant from QC, training and dumps in B, nothing written into QC. The unpatched script refuses the 10-field line at arming (a forgotten QC fails safe). `cq_setup.sh`: same tmux commands without QC; with QC it runs QC's scripts; a changed file in QC is refused; a `GPUS` list is handed on; only GPUs named in `GPUS` are used.
- Lane rule: the reviewed `test_other_on.sh` (715166a0) on the patched `cq.sh`: **13 of 13**, output byte-equal to the unpatched script's (`lanetest_patched.out`); the lane section of the script (from `# ---- lanes` to `# ---- arming`) is byte-equal in both.
- Real tools on the real 20k-step checkpoint of w2a_swad_f0_s5 (`realtest.log`): old slim = patched slim without `--keys`, byte-equal (md5 6fac3b9a, 598 MiB); `--keys swad_bn,swad` 199 MiB; a missing key is refused. Both dumps made from that 2-set slim with the unpatched `bench_infer.py` and the exact arguments `cq.sh` renders (CPU): `key swad_bn` 132.6 MiB and `key swad` 132.2 MiB, 107 cells, manifests name the run ids and keys. Share of equal pred px against the gaint GPU dumps of the same run: 1.000000 with the same weight set, 0.991670 with the other one, so each dump used the right weights.
- Patched `cq.sh` with the real card code (bench.cards of 89b9ea5), QC != B, on the 09:36 preview list in the default order (`render_gaint_default.log`): 149 rendered lines; **the 74 carried lines are byte-equal to lines of cv02 c3all's own jobs_rendered.txt (97bb83fc)** after mapping the sandbox paths; 75 swad lines. The same on the 09:10 list in the other order (`render_gaint.log`): 151 lines, 76 of 76.
- `cq_c3swad.patch` on a fresh `git archive 89b9ea5`: `git apply --check` rc 0, and the result equals my tested tree (`diff -r` empty). My archive + REVISION gives CODE.md5 7cde26e4 = the cv02 deploy's.
- `c3swad_make_jobs.py`: default order as ruled; `--alternate` gives the 09:10 list byte for byte (9fa16c46); both orders hold the same lines; refusals (existing output, unknown started name, `--no-swad` with `--alternate`).
- `c3swad_handover.sh` and `c3swad_dumptest.sh` (`handover_dry.out`): every step dry-run; refusals as intended (no freeze, wrong QC pins, QC = B, arm while c3all can start, wrong mode or option, a queue name the disk guard does not cover, QC = live deploy for the dump test). The QC comparison was run locally on two stage-like folders and gives the expected file list.
- `c3swad_verdict.py` with the rule of 09:30:
  - on the published screen read (cv5v2; mechanics only, `verdict_mechanics_on_screen_read.txt`): it reproduces W2A_READ.md (+0.0135 [+0.0051, +0.0221]; ARTS 1.203 and 1.218; per seed +0.0150, +0.0119; layer4 below 0.8 in 7 of 10); verdict line: carried by swad (failing items of swad_bn: ARTS width at OP-A on both cell sets);
  - `c3swad_verdict_test.py`, **15 of 15** (`verdict_test.out`): copies of the screen read with single values changed by hand (synthetic, not results). The two cases the lead asked for: B, the only failing item of swad_bn is a per-source width at OP-W (ARTS, clean cells, set to 1.16) -> carried by swad; C, a pooled width fails (1.20) -> not confirmed, guards named, no carry. Also: all passing -> confirmed; headline failing by delta or by the interval -> not confirmed (no confirmed gain); carry possible but swad fails a guard or the headline -> not confirmed with the reason; a per-source width beside the inactive guard -> no carry; a source below 40 cells is not judged; band edges 1.1499 / 1.1501 / 0.8499; false alarms 1.49 x / 1.51 x.
- `c3swad_class_guard.py` on the screen read: the lead's class_guard.txt byte for byte (cb98b8ff).
- After all tests: bench_wt_final, bench_wt_w2, bench_wt_b and el_bench have 0 tracked changes; no folder bench_reads/c3swad, no bench_relay/c3swad, no bench_wt_c3s; nothing of this request exists on cv02.

## 11. Lead's rulings (17 Nov 2026, 09:30, on the questions of version b207c499)
| | Question | Ruling | Where it is in the files |
|---|---|---|---|
| Q1 | patch route (commit on 89b9ea5 in a new worktree, deploy as QC, B stays the live deploy) | yes, subject to the review | sections 2, 4, 9 |
| Q2 | logp 0 for both swad dumps | yes | job line (section 1), `c3swad_make_jobs.py` |
| Q3 | slim keeps swad_bn and swad only | yes | patch (`--keys`) |
| Q4 | order | **changed: swad first is the default** (PF, swad, HRNet, HOUSE); the alternating order stays as the option `--alternate` | `c3swad_make_jobs.py`, `c3swad_handover.sh`, section 3 |
| Q5 | the carry rule | **changed: widened** to a per-source width at either operating point on either cell set; new verbatim text | section 7, `c3swad_verdict.py`, `c3swad_verdict_test.py` |
| Q6 | wording when swad_bn fails the headline | yes: "not confirmed (no confirmed gain)" (part of the new rule text) | section 7, `c3swad_verdict.py` |
| Q7 | false crack px at most 1.5 x PF, share printed beside | yes | section 7, `c3swad_verdict.py` |
| Q8 | arm right after freeze, settle and build | yes | section 9 step 9 |
| Q9 | reorder today without swad | no: one handover only, after the review PASS; `MODE=reorder` stays in the script; reconsidered only if there is no PASS by 14:00 | section 3 |
| Q10 | cv02 dump dry test | yes, after the review PASS, before the handover; it must obey the lane rule | section 9 step 4, `c3swad_dumptest.sh` (GPU list added) |
Beyond Q4 and Q5 the files changed in three small ways (E): `c3swad_dumptest.sh arm` passes the GPU list (Q10); `c3swad_chain_test.sh` has 2 more checks (the `GPUS` list); `c3swad_check.sh` lists the new test file's md5. The patch and its five files are unchanged.

## 12. Not verified
- swad run time and peak memory on cv02 (estimates from gaint).
- The patched chain on a cv02 GPU and with the real relay (the dump dry test covers the chain; the relay of a run with two dump folders is code read only: it tars every RUN.md5 path and compares the file count).
- The cv02-writing steps of `c3swad_handover.sh` and `c3swad_dumptest.sh` (freeze, render, place, guard, arm): dry-run only. The QC check's passing case was run on local copies, not on cv02.
- The dump test's lane rule has the gap named in section 9 step 4 (a training start on its GPU in the seconds before a dump's live check).
- That every W1-C and rows 2 run has its slim copy on gaint (section 5, optional room on cv02).
- How many lanes the other users leave.

## 13. Files (H = T/harness/c3swad; `md5sum` at 09:41 IST, 17 Nov)
| File | md5 | against b207c499 |
|---|---|---|
| cq_c3swad.patch | 524a70e64d2f8950ba98398f2f1423c6 | same |
| c3swad_commit.sh | 33c661eb89ae3fd9bf522def0ffcfcfa | same |
| c3swad_make_jobs.py | c8748ae68dc91e3fa9572d761fe63dc5 | changed (Q4) |
| c3swad_handover.sh | 6d397ca6f7e14577bdff33f9372c05ba | changed (Q4: option name, comments) |
| diskguard3.sh | 92794405dc207e4ecae8e47a620b52fb | same |
| c3swad_relay.sh | 535a62a239dbe3f47c863b9d6540a459 | same |
| c3swad_check.sh | 2213db46196d994a69a463f41e0db78e | changed (md5 list) |
| c3swad_dumptest.sh | cdb377648867af2dc1838cc00e44b887 | changed (Q10: GPU list) |
| run_read_c3swad.sh | c8efd03e69afe4990ba8177c57dd99b7 | same |
| c3swad_verdict.py | 7a48b1a18a0d34b8ca689722d2648a76 | changed (Q5) |
| c3swad_verdict_test.py | 2e1358528dc76ba4cbed6a0ef7169e28 | new (Q5) |
| c3swad_class_guard.py | c9022bcc9ddb964298bcd38bf01ab375 | same |
| c3swad_chain_test.sh | cdb661c96f88a05bf52d7319269f00d6 | changed (2 more checks) |
| evidence/chain_test.out | 31259616dc18be7322a4a30dc97f8db4 | new run |
| evidence/lanetest_patched.out | 9eb7673eedd6b7ae1948031050f14bd0 | new |
| evidence/realtest.sh | ad6cb89613e470909f2913a27c923f5b | same |
| evidence/realtest.log | c47d3af72e6fcebf8ca4064e4494de12 | same |
| evidence/render_gaint.sh | 5c616ea86eddc73bf2766111c8302da9 | same |
| evidence/render_gaint.log | 723129962658fd3b3597d6d1f3baa329 | same |
| evidence/render_gaint_default.log | 93c1c26315ae14a970883173efdf5350 | new |
| evidence/handover_dry.out | 225224ba06fd14423640c843360f1329 | new run |
| evidence/check_20261117.out | 897c841c68214d559cb4311896033a4d | new run |
| evidence/preview_jobs_default_20261117_0936.txt | 29388346e2176ce1f2f77a1136b0ab84 | new |
| evidence/preview_jobs_20261117_0910.txt | 9fa16c467df53a87940aa86843e84225 | same |
| evidence/verdict_mechanics_on_screen_read.txt | a3c2fa768f69d02a04c4acf681d7b24e | new run |
| evidence/verdict_test.out | a9d9874cd13fb6eaff8bc3d87b39b5fb | new |
Patched files inside the patch (unchanged): cq.sh 5222150ba40130d41a04af4f7d17dbfa, cq_setup.sh 630b1307a5b3cc99da251cd6eecc8672, slim_ckpt.py 20712dd3af1e6b86720a9633b419de00, bench/methods_cv02/swad_const_pf_v11.yaml 618cea2f57864ac4a916da00845da9da, tests/test_bench_cq_readouts.py 0216a2cf5ea2b3d3e627d80fb196f22c (the same values are pinned in c3swad_commit.sh and c3swad_handover.sh).
Scratch trees and sandboxes of the tests are in the builder's session scratch folder and are not needed for the launch; every test can be run again from the files above (chain test: `OLD=<archive of 89b9ea5> NEW=<the same + patch> bash H/c3swad_chain_test.sh <new dir>`; verdict test: `python -B H/c3swad_verdict_test.py <new dir>`).
Ruling time (lead's correction of 17 Nov): the rulings of section 11 were made at 09:30 IST; the lead's message said 09:35 by mistake. This request now says 09:30 everywhere. The comment lines c3swad_verdict.py l.7, c3swad_verdict_test.py l.7, c3swad_make_jobs.py l.11 and the header line of evidence/handover_dry.out still say 09:35; they were left as they are (the lead: nothing else changes), so every md5 in the table above still holds.
Stray file (E): H/__pycache__/ holds one .pyc from a compile check of mine at 09:32. It is not used by anything. I did not remove it (no deletion).
