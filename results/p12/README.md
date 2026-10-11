# P12: Mean Teacher with the supervised labelled view, at 5% labels (23 cells), L3 base. Results

Protocol: `protocols/P12_matched_5pct.md`, locked before any run.

**Runs**
- cv02 (RTX A6000): 15 runs, 11 Oct 06:30–16:09 IST. gaint (RTX PRO 4500): 6 SSL runs, 03:57–15:21 IST. Every run has rc = 0. All are 20,000 steps; the EMA teacher is evaluated.
- Code: commit `24590fb`, with `ssl.labeled_aug=supervised` (P11's matched view).
- gA10 (rule 7, gaint calibration) is still training; it is added when it finishes.

**Files**
- `raw/`: re-score JSONs, `launch.log`, `launch_gaint.log`.
- `p12_rules.txt`.
- `per_image_test.txt`: the bootstrap and source split (cv02 runs only).
- `fig_p12_bars.png`.
- `per_image.json` and `hist_revised.npz`.
- The whole set is reproduced by `bash scripts/post_ssl.sh p12 <gpu> 15`.

## Results
Test, revised labels, mean ± sd over seeds (cv02 0–2; gaint SSL 3–5; gaint A5 0–2).

| Arm | HW | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|---|
| **A5c**: supervised 5% | cv02 | – | 0.305±0.007 | 0.271±0.018 | 0.721±0.013 | 0.891±0.020 | 0.287±0.004 | 0.270±0.019 |
| D5 (P10): loss off, SSL labelled view | cv02 | 455 | 0.243±0.005 | 0.243±0.006 | 0.629±0.014 | 0.855±0.030 | 0.232±0.009 | 0.251±0.008 |
| **Dm5**: loss off, matched view | cv02 | 455 | 0.288±0.016 | 0.257±0.092 | 0.696±0.019 | 0.888±0.004 | 0.276±0.018 | 0.248±0.086 |
| **Cm5**: tolerant PL, matched view | cv02 | 455 | **0.311±0.010** | 0.274±0.139 | **0.737±0.014** | 0.857±0.077 | 0.329±0.016 | 0.348±0.121 |
| **Dmx5**: loss off, matched, external | cv02 | 11,938 | 0.305±0.002 | 0.270±0.074 | 0.727±0.005 | 0.879±0.022 | 0.291±0.001 | 0.256±0.065 |
| **Cmx5**: tolerant PL, matched, external | cv02 | 11,938 | 0.295±0.014 | 0.256±0.040 | 0.714±0.027 | 0.835±0.031 | 0.300±0.011 | 0.319±0.054 |
| A5 (P10) | gaint | – | 0.298±0.005 | 0.277±0.055 | 0.708±0.012 | 0.890±0.014 | 0.282±0.003 | 0.270±0.050 |
| gDm5 | gaint | 455 | 0.280±0.009 | 0.269±0.030 | 0.688±0.017 | 0.906±0.011 | 0.270±0.008 | 0.261±0.028 |
| **gCm5** | gaint | 455 | **0.327±0.009** | 0.345±0.091 | **0.766±0.011** | 0.888±0.008 | 0.352±0.009 | 0.400±0.048 |
| L3 10% (P6) | cv02 | – | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| L3 100% (P6) | cv02 | – | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

## Locked rules (primary: crack IoU, inactive IoU, crack relF1@2)
Each cell shows the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| Dm5 − A5c (rule 1, descriptive) | −0.017 (0.020) | −0.015 (0.109) | −0.025 (0.027) | n.d. by the seed rule; the bootstrap shows a crack handicap (below) |
| Dm5 − D5 (rule 1, descriptive) | **+0.045 (0.019)** | +0.014 (0.107) | **+0.068 (0.027)** | the matched view removes most of P10's handicap |
| **Cm5 − Dm5 (rule 2)** | **+0.023 (0.022)** | +0.018 (0.192) | **+0.040 (0.027)** | **Cm5 helps** |
| Cmx5 − Dmx5 (rule 2) | −0.010 (0.016) | −0.013 (0.097) | −0.013 (0.031) | Cmx5 does not help |
| Cm5 − A5c (rule 3) | +0.006 (0.014) | +0.003 (0.161) | +0.015 (0.022) | **fails**: SSL does not beat supervised at 5% on cv02 |
| Cmx5 − A5c (rule 3) | −0.010 (0.018) | −0.015 (0.051) | −0.008 (0.034) | fails |
| gCm5 − gDm5 (rule 6) | **+0.047 (0.015)** | +0.077 (0.111) | **+0.078 (0.024)** | **replicates** rule 2 (same sign, ≥ half the size on both passing metrics) |
| gCm5 − A5 gaint (rule 6) | +0.029 (0.012) | +0.068 (0.123) | +0.058 (0.019) | passes the arithmetic; **cannot rescue** the failed cv02 rule 3 |
| gA10 − L3 10% (rule 7) | pending | | | gA10 still training on gaint |

- **Width check (rule 4, against the matching Dm arm):** relP@2 drops by 0.031 (Cm5) and 0.044 (Cmx5). Neither exceeds 0.05. Against A5c, Cmx5 drops by 0.056; the script flags this, but the protocol's check is against Dm.
- **Gap closed** by Cm5 (vs L3@100% − A5c): crack IoU 3%, inactive IoU 2%, crack relF1@2 10%.
- **Interaction with 10% (P11), descriptive:** (Cm − Dm) at 5% minus at 10%: crack IoU +0.014, inactive IoU −0.053, relF1@2 +0.022. The loss moves crack more at 5% and inactive less.

## Required robustness reporting
Image bootstrap: cells resampled, paired, 2,000 resamples. Test IoU, cv02 runs.

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| **Dm5 − A5c, crack** | −0.017 | −0.013 | **[−0.024, −0.010]** | 0.00 |
| Dm5 − A5c, inactive | −0.015 | −0.018 | [−0.039, +0.011] | 0.11 |
| Dm5 − D5, crack | +0.045 | +0.041 | [+0.035, +0.056] | 1.00 |
| **Cm5 − Dm5, crack** | +0.023 | +0.009 | **[+0.005, +0.036]** | 0.99 |
| Cm5 − Dm5, inactive | +0.018 | +0.004 | [−0.051, +0.073] | 0.71 |
| Cmx5 − Dmx5, crack | −0.010 | −0.018 | [−0.023, +0.000] | 0.03 |
| Cm5 − A5c, crack | +0.006 | −0.004 | [−0.009, +0.015] | 0.80 |
| Cm5 − A5c, inactive | +0.003 | −0.014 | [−0.067, +0.060] | 0.54 |
| Cmx5 − A5c, crack | −0.010 | −0.017 | [−0.021, −0.002] | 0.01 |

**Source split (crack, Cm5 − Dm5):**
- CSIR+ARTS (21 cells): −0.025 [−0.061, +0.004].
- CFVS/BMRK/SDLE (29 cells): +0.032 [+0.016, +0.044].

**Required count:** inactive is present in 2 of the 23 labelled cells (shared with P10; `results/p10/labelled_set_counts.txt`).

**Reading:**
- **The loss effect on crack holds at 5% and replicates on gaint.** Cm5 − Dm5 passes the seed rule and the cell bootstrap on cv02. It shrinks to +0.009 without the top 3 cells, and it comes from the CFVS/BMRK/SDLE cells; on CSIR+ARTS its sign is negative (CI covers 0). On gaint, with fresh seeds, the same contrast is twice as large on crack IoU and relF1@2.
- **Inactive is not measurable at 5%.** Seed sd reaches 0.14 (2 of 23 labelled cells contain it). No inactive contrast is detectable in either direction.
- **The loss-off control is below supervised on crack, robustly.** Dm5 − A5c = −0.017 [−0.024, −0.010], in both source groups. That is larger than at 10% (P11: −0.007). gaint shows the same size descriptively (gDm5 − A5: −0.018; different seeds). The matched view removed the labelled-view part of the handicap (Dm5 − D5 = +0.045), so what remains is consistent with BatchNorm mixing. P13 tests that directly at 5% with a separate forward.
- **SSL vs supervised at 5%: no on cv02.** Cm5's crack gain over Dm5 (+0.023) about cancels the Dm5 handicap (−0.017), leaving +0.006 against A5c, not detectable. On gaint the same comparison passes the arithmetic (+0.029 crack IoU), but gaint cannot rescue a cv02 rule. The two machines disagree on the net SSL-vs-supervised verdict with 3 seeds each, which is why P13's primary contrast uses 5 seeds.
- **The external pool does not help at 5%.** Cmx5 ≈ Dmx5, and Cmx5 is below A5c on crack in the bootstrap (−0.010 [−0.021, −0.002]). Unlike Dm5, Dmx5 shows no crack handicap against A5c (0.305 vs 0.305).

**Bin-0 share** (GT px scored < 0.001, test):

| Arm | crack | inactive |
|---|---|---|
| A5c | 0.567 | 0.661 |
| Dm5 | 0.588 | 0.686 |
| Cm5 | 0.491 | 0.534 |
| Dmx5 | 0.561 | 0.651 |
| Cmx5 | 0.546 | 0.498 |

As in P8–P11, pseudo-labels de-saturate both classes (Cm5 vs Dm5). With the external pool the shift is smaller on crack (Cmx5 vs Dmx5).

## Caveats
- One split; 3 seeds per arm; 50 test cells.
- Inactive: 2 of the 23 labelled cells contain it.
- gaint arms use seeds 3–5; gaint's A5 uses seeds 0–2. They are never pooled with cv02.
- The relF1@2 bootstrap is in E1 (`results/e1`), not here.

## E1 addendum (after the locked analysis; descriptive)
Per-cell task metrics and the relF1@2 bootstrap, from `results/e1/e1_p12.md`. Paired image bootstrap, 2,000 resamples. Test = 50 cells; ext = 106 extension cells from unseen modules. E1's pooled test IoU equals the re-score exactly, and its leave-top-3-out matches `per_image_test.txt`.

| Contrast | Set | crack relF1@2 (pooled) | crack false alarm | inactive IoU (pooled) | inactive cell IoU |
|---|---|---|---|---|---|
| Cm5 − Dm5 | test | **+0.040 [+0.015, +0.061]** | 0 vs 0 | +0.018 [−0.051, +0.073] | +0.049 [−0.007, +0.110] |
| Cm5 − A5c | test | +0.015 [−0.005, +0.030] | 0 vs 0 | +0.003 [−0.067, +0.060] | +0.043 [−0.024, +0.116] |
| gCm5 − A5 (gaint) | test | **+0.058 [+0.037, +0.079]** | 0 vs 0 | **+0.068 [+0.022, +0.130]** | **+0.101 [+0.040, +0.176]** |
| Cm5 − A5c | ext | +0.000 [−0.039, +0.038] | **+0.095 [+0.035, +0.162]** (worse) | **+0.065 [+0.014, +0.128]** | **+0.212 [+0.065, +0.351]** |
| Cmx5 − A5c | ext | **−0.068 [−0.098, −0.041]** | **+0.234 [+0.142, +0.329]** (worse) | +0.008 [−0.041, +0.036] | **+0.130 [+0.079, +0.188]** |
| gCm5 − A5 (gaint) | ext | +0.022 [−0.014, +0.056] | **+0.104 [+0.046, +0.169]** (worse) | **+0.126 [+0.029, +0.246]** | **+0.445 [+0.218, +0.631]** |

- **cv02 test:** the crack relF1@2 gain of Cm5 over Dm5 is robust over cells; over A5c it is not.
- **gaint test:** gCm5 beats gaint's A5 on crack relF1@2 and on inactive, robustly over cells. It is the clearest SSL-over-supervised result so far, but it is on gaint with seeds 3–5 vs 0–2, and the locked rules give gaint no say.
- **Unseen modules, same pattern as P11:** tolerant PL raises crack false alarms (by about 0.10 of crack-free cells) and improves inactive. The external-pool arm over-predicts inactive there (area error +0.69 pp) and loses crack.
