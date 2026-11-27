# FINAL_RULE: the final model and the reads that check it (final_builder, 21 Nov 2026, 00:45 IST; U-update 01:25 IST)

**Written before any new number.** At this time no D4 dump of a cv5v3 c3x or c3_pf_v11 run exists, no full-pool run exists,
and nothing of this package has run on any GPU. Numbers quoted below are earlier registered reads (E, file named). The
lead pins this file's md5 in LAUNCH_REQUEST_final.md before arming; any change after that is a new registration with its
time. Tags: E = measured in a cited file, S = judgement, D = decision with its record.
**Updated 21 Nov (before any number) with the user's decisions of 20/21 Nov, relayed by the lead** (D, lead's message to
final_builder): (U1) relF1@2 decides every crack contrast; strict crack IoU is printed only with its convention band and
decides nothing. (U2) The user approved the one end-of-project **E1 opening** (106 cells) as the final evaluation with at
most 3 candidates: **C1** full-pool PF; **C2** full-pool HRNet + SWAD (readout swad) + D4 TTA; **C3** the 5-seed ensemble of
C2; and one legacy **test50 opening (#19)** for the public table (old masks v0 and v1.1). The opening (its rule, read code,
v0 labels, public metrics, the sealed-set ensemble path) is built by opening_builder, not here. This rule therefore never
changes the approved candidates: where a CV5 read does not support a part of C2 / C3 it raises a FLAG for the lead (and the
user) before the opening is frozen (section 4).

## 0. Selection bias, stated first
- The candidate's readout **swad** (COMBO_SWAD = `c3x_hrnet_swad_v11 .swad`) was chosen **after** the c3x read
  (results/C3X_READ.md, 19 Nov 01:20). That read's registered primary readout was swad_bn (COMBO); its verdict is
  **NOT CONFIRMED** (COMBO fails the ARTS width band and the false-crack-pixel guard). COMBO_SWAD was a declared secondary
  readout that failed only ARTS width on the 416 clean cells, so it could not carry the claim (E, C3X_READ.md).
- Therefore every CV5 number of a COMBO_SWAD-based arm on the cv5v3 cells (532, and the 416 clean subset) is
  **selection-biased upward**: of two readouts of the same runs, the one that looked better on these very cells was kept.
  The bias is not estimated here (S: the two readouts differ by about +0.001 relF1@2 and 1.8x in false crack px, so the
  choice was driven by the guard, not by the headline; the headline bias is likely small but cannot be bounded on these
  cells).
- The **D4 increment** (read b below) is a new factor on the same checkpoints and the same cells; it carries no selection on
  its own, but it is read on cells that already selected the readout.
- **The unbiased test of the final model is the sealed-set opening**: E1 (approved by the user, U2) decides; legacy test 50
  (#19, approved) is the public-comparison track (harness/final/PUBLIC_BENCH.md section 8). It is NOT part of this package:
  opening_builder registers its rule and builds its read side. No CV5 read below can confirm the final model; read (c) is
  printed with the words "selection-biased" on every line.

## 1. The final model and the approved E1 candidates (definition, fixed now)
| Item | Definition |
|---|---|
| Recipe (C2, C3) | card `bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml` (md5 98f152de, commit 03375d4): HRNet-W18 encoder, U-Net++ decoder, PF encoder schedule, constant LR, SWAD uniform average over steps 10,000 to 20,000, 20,000 steps |
| Training data (C1, C2, C3) | all 532 pool cells (legacy train 478 + val 54), label set v1.1, root `pool532_v11` (scripts/bench_make_pool_root.py at F; no sealed cell in any list; val = test = the cv5v3 fold-0 held-out list as an in-sample monitor whose numbers are never read) |
| Seeds | 5, 6, 7, 8, 9: five independent full-pool models per card, trained on cv02 (one GPU model, fp32) |
| Readout | C2, C3: weights key `swad` of latest.pth (the uniform average, no BN re-estimate), saved for every seed (latest.pth on cv02 holds all six readouts; slim.pth keeps swad_bn and swad). C1: key `model` (slim.pth keeps it) |
| Inference | C2: `bench_infer.py --tta d4` at F: 8 views (4 rotations x flip), view-averaged softmax, fp32, 512 px; pred = argmax over the 24 classes of log(p + 1e-12) (ttafix e25728e); OP-A (argmax, no bias, no threshold). C3: the mean of the 5 seeds' D4 softmax, then the same argmax (the sealed-set ensemble path is opening_builder's code). C1: plain; shown also with D4 (descriptive) iff read (a) is CONFIRMED (section 4) |
| Unit | C2 is a **single model**: each of the 5 seed models is scored on its own; its headline is the mean over the 5 seed models with their range; the deployable single model is **seed 5**, designated now (no selection by score). C3 is one ensemble of the same 5 models. Which of C2 / C3 is "the final model" is decided by the E1 opening rule (opening_builder), not here; S, recommendation: C2 primary (deployable at 1/5 of C3's cost; the public rows are single models), C3 reported beside |
| CV5 evidence for C3 | none in this package: a CV5 ensemble read needs logp dumps (about 1 GB per dump, 25 GB on cv02 per arm), which the cv02 disk does not hold beside this package; the earlier W1-G evidence is B5's D4ENS3 (3 seeds x D4) +0.0017 relF1@2 over single-model D4 (results/stageB/B5_msc_tta.md, cv5v2). A CV5 ensemble read can be added as its own dump-only queue with logp 1 (lead's choice; LAUNCH_REQUEST_final.md section 9) |
| Baseline | C1 = PF = card `house_r34_unetpp_pf_v11` (md5 a4a46a52), readout model, same full-pool root, seeds 5 to 9 |

Single-model D4 dumps on a sealed set need no code change: bench_infer.py at F allows `--tta d4` with `--opening` (it refuses
only `--logp` there; E, scripts/bench_infer.py l.146-150). C3 on a sealed set needs logp or an in-process ensemble: a code
change by opening_builder.

## 2. CV5 reads of this package (cv5v3, 5 seeds x 5 folds, out-of-fold, cv02 A6000 dumps, relayed to gaint)
Arms (25 runs each; seeds 5 to 9; folds 0 to 4):
| Arm | Runs / readout | Dumps |
|---|---|---|
| PF | `c3_pf_v11_f<k>_s<s>`, model, plain | existing (relay c3base; bench_infer afd91642) |
| PF_D4 | the same checkpoints, `--tta d4` | new: `c3_pf_v11_f<k>_s<s>.tta_d4` (bench_infer 32e0b67c at F) |
| CS | `c3x_hrnet_swad_v11_f<k>_s<s>`, swad, plain (= COMBO_SWAD) | existing (relay c3x, `.swad`; afd91642) |
| CS_D4 | the same checkpoints, swad, `--tta d4` | new: `c3x_hrnet_swad_v11_f<k>_s<s>.swad.tta_d4` |
| CB | the same c3x runs, swad_bn, plain (= COMBO) | existing (relay c3x) |
| CB_D4 | swad_bn, `--tta d4` | new: `c3x_hrnet_swad_v11_f<k>_s<s>.swad_bn.tta_d4` |

**Primary reads (three, all decided on crack relF1@2):**
- **(a) PF_D4 - PF**: replication of the gaint TTA result (B5: D4 - PLAIN +0.0173 [+0.0115, +0.0230], W1-G PF, cv5v2,
  2 seeds) on another split (cv5v3), machine (cv02) and 5 seeds. No selection: the cleanest TTA evidence of the package.
- **(b) CS_D4 - CS**: the TTA increment on the candidate (same checkpoints, same readout). The read tool (bench_read_w1
  fdb56b78) bootstraps every contrast with seeds unpaired (boot_pair, paired_seeds=False; no option), so the interval of (b)
  is wider than a seed-paired one (conservative); the seed-paired differences are printed beside.
- **(c) CS_D4 - PF**: the candidate against the baseline. **Selection-biased** (section 0); a necessary check, never a
  confirmation.

**Metric and margin.** Crack relF1@2 decides (dataset_audit/REPORT.md F1: relF1@2 contrasts move by at most 0.0031 under
label-convention variants). Margin M(metric) = max(0.01, 2 x SE) of the PF A/A (`--aa PF:5,6:7,8`, plain PF, same read),
computed separately for each cell set, taken at OP-A and used at OP-A and OP-W (as the c3x read).

**Headline of a contrast X - R:** relF1@2 delta >= M and the lower end of the 95% interval (two-stage group bootstrap,
cv5v3 groups) > 0, at OP-A **and** OP-W, on the 532 cells **and** on the 416 clean cells (four values).

**Guards** (the c3x guards; each at OP-A and OP-W on both cell sets; point values, bounds inclusive; reference R = the
contrast's reference arm):
1. width_pooled: mean crack width ratio X / R in 0.85 to 1.15;
2. width_source: the same per source with >= 40 cells in that cell set;
3. false_alarm: false crack px on crack-free cells X <= 1.5 x R; for (b) also X <= 1.5 x PF (the lead's guard is against PF;
   a separate item, false_alarm_pf, that counts as a false-alarm item in section 4);
4. inactive: inactive IoU delta X - R >= -M(inactive IoU);
5. miou: mIoU-R13 delta X - R >= -M(mIoU-R13).

**Outcome per contrast:** CONFIRMED = headline and every guard pass. GAIN, FAILING GUARDS NAMED = headline passes, some
guard fails (each failing item named). NOT CONFIRMED = headline fails; then NO LOSS if the interval's lower end > -M at all
four values, else LOSS.

**Printed beside, deciding nothing (U1):** strict crack IoU of every contrast, only with its interval and the
**convention band +-0.019**: the largest shift of a strict-IoU contrast when the same predictions are re-scored on the
1-px centreline, the v1.1 and the 3-px labels (dataset_audit/REPORT.md F1: HOUSE - PF +0.0015 / +0.0179 / +0.0367;
SWADBN - PF +0.0047 / +0.0180 / +0.0342; HRNET - PF +0.0008 on v1.1, -0.0109 on 3 px). A strict-IoU delta inside
+-0.019 is labelled "inside the convention band"; outside it, "outside the band" (still deciding nothing). Inactive IoU (pooled; label-noise band +-0.05 to 0.07, audit F4). Per-seed differences.
The A/A. Descriptive contrasts: CB_D4 - CB, CB_D4 - PF, CS - PF (the c3x secondary, already read), CS_D4 - PF_D4 (the
candidate against the baseline both with D4).

## 3. Cell sets and operating points
Both cell sets decide together: all 532 pool cells and the 416 clean cells (`--score-exclude
benchmark/splits/score_exclude_v3.txt`, md5 6d48dfbd); one read gives both. OP-A = argmax (the final model's rule); OP-W
= cross-fitted width match to PF (bench/crossfit_op.py), a robustness check only. OP-F is not used.

## 4. What promotes, flags, or is descriptive (the approved candidates are never changed by a CV5 read)
| Read outcome | Consequence |
|---|---|
| (b) CONFIRMED | D4 in C2 / C3 is supported on CV5 |
| (b) GAIN with only width items failing (pooled or per source) | D4 in C2 / C3 is supported on CV5; the failing width items are named and handed to the opening rule as items to re-read on E1 (descriptive there) |
| (b) GAIN with a false-alarm (incl. false_alarm_pf), inactive or mIoU item failing | **FLAG D4**: CV5 does not support D4 on the candidate without a guard failure; the lead takes it to the user before the E1 opening is frozen (keep C2 / C3 with D4 as approved, or replace D4 by plain inference); CS - PF is printed beside as the plain alternative (selection-biased) |
| (b) NOT CONFIRMED (no loss or loss) | **FLAG D4**, as the row above (D4 costs 8x inference without a confirmed CV5 gain on the candidate) |
| (c) headline passes and no false-alarm, inactive or mIoU item fails (width items named, if any) | C2 passes its CV5 check; labelled selection-biased; the E1 opening is the test |
| (c) headline fails, or a false-alarm, inactive or mIoU item fails | **FLAG C2**: the lead looks (and tells the user) before the E1 opening is frozen; the full-pool runs stay as trained artefacts |
| (a) | replication only: "B5 TTA result replicated on cv5v3 / cv02" iff (a) is CONFIRMED; else "not replicated" with the failing parts named. It decides nothing about C2 / C3. C1 is also shown with D4 in the opening (descriptive) iff (a) is CONFIRMED |
| CB_D4 - CB, CB_D4 - PF, CS - PF, CS_D4 - PF_D4, strict IoU, inactive IoU, per-class table | descriptive; never promote, flag or drop |
| swad vs swad_bn | not re-decided: swad is fixed by the lead's post-hoc choice of 19 Nov (section 0) and approved by the user for C2 / C3 (U2); the CB arms are information only |

The verdict tool (harness/final/final_verdict.py) prints, in this order: (a), (b), (c) with their guards; when (b) flags D4,
CS - PF with the (c) criteria as information for the lead's decision; then the decisions (replication, D4 supported or
FLAG D4, C2 check passed or FLAG C2); then the descriptive lines. It reads only read.json of the registered read.

## 5. Full-pool runs
- 10 runs on cv02 (candidate card and PF card, seeds 5 to 9) on `pool532_v11`. The chain makes no dump (no held-out cell);
  slim.pth keeps the card's weights_key and, for the candidate, `swad`; latest.pth (all readouts) stays on cv02. These are
  exactly the checkpoints C1, C2 and C3 need: C1 = `fin_pf_v11_pool_s<s>` key model; C2 = `fin_hrnet_swad_v11_pool_s<s>` key
  swad with D4; C3 = the same five C2 checkpoints, ensembled. All under /tmp/noob_el/bench_821dfad/experiments/ (deploy of F).
- **No number is read from a full-pool run before the opening**: the trainer's end-of-run val / test numbers are in-sample
  (the monitor list is training cells) and are never printed or read (step lines only are grepped).
- Their only registered use is the sealed-set openings approved by the user (E1 with C1 to C3; test50 #19), under
  opening_builder's rule. Sealed-set dump lines are not in this package's queue.

## 6. Read checks (the read script refuses, before creating its output folder, unless all hold)
- read tools: bench_wt_final at 89b9ea5 clean, `scripts/bench_read_w1.py` fdb56b78 (unchanged, as the c3x read);
  `--groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv` (d880a769), score_exclude_v3.txt (6d48dfbd).
- 150 dump folders, 25 per arm, relayed with `.ok` and the `relayed` log line; every manifest: run id, fold, seed,
  weights key (model / swad / swad_bn), step 20000, set cv5v3_f<k>, fp32, open set, train_code_revision (89b9ea5 for PF and
  PF_D4, 03375d4 for the c3x arms), tta = false for PF / CS / CB and {mode d4, scales [1.0], d4 true, views 8} for the D4
  arms; one device over all 150 (NVIDIA RTX A6000); writers exactly two: bench_infer.py afd91642 for the three plain arms
  and 32e0b67c (F) for the three D4 arms (the code proof shows the plain path of both writes the same bytes).
- The read runs once (the registered read); a repeat needs TAG and is not the registered read.

## 7. Clarifications made before pinning (21 Nov, before any number; from the read-tool build)
1. (b) is read with the tool's unpaired-seed bootstrap (conservative); seed-paired differences beside (section 2).
2. (superseded by U2 the same night, before any number) If (b) does not support D4, the read FLAGS it for the lead and the
   user and prints CS - PF with the (c) criteria as information; it no longer drops D4 or gates the opening itself.
3. C1 (PF) is also shown with D4 in the opening iff (a) is CONFIRMED (section 4, row (a)); descriptive.
4. The (b) false-alarm check against PF is the item false_alarm_pf and counts as a false-alarm item (section 2, guard 3).
