# Opening request: the final opening of the sealed sets (E1 opening #8, test50 opening #19) (opening_builder, 21 Nov 2026)

Status: **built and tested on gaint CPU only. Nothing launched, no GPU used, no queue placed or armed, no deploy made, cv02 not
touched, no sealed dump made, no sealed label, prediction or label summary read, no commit pushed.** Commits G (on F) and R (on
the read tree 89b9ea5) exist locally only. The opening itself happens only after an independent review and the lead's go, and
after the fin package has trained the 10 full-pool runs and read its CV5 TTA verdict.
Notation: T = /home/yugma/mtp/research/team_2026-11-12_frontier, H = T/harness/final/opening, F = 821dfadf49116cc6d5fdbd6697e263dd7cf0f834
(bench_wt_fin), G = 8bd1c2761c85f4721e444a8bf7124d2e5804973a (tree 38a8cdfd..., worktree /home/noob/work/bench_wt_openg, branch
bench_open_g), R = 0c72cf942a5cc89accfcd02e1d2b443a033549d9 (three commits on 89b9ea5: 82ea81c, the fix 19764b2, and 0c72cf9
(review round 1 N15: two test asserts, no code); tree 57eaeef9...,
worktree /home/noob/work/bench_wt_open, branch bench_open_read), IO = /home/noob/work/bench_open_io (gaint, made by the registration), GB = cv02 /tmp/noob_el/bench_8bd1c27 (the
deploy of G), FB = cv02 /tmp/noob_el/bench_821dfad (the deploy of F: G's code reference), F2B = cv02 /tmp/noob_el/bench_9967d59
(the deploy of F2 = 9967d59a, where the 10 full-pool runs live after the fin2 resume), DS = cv02 /tmp/noob_el/bench_data_sealed (staged images).
E = measured by a command of this build; S = judgement; D = decision with its record.

## 0. What the opening does (one page)
- **Rule:** H/OPENING_RULE.md (written before any number of the final models). Candidates as the user fixed them (21 Nov 00:22):
  C1 full-pool PF (key model, plain); **C2 full-pool HRNet-W18 U-Net++ + SWAD (key swad) + D4 = the final model**; C3 = mean
  softmax of the 5 C2 seeds' D4 probabilities. Beside, deciding nothing: E-PF (5-seed PF ensemble, the equal-cost comparator of
  C3) and C1-D4 (only if the fin read replicates B5's TTA result). OP-A only; no threshold or bias on any sealed cell.
- **E1 decides** with one primary contrast: C2 - C1 crack relF1@2, seed-aware two-stage bootstrap (71 source-image clusters x
  model draws within arm, 2,000 draws), M 0.010; guards width pooled and CSIR (0.85 to 1.15), false crack px on crack-free cells
  (<= 1.5 x), mIoU-R13 (>= -0.010); inactive reported only. **Power is low** (S, OPENING_RULE section 6): about 18% / 35% / 52%
  / 80% at a true +0.020 / +0.030 / +0.038 / +0.053; the likeliest honest outcome at the CV5-sized effect is "NOT CONFIRMED,
  interval holds 0".
- **test50 is the public table only:** Pratt median IoU rules A / B / C (spacing = union of 1, 2, 3), PV-S3 pooled 3-class with
  both background rules, the SEiPV family, all on v0 (masks_coded); our protocol card on v1.1 (all 50, clean 49, 16 cells
  without a module link); one secondary contrast; leakage disclosed.
- **Dumps:** 20 lines (30 with C1-D4), one cv02 queue `open` of dump-only jobs (G's cq.sh sealed-opening mode), strict lanes,
  MAXC 4. **Read:** gaint CPU, R, once.

## 1. Files (H) and md5
See section 12 (filled at the end of the build; `md5sum` of every file).

## 2. Commit G on F (the dump side; cv02)
`git -C /home/noob/work/bench_wt_openg diff 821dfad 8bd1c27 --stat`: 4 paths, nothing else.
| Path | Change |
|---|---|
| bench/q/cv02/cq.sh (6371dc56) | **sealed-opening queue mode**: a queue dir with the file `SEALED` (lines `e1_106 <opening>`, `test50 <opening>`, `manifest <md5 of DATA_S/MANIFEST.md5>`) takes ONLY eight-word dump-only lines `--dumpof <run dir> --key <key> --tta <mode> --set <set>` of a run on its own full-pool root (`DATA_F/roots/pool532_v11`); name must end with `.<set>`; the usual dump-only checks (run dir pattern, key, mode, cfgcheck of the run's config) apply; the command adds `--opening <that set's opening>` and, with logp 1, `--logp --ens-member`; arming checks the SEALED file, DATA_S's MANIFEST.md5 (md5 and `md5sum -c`) and that DATA_S holds no mask / ignore dir; sealed images come from DATA_S (`BENCH_EXT`, `BENCH_LABELED` exported only in that mode). Without SEALED every line renders and runs as at F (a `--set` word is refused with F's message); with SEALED any training or open line is refused. |
| scripts/bench_infer.py (a3268638) | `--ens-member`: allowed only on a sealed set with `--opening` and `--logp`; then `--logp` is allowed on a sealed set (otherwise still refused) and the manifest gets `"ens_member": true`. Nothing else changes (no new manifest key without it). |
| tests/test_bench_cq_sealed.py | 24 sandbox tests (render with opening / ens-member; refusals: bad extra, set not in SEALED, name, root, cfgcheck, training / open lines in a sealed queue, `--set` without SEALED, SEALED file and DATA_S checks incl. a mask dir); open lines render byte-equal to F's cq.sh |
| tests/test_bench_infer_sealed.py | 7 end-to-end CPU tests with a tiny random U-Net++ and synthetic images named by the test stems: refusals (logp on sealed without ens-member; ens-member on an open set, without logp, without opening); a D4 ens-member dump on test50 (sealed, opening, ens_member true, tta d4, writer = G); its logp is the view-averaged log-softmax and a one-member ensemble from it gives the member's pred; **val54 dumps byte-identical to F's bench_infer** (all cell md5s equal; manifests differ only in code_repo / code_commit / list_file path / writer / written) |

## 3. Commit R on the read tree 89b9ea5 (the read side; gaint)
`git -C /home/noob/work/bench_wt_open diff 89b9ea5 0c72cf9 --stat`: 9 paths (commits 82ea81c, then 19764b2: the sealed
ensemble's pred rule, found by the chain smoke, section 7).
| Path | Change |
|---|---|
| bench/cellmeta.py | label set **v0** = `<labeled>/masks_coded`, no ignore, the 582 legacy cells only (refused before any mask is opened otherwise); every scored file md5-checked: bench/sets/masks_v0_pool532.md5 (the 532 pool cells; md5 a3fa609f pinned) and, for the 50 test cells, the manifest written at registration (env BENCH_MASKS_V0_SEALED + its md5 BENCH_MASKS_V0_SEALED_MD5; must list exactly the 50) |
| bench/sets/masks_v0_pool532.md5 | md5sum lines of the 532 pool masks_coded files (open cells only) |
| scripts/bench_score.py | `--labels` accepts v0 (one line + doc) |
| bench/public_metrics.py (new) | PUBLIC_BENCH 6c: merge / iou_cell, Pratt medians rules A / B / C and median recall (crack, gridline, inactive, ribbons, spacing = union 1, 2, 3; avg defects), PV-S3 pooled with both background rules, SEiPV family (miou24.py `summarise` copied, md5 787e920e named; + micro IoU) |
| bench/derived.py, scripts/bench_ens_dump.py | sealed path only with `--opening NAME`: every member must be a dump of one sealed set at that opening with `ens_member` true (else SealedSetError); derived run id = the prefix; ensemble logp refused; **pred = argmax of the float32 log(pbar + 1e-12) that oth and m_crack come from** (the ttafix rule; decision_rule argmax24_of_log_mean_softmax; argmax pbar failed dumpfmt.check_cell at 181 px of a near-tie cell in the chain smoke); manifest set_kind sealed, opening, members' tta and checkpoint md5s. Without `--opening` unchanged (argmax pbar) (sealed members are refused with SealedSetError; open fold-less members refused as before) |
| scripts/bench_open_read.py (new) | the opening read: per model / arm metrics at OP-A (relF1@1/2/3, relP@2, relR@2, strict crack IoU, inactive IoU, mIoU-R13, width ratio, false crack px and share on crack-free cells, components, per-class IoU of ROB13), subsets (all, per source, half-cut / full by cells.tsv `cell_type`, crack / crack-free cells, named lists), contrasts with the **seed-aware** and the **fixed-model** cluster bootstrap (2,000, Random(0)), A/A, `--public` rows; refuses mixed set / labels / scorer / precision / device / cell order |
| tests/test_bench_public_metrics.py, tests/test_bench_opening_read.py | 12 + 23 tests (section 7; round 1 added the CLASSES and pooled P / R / F1 asserts) |

## 4. The sealed-set ensemble path (task 3) and its disk
- **Design (S: the smallest change):** the C2 dumps on E1 are written once with float16 logp (`--logp --ens-member`), so each
  serves as a C2 single model (its pred) and as a C3 member (its logp). C3 = `bench_ens_dump.py --opening e1_open8_final` on
  gaint after the relay: pbar = mean exp(logp_s) in float32 (the B5 D4ENS3 machinery, derived.ens_maps, i.e. the same path
  as the only CV5 ensemble evidence), pred = argmax log(pbar + 1e-12) (the ttafix rule; equal to argmax pbar except where
  float32 log merges two adjacent pbar values, where argmax pbar would fail the dump check and abort the read). E-PF the same on the C1 dumps (plain views). No ensemble
  logp is written; test50 gets no logp at all.
- **Alternative not built (S):** an in-process ensemble inside bench_infer (exact float32 mean, no logp on disk) needs a
  multi-run bench_infer and a multi-run dump-only line in cq.sh: a larger change to two reviewed tools. The float16 logp path
  differs from the exact mean only at float16 near-ties (E: a one-member ensemble from the stored logp equals the member's pred in
  > 99% of px in the tiny-model test; on CV5, B5's D4ENS3 used the same path).
- **Disk on cv02 (S from E sizes):** E1 C1 and C2 dumps with logp about 1.0 GB each (E: a 107-cell PF dump with logp is 992 MB on
  gaint; B5's D4 logp dumps 0.96 to 1.0 GB): 10 x 1.0 = **10 GB**; E1 C1-D4 5 x 0.13 GB; test50 10 (15) x about 0.06 GB; sealed
  images 10 MB. **Peak about 11.5 GB** if nothing is removed (arm refuses below 35 GB free: 11.5 + the 20 GB floor, rounded).
  E1 106 cells, test50 50 cells. The 10 latest.pth of fin stay (7.8 GB, fin's plan).
- **Disk on gaint:** the relay about 11.5 GB + 2 ensemble dumps 0.26 GB + records and reads < 0.5 GB = **about 12 GB**. gaint had
  42 GB free on 21 Nov 05:00; fin's relay adds about 12.5 GB first, so the opening relay will likely go to the NAS
  (round 1: the NAS dir `/mnt/nas/noob_el_archive/bench_relay/open` is now the default RD of opening_relay.sh,
  run_opening_read.sh and opening_queue.sh unstage; RD=<gaint dir> for all three if the NAS is down).

## 5. Job lines (task 4; NOT in any queue dir)
H/jobs/jobs_open_c1d4_no.txt (20 lines, md5 07e34090) and H/jobs/jobs_open_c1d4_yes.txt (30 lines, md5 3a308b9c; both regenerated
for F2B in the fin2 change set, otherwise equal to the earlier 2e421795 / dbd54984), made by
H/opening_make_jobs.py; the registration writes the one the fin verdict selects into IO/jobs.txt (pinned by its md5). Shape:
`fin_hrnet_swad_v11_pool_s5.swad.tta_d4.e1_106|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|5|/tmp/noob_el/bench_data_fin/roots/pool532_v11|0|11510|6200|1|--dumpof /tmp/noob_el/bench_9967d59/experiments/fin_hrnet_swad_v11_pool_s5 --key swad --tta d4 --set e1_106`
| Set | C2 (swad, d4) | C1 (model, plain) | C1-D4 (model, d4; iff (a) replicated) | logp |
|---|---|---|---|---|
| e1_106 | 5 | 5 | 5 | C2 and C1: 1 (C3 and E-PF members) |
| test50 | 5 | 5 | 5 | 0 |
**GPU (S from E):** cv02 plain dumps of these cards took 26 to 31 s (c3x) and 84 to 93 s (PF with a 1 GB logp write) per fold;
D4 = 8 forward passes: about 2 to 5 min per E1 C2 dump. E1 about 30 min, test50 about 15 min, + about 20 min with C1-D4: **about
0.75 to 1.1 GPU-h**, wall about 30 to 60 min (MAXC 4, GAPSEC 30). **CPU (gaint) for the read:** see section 7 (chain smoke).

## 6. Procedure (who runs what, in order; T and H in full when run)
| # | Who | Command / action | Stop path |
|---|---|---|---|
| 0 | fin, fin2 | the 10 full-pool runs end in **fin2** (the resume of fin's step-18000 checkpoints in F2B = /tmp/noob_el/bench_9967d59; FINAL_RULE_ADDENDUM_1.md): `trained fin_* rc=0` for all 10 and fin2's `BENCH CV02 Q ALL DONE`, and fin2's relay to /mnt/nas/noob_el_archive/bench_relay/fin2 ends with `RELAY ALL DONE: 10 of 10` (slim + LATEST.md5); `opening_queue.sh check` refuses before both; the fin CV5 TTA read writes /home/noob/work/bench_reads/final_tta/verdict.txt | |
| 1 | lead, user | FLAG D4 / FLAG C2 of the fin verdict, if any, ruled (keep the candidates, or a new version of OPENING_RULE.md and a re-review) | |
| 2 | reviewer | independent review of this request, OPENING_RULE.md, G, R and the H scripts (section 8); PASS pinned to OPENING_RULE.md's md5 | |
| 3 | lead | `RULE_MD5=<reviewed md5> [FLAGS_RULED='<ruling>'] bash H/opening_register.sh`: IO/jobs.txt (C1-D4 by the verdict), IO/stage (sealed images + lists, MANIFEST), IO/reg (E1 mask / ignore hashes, v0 test50 hashes, nolink list), IO/REGISTERED.txt (read-only); prints its md5 and two ledger rows | refuses on any pin; nothing sealed beyond file hashes and image copies |
| 4 | lead | adds row #8 to team_2026-10-31_next/e1_openings.md and row #19 to T/benchmark/test_openings.md section B ("registered, NOT opened", REGISTERED.txt md5) and a log.md line, **before step 5** | |
| 5 | lead | `bash T/harness/c3base/c3_deploy.sh 8bd1c2761c85f4721e444a8bf7124d2e5804973a` (GB; prints CODE.md5 and CV02_CODE_OK) | refuses if GB exists |
| 6 | lead | `G=8bd1c27... bash H/opening_queue.sh check` (cv02 read-only: GB pins and diff to FB = G's 4 paths; the 10 fin latest.pth = relayed LATEST.md5 and `trained rc=0`; root pins; names free) | |
| 7 | lead | `G=... bash H/opening_queue.sh stage` (IO/stage -> DS by tar; md5sum -c; read-only; no mask dir) | DS exists: refused |
| 8 | lead | `G=... bash H/opening_queue.sh render` (render-only cq.sh of GB with SEALED in a scratch dir; `render compare: 0 FAIL`) | nothing starts |
| 9 | lead | `G=... bash H/opening_queue.sh guard` (disk guard 7 for queue open, HOLD below 20 GB; arm refuses without it; renamed from 6, which fin2 uses), then `G=... bash H/opening_queue.sh place` (Q = /tmp/noob_el/bench_q/open: jobs.txt, SEALED read-only, LPG 1, MAXC 4, no SHARE file) then `DRY=1 ... arm`, then `G=... GAPSEC=30 bash H/opening_queue.sh arm` | `touch /tmp/noob_el/bench_q/open/HOLD`; a running dump by its recorded PID only (as fin's step 8) |
| 10 | lead | `G=... bash H/opening_relay.sh` (relay_w1c.sh 74a2ec3d unchanged; RD default the NAS dir, its parent made by mkdir -p) | `touch <RD>/STOP` |
| 11 | lead | ticks: `G=... bash H/opening_queue.sh status` | |
| 12 | lead | after `RELAY ALL DONE: N of N`: `REG_MD5=<md5> bash H/run_opening_read.sh` in tmux from a clean shell (round 1: it refuses if a test-only variable is set), ONCE (refuses before writing anything unless every check passes); output /home/noob/work/bench_reads/open_final (records, ens, read_e1, read_t50_v11, read_t50_v0, verdict.txt, MD5.txt) | |
| 13 | lead | ledgers: "opened <start> to <end>", the verdict line, the result file; `G=... bash H/opening_queue.sh unstage` (round 1: first removes the 20 / 30 sealed dump dirs from GB/dumps, each only after gaint's md5sum -c of its relayed copy and cv02's md5sum -c against the same RUN.md5, then DS from cv02); logp dumps archived to the NAS (lead's choice) | |

## 7. Tests run (E; CPU only, nice 19, <= 8 threads)
| Test | Result |
|---|---|
| pytest G (full, 821dfad's suite + 2 new files) | **839 passed, 5 skipped, 0 failed** (F: 808 passed, 5 skipped; + 31 new), 454 s (evidence/pytest_full_G_8bd1c27.log; a first run without the git-ignored `data/labeled` link of bench_wt_fin had 1 environment failure, test_shv_reproduces_shv1_on_real_val_cells, kept as evidence/pytest_full_G_8bd1c27_nolink.log) |
| pytest R (full, 89b9ea5's suite + 2 new files) | at R = 0c72cf9 (round 1): **783 passed, 4 skipped, 0 failed** (evidence/pytest_full_R_0c72cf9.log); at 19764b2: **782 passed, 4 skipped, 0 failed**, 182 s (evidence/pytest_full_R_19764b2.log); at 82ea81c: 780 passed, 4 skipped (evidence/pytest_full_R_82ea81c.log) |
| G: tests/test_bench_cq_sealed.py + test_bench_cq_final.py + test_bench_cq_readouts.py + test_bench_cq_cv5v3.py | 73 passed |
| G: tests/test_bench_infer_sealed.py | 7 passed (about 6 CPU-min) |
| R: tests/test_bench_public_metrics.py | 11 passed: synthetic rules; **equality on open cv5v3 fold-0 dumps of c3_pf_v11_f0_s5 and c3x_hrnet_swad_v11_f0_s5.swad (v1.1)**: SEiPV family == miou24.py `cm_of` + `summarise` (taken from the file by AST, md5 787e920e) exactly; per-image (TP, FP, FN) == pratt_scores.py's expression (taken from the file, md5 2ebb158b) for crack / gridline / inactive in every cell, Pratt medians A / B / C == src/evaluation/metrics.py `pratt_median`; spacing, ribbons and PV-S3 pooled == recomputation from the arrays |
| R: tests/test_bench_opening_read.py | 23 passed: v0 (open fold; pinned manifest; E1 refused before any mask is opened; test50 refused without the registration env; positive and tampered paths on SYNTHETIC masks); sealed ensemble == open-path ensemble byte for byte on relabelled open dumps; foreign members (other opening, no ens_member, open set_kind), logp, fold-less open members refused; derived_meta unchanged without opening; clusters 71 (E1) / 48 (test50); the read on synthetic records (identical arms 0; point = mean of model metrics; seed-aware wider than fixed; deterministic; refuses overwrite and mixed inputs; --public rows); the sealed pred rule passes the cell check on a constructed near-tie ensemble where argmax pbar fails it (only pred differs), and the open path keeps argmax pbar |
| H: opening_verdict_test.py | 21 passed (evidence/opening_verdict_test.out): CONFIRMED; each guard failing alone; inclusive edges (width 0.85 / 1.15, CSIR, false px 1.5 x, mIoU -0.010, Delta = M); strict edges (lo = 0, Delta < M, WORSE); guards never rescue a failed headline; inactive never decides; band label; missing values fail closed; 5 tampered rule constants each change an outcome; main() end to end on reads made by bench_open_read; refusals of the wrong shape |
| H: opening_render_smoke.sh G | **render compare: 0 FAIL** for both job lists (20 and 30 lines) through G's real cq.sh (real yget on G's cards; cfgcheck stubbed: cfgcheck called once per line); the same lists without SEALED refused (evidence/render_smoke/) |
| H: opening_chain_smoke.sh G R | **the whole chain on synthetic data, rc 0** (evidence/chain_smoke/): registration (synthetic label dirs, real stem lists) -> the 30 lines of the C1-D4 list run by G's bench_infer exactly as cq.sh renders them (CPU, tiny random U-Net++; 875 s) and laid out as relayed units -> run_opening_read.sh: manifest check 30 OK, 45 records, C3 and E-PF by bench_ens_dump --opening, the three reads (E1 106 cells / 71 clusters; test50 50 / 48), verdict written (synthetic numbers, meaningless); **read wall about 3.5 min** at 8 workers (records 14 s, ensembles 12 s, E1 read 96 s, test50 reads about 40 s each); negatives refused with no output folder: wrong REG_MD5, a tampered manifest (weights_key), an existing output. **Two earlier attempts found two fail-closed paths** (kept as evidence): attempt 1, a plain dump of a random 2-channel model failed dumpfmt.check_cell at a float32 near-tie (pre-existing plain path of F, unchanged; OPENING_RULE section 2 contingency; section 9.8); attempt 2, the ensemble (argmax pbar) failed it at 181 px: fixed in R (19764b2, the ttafix pred rule on the sealed path) |

## 8. Checks a reviewer should rerun (CPU, nice 19)
1. `git -C /home/noob/work/bench_wt_openg diff 821dfad 8bd1c27` (4 paths) and `git -C /home/noob/work/bench_wt_open diff 89b9ea5 0c72cf9` (9 paths); read cq.sh's sealed branch and bench_infer's two guards; bench_ens_dump / derived with and without `--opening`.
2. `cd /home/noob/work/bench_wt_openg && python -m pytest -q tests/test_bench_cq_sealed.py tests/test_bench_cq_final.py tests/test_bench_infer_sealed.py`; `cd /home/noob/work/bench_wt_open && python -m pytest -q tests/test_bench_public_metrics.py tests/test_bench_opening_read.py`; `cd H && python -m pytest -q opening_verdict_test.py` (CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4).
3. `bash H/opening_render_smoke.sh 8bd1c2761c85f4721e444a8bf7124d2e5804973a <new out dir>` (0 FAIL twice; negatives refused).
4. `PAR=2 bash H/opening_chain_smoke.sh 8bd1c27... 0c72cf9... <new out dir>` (about 30 to 50 CPU-min): read rc 0, verdict written, 3 negatives refused.
5. Own boundary cases on opening_verdict.decide (section 7 row H) and one mutation of public_metrics (e.g. rule B scoring 1) that the tests must catch.
6. The rule: OPENING_RULE.md sections 4 to 7 against the user's decisions (log.md 21 Nov 00:22), PUBLIC_BENCH.md 6c and FINAL_RULE.md section 4; the power numbers of section 6; the disclosures of section 10.
7. That nothing in the package reads a sealed label or prediction before step 12: grep the H scripts for masks / ignore / masks_coded (only file hashes in opening_register.sh; the read in run_opening_read.sh).

## 9. Choices for the lead (my recommendation first; built as recommended)
1. **Primary contrast and interval:** C2 - C1 relF1@2, seed-aware (recipe-level; the CV5 reads' and opening #7's convention)
   with the fixed-model interval beside. Alternative: fixed-model as primary (narrower, SE about 0.013, MDE about 0.036; a claim
   about the trained artefacts only). Recommendation: seed-aware.
2. **M on E1 = 0.010** (the protocol's cv02 relF1@2 margin), not re-estimated on E1 (an E1 A/A is printed, descriptive).
3. **E-PF on E1** (5 C1 logp dumps, +5 GB): protocol 6.1 (c) asks for the equal-cost comparator beside an ensemble row.
   Dropping it: set logp 0 on the E1 C1 lines (new job list md5), S2 / S5 are then not printed.
4. **C3 not on test50** ("the final model" there is C2, per the user's decision). Adding it: logp 1 on the test50 C2 lines and a
   second ensemble; +2.4 GB.
5. **OP-A only** on both sets (OP-W needs a fitted bias: on a sealed set that would be tuning).
6. **Inactive** reported, never a guard on E1 (10 inactive cells).
7. **logp dumps kept** after the read (NAS) for the record; the sealed images removed from cv02 after the relay (`unstage`).
8. **C1 stays plain** (as FINAL_RULE defines it). Risk found by the chain smoke (E, evidence/chain_smoke_attempt1_plain_neartie.txt):
   the plain path's pred (argmax of the logits) can disagree with the maps from log(p + 1e-12) at a float32 near-tie of the two
   top classes, and dumpfmt.check_cell then fails the dump closed (rc != 0; nothing relayed). It happened once in 6 dumps of a
   random 2-channel test model; none of the CV5 plain dumps of these cards is recorded as failing it (S: rare for trained
   models). The rule pre-registers the remedy (OPENING_RULE section 2: that one dump redone with `--tta id` in an amended
   second queue, the read's expectation changed by a reviewed edit). Alternative now (lead's choice): define C1 as `--tta id`
   from the start (pred = argmax log(p + 1e-12), the ttafix rule; probabilities the same single view); not built.

## 10. Not tested
- Anything on cv02 or a GPU: deploy of G, check / stage / render / place / arm / status / unstage against cv02 (the steps were
  written from final_queue.sh's reviewed pattern; the render path of G's cq.sh ran for real in the local render smoke), GPU
  memory and time of the sealed dumps, the relay of a sealed unit (relay_w1c.sh is unchanged and relays what RUN.md5 lists).
- The real registration (it hashes sealed mask files and copies sealed images: the lead's step 3); it ran on synthetic dirs in the
  chain smoke.
- The real read on real dumps (the chain smoke runs the same script on synthetic data with test overrides for the paths and pins).

## 11. Open questions for the lead
1. Primary interval (section 9.1) and M (9.2): confirm or rule otherwise **before** registration.
2. E-PF on E1 (9.3) and C3 on test50 (9.4).
3. Does cv02 still hold `/tmp/noob_el/ext117` (E1 images AND masks from the October era; handbook 14 lists it)? The opening
   stages images only into a new DS; an old copy with masks, if present, should be moved to the NAS (lead's or user's call).
4. gaint disk: after fin's relay the opening relay likely needs the NAS (section 4).
5. The 18-opening multiplicity note of test50 and the 7-opening note of E1 are in the verdict's disclosures; the paper's ledger
   wording is the lead's.

## 12. Files, md5 and evidence (after review round 3 fixes)
| File | md5 | Role |
|---|---|---|
| OPENING_RULE.md | 065a7dddfff2efd4897503561955093f | the registered rule (pin in the review; opening_register.sh default RULE_MD5) |
| opening_make_jobs.py | 6ad871e03b78199de5cda704afe9b517 | job list builder (20 / 30 lines) |
| jobs/jobs_open_c1d4_no.txt | 07e340907e7d7511c5d2081177ded87e | job list without C1-D4 |
| jobs/jobs_open_c1d4_yes.txt | 3a308b9ca8025bd991ebfaf51e17c6ca | job list with C1-D4 |
| t50_nolink.txt | 66f48dc371fbdf8bf95eb66287e74283 | the 16 test cells without a pool cell in their module (from sealed_image_ids.tsv 201b0ec3) |
| opening_register.sh | fdcd3b5923b495ea6360290ec20b8f26 | step 3: registration (gaint only) |
| opening_queue.sh | 451a053db3cdeab5ff775f9b116f5d70 | steps 6 to 9, 11, 13: check, stage, render, place, arm, status, unstage (cv02) |
| opening_rendercmp.py | c42cc6dbeb80c1c9c25aa71fa9bb6d08 | render check (templates + semantics) |
| opening_relay.sh | 4f2a28a36e459b2766218a4b3cf091cb | step 10: relay (relay_w1c.sh 74a2ec3d unchanged) |
| run_opening_read.sh | 2525575e2945c8dfe0966969841a71d8 | step 12: the read (refusals, records, ensembles, reads, verdict) |
| opening_verdict.py | 433f61debeb3135c0aad51524e19add9 | the rule applied to the reads |
| opening_verdict_test.py | a8895db3a878c281723deef18a897141 | verdict tests (27) |
| opening_render_smoke.sh | fec8cd238f761493dfb3b68e854f4bf7 | builder's local render smoke (done; evidence/render_smoke) |
| opening_chain_smoke.sh | e0c67c75d57464de8129c96b5fb60bae | builder's synthetic end-to-end dry run (done; evidence/chain_smoke) |
| v11_filecheck.sh | dcc3bfe4f72250c1a93a35904c269d31 | round 1 N9: per-file md5 check of the test50 v1.1 masks / ignore (called by run_opening_read.sh) |
| diskguard7.sh | 1771e3fc339026387694cd3951bd5226 | cv02 disk guard for queue open (= diskguard5.sh 2719c5f7 with the names changed; renamed from diskguard6 for fin2, REVIEW_FIN2 N2) |
| opening_unstage_smoke.sh | bdd1b1dff1a12d8c7e6e964e7e30fbe3 | round 1: builder's local test of unstage (done; evidence/unstage_smoke) |
| opening_testmode_guard_test.sh | d6c91976910eae407b17143ed440f4a1 | round 2 B2: negatives and controls of the TEST_MODE path guard (done; evidence/testmode_guard_test.out) |
| AMENDMENT_C1_TTAID.md | 43d2da5838bf2c3c4befd46866acbf72 | round 1 N12: the pre-written C1 --tta id amendment (NOT applied) |
| amendment_c1_ttaid/make_amend.py | 2546103d53abfd05c3f267cf1273cc87 | amendment: job list and record builder (not applied) |
| amendment_c1_ttaid/opening_rendercmp.py.patch | 2f317ce0a47d52ebb4856ad0d06807cc | amendment patch (not applied) |
| amendment_c1_ttaid/opening_queue.sh.patch | bcfec40d0185b266e960acbfa1352feb | amendment patch (not applied) |
| amendment_c1_ttaid/opening_relay.sh.patch | 66e2bf8acbc9183ade4abfa130844395 | amendment patch (not applied) |
| amendment_c1_ttaid/run_opening_read.sh.patch | 49271426ba19e0b94399204802a8da30 | amendment patch (not applied) |
| evidence/ | 75923e469223cb5b628b97488d79812c (MD5_evidence.txt, 80 files) | outputs of section 7 |

Commits (local only, not pushed): G 8bd1c2761c85f4721e444a8bf7124d2e5804973a (tree 38a8cdfdfd739e631547792e63dc4c1e707d21bb, parent F 821dfad; unchanged in round 1; bench_wt_openg clean) and R 0c72cf942a5cc89accfcd02e1d2b443a033549d9 (tree 57eaeef9669ebb89524a3b960967b455490760e5; 82ea81c, 19764b2, 0c72cf9 on 89b9ea5; bench_wt_open clean). Pinned in the scripts: G, its tree and F (opening_register.sh, opening_queue.sh, run_opening_read.sh, opening_relay.sh), R and its tree (opening_register.sh, run_opening_read.sh), G's cq.sh 6371dc56 and bench_infer.py a3268638 (opening_queue.sh PINS, run_opening_read.sh writer), diskguard7.sh (opening_queue.sh), F2 and its tree (opening_register.sh; F2 also in run_opening_read.sh), OPENING_RULE.md 065a7ddd (opening_register.sh default RULE_MD5), opening_make_jobs.py, t50_nolink.txt, the E1 / test50 list md5s, masks_v11 MANIFEST 9c0e0687, the pool root pins and DATA_MD5 (as fin), relay_w1c.sh 74a2ec3d. The two worktrees carry git-ignored data links (data/labeled; R also data/escdd_masks, data/unlabeled) as bench_wt_fin / bench_wt_final do.

## 13. Review round 1 (T/harness/REVIEW_OPENING.md 3f7d6d4e, FIX with B1): what changed (no number, bound or decision)
OPENING_RULE.md is unchanged (69f0c0f3): every change implements what the rule already says (band on strict IoU, both inactive
intervals, per-class and component tables, the fin decisions quoted, OP-A disclosed) or protects the procedure. G is unchanged.
| Item | Change | Where |
|---|---|---|
| **B1** | `band(d)` = "inside / outside the convention band +-0.019; decides nothing" (BAND from FINAL_RULE section 2) and `siou()` print every strict crack IoU delta: P, S1 to S5, C1-D4 - C1, C2 - C1-D4, every E1 stratum, the test50 contrasts. Test: every verdict line with "strict" and a signed number carries the band, and a mutant without it is caught. Chain smoke verdict: 17 such lines, 0 without the band | opening_verdict.py, opening_verdict_test.py |
| N2 | inactive IoU with both intervals (seed-aware and fixed-model); per-class IoU of the 13 robust classes (arm means); crack (>= 20 px) and inactive (>= 100 px) component recall / precision | opening_verdict.py |
| N3 | `--fin-verdict` (run_opening_read.sh passes FIN_VERDICT, default the fin read's verdict.txt): md5 must equal the registered one; its decision lines (a), (b), (c) are quoted (exactly one each); MECHANICS lines refused | opening_verdict.py, run_opening_read.sh |
| N4, N5 | disclosures: C2 is entry class (c) (8 views) against C1's 1 view, and without C1-D4 nothing separates the D4 part; OP-A only is a stated deviation from protocol 5.4 (G1 / G2 take OP-W's role) | opening_verdict.py |
| N6, N7 (relay) | RD default `/mnt/nas/noob_el_archive/bench_relay/open` in opening_relay.sh (parent made by mkdir -p before df), run_opening_read.sh and opening_queue.sh unstage (`RD=${RD:-...}`); one variable name RD | opening_relay.sh, run_opening_read.sh, opening_queue.sh |
| N7 (cv02) | `guard` step: diskguard6.sh (= diskguard5.sh for queue open; HOLD below 20 GB), arm refuses without it; `unstage` first removes every sealed dump dir from GB/dumps, each only after gaint's md5sum -c of its relayed copy and cv02's md5sum -c of every listed file against the same RUN.md5 (plus one dir, exact file count), log /tmp/noob_el/removed_relayed_dumps_open.log; then DS | diskguard6.sh, opening_queue.sh |
| N9 | before the output folder: the 50 test cells' v1.1 masks and ignore files (100) md5-checked file by file against MANIFEST.md5's lines | v11_filecheck.sh, run_opening_read.sh |
| N10 | ledger rows printed in the column format of their table, each checked against that table's header line: e1_openings.md (7), test_openings.md section B (6; where #1 to #18 are) and, as an alternative, section E (7) | opening_register.sh |
| N11 | steps 3 and 12 refuse when a test-only variable is set (register: IO, FIN_VERDICT, G, R, EXT_DIR, LABELED_DIR, MASKS_V11_DIR, REPO_G, SKIP_GIT, RULE_MD5 other than the pin; read: IO, RF, READ_ROOT, RT, BENCH_EXT, BENCH_LABELED, BENCH_MASKS_V11, CELLS_TSV, PINS_FILE, DEVICE_OK, FIN_VERDICT, V11_FILECHECK_MANIFEST) unless TEST_MODE=1; a TEST_MODE registration starts with a 'TEST MODE' line and the read refuses it outside TEST_MODE, and refuses TEST_MODE against a real registration; register also refuses a fin verdict with MECHANICS lines outside TEST_MODE | opening_register.sh, run_opening_read.sh, opening_chain_smoke.sh (TEST_MODE=1) |
| N12 | the C1 `--tta id` amendment pre-written, NOT applied: AMENDMENT_C1_TTAID.md, amendment_c1_ttaid/ (make_amend.py + 4 patches; dry-run apply OK, tested on copies) | new files |
| N15 | verdict test hi = 0 is not WORSE; R commit 0c72cf9: public_metrics tests assert CLASSES and the pooled P / R / F1 exactly (both mutants the review found now fail the tests) | opening_verdict_test.py, R |
Pins changed: R 19764b2 -> 0c72cf942a5cc89accfcd02e1d2b443a033549d9 (tree 57eaeef9669ebb89524a3b960967b455490760e5) in opening_register.sh
and run_opening_read.sh; opening_register.sh default RULE_MD5 still 69f0c0f3; opening_queue.sh pins diskguard6.sh (8eb052e1).
Not taken: N1 (R's read.txt stays without the band: the verdict is the result file), N13, N14 (wording; noted).

**Round 1 tests (E; CPU, nice 19, <= 8 threads):**
| Test | Result |
|---|---|
| opening_verdict_test.py | **27 passed** (21 + B1 band test + its mutant + band helper + hi = 0 + N2/N3 printed + fin refusals) (evidence/opening_verdict_test.out) |
| R at 0c72cf9: tests/test_bench_public_metrics.py | 12 passed; the review's two missed mutants (spacing [1, 2]; F1 = PR / (P + R)) each fail the new test |
| R at 0c72cf9: full suite | **783 passed, 4 skipped, 0 failed**, 185 s (evidence/pytest_full_R_0c72cf9.log) |
| chain smoke (TEST_MODE, final scripts: verdict 65cfcf52, read eaf7661a, v11_filecheck dcc3bfe4) | **read rc 0**; dumps 30 of 30 in 871 s; the three read.txt md5-equal to round 0 (ca6196ee / 4ef5ad79 / 56a70ffd: no number changed); verdict: 17 strict-IoU delta lines, all with the band; (a) / (b) / (c) quoted; both inactive intervals; per-class and component tables; entry-class and OP-A lines; negatives refused with no output folder: wrong REG_MD5, a tampered manifest, overrides without TEST_MODE, a v1.1 file changed after registration, an existing output (evidence/chain_smoke/; round 0 kept in evidence/chain_smoke_round0/) |
| N11 early refusals (scratch IO) | register: an override without TEST_MODE, RULE_MD5 other than the pin; read: an override without TEST_MODE, TEST_MODE against a registration without the TEST MODE line: all refused before anything is read (evidence/n11_refusals.out) |
| v11_filecheck.sh on the open val54 cells | OK 108 files; a copy OK; one changed file and an unknown stem refused (evidence/v11_filecheck_test.out) |
| opening_unstage_smoke.sh (stub ssh, scratch) | relay not done: refused, nothing removed; one cv02 file differing from its relayed copy: that dir kept, the other 2 removed, step refused, DS kept; all equal: 3 dump dirs and DS removed, RUN.md5 files kept, 5 log lines (evidence/unstage_smoke/) |
| amendment | evidence/amendment_test.out (AMENDMENT_C1_TTAID.md section "Tests run") |


## 14. Review round 2 (T/harness/REVIEW_OPENING.md 080db63a, FIX with B2): what changed
Only opening_register.sh and run_opening_read.sh changed (no number, pin or registered file): **B2**, a TEST_MODE path guard placed
right after the override check, before any read, hash or mkdir. With TEST_MODE=1 every label, mask, ignore, image, relay,
output and fin-verdict path variable must be set explicitly (register: IO, FIN_VERDICT, EXT_DIR, LABELED_DIR, MASKS_V11_DIR;
read: IO, RD, RF, READ_ROOT, BENCH_EXT, BENCH_LABELED, BENCH_MASKS_V11, CELLS_TSV, FIN_VERDICT, V11_FILECHECK_MANIFEST), each
path and the sub-paths the script opens (stems_eval.txt, images, masks, ignore, masks_coded, MANIFEST.md5) must resolve
(readlink -m, symlinks followed) under /home/noob/work/bench_int_io, and no symlink inside those scratch dirs may resolve outside
it. Also: the amendment's run_opening_read.sh.patch was regenerated against the new file (dc90b10a; the same 29 changed lines;
`patch --dry-run` exact); OPENING_RULE.md, G and R are unchanged.
| Test (E; synthetic dirs only, never production paths; the "real tree" paths used do not exist) | Result |
|---|---|
| opening_testmode_guard_test.sh (evidence/testmode_guard_test.out) | **0 FAIL**: register R1 FIN_VERDICT left at its default, R2 EXT_DIR inside the real tree, R3 a scratch EXT_DIR whose masks dir is a symlink into the real tree, R4 one mask file symlinked into the real tree: all 'REFUSED (TEST_MODE guard)'; R5 control (all scratch) passes the guard and refuses later ('fin verdict ... missing'); no IO made. Read D1 READ_ROOT and D2 BENCH_MASKS_V11 left at their defaults, D3 BENCH_LABELED inside the real tree, D4 RD on the real relay tree, D5 a scratch RD holding a symlink into the real relay tree: all refused by the guard; D6 control passes it and refuses at 'no IO/REGISTERED.txt'; no output folder made |
| chain smoke (TEST_MODE, all paths scratch; register 7ce23ec0, read 010723bd) | **read rc 0**; the guard passes in both scripts; the three read.txt md5-equal to rounds 0 and 1 (ca6196ee / 4ef5ad79 / 56a70ffd); the 5 negatives refused with no output folder (evidence/chain_smoke/; round 1 kept in evidence/chain_smoke_round1/) |

## 15. fin2 change set (REVIEW_FIN2.md 9d11087e N2, N3; LAUNCH_REQUEST_fin2.md c8f1df79), before review round 3
The full-pool runs failed at their step-20000 validation under F and are repaired by the resume queue fin2 (F2 = 9967d59a, deploy
F2B = /tmp/noob_el/bench_9967d59; steps 1 to 18,000 under F, the rest under F2; FINAL_RULE_ADDENDUM_1.md, written by
final_builder2). G stays on F (dump-only, no eval code), FB stays G's code reference. Changed (no candidate, readout, contrast,
statistic, guard or number):
| Item | Change | Where |
|---|---|---|
| N2 | the opening's disk guard renamed diskguard6 -> **diskguard7** (file, tmux bench_diskguard7, DISKGUARD7_STOP, diskguard7.log; body = diskguard5.sh up to the names); fin2 keeps diskguard6 | diskguard7.sh, opening_queue.sh |
| N3 jobs | EXP = /tmp/noob_el/bench_9967d59/experiments (the `--dumpof` source of every line); both job lists regenerated: equal to the earlier lists except the deploy dir (07e34090 / 3a308b9c) | opening_make_jobs.py, opening_rendercmp.py, jobs/ |
| N3 check | fin_check: latest.pth in F2B, LATEST.md5 of fin2's relay (RF = /mnt/nas/noob_el_archive/bench_relay/fin2), 'trained <run> rc=0' for all 10 and 'BENCH CV02 Q ALL DONE' in /tmp/noob_el/bench_q/fin2/launch.log, and 'RELAY ALL DONE: 10 of 10' in fin2's relay log: the opening cannot pass `check` (nor `arm`) before fin2 and its relay ended | opening_queue.sh |
| N3 read | expected train_code_revision = F2 (the full-pool runs' deploy) for every dump; RF default = fin2's NAS relay; the registration must hold the line `runs F2 9967d59...` | run_opening_read.sh |
| N3 register | F2 pinned with its tree (adcdf7ec; git check) and recorded as `runs F2 <F2> (deploy /tmp/noob_el/bench_9967d59 ...)`; MAKE_MD5 and RULE_MD5 pins updated | opening_register.sh |
| N3 rule | OPENING_RULE.md **32ac11dc** (was 69f0c0f3): section 2 "All checkpoints" paragraph (l.33-37: F2B location, steps under F / F2, fin2's relayed LATEST.md5, train_code_revision F2), section 8 (l.161: train_code_revision = F2, fin2's LATEST.md5), section 9 step 1 (l.167-170: fin2 ALL DONE and its relay before the opening), and a 4-line dated edit note in the header (l.9-12); diff in evidence/rule_edit_fin2.diff; nothing else changed | OPENING_RULE.md |
| fixtures | render and chain smokes build the fake runs in bench_9967d59 (chain smoke: REVISION = F2); the guard test gained R6 (control with the G / R / F2 git pins checked) | opening_render_smoke.sh, opening_chain_smoke.sh, opening_testmode_guard_test.sh |
| amendment | the patches for opening_rendercmp.py, opening_queue.sh and run_opening_read.sh regenerated (the same changed lines; all four `patch --dry-run` exact); make_amend.py unchanged | amendment_c1_ttaid/, AMENDMENT_C1_TTAID.md |
**Tests (E; synthetic, never a production path):** guard test 0 FAIL (R1 to R6, D1 to D6; evidence/testmode_guard_test.out); render
smoke 0 FAIL for 20 and 30 lines with both negatives refused (evidence/render_smoke/); unstage smoke as before (evidence/unstage_smoke/);
amendment test as before (evidence/amendment_test.out); chain smoke: see evidence/chain_smoke/ (result line below).
Chain smoke result (TEST_MODE, all paths scratch, fake runs in bench_9967d59 with REVISION F2): **read rc 0**; manifest check 30 OK
with train_code_revision F2; the registration holds `runs F2 9967d59...`; the three read.txt md5-equal to rounds 0 to 2 (ca6196ee /
4ef5ad79 / 56a70ffd: no number moved); the 5 negatives refused with no output folder (this run is kept in evidence/chain_smoke_round3/; the round-2 run's folder was
removed in round 4 for space, its read.txt md5s are the ones above).

## 16. Review round 3 (REVIEW_OPENING.md d6e2d72f, FIX with B3) and the lead's items (i) to (iv)
| Item | Change |
|---|---|
| **B3** | tm_in in opening_register.sh and run_opening_read.sh refuses a non-absolute path before resolving it (`case "$1" in /*) ;; *) tm_no "... is not an absolute path"`), in place on the same line (no line shift). New negatives, run from a scratch dir: register R7 (EXT_DIR=ext), read D7 (BENCH_LABELED=data/labeled) and D8 (READ_ROOT=reads): all 'REFUSED (TEST_MODE guard): ... is not an absolute path'; guard test 0 FAIL over R1 to R7 and D1 to D8 (evidence/testmode_guard_test.out) |
| (i) | the verdict quotes the registration's `runs F2 ...` line as a disclosure (the fin2 resume); outside --mechanics a registration without exactly one such line is refused; 2 test additions, opening_verdict_test.py 28 passed (evidence/opening_verdict_test.out) |
| (ii) | opening_queue.sh header: "fin2's disk guard 6" (comment only) |
| (iii) | AMENDMENT_C1_TTAID.md step 4: "disk guard 7 already covers `open`" |
| (iv) | OPENING_RULE.md header note: "before registration and before any number of the final models" -> **new md5 065a7ddd** (was 32ac11dc); one line, wording only; opening_register.sh RULE_MD5 pin updated |
The four amendment patches still apply exactly (`patch --dry-run`, no offset); their md5s are unchanged.
Chain smoke rerun with the round-4 files (TEST_MODE, all scratch; rule 065a7ddd registered): **read rc 0**; the three read.txt
md5-equal to rounds 0 to 3 (ca6196ee / 4ef5ad79 / 56a70ffd: no number moved); the verdict quotes `runs F2 9967d59...`; the 5 negatives
refused with no output folder (evidence/chain_smoke/; the round-3 run in evidence/chain_smoke_round3/).
