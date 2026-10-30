# SK1 null diagnosis: data pack from agent 3 (22 Oct 2026)

**Purpose and scope**
- Input for `null_diagnosis.md` (critics lead).
- Facts only; readings are marked "Reading".
- All CPU-only so far, from training logs: `pseudo_labels.csv` (500-step windows) and the 50-step stdout lines.
- No GPU used.

**Sources**
- Full tables: `~/mtp/research/results/sk1/diag_trajectories.md`.
- Script: `scripts_cv02/sk1_traj.py`, run in cv02 `el_sk1/experiments`.

## D1. Confident background pseudo-labels over training (teacher main head)
Values are the share of all unlabelled pixels: mean over 5 seeds, with the range in brackets.

| Step | 2.5k | 4k | 6k | 8k | 10k | 12k | 14k | 16k | 18k | 20k |
|---|---|---|---|---|---|---|---|---|---|---|
| BsD5, confident | 0.80 | 0.86 | 0.89 | 0.91 | 0.92 | 0.93 | 0.94 | 0.95 | 0.96 | 0.96 |
| BsD5, background | 0.63 | 0.65 | 0.66 | 0.66 | 0.67 | 0.67 | 0.68 | 0.68 | 0.69 | 0.69 |
| BsDB5, confident | 0.22 | 0.27 | 0.59 [0.32–0.76] | 0.84 | 0.79 [0.37–0.91] | 0.88 | 0.89 | 0.93 | 0.93 | 0.81 [0.41–0.93] |
| BsDB5, background | 0.01 | 0.02 | 0.32 [0.01–0.49] | 0.57 | 0.53 [0.08–0.67] | 0.62 | 0.62 | 0.66 | 0.66 | 0.54 [0.14–0.66] |
| BsDBn5, confident | 0.38 [0.19–0.70] | 0.60 [0.26–0.82] | 0.79 | 0.88 | 0.91 | 0.93 | 0.92 | 0.79 [0.27–0.92] | 0.28 | 0.27 |
| BsDBn5, background | 0.19 [0.00–0.50] | 0.36 [0.04–0.59] | 0.53 | 0.63 | 0.66 | 0.67 | 0.65 | 0.52 [0.00–0.66] | 0.003 | 0.000 |

- **Padding:** 0.165 in every arm at every step.
- **Confident crack:** 0.0011–0.0015 at all steps in BsD5 and BsDB5. BsDBn5 is about 2× higher early (0.0023–0.0027 to 4k), then equal.

**Reading.** Background pseudo-labels are scarce in both ABSH arms in two phases:
1. Early, until about 6k: BsDB5 has almost none until 4k.
2. Late, after about 14–16k: BsDBn5 in all seeds; BsDB5 s1 at 20k.

So "BsDBn5 has no background pseudo-labels" holds only for the last ~4–6k steps. In between, both arms have background at about the BsD5 level.

## D2. The head transfer undoes the labelled fit late in training
Supervised loss on the labelled batch (main head; mean of the 50-step lines inside each block, 5 seeds):

| Block (steps) | 0–2k | 2–4k | 4–6k | 6–10k | 10–14k | 14–18k | 18–20k |
|---|---|---|---|---|---|---|---|
| BsD5 | 0.663 | 0.229 | 0.159 | 0.107 | 0.060 | 0.031 | **0.023** |
| BsDB5 | 0.593 | 0.197 | 0.173 | 0.128 | 0.085 | 0.081 | **0.111** |
| BsDBn5 | 0.615 | 0.222 | 0.196 | 0.140 | 0.092 | 0.130 | **0.220** |
| AB5 | 0.593 | 0.192 | 0.185 | 0.158 | 0.099 | 0.069 | **0.067** |
| A5c (P12 s0, P13 s3–4; step 20k) | | | | | | | **0.013–0.014** |

head_drift = ‖main_l − aux_l‖:

| Block (steps) | 0–2k | 2–4k | 4–6k | 6–10k | 10–14k | 14–18k | 18–20k |
|---|---|---|---|---|---|---|---|
| BsDB5 | 2.65 | 4.62 | 3.73 | 2.35 | 1.24 | 0.33 | 0.04 |
| BsDBn5 | 2.62 | 3.12 | 3.02 | 2.32 | 1.64 | 0.58 | 0.06 |
| AB5 | 2.65 | 4.80 | 5.45 | 4.59 | 2.15 | 0.57 | 0.05 |

**Reading (mechanism, untested).**
- The transfer pulls the main head 1% toward the balanced head at every step. Its pull does not decay, while the gradient that fits the labelled data does decay with the cosine LR.
- Late in training the evaluated head therefore becomes the balanced head (drift → 0.04–0.06).
- The supervised loss of the evaluated head rises 2–10× above the no-ABSH value, which is consistent with a head trained to see background at keep rate 0.005.
- That same head then loses ≥ 0.95 confidence on background (D1), which removes background from the main pseudo-labels.
- In SKCDF the same per-iteration ω = 0.99 runs under SGD poly-LR with best-val selection, so their evaluated checkpoint may come from before this end state. Not verified.

## D3. Keep rates (balanced-head masks)
- Labelled `aux_keep_l`: about 0.039 (BsDBn5, no band) and about 0.044 (BsDB5, band), constant over training.
  - Each present class contributes about N_ref/N_total ≈ 0.3% of pixels, and about 12 classes are present.
- Unlabelled `aux_keep_u` (BsDBn5): 0.20 at 2–4k, 0.26 at 6–10k, then 0.08 at 14–18k and 0.04 at the end. The fall follows the keep-probability anneal and the falling confidence.
- Balanced-head crack pseudo-label share: BsDBn5 0.0037 at 2–4k, falling to 0.0015 by 20k; BsDB5 about 0.0010–0.0015 throughout.

## D4. Already in `results.md` (test)
- **Crack bin-0 share:** BsD5 0.523, BsDB5 0.515, BsDBn5 0.422, BsD5+LA 0.482, A5c 0.569, AB5 0.572.
- **Crack precision / recall:**
  - BsD5 0.618 / 0.412;
  - BsDBn5 0.595 / 0.439;
  - BsD5+LA 0.582 / 0.452.
- **Main head vs balanced head at 20k:** they agree to ≤ 0.002 IoU in every run.

## Available on request (inference only, cv02, booked GPU)
- Per-cell crack FN/FP split by cell type and source, before (BsD5) vs after (BsDB5, BsDBn5): from `per_image.json`, no GPU.
- Confident-miss maps: share of GT crack/inactive px at p < 0.001, per cell, all arms. Needs one inference pass.
- Scoring an intermediate checkpoint is not possible: only `latest.pth` (step 20k) is kept, and `best.pth` is best-val. The step-14k state cannot be re-scored without retraining.
