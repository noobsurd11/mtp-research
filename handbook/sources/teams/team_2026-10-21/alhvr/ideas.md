# ALHVR track: critic's ideas (agent 2)

Started 21 Oct 2026, 14:00 IST. Every paper below was returned by the Research MCP; ids are as returned. Our own measurements cite repo files. "Reading:" marks interpretation.

## 0. What we already know (sets the bar for any new run)
- Ω3 (neither network confident) holds 71% of GT crack on 383 held-out train images; P5 gives 72%, with strict precision 0.27 and 0.64 within 2 px (`analysis/alhvr_audit.md`; `results/p5_region_pl/README.md`).
- DTCT winner accuracy in Ω3: crack 61.9%, inactive 51.2% (handbook 05 §6.3).
- Cross-network prototypes: crack accuracy 4.6% (1.1% per batch). Prototype fixes are a closed negative result (handbook 05 §6.3).
- The project's best SSL arm so far is BsM5 (hard PL + CutMix + separate BN): +0.029 / +0.107 / +0.045 over A5c on cv02, 5 v 5 (handbook 00 fact 8).
- Reading: any ALHVR result has to be read against BsM5, not only against supervised. "ALHVR beats SL" alone is not a contribution if a plain MT recipe already does better.

## 1. Which ALHVR component could genuinely help rare thin defects

### 1a. DTCT alone (drop CG-CPCL). Highest prior.
- Why: the value premise holds for crack (most crack is in Ω3), and DTCT is the only part whose signal for crack is better than chance (62%). CG-CPCL's prototype signal is near zero for crack (4.6%). Its CE also sits on a floor of about 1.41 at K = 24, so it adds loss value without useful gradient (audit item 5).
- Reference code detail that matters: the prototype loss compares network 1's *perturbed* features with network 2's prototypes (`compute_prototype_loss`: `calDist_2D(fts_aux1, prototype2)`). These are two independently initialised feature spaces with no alignment term. Reading: this is a structural reason the cross-network prototypes are dead. It is not a porting bug, and it will not be fixed by λ scheduling.
- Fix DTCT's target for K = 24: use class-normalised sharpening (softmax(log p / T)) instead of elementwise binary sharpening. Elementwise sharpening sends the target to about the zero vector whenever the winner's max prob < 0.5 (audit item 4). One change, flag already exists (`alhvr.sharpening: softmax`).
- Optional: an offset-tolerant DTCT target (R = 2 px, as in the P7 tolerant PL). P5 says the winner is in the right place but the wrong pixel (0.27 strict vs 0.64 at 2 px). Arm only after 1a passes.

### 1b. Check FeatureDropout against thin cracks before trusting γ (diagnostic, no training)
- Reference `FeatureDropout` zeros every spatial position whose channel-mean activation exceeds U(0.7, 0.9) × the per-image max (`networks/unet.py`). γ and the regions are computed from the **perturbed** confidences.
- Hypothesis: if crack pixels are among the most activated positions, the perturbed branch loses exactly the crack evidence. Crack then lands in Ω3 because of the perturbation, not because of genuine ambiguity.
- Probe, about 2 min on any trained pair: per level, the share of GT crack pixels (and of background) zeroed by FeatureDropout, and the Ω3 share of crack under FeatureNoise only against FeatureDropout only.
- If crack is dropped at several times the background rate, propose noise-only perturbation as the EL adaptation.

### 1c. Class-aware γ: low prior, already measured
- P5: per-class γ moves 40 points of crack out of Ω3 only by lowering precision (`results/p5_region_pl/README.md`). Do not spend a run on it unless 1a passes.

### 1d. Batch-global γ with few unlabelled images
- γ is the mean of the lowest 80% of confidences over the whole unlabelled batch. With 8 images of 512², crack is about 0.2% of pixels, so γ is set entirely by background and structure classes. Reading: this is the right premise for ACDC organs and a questionable one for crack. Cheap diagnostic: log the crack share of Ω1/Ω2/Ω3 per logged step from GT on a held-out labelled stream (or from the trainer's existing diagnostics).

## 2. Rival hypotheses a reviewer would raise (each is one arm)
- **BUR, the opposite allocation:** labelled loss focused on high-uncertainty regions, unlabelled loss only on low-uncertainty regions. Zhou et al., "Bidirectional uncertainty-aware region learning for semi-supervised medical image segmentation", Neural Networks 2026, doi:10.1016/j.neunet.2026.109532 (arXiv 2502.07457). Reading: for rare thin classes, ambiguous crack pixels may be better learned from the 23 labelled images than from 62%-accurate pseudo-labels.
- **CSL**, random masking of reliable pixels: Liu and Liu, "When Confidence Fails: Revisiting Pseudo-Label Selection in Semi-Supervised Semantic Segmentation", ICCV 2025, doi:10.1109/iccv51701.2025.02031. Class-agnostic counterpart of ALHVR's Table 1.

## 3. Fair baselines a reviewer would demand
1. **Supervised, same machine, same steps** (= the loss-off control if the forward is separated as in P13). Mandatory.
2. **ALHVR λ = 0 control** with the identical two-network forward. Mandatory if the forward is not bit-identical to supervised.
3. **CPS**: Chen et al., "Semi-Supervised Semantic Segmentation with Cross Pseudo Supervision", CVPR 2021, doi:10.1109/cvpr46437.2021.00264. Same two networks, same init, hard cross pseudo-labels everywhere, no routing. It answers whether ALHVR's region routing adds anything over plain two-network co-training. ALHVR's own Table 1 is built on CPS.
4. **BsM recipe (our MT, hard PL + CutMix, separate BN)**, rerun on the same machine. It answers whether ALHVR beats the project's existing best SSL recipe.
5. **DCF routing**: Wan et al., "Breaking error coupling via divergent–convergent coordination for semi-supervised medical image segmentation", Medical Image Analysis 2026, doi:10.1016/j.media.2026.104236. The ALHVR-citing routing baseline (handbook 05 §6.4). Its code availability is unchecked, so it is lower priority than 3 and 4.
6. **Two-network compute control (descriptive):** ALHVR trains two networks, i.e. 2× parameters and compute. We score network A only, so no ensemble gain enters. State this in every table.
- Also relevant, MCF (ancestor of DTCT): Wang et al., "MCF: Mutual Correction Framework for Semi-Supervised Medical Image Segmentation", CVPR 2023, doi:10.1109/cvpr52729.2023.01502.

## 4. Rare-class SSL ideas (not ALHVR, for later)
- Re-distributing pseudo-labels to the labelled class prior (DARS): He et al., ICCV 2021, doi:10.1109/iccv48922.2021.00685. Directly targets collapse of rare classes in pseudo-labels, which P10 saw at 5%.
- Adaptive equalization (AEL): Hu et al., arXiv:2110.05474. Rare-class sampling and loss reweighting for SSL segmentation.
- Weak-to-strong consistency (UniMatch): Yang et al., CVPR 2023, doi:10.1109/cvpr52729.2023.00699. The standard modern SSL baseline; its feature-perturbation stream is the closest analogue to ALHVR's perturbed decoder.

## 5. Data ideas (with agent 4, see `data/decision.md`)
- HF `sasan/scdd-unlabeled` (159,332 cells, by an E-SCDD co-author) looks like a mirror of Pratt's 150k Dropbox pool. ALHVR was designed for large unlabelled pools, so a pool-size arm is natural. It is gated on content dedup against our 582 + E1 + the 17 new `_rf` cells, and on the pool-mismatch facts (handbook 03 §6). Not for the first protocol.
