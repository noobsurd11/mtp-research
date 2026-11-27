# T3B_RULE: few-shot layout adaptation inside E1 (E1 opening #9)

t3b_builder, 21 Nov 2026. **Written before any T3b number exists**: no T3b model is trained, no T3b dump exists, and the
zero-shot comparator's E1 dumps (opening #8) have not been opened by this build. Nothing here was chosen after looking at an E1
label, an E1 prediction or a T3b number. Frozen by its md5 in the registration record (`t3b_register.sh`); any change after
registration is a new registration. Tags: E = in a cited file; S = judgement; D = decision with its record.
T = `/home/yugma/mtp/research/team_2026-11-12_frontier`, H3 = T/harness/t3b, K = the code commit of LAUNCH_REQUEST_t3b.md.

## 0. Decided, and by whom (D)
- User, 21 Nov about 14:35 IST (T/log.md 14:38): "go with thesis tables, run T3b on free GPUs". The user accepts that E1
  becomes training data for T3b models and stops being a clean zero-shot set after this opening.
- Lead, 21 Nov 14:38 / 14:40 (T/log.md; brief to t3b_builder): the design in sections 2 to 10 (folds, arms, recipe, seeds 5 to
  7 instead of the proposal's 2, deployable models, monitor, label map, primary, guards, beside, separation, one opening).
- Design source: T/benchmark/T3B_PROPOSAL.md (benchdesign, 12 Nov). Order rule (proposal 6.1): the T3 table is frozen first;
  E1 opening #8 (the final opening) is read and closed (E, T/results/FINAL_OPENING_READ.md; ledger e1_openings.md #8 OPENED).

## 1. Question, set, opening
- Question: how much does the final recipe gain on E1's layouts once it has labelled cells of them (half-cut cells, the E1
  modules), measured out of fold by image id, against the same recipe zero-shot.
- Set: E1 = `e1_106` (106 cells, 71 source images = 71 modules; 62 half-cut; list ext117/stems_eval.txt 5266806b). Clusters for
  every interval: the 71 source images (stem without its cell suffix), as openings #4 to #8.
- Opening: **E1 opening #9** `e1_open9_t3b` (ledger team_2026-10-31_next/e1_openings.md). Sealed dump sets `e1t3b_f0..4` (the
  held-out cells of each fold; bench/sets.py at K). The zero-shot comparator's dumps belong to opening #8 and are re-scored here.

## 2. Folds and the half (frozen; H3/lists, LISTS.md5 5c86318a0d3c628bf3f9711fe7081fb5)
- K = 5 folds by image id = column `k5_fold` of T/benchmark/out/t3b_draft_folds.tsv (md5 49e70413, 12 Nov), unchanged.
  `H3/t3b_make_lists.py` reads only that file and the E1 list; no mask, image or prediction.
- Held-out lists `e1t3b_f<k>.txt` (E1 list order): 22 / 22 / 20 / 21 / 21 cells, 12 / 14 / 14 / 16 / 15 image ids (E, LISTS_REPORT.txt).
  md5: f0 9581b3e2, f1 c1e8bcf5, f2 5067b76b, f3 92f8e87d, f4 60aa7c33 (copied byte-equal into K's bench/sets/).
- Half of fold k (`t3b_half_f<k>.txt`): of the U training-side image ids, floor(U / 2), chosen deterministically to minimise
  |hard(H) - hard(U) / 2| / hard(U) + |cells(H) - cells(U) / 2| / cells(U) (hard = crack px of the cells with e1_stratum
  half-cut + scuff, from the draft file's columns), greedy start then best-swap descent (the script's docstring). Result (E):

| Fold | train-side cells / ids | half ids / cells (share) | hard crack px share | all crack px share |
|---|---|---|---|---|
| 0 | 84 / 59 | 29 / 42 (0.500) | 0.499 | 0.565 |
| 1 | 84 / 57 | 28 / 42 (0.500) | 0.501 | 0.558 |
| 2 | 86 / 57 | 28 / 43 (0.500) | 0.500 | 0.426 |
| 3 | 85 / 55 | 27 / 42 (0.494) | 0.501 | 0.524 |
| 4 | 85 / 56 | 28 / 43 (0.506) | 0.496 | 0.529 |

## 3. Arms, recipe, seeds (33 trainings)
| Arm | Runs | Training list (root) |
|---|---|---|
| **ALL** | `t3b_all_f<k>_s<s>`, k 0 to 4, s 5 to 7 (15) | pool532_v11's 532 cells + every E1 cell outside fold k (84 to 86) (`t3b_all_f<k>`) |
| **HALF** | `t3b_half_f<k>_s<s>` (15) | the 532 + `t3b_half_f<k>.txt` (42 or 43) (`t3b_half_f<k>`) |
| deployable | `t3b_deploy_s<s>`, s 5 to 7 (3) | the 532 + all 106 E1 cells (`t3b_deploy`); **never scored on E1** |
- Recipe: exactly C2's (card `bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml` md5 98f152de: HRNet-W18 U-Net++, PF encoder
  schedule, constant LR, SWAD uniform average over steps 10,000 to 20,000, 20,000 steps, batch 8, 512 px, label set v1.1 opts).
  Only `data.root` (the training list) differs from `fin_hrnet_swad_v11_pool_s<s>`. Seeds 5, 6, 7 (the zero-shot comparator's).
- Readout `swad` of latest.pth at step 20000 (final weights; best.pth never read); inference D4 (8 views, bench/tta.py, fp32,
  TF32 off, batch 8), pred = argmax of log(p + 1e-12) over 24 classes (OP-A). **No threshold, bias, view weight or checkpoint
  is set on, or chosen with, any E1 cell.**
- Code: K = merge of F2 (9967d59) and G (8bd1c27) + R's 3 read commits + the T3b changes. The training path (scripts/train.py,
  src/, configs/, bench/methods*, bench/cards.py, bench/tta.py) is byte-equal to F2 (t3b_codeproof.sh); dumps by K's
  bench_infer.py (G's sealed path + the trained_on_e1 mark).

## 4. Training roots and the monitor (no held-out E1 label is reachable)
- Every T3b root: splits/train.txt = pool532_v11's train.txt (532, md5 d374fd84) + the root's E1 cells; **val.txt = test.txt =
  pool532_v11's monitor** (the 107 cv5v3 fold-0 pool cells, md5 79816ba6), training cells, an in-sample monitor whose numbers
  are never read; masks_v11/ and labeled/images/ hold links ONLY for the stems of the three lists. A fold root lists and links
  no held-out E1 cell; held-out images appear only in the dump list (DATA_S). The pool part of every DATA_MANIFEST.md5 equals
  pool532_v11's (md5 33e65b3f: the same 532 image and mask bytes).
- Why train.py cannot touch a held-out E1 label (E, K = F2 for train.py): it reads masks only as `<root>/masks_v11/<stem>.png`
  for stems of train.txt (labelled stream, class counts), val.txt and test.txt (val / test loaders; the val metric picks
  best.pth, never read); F2's eval change accepts 255 only when every val / test cell is a training cell (true here); the BN
  re-estimate (weight_avg.train_fold_loader) reads train.txt only. A held-out stem is in no list and has no link; the
  builder asserts it and the train smoke runs with the held-out files deleted (t3b_train_smoke.sh).

## 5. Data build (after registration only)
`t3b_queue.sh build` runs K's scripts/bench_make_t3b_roots.py on gaint after the registration: it md5-checks every E1 image,
mask and ignore file against the registration's `reg/e1_files.md5` before decoding it, writes IO/data (files/, the 11 roots,
ROOTS_t3b.md5, E1_LABELS.tsv, LINKS.tsv, MANIFEST.md5) and re-checks everything (`--check`). Staged to cv02 by tar as
/tmp/noob_el/bench_data_t3b (DT); the images of all 106 E1 cells for the dumps as /tmp/noob_el/bench_data_sealed (DS, images
and list only).

## 6. E1 labels for training (bench/t3b_labels.py at K)
- Class map (proposal 6 rule 6): 0 to 23 unchanged; 24 -> 2 (sp_mono); 29 -> 1 (sp_multi); 25 to 28 (scuff, corrosion cell,
  brightening, star) -> 255; every px with ext117/ignore > 0 -> 255 (the trainer's data.mask_ignore_value; the loss ignores it).
- Equality with the E1 scorer (asserted per cell): bench_score scores ext117/masks with keep = (ignore == 0) and m0core asserts
  gt < 24 on every kept px. The training label equals the scoring GT on every kept px and is 255 on every other px. A value 24
  to 29 on a kept px (which the scorer would refuse) refuses the build. ext117 was built with 24 -> 2 and 25 to 28 -> 0 plus
  ignore (E, results/e1/README.md); label = where(ignore==0, mask, 255); the class map changes no output px.

## 7. Dumps, out-of-fold records, the comparator
- 30 sealed dumps (queue t3bopen): each fold model `t3b_<arm>_f<k>_s<s>` dumps ONLY its held-out set `e1t3b_f<k>` (swad, D4,
  no logp) at opening e1_open9_t3b. bench_infer refuses a T3b set from an unmarked run and any set that overlaps the run's
  training list; cq.sh refuses a T3b set from another fold's root or the deploy root.
- Per arm and seed, `bench_t3b_oof.py` joins the 5 fold records into one out-of-fold record over the 106 cells (each cell's
  record copied unchanged from the one model that held it out). Arm value = mean over seeds of the pooled metric.
- **ZS = the zero-shot comparator**: opening #8's C2 dumps of `fin_hrnet_swad_v11_pool_s5/s6/s7` on e1_106 (swad, D4; relayed to
  /mnt/nas/noob_el_archive/bench_relay/open), file hashes registered, re-scored by K's scorer at the read (the cells are
  compared with opening #8's records, information). Same recipe, seeds and inference; never trained on E1.

## 8. The primary contrast, guards, outcomes, and what is printed beside
**Metric:** crack relF1@2 at OP-A, pooled over the scored px of the 106 cells (opening #8's definition).
**P:** Delta = mean over seeds 5 to 7 of relF1@2(ALL_s, out of fold) minus mean over seeds 5 to 7 of relF1@2(ZS_s).
**Interval:** seed-aware two-stage bootstrap, the code path of opening #8 (`scripts/bench_open_read.py` boot): per draw the 71
clusters with replacement, then for each arm independently 3 models with replacement; 2,000 draws, random.Random(0); 95%
percentile interval. **M = 0.010.**

| Outcome | Condition |
|---|---|
| **CONFIRMED** | Delta >= M, lower end > 0, guards G1 and G2 pass |
| **GAIN, FAILING GUARDS NAMED** | Delta >= M and lower end > 0, a guard fails (named) |
| **NOT CONFIRMED** | otherwise: "WORSE" if the upper end < 0, else "interval holds 0" (with the sign of Delta) or "below M" |

**Guards** (arm means over the 3 seeds; bounds inclusive): **G1** false crack px on the crack-free cells (GT crack px 0 under
the E1 labels; 74 cells, E: FINAL_OPENING_READ.md) ALL <= 1.5 x ZS; **G2** mIoU-R13 Delta >= -0.010.
**Width:** the predicted crack width ratio ALL / ZS is printed, **not a guard**: E1 labels are about 1.5 x wider than the pool
labels (proposal section 5), so a model trained on E1 learns the wider width.
**Printed beside, deciding nothing:** HALF - ZS and ALL - HALF (seed-aware and fixed-model intervals); any-hit crack component
recall (>= 20 px components, hit = any px within 2 px of a predicted crack px) and recall at >= 50% covered, per arm; strata
full (44) / half-cut (62) / hard = half-cut + scuff (29) / half-cut without scuff (33) (from the draft file's e1_stratum,
frozen in lists/t3b_strata.tsv), crack and crack-free cells, CSIR / BMRK; inactive IoU (reported only); mIoU-R13; strict crack
IoU with the convention band +-0.019; per-class IoU of the 13 robust classes; per-seed values; the fixed-model interval of P.

## 9. Separation
- Every T3b dump manifest carries `trained_on_e1: true` and `e1_train_cells` (bench_infer at K: the run's training list holds an
  E1 stem); records (bench_score) and out-of-fold records carry it. The training run itself is marked by its root
  (T3B_ROOT.json, trained_on_e1 true) and its name prefix `t3b_`; train.py is unchanged.
- Refusals at K: bench_score records scores a marked dump only on e1t3b_f<k> (and an e1t3b set only from a marked dump);
  bench_score summary, derived dumps (ensembles) and bench_open_read refuse marked records; only `bench_open_read --t3b ZS`
  (the T3b card) holds both, with ZS unmarked and every other arm marked and out-of-fold, ZS labelled "zero-shot comparator" on
  every line. A T3b model cannot be dumped on e1_106 (bench_infer's train-overlap guard).
- No T3b number enters a T3 table or an E1 column of any other track.

## 10. Procedure (details: LAUNCH_REQUEST_t3b.md section 6)
1. Independent review: PASS pinned to this file's md5. 2. **Registration** (lead, `t3b_register.sh`): job lists, DS stage
(images), E1 file hashes, ZS unit hashes, REGISTERED.txt; ledger row #9 and bullet ("E1 is training data for T3b models from
this date") **before** any build or staging. 3. Build (gaint), deploy K, check, stage DT and DS. 4. Queue t3b (33 trainings;
LPG 1, MAXC = free GPUs at arm, SHARE_TRAIN 20480, no SHARE_DUMP, disk guard 8) and its relay. 5. After t3b's ALL DONE: queue
t3bopen (30 sealed dumps, strict lanes) and its relay. 6. **Read once** (`run_t3b_read.sh`). 7. Ledger "opened"; **unstage**:
the 30 dump dirs (after md5 checks of the relayed copies), DS and DT removed from cv02: no E1 image, label or prediction stays
there. Repeats need TAG and are not the registered read.
- **Failures are not replaced silently:** a training that ends rc != 0 blocks t3bopen (`render2` refuses); a re-run of exactly
  that line (same card, seed and root) in a repair queue is a dated amendment (ledger line) before t3bopen; a failed dump the
  same. No run is dropped from an arm: the read refuses unless all 30 fold dumps exist.
- The 33 run dirs (models; no E1 image or label) stay on cv02 after unstage (about 32 GB); the deployable models' slim.pth
  (swad_bn, swad) are relayed with the training units; removing the latest.pth files later is the lead's call.

## 11. Power (S, before any number)
- SE of P: opening #8's 5-v-5 seed-aware SE was 0.0265 (E, FINAL_OPENING_READ.md); with 3 seeds per arm the seed part grows
  (x sqrt(5/3) if half the variance is seed composition), so SE about 0.030 (S). Power = Phi(Delta / SE - 1.96): about 52% at
  +0.06, 76% at +0.08, 91% at +0.10; the smallest effect with 80% power is about +0.085.
- Expected (proposal section 5, S): a gain of +0.10 or more is plausible if layout labels close part of the hard-stratum gap
  (zero-shot recall 0.13 there); smaller gains, ALL - HALF, the strata and inactive are underpowered (about 9 effective images).

## 12. Disclosures (printed in the verdict)
E1 becomes training data from the registration (no later zero-shot claim on E1 by this team); ZS is opening #8's C2, re-scored;
concentration (half of the crack px in 3 images, the hard crack cells in 10); folds by image id may be optimistic for a truly
new site (neighbouring CSIR ids may share handling marks); label width (1.5 x; relF1@2 decides, strict IoU only with its band;
relF1@2 is less width-sensitive than strict IoU but not immune, so any-hit recall is printed); 3 seeds (lead's choice; the
seed-aware interval then resamples 3 models per arm); one primary contrast; dumps on cv02 (one GPU model), the read on gaint.
