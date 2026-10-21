# SKCDF track, design (agent 3, 21 Oct 2026)

Sources: SKCDF paper (`literature/pdfs/skcdf_cvpr2025/`, local only), official code `github.com/yinguanchun/SKCDF` at `12f807d` (cloned read-only to the scratchpad; file:line refs below are to that commit), P17 (`results/p17/README.md`), handbook 07, 10, 13, 14.

## 1. What SKCDF has, and what each part was built for

| Component | Paper / code | Built for (Synapse, 3-D CT) | Its own ablation (Table 3, 20% Synapse, avg Dice) |
|---|---|---|---|
| Baseline | Plain self-training: PL = argmax of the *current* model's labelled decoder, no threshold, no EMA teacher, joint BN, λu = 10 (`train_skcdf.py:249-278`) | | 44.66 |
| DF: data-flow decoupling | Unlabelled loss goes through `decoder_u`; `decoder_u ← 0.99·decoder_u + 0.01·decoder_l` per iteration (Eq. 6; `:227-231`) | Protect the labelled decoder from noisy PLs | +12.74 (57.40) |
| SKCM: cross-attention | Channel-wise local + global cross-attention between the labelled and unlabelled halves of the batch at the bottleneck; self-attention at inference (`models/SKCDF.py:751-770`) | "Same organ, fixed location across patients" | +1.77 over DF (59.17) |
| ABSH: auxiliary balanced head | A second 1x1 head on each decoder. Its loss is masked by a per-pixel Bernoulli draw with keep prob p_c = min_c N_c / N_c (`:205`, N from the first 4 labelled volumes, `:191-203`); unlabelled side: PL from the labelled aux head, keep prob annealed linearly from 1 to p_c over training (`:265-272`). Head transfer each iteration, order H→D→H: main_l ← EMA(aux_l), decoder_u (incl. both heads) ← EMA(decoder_l), main_u ← EMA(aux_u), ω = 0.99 (`:220-238`) | Small organs ignored by a head trained on frequency-skewed voxels (gallbladder 0 → 62) | +6.17 over DF (63.57; the text says 7.17, Table 3 gives 6.17) |
| Inference | `decoder_u` main head (`:315`) | | Table 4: with transfer, u 57.40 vs l 57.21 |
| λu | 10, sigmoid ramp over all 1500 epochs (`:26`, `:55-65`): 0.07 at start, 2.9 at mid-run, 10 only at the end; run mean ≈ 4.0 | | not ablated |
| Selection | best val Dice + early stop (`:338-346`) | | (we use final-step weights) |

Masking detail in code (`:259`, `:276`): masked pixels get logits × 0 and label × 0 (= background). Their gradient is zero, so this is an ignore mask whose CE is still averaged over all pixels: each kept pixel has the same per-pixel weight as in the main loss. The head becomes balanced because its positive/negative counts are balanced, not because rare pixels are up-weighted.

## 2. Why P17 found nothing, and what is left
- P17 ported DF alone onto BsM5: BsD5 − BsM5 −0.006 / +0.011 / −0.008, n.d.
- DF's +12.74 is measured against a baseline that lets every unthresholded current-model PL into the labelled decoder at λ up to 10, with joint BN. Our BsM5 already limits that harm: PL from an EMA teacher, confidence ≥ 0.95, separate BN, λ = 1. DF had little left to fix. P17 is consistent with that (n.d., not worse).
- P17 left one signal that points at the class prior, not at PL noise: half of all GT rare pixels get p < 0.001 (bin-0 share crack 0.526 / inactive 0.544 for BsD5; 0.440 / 0.442 for BsM5; 0.572 / 0.729 for A5c). These are confident misses: the head's prior sits far on the background side. At 5% crack is 0.30% and inactive 0.34% of labelled pixels (counted 21 Oct on gaint, `masks_escdd`, 23 cells).
- Hard PLs at 0.95 also feed the student almost no rare pixels from unlabelled cells, so the unlabelled loss mostly reinforces background.

**ABSH is the one SKCDF component aimed at that failure.** It trains a head on class-balanced pixels and pulls the evaluated head toward it every step. It was untested in P17.

## 3. Components and the decision per component

| Component | Decision | Reason |
|---|---|---|
| DF | Keep (base = BsD5) | ABSH in SKCDF sits on DF (H→D→H chain needs `decoder_u`); BsD5 ≈ BsM5 (P17), so it costs nothing; the reference runs exist |
| ABSH | **Test (primary)**, adapted (§4) | Targets the measured failure (rare-class prior, PL starvation) |
| SKCM | **Not ported** | +1.77 in their own ablation (n = 3 seeds, sd 0.9 to 2.0); its premise (same organ at a fixed location in every volume) does not hold for cracks, which sit anywhere on the cell; it pairs labelled with unlabelled images at train time but runs self-attention at test time; heavy at 512² |
| λu = 10 | **Not in v1** (candidate for v2) | Second question; their effective mean λ ≈ 4. Under DF a higher λ cannot touch the labelled decoder, so "DF enables a larger λ" is a clean follow-up (2x2: coupling x λ) |
| PL from current student, no threshold | Not ported | Our EMA teacher + 0.95 is the stronger recipe here (P13 BsM5); changing it is a separate question |
| Inference via `decoder_u` | Pre-registered **secondary** contrast; teacher stays primary | Comparability with P13–P17; P17 saw `decoder_u` above the teacher on crack in 5/5 seeds (+0.005 to +0.009), descriptive only |
| Best-val selection | Not ported | Standing rule: final-step weights |

## 4. Adapting ABSH to 2-D EL cells (each choice fixed before any run)

1. **Keep probability (clip and reference).** p_c = min(1, N_ref / N_c), N_ref = min(N_crack, N_inactive), N_c counted over **all** labelled cells of the split (23 at 5%), not 4. SKCDF's min over all present classes (`:205`) would let splice (1,944 px in 2 cells, not a target) set the scale and keep crack with p = 0.11. Our target classes are crack and inactive, so they set the reference; classes rarer than that get p = 1. At 5% (21 Oct count): crack 1.00, inactive 0.876, background 0.0049, padding 0.0113, other present classes 0.08 (ribbons) to 0.86 (corrosion); splice, material and gridline 1. Inactive's N comes from 2 cells (A1 in doc 13); p_inactive ≈ 0.88 is close to 1 either way, so the 2-cell count barely matters.
2. **Thin-structure band.** Pixels within 2 px (Chebyshev, 5x5 max-pool) of a rare-class target (crack or inactive, GT or PL) are always kept. Reason: a crack is 1 to 2 px wide; its width is decided by the background pixels next to it. With p_bg ≈ 0.005 the balanced head would almost never be penalised for a crack 2 px too wide, and the head transfer would carry that fattening into the evaluated head. The band adds about 2 negatives per crack pixel, so the head stays balanced. R = 2 matches the project's tolerance radius and relF1@2. Because this departs from SKCDF, a secondary arm runs without it.
3. **Normalisation.** Aux CE: sum over kept pixels / all pixels (SKCDF's effective scaling, §1). Aux Dice (crack, inactive, as `ce_dice`): over kept pixels only. So rare pixels get no extra per-pixel weight in the encoder; only the head's class balance changes.
4. **Heads.** smp U-Net++ head (`Conv2d 16→24, 3x3`). `aux_l` = copy of the labelled head at step 0; in SSL arms `aux_u` = copy too. Identical init means the transfer starts as a no-op.
5. **Unlabelled side.** `aux_u` (on `decoder_u` features of the strong CutMix view) learns from the EMA teacher's **aux head** argmax on the weak view, same confidence rule (≥ 0.95) as the main PL. Keep prob annealed linearly from 1 at step 0 to p_c at step 20,000 (SKCDF `:267`, epochs → steps), plus the band. Same λ as the main unlabelled loss. Only one thing changes relative to BsD5's PL rule: the balancing.
6. **Head transfer** after each optimizer step, SKCDF order H→D→H, ω = 0.99: (a) main_l ← ω·main_l + (1−ω)·aux_l; (b) `decoder_u`, main_u, aux_u ← ω·self + (1−ω)·(decoder_l, main_l, aux_l) (code transfers both heads with the decoder, `:227-231`); (c) main_u ← ω·main_u + (1−ω)·aux_u. Supervised arm: (a) only.
7. **Teacher.** EMA (0.999) of the student including `aux_l`. The evaluated weights stay "teacher encoder + labelled decoder + main head".
8. **Bernoulli draws** are a pure function of (seed, stream, step), as every other random draw in the trainer.

## 5. Questions and expected outcomes
- **Q1 (primary).** On BsD5 at 5%, does adapted ABSH raise rare-class IoU? Mechanism predicts: higher crack/inactive recall and AP, lower bin-0 share; risk: lower precision, fattening, more false crack on `CSIR_00070_r8_c4`.
- **Q2.** Is the gain SSL-specific? ABSH on the supervised arm (labelled side only). If AB5 − A5c ≈ BsDB5 − BsD5, ABSH is a class-imbalance fix for the head, not an SSL method, and the thesis should say so.
- **Q3.** Does the thin-structure band matter? BsDB5 vs BsDBn5 (SKCDF's mask, our reference and clip).
- Reading map: Q1 pass + Q2 n.d. → balanced PLs help (SSL-specific). Q1 pass + Q2 pass of similar size → head re-balancing, not SSL. Q1 worse → balancing harms thin structures (read precision and Q3).

## 6. Why this can succeed where P17 did not
P17 tested a guard against PL noise in a recipe that already guards against it. ABSH changes what the evaluated head predicts on rare pixels, which is where 44 to 53% of GT rare pixels are confidently missed. Synapse's evidence for it is a small-organ effect (+6.17 avg Dice, gallbladder 0 → 62 in Table 3 row 4 vs row 2). Our supervised loss already has a Dice term on crack and inactive, which is a partial rebalancing, so the gain may be smaller than on Synapse; that is what the seeds will show.

## 7. Compute (needs the leader's / critic's call)
- gaint has 1 GPU (RTX PRO 4500, 32.6 GB; 5.9 GB held by another python process on 21 Oct 13:38 IST) shared with the ALHVR track. The protocol needs 15 new runs plus references. On gaint the 5-seed references (A5c, BsD5) do not exist and would need 10 more runs: about 25 runs, roughly 1.5 to 2 days of the only GPU.
- cv02 (8x A6000) holds A5c s0–4 and BsD5 s0–4 at 5 seeds, same machine type as every P-series rule. Reusing them needs an identity check (protocol §7). New runs: 15, about 5 h on 5 to 8 GPUs.
- **Proposal: cv02**, all arms and references on cv02, backup relay to gaint afterwards. This is the "extra capacity" case in the README. Fallback if the leader prefers gaint: run all 5 arms on gaint at 5 seeds (25 runs), no reuse.
