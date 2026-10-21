# ALHVR on EL: diagnosis and design (agent 1, 21 Oct 2026)

Status: design for protocol_v1. §D0 rules were fixed before D0 ran (log 14:10 IST); results in §D0-results.
Sources: paper + supplement (CVF open access, read in full), reference code (gaint `refs/ALHVR/train_ALHVR/code`), `docs/alhvr_port_notes.md`, `analysis/alhvr_audit.md`, handbook 05 §6, 10, 13 B3/E11, P5. D0 raw files: `alhvr/d0/`.

## 1. Why the old port is not evidence (handbook 13 B3, E11; audit §1)
- λ followed the reference whole-run ramp (0.1·exp(−5(1−t/T)²), full only at the last step) under Adam with cosine-to-zero LR. LR-weighted mean λ 0.0156 (reference at constant LR: 0.0393); λ·unsup/sup was 0.7% at step 2k and 17.7% at 10k, and reached 89% only at step 19k, when LR was 0.6% of peak.
- Old-era base: from-scratch SA-U-Net++, weighted CE, batch 4+4, joint BN with the perturbed pass, coin perturbation.
- So "ALHVR = its λ=0 control" says nothing about ALHVR. Still standing: cross-network prototypes were 4.6% correct on Ω3 crack (old nets).

## 2. What ALHVR is, and what the paper actually shows
- Two independently initialised networks, no EMA. Each: clean pass + feature-perturbed pass (same decoder). γ = mean of the lowest β = 0.8 share of the mean perturbed confidence, over the whole unlabelled batch. Ω1 (both ≥ γ): **no unlabelled loss**. Ω2 (one confident): CG-CPCL, cosine-to-prototype CE toward the confident partner's argmax + a cosine pull. Ω3 (neither): DTCT, MSE from the perturbed output to the sharpened clean output of the more confident network + entropy of both outputs.
- Paper facts checked in the PDF: λ(t) = 0.1·exp(−5(1−t/t_max)²) (the square is printed; settles the note conflict in handbook 05 §6.2). Sharpening cites [29] = UDA (Xie 2020), whose sharpening is class-normalised; the code's elementwise form is a code deviation.
- Table 5 (ACDC 10%): baseline with neither module 86.61 Dice, CPCL only 89.32, DTCT only 89.19, both 90.56; supervised U-Net 81.59 (Table 2). So most of the gain over supervised (+5.0 of +9.0) comes from the unnamed two-network baseline, not from the modules (+3.95).
- Table 1 (CPS on ACDC 10%): masking out Ω1 gives the best Dice (88.58 vs 85.34 with all regions). This is the premise. It is untested on thin rare classes.
- ACDC is trained as 2-D slices (256²): 136 labelled / 1,176 unlabelled slices at 10%. Our 5% split: 23 labelled / 455 unlabelled cells at 512². Unlabelled pixels: 119.3M vs 77.1M; U:L ratio 19.8 vs 8.6. **The in-domain pool is not small relative to ALHVR's ACDC setting.** What differs is the class structure: K = 24 vs 4, crack 0.19% of train pixels, 1–2 px wide; inactive in 2 of 23 labelled cells.

## 3. D0: pre-design diagnostic (inference only)
Surrogate pair = two A5c supervised runs (L3 base, 5%, final weights); pairs (p12_A_5pct_s0, s1) and (p13_A_5pct_s3, s4) (configs differ only in run_name and seed). Data: the 455 unlabelled cells (seed-0 5% split), batches of 8, train-mode BN with frozen running stats. Revised masks only score routing and targets. Script `alhvr/d0/d0_alhvr_probe.py` (gaint `/home/noob/work/alhvr_diag/`).
Caveat fixed in advance: fully and independently trained nets are more confident and less correlated than A and B at λ-on (step 2,000). D0 sizes mechanisms; it does not forecast the run.

Rules (fixed before running):
- **D0-1 feature layer.** CG-CPCL uses `x_0_4` (decoder output, full res, 16 ch; the paper's "second-to-last layer") unless `x_0_1` (1/8 res, 128 ch; the reference code's resolution) beats it by > 0.02 on cross-network Ω2a crack accuracy.
- **D0-2 sharpening.** Class-normalised (UDA form) regardless; D0 only sizes the elementwise failure.
- **D0-3 FeatureDropout.** If the dropout-perturbed pass keeps < 50% of the clean pass's crack predictions, use FeatureNoise only.
- **D0-4 λ.** Each SSL arm's λ_max = BsM ratio / arm ratio (median ‖∇L_u‖/‖∇L_sup‖ over 12 batches, network A), mean over pairs, rounded (log scale) to {0.01, 0.03, 0.1, 0.3, 1, 3, 10}. This matches each arm's unlabelled gradient share to BsM5's at λ 1.
- **D0-5 CG-CPCL.** Kept in the full arm. If the crack prototype is present in < 50% of batches or cross-network Ω2a crack accuracy < 0.10, flag "near-inactive for crack".

## D0-results
D0 ran with the reference coin (dropout | noise). D0-3 fired, so D0b repeated the probe with noise only, the configuration the arms use; D0-1/4/5 are applied to D0b. Two numbers per cell = pair 1, pair 2.

| Measure | D0 (coin) | D0b (noise only) |
|---|---|---|
| γ | 0.957, 0.974 | 0.989, 0.989 |
| pixel share Ω1 / Ω2 / Ω3 | 0.72/0.26/0.017; 0.80/0.19/0.017 | 0.91/0.066/0.022; 0.91/0.066/0.022 |
| GT crack in Ω1 / Ω2 / Ω3 | 0.65/0.31/0.04; 0.67/0.28/0.05 | 0.69/0.24/0.07; 0.65/0.26/0.09 |
| GT inactive in Ω1 / Ω2 / Ω3 | 0.58/0.35/0.07; 0.56/0.35/0.09 | 0.55/0.33/0.12; 0.45/0.36/0.19 |
| Ω3 winner crack precision (strict; 2 px) | 0.38, 0.34; 0.76, 0.71 | 0.29, 0.29; 0.65, 0.66 |
| Ω3 GT-crack recall by winner | 0.26, 0.24 | 0.16, 0.14 |
| Ω3 share with winner max p < 0.5 | 0.0008, 0.0012 | 0.0020, 0.0024 |
| Ω2 partner-target crack precision (strict; 2 px) | 0.44, 0.44; 0.81, 0.83 | 0.39, 0.39; 0.79, 0.79 |
| Ω2 GT-crack recall by target | 0.37, 0.34 | 0.35, 0.34 |
| BsM-like PL (≥ 0.95, net A): pixel share; crack precision (strict; 2 px); GT-crack coverage | 0.96; 0.48, 0.50; 0.86, 0.88; 0.37, 0.35 | same (no perturbation) |
| dropout pass keeps clean crack predictions | 0.022, 0.019 | n/a |
| noise pass keeps clean crack predictions | 0.91, 0.92 | – |
| FeatureDropout keep rate, levels 1–4 (all cells) | 0.003–0.014 | – |
| same at GT-crack cells | 0.002–0.021 | – |
| cross-net Ω2a crack acc, `x_0_1` / `x_0_4` | 0.000, 0.055 / 0.048, 0.228 | 0.000, 0.028 / 0.086, 0.330 |
| own-net Ω2a crack acc, `x_0_4` | 0.18, 0.25 | 0.48, 0.40 |
| cos(A proto, B proto), `x_0_1` / `x_0_4` | 0.000 / 0.49, 0.41 | same |
| crack prototype present (batches) | 1.00 | 1.00 |
| grad ratio ‖∇L_u‖/‖∇L_sup‖ at λ 1: BsM / CPS / ALHVR-EL full / DTCT only / reference code | 28.4, 20.6 / 215, 118 / 300, 235 / 183, 144 / 183, 144 | 28.4, 20.6 / 60.2, 32.4 / 201, 171 / 91.3, 61.7 / 89.4, 61.3 |

Verdicts on the rules (D0b):
- **D0-1:** `x_0_4` (cross crack acc 0.086/0.330 vs 0.000/0.028). The 1/8-resolution features of two independently trained nets sit on disjoint channels (prototype cos 0.000, checked by hand: 4e-40 with norms 0.40/0.65), so the reference-code layer cannot carry cross-network prototypes at all.
- **D0-2:** class-normalised sharpening. The elementwise failure (audit item 4) is negligible on this base: 0.2% of Ω3 pixels, target sums 0.997. It mattered on the old from-scratch nets, not here.
- **D0-3 fired:** FeatureDropout zeroes 96–99.7% of positions at encoder levels 1–4 (keep threshold 0.7–0.9 × max attention), and the dropout pass keeps 2% of the clean crack predictions. Crack and non-crack cells are dropped alike, so it is not crack-specific; it erases the encoder. Noise only.
- **D0-4 (superseded by D0c, below):** λ_max per pair: full 0.141, 0.120 → mean 0.131 → **0.1**; DTCT-only 0.311, 0.333 → 0.322 → 0.3; CPS 0.472, 0.635 → 0.553 → **1.0** (borderline: the log midpoint of 0.3 and 1 is 0.548). The paper's own 0.1 coincides with the full arm. For the DTCT-only ablation the protocol keeps λ 0.1 (the full arm's), so full − DTCT-only differs in CPCL only; 0.3 is reported, not used.
- **D0c (gradient probe re-run with the worktree's own loss code and the exact arm configs, incl. `pull: target`; `d0/d0c_grad.json`):** λ_max per pair AL 0.110, 0.132 → **0.1**; DTCT-only 0.262, 0.340 → 0.3 (not used: ALd5 inherits AL5's 0.1); CPS 0.451, 0.731 → 0.591 → **1.0** (clear of the 0.548 midpoint); CPS routed 0.741, 1.088 → 1.0 (inherits CPS's 1.0). D0b's gradient probe used my reimplementation with the pull term off, so D0c is the one applied.
- **D0-5:** crack prototype present in 100% of batches; cross-net Ω2a crack acc mean 0.208 ≥ 0.10 → not flagged (pair 1 alone, 0.086, is below).

What D0 says about ALHVR on this base (reading):
1. **Routing leaves most rare-class pixels with no unlabelled loss.** With noise only, Ω1 is 91% of pixels and holds 65–69% of GT crack and 45–55% of GT inactive; ALHVR applies nothing there. Ω2+Ω3 hold 31–35% of crack on 9% of pixels. The BsM rule trains on 96% of pixels, covering 35–37% of GT crack as crack at precision 0.48–0.50 (0.86–0.88 within 2 px). In the old port Ω3 held 71% of crack; the pretrained, CE+Dice base is much more confident, so the "high-value region" premise must be re-tested here. CPS5 vs AL5 is that test (routing vs all pixels).
2. **DTCT targets on crack are "right place, wrong pixel"**: strict 0.29, within 2 px 0.65 (as P5).
3. **Ω2 targets are better than Ω3's** (crack 0.39 strict, 0.79 within 2 px).
4. **The masked-mean normalisation concentrates the gradient**: DTCT's MSE is averaged over Ω3 pixels only (2% of pixels), so per-pixel weight is ~45× a full-image mean. This is why the ALHVR gradient ratios at λ 1 are 3–9× BsM's, and why λ 0.1 (paper) matches BsM's share.
5. **Feature layer and perturbation must change for this encoder**; both are reference-code choices that do not transfer.

## 4. Design: ALHVR-EL (per component)

| Component | Reference | ALHVR-EL | Grounds |
|---|---|---|---|
| Base | 2-D U-Net from scratch, CE+Dice, SGD 0.01 const, 30k, 8+8 | P-series L3: smp U-Net++ ImageNet R34, CE+Dice (crack, inactive), label-safe aug, revised masks, Adam 1e-3 200-step warm-up + cosine to 0, 20k steps, 8+8, bf16 | Comparison must be against today's supervised and SSL arms (handbook 10, 11) |
| Two networks | different random inits | both ImageNet encoder; decoders differ by init seed (seed+1, built under a forked RNG) | Base recipe; D0 shows the pair still disagrees on 9% of pixels under noise |
| BN | one joint batch; decoder BN sees clean and perturbed passes | labelled forward per network updates BN; unlabelled clean + perturbed passes inside `frozen_bn_stats` | P12: joint BN cost −0.017 crack IoU at 5%; P13 fix. At λ = 0, network A is the supervised run bit for bit (CPU test; GPU check C1) |
| Views | one augmented view | one label-safe view (flips, rot90, brightness/contrast), own instance for the unlabelled stream; no CutMix | Faithful (feature perturbation is ALHVR's perturbation); label-safe for 1–2 px cracks (P6) |
| Perturbation | coin: FeatureDropout or FeatureNoise on every encoder level | FeatureNoise only, on encoder features 1–5 (feature 0 is the input image, unused by the decoder) | D0-3 |
| γ, regions | β 0.8, batch-pooled, perturbed confidences | unchanged | Paper; β untuned (Table 6 range 0.7–0.8) |
| CG-CPCL | 1/8-res feature, cosine logits scale 1, pull to all prototypes, prototypes from the batch | `x_0_4` full-res decoder output; scale 10; pull only to the pseudo-label's own prototype (`pull: target`); absent classes skipped; prototypes not detached (as reference) | D0-1; scale 1 has an irreducible CE floor of 1.41 at K = 24 (audit 5); pull-to-all contradicts the CE (port notes 5.3) and Eq. 20 reads as the target prototype |
| DTCT | elementwise sharpening T 0.1, target not detached, MSE on Ω3 + entropy | class-normalised sharpening T 0.1; target detached; MSE + entropy unchanged | D0-2; [29]; a teacher is a target |
| λ | whole-run ramp to 0.1 | 0 for 2k steps, linear to λ_max by 4k, then constant (the P-series schedule, = BsM5's); λ_max by D0-4 | Audit 1. LR-weighted mean λ = 0.715·λ_max (0.0715 at 0.1; reference 0.039; old port 0.0156); 62% of LR mass after step 4k |
| Evaluation | best-val per network | network A, final step (latest.pth), test, revised masks; B and the A+B ensemble descriptive | Standing rules |

Not adopted, with reasons: per-class γ (P5: moves crack out of Ω3 only by lowering precision); tolerant targets (CsM5 − BsM5 n.d., P13 Am. 2); CutMix in ALHVR arms (would make AL5 − CPS5 / AL5 − A5 test CutMix too; possible follow-up); external pool (in-domain pool is already larger than ACDC's relative to labels).

## 5. Arms (detail in protocol_v1)
A5 supervised (new commit; λ = 0 control), AL5 ALHVR-EL (λ 0.1), ALd5 = AL5 with CPCL off (λ 0.1), CPS5 = same two-network pipeline with CE from each perturbed output to the partner's clean argmax on all pixels (λ 1.0), CPSm5 = CPS5 with Ω1 zeroed (the one-change routing test, λ 1.0; added after agent 2's point 3), BsM5 reference (reused if check C2 passes and D7 = no). cv02, 5 seeds each.
