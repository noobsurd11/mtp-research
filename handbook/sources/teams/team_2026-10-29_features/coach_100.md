# coach: settings for protocol_100 (MIM100 / CP100 vs SUP100), 30 Oct 2026

These are binding inputs for runner's `protocol_100.md`; APPROVED follows once they are folded in and smoked. Tags: E measured, S judgement.

## 0. New fact that drives (a) (E, CPU read on gaint, 30 Oct about 10:20)
Per-tensor cosine of encoder conv weights, final (step 20k) vs init, house recipe (Adam 1e-3, coupled L2 wd 1e-4, 20k steps):

| stage | MIM moved it, cos(MIM, ImageNet) | A5c-f1, cos(final, ImageNet) | MIM5, cos(final, MIM init) | SUP100 p6_L3 s0, cos(final, ImageNet) | SUP100 s0 vs s1 | norm final/init (SUP100) |
|---|---|---|---|---|---|---|
| conv1 | 0.996 | 0.980 | 0.976 | 0.985 | 0.997 | 0.86 |
| layer1 | 0.859 | 0.379 | 0.327 | 0.396 | 0.623 | 0.75 |
| layer2 | 0.761 | 0.135 | 0.139 | 0.150 | 0.223 | 0.60 |
| layer3 | 0.618 | 0.010 | 0.005 | 0.018 | 0.037 | 0.09 |
| layer4 | 0.533 | −0.001 | −0.000 | 0.001 | 0.007 | 0.06 |

- In every fine-tune, including SUP100 at 100%, layer3-4 end orthogonal to their init, and to each other across seeds. Their norms fall to 2-9% of init.
- So only conv1 and part of layer1 carry any init into the final model. The deep ImageNet features are re-learned from labels, and so were MIM's.
- This explains MIM5's n.d. MIM changed mostly layer2-4, and fine-tuning erased exactly those (MIM5 final vs MIM init 0.000-0.139).
- Likely cause (S): Adam with coupled L2 on conv weights followed by BN (scale-invariant). The norm decays far below init, the angular step per update grows, and the direction randomises.
- The optimizer was never varied in R1-R5 or the P-series.

**Handbook paragraph (encoder erasure, 30 Oct 2026, E unless tagged).** The house fine-tune leaves almost nothing of the encoder's init in the deep layers, whichever init it starts from. The recipe is Adam lr 1e-3, coupled L2 weight decay 1e-4, 200-step warmup and cosine, 20k steps, batch 8 (`configs/base.yaml`).
- **Measurement:** per-tensor cosine between final (step 20,000, `latest.pth`) and initial encoder conv weights, averaged per ResNet-34 stage. Runs: A5c-f1 s0 and s1 (5%), MIM5 s0 (5%, MIM init), SUP100 `p6_L3_100pct_s0` and s1 (100%), all on gaint `el_f1` / `cv02_noob_el`.
- **Cosine to init:** conv1 0.96-0.99; layer1 0.33-0.40; layer2 0.13-0.15; layer3 0.005-0.018; layer4 −0.001-0.001.
- **Across seeds:** two SUP100 seeds agree with each other only at conv1 (0.997) and layer1 (0.62). At layer2-4 they are 0.22, 0.04 and 0.007.
- **Norms** (mean over tensors of the per-tensor norm ratio; runner's stage-concatenated L2 gives 0.86 / 0.75 / 0.63 / 0.10 / 0.06):  final/init ratios are 0.86 (conv1), 0.75 (layer1), 0.60 (layer2), 0.09 (layer3) and 0.06 (layer4) for SUP100. At 5% they are 0.00-0.06 in layer3-4.
- **What this means:** in every model trained so far, including FINAL's members, the ImageNet init survives only in conv1 and partly layer1. layer3-4 are re-learned from labels.
- **Consequences:**
  - Any encoder pretraining (ImageNet, MIM5, P15's UCF-EL) can only act through the first two stages under this recipe. That is consistent with MIM5's n.d.: MIM changed mostly layer2-4 (cosine to ImageNet 0.53-0.76), and fine-tuning reset them (MIM5 final vs MIM init 0.000-0.139).
  - The optimizer (Adam vs AdamW, encoder lr and weight decay, freezing) was never varied in the P-series or Track M R1-R5. Every "init does not matter" or "pretraining does not help" result so far is conditional on this recipe.
- **Mechanism (S):** conv weights followed by BatchNorm are scale-invariant. Under Adam with coupled L2 their norm decays far below init, the angular step per update grows, and the direction randomises before the cosine schedule freezes it.
- **Test (protocol_100):** SUP100-PF and MIM100-PF use an encoder-preserving fine-tune: frozen for 1k steps, then 0.1x lr, encoder wd 0.

## (a) MIM100: an encoder-preserving fine-tune (PF), part of the arm
- **PF package** (the encoder param group only; decoder and head as house):
  - encoder frozen for steps 0-999 (no grad; BN in train mode, so its running stats adapt);
  - then encoder lr ramps 0 → 0.1 × base over 1,000 steps, on top of the house warmup/cosine (peak 1e-4);
  - encoder weight decay 0.
- **Why PF and not plain:**
  - Plain MIM100 would test only conv1/layer1 transfer, which MIM5 already showed to be n.d.-negative.
  - Lower lr alone keeps the coupled-L2 shrinkage; wd 0 is what stops the norm collapse.
  - The freeze stops a random decoder's early gradients hitting pretrained features (same logic as the MIM pretraining freeze).
- **Smoke gate (val-blind):** MIM100-PF at step 2,000. Per-stage mean cosine to encoder_final must be ≥ 0.5 for layer3 and layer4; else PF is not preserving, so fix it before launch. Report the same table at 20k.
- **Code:** one switch, e.g. `training.encoder_pf={freeze:1000, ramp:1000, lr_mult:0.1, wd:0}`.
  - Absent: bit-identical to house (I1).
  - Test: freeze 0, mult 1, wd = base, ramp 0 equals house (I2-like).
- **Attribution (my recommendation: a 4th arm SUP100-PF, ImageNet init + PF):**
  - MIM100-PF vs SUP100 changes the init and the optimizer together. The table shows the optimizer change is large, not cosmetic.
  - SUP100-PF is also a recipe candidate in its own right. Track D found frozen ImageNet stride-4/8 features rank BMRK crack better than a fine-tuned encoder, and PF keeps them.
  - The 3 contrasts:
    - MIM100-PF − SUP100-PF: the pool question, clean;
    - SUP100-PF − SUP100: the recipe question;
    - MIM100-PF − SUP100: the bottom line.
  - If team-lead keeps 3 arms: MIM100-PF − SUP100 is the test. SUP100-PF (5 seeds) is pre-registered as a conditional control that runs only on a pass, and nothing is claimed as "the pool helps" before it. A null closes "MIM init + PF at 100%".

## (b) CP100: paste rate and weight
- **Library:** all train cells minus the 7 D7 twins. The twins' cracks are test-cell cracks, and pasting them multiplies test exposure.
  - Same filters as CP5 (≥ 20 px, contrast ≥ 3 GL, edge and inactive ring) plus the P3 residual fix.
  - Count, per-source composition and kept-list md5 frozen in the protocol.
- **Backgrounds:** the pool part of `mim_pool_v11` only (`p_pool 1.0`); at 100% there are no unlabelled train cells. Held-out: the 256 monitor cells, decoy only.
- **Rate and weight unchanged from CP5:** λ 1, cp.batch 4, K ~ U{1,2,3}, components sampled uniformly, no source rebalancing.
  - Why: at 100% the labelled stream already holds every real crack shape. CP adds only crack-on-new-backgrounds.
  - More components lower memorisation risk but are no reason for more weight. A higher rate mainly raises the shortcut and precision risk the decoy test guards.
  - Runner measures labelled crack px per step at 100% (smoke) and states it. If it exceeds 12k px/step, cp.batch goes to 8, keeping pasted/labelled ≥ 0.4.
- **Gates and rule as CP5:** decoy go/no-go at 2k vs SUP100 2k on the same machine; E3b on the 20k checkpoints; a crack claim needs C1 and C2 (LA-matched), two-set rule. CP100 keeps the house optimizer (one change per arm).

## (c) Baseline
- **gaint arms:** fresh SUP100 5 seeds on gaint at the arms' deploy commit. The cv02 seeds are invalid there:
  - A6000 and Blackwell kernels are not bit-identical;
  - the seeds come from two commits (824fab0, bac5264);
  - the house rule is one hardware type and one commit.
- **cv02 arms:** reuse `p6_L3_100pct_s0-2` + `p16_A_100pct_s3-4` only if I1 passes on an A6000 at the deploy commit, all switches off, 100% opts. The stdout loss/lr/val lines must be bit-identical for 2,000 steps against both `p6_L3_100pct_s0.stdout` and `p16_A_100pct_s3.stdout`, and the data md5 must equal what those runs used. Otherwise run a fresh SUP100 on cv02.
- **Machine (S):** cv02 if ≥ 4 GPUs are free. 15-20 runs take about 3-5 h there vs about 13-17 h on gaint (3 concurrent, about 2.5 h each, CP 1.5x). All arms on one machine.

## Rule, power, ensemble
- Rule 1 /3 vs SUP100 (and the PF contrasts above), primaries and the two-set verdict as MIM5; /5 descriptive.
- **Power (E, Track M):** without the noisy cell, SUP100's thresholds sit at the 0.01 floor for crack and relF1. On all 50 the crack threshold is about 0.09, because one seed in five fails on CSIR_00070. In practice a pass is noNoisy BETTER with a same-sign n.d. on all 50.
- **Expectation (S):** n.d. for MIM100-PF and CP100. SUP100-PF is the open question.
- **If a pass:** compare the arm's 5-seed mean-softmax ensemble with the same-machine SUP100 ensemble.
  - The crack bias is chosen on val by FINAL's rule: max val relF1@2, val precision drop < 0.05, TTA off.
  - Paired image bootstrap as Track M contrast 1.
  - FINAL 0.492 is the yardstick. It is the comparator itself only if the cv02 seeds are reused on cv02.
- **Multiplicity:** 3-4 contrasts x 3 primaries x 2 sets, no correction, disclosed.

## Speed-ups (team-lead, 30 Oct about 10:50; 20 runs on gaint, 3 at once, about 20 h)
1. **Val only at start and end: YES, if identity is proven.**
   - The reported numbers use final-step weights; best.pth and the val curve are unused.
   - Condition: at the deploy commit, val_every 500 vs val off (val at step 0 and 20,000 only) gives bit-identical loss/lr lines for ≥ 2,000 steps, spanning 4 skipped vals.
   - The check runs for the house opts and for the CP opts. The train loader has its own seeded generator (`train.py` l.446), but the val loader's iterator may draw from the global RNG, so prove it rather than assume it.
   - The identity runs themselves (I1, PF neutral, λ 0) keep val every 500, because their val lines are part of the check.
   - Expected gain: about 5-10% (S).
2. **bf16 autocast: already on.**
   - `configs/base.yaml` has `amp: true, amp_dtype: bfloat16`, and every run log shows `amp=True(bfloat16)`. SUP100, A5c and all arms already use it, so there is nothing to switch.
   - Any further numeric speed-up is NO for this protocol: TF32, channels_last, `cudnn.benchmark` (it also breaks `deterministic: true`), torch.compile.
   - Why: it breaks I1 against 1be64e1, and the erasure dynamics depend on optimizer numerics. An untested numeric change would sit under the recipe contrast (SUP100-PF − SUP100-g), which is exactly the dynamics PF changes.
3. **Optional (mine): a 4th concurrent lane through the allocator, not numerics.**
   - Runner checks `max_memory_allocated` per fine-tune in a smoke. If it is ≤ 5.5 GB, set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` for all runs; that lowers reserved memory without changing numerics. Four fine-tunes may then fit: 5.9 + 4 x 5.5 = 27.9 GB, leaving ≥ 2 GB.
   - Condition: a 1,000-step identity with the setting on vs off, and the ≥ 2 GB-free rule held by the existing gate.
   - Gain: up to about 1.3x throughput if 4 lanes fit. CP (9.5 GB) stays one at a time.

## Rulings after diag_5pct_to_100pct.md (30 Oct 11:04)
1. **MIM: team-lead's read is confirmed.**
   - The MIM5 null bounds MIM only under the house optimizer. That optimizer erases layer2-4, where MIM acted (§0; MIM5 final vs MIM init 0.000-0.139).
   - diag's addendum retracts its own "don't lower the encoder lr" for the same reason, and diag's "MIM5 drift" measurement is §0.
   - So **MIM100-PF − SUP100-PF stays the direct answer to the user's question**, with SUP100-PF unconditional.
   - diag's expected MIM100 −0.010 to +0.005 applies to plain MIM100 only. Under PF the expectation is unknown (S), and the pre-stated expectation in protocol_100 must say so.
2. **CP100 backgrounds: pool only (`mim_pool_v11` pool part, 11,219 cells). K 1-3 per background in both designs.**
   - Why: each labelled train cell is already seen about 335 times in the labelled stream (20k x 8 / 478), so as backgrounds it adds no variety.
   - Pasting onto it needs new GT-aware ring/ignore code, or the 2-6 px ring labels real cracks as not-crack. That is a new code path with no expected gain, while the 11k pool cells are the variety the COCO evidence favours.
   - The classic in-batch copy-paste (paste into the labelled batch with full-label loss, R doi:10.1109/cvpr46437.2021.00294) is a different arm. It is a follow-up only if CP100 shows a same-sign gain.
3. **Power (diag, E):** clean MDE at 100% is crack 0.012 and inactive 0.032. protocol_100 states both next to each arm's pre-stated expectation (rule 3 of `coach_strategy.md`).
