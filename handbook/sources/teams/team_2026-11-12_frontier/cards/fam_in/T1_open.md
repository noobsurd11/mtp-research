# T1 open papers: 16 scout records the first T1 team did not take (best first)

## P003 | ERM++: An Improved Baseline for Domain Generalization
- id arxiv:2304.01973 | 2025 | WACV | score 74 | bench 60 | dirs D35 | code https://github.com/piotr-teterwak/erm_plusplus
- mechanism: A tuned plain-ERM recipe: average all weight iterates (MPA), warm-start the new head on a frozen backbone, set training length on val then retrain on train+val, stronger init, unfrozen BN.
- scout's adaptation: MPA as a running mean of all U-Net++ weights from step 2k to 20k with BN stats recomputed on train; warm start = PF's 1k frozen steps; fix the schedule (plateau lr drops, cap 80k) on the module-grouped 5-fold CV, then retrain the final model on all 532 train+val cells.
- evidence: R (full text, Table 2a, ResNet-50, 5 DomainBed datasets): ERM++ 68.9 avg; without MPA 65.9 (-3.0, largest), without full data 67.7, without strong init 67.6, without unfrozen BN 68.3, without Auto-LR 68.4, without war... | prior overlap: BRIEF section 5 optimizer row: EMA/SWA and longer schedules never varied; PF covers only the warm-start part. Open.

## P044 | Foreground Sampling and Spatial Support in Pavement Crack Segmentation
- id doi:10.21203/rs.3.rs-11088886/v1 | 2026 | Research Square preprint | score 66 | bench 70 | dirs D35 | code none found
- mechanism: Controlled study at 2 px tolerance AP: crack-biased crop sampling hurts because it makes background area unreachable; GroupNorm instead of BatchNorm lifts a random-crop U-Net.
- scout's adaptation: (a) Swap every decoder BatchNorm2d in U-Net++ for GroupNorm(16) while the pretrained encoder keeps BN, batch 8 of mixed sources. (b) Any crack/inactive oversampling or cropping we add must keep the whole cell reachable. Their paired-seed, prespecified-contrast protocol with a practical floor is a...
- evidence: R (full text): Crack500 full-res, U-Net from scratch, AdamW 3e-4, 20k updates, batch 16, BCE+Dice, flips+rot90, 3 paired seeds. AP2 random crops 0.812 (BN), positive-only 0.789, 10% positive 0.730; positive-only made ... | prior overlap: none; normalisation and sampling never varied here.

## P166 | Surgical Fine-Tuning Improves Adaptation to Distribution Shifts
- id arxiv:2210.11466 | 2023 | ICLR | score 55 | bench 30 | dirs D35 | code none found
- mechanism: Tuning only a subset of layers matches or beats full fine-tuning; the best block depends on shift type (input-level shifts favour early layers); tuning more parameters on small data forgets pretrained information.
- scout's adaptation: Arms: train stem+layer1-2 with layer3-4 frozen at ImageNet; and the reverse. Decoder always trained. E1 shift (scuff streaks, half-cut layout, contrast) is input-level, so early-layer tuning is predicted to help E1.
- evidence: Seven real-world tasks, three shift types; first-layer tuning best for image corruptions (abstract). | prior overlap: Partial: PF freezes the whole encoder for 1k steps only. Block-wise permanent freezing never run.

## P179 | Rethinking the Hyperparameters for Fine-tuning
- id arxiv:2002.11770 | 2020 | arXiv | score 52 | bench 40 | dirs D35 | code none found
- mechanism: Optimal effective lr and momentum for fine-tuning depend on source-target similarity; reference-based regularisation can fail for dissimilar datasets.
- scout's adaptation: Run the never-run grid: encoder lr {1e-4,3e-4,1e-3} x decoder lr {1e-3,3e-3} x beta1 {0.9,0.95}, on module-grouped 5-fold CV. Also warns that EL is dissimilar to ImageNet, so L2-SP / SPD may need small lambda.
- evidence: Extensive transfer benchmarks (classification); momentum and effective lr matter; regularisation toward init not always helpful on dissimilar data. | prior overlap: none. lr fixed at 1e-3 Adam (PF 0.1x on encoder) in every run so far.

## P185 | LiNeS: Post-training Layer Scaling Prevents Forgetting and Enhances Model Merging
- id arxiv:2410.17146 | 2024 | arXiv | score 52 | bench 25 | dirs D35 | code https://github.com/wang-kee/LiNeS
- mechanism: Post-training edit: scale each layer's fine-tuning delta linearly with depth, shallow layers near pretrained, deep layers keep the task update.
- scout's adaptation: Zero training on house and PF checkpoints; scale encoder deltas by depth, plus the inverse ordering because our erasure sits in layer3/4; BN stats recomputed; scale chosen on val.
- evidence: Reduces forgetting and improves OOD generalisation and multi-task merging in vision and NLP benchmarks (abstract; numbers not retrieved). | prior overlap: none

## P214 | Neural Network Optimization Reimagined: Decoupled Techniques for Scratch and Fine-Tuning (DualOpt)
- id arxiv:2604.22838 | 2026 | TPAMI | score 50 | bench 35 | dirs D35 | code none found
- mechanism: For fine-tuning, a per-step weight rollback toward upstream weights inside the optimizer, with rollback strength adapted per layer; evaluated on classification, detection, semantic and instance segmentation.
- scout's adaptation: Encoder-only rollback with layer3/4 rolled back hardest; second regulariser if SPD wins.
- evidence: State of the art across classification, detection, semantic and instance segmentation (abstract; numbers not retrieved). | prior overlap: Partial via PF, same as SPD.

## P217 | Sharpness-Aware Gradient Matching for Domain Generalization (SAGM)
- id arxiv:2303.10353 | 2023 | CVPR | score 50 | bench 35 | dirs D35 | code https://github.com/Wang-pengfei/SAGM
- mechanism: Minimise empirical risk, perturbed loss and their gap together, aligning gradient directions; better DG than SAM at equal cost.
- scout's adaptation: Drop-in replacement for SAM in the PF recipe; target E1. Run only if SAM moves E1.
- evidence: Outperforms SOTA on PACS, VLCS, OfficeHome, TerraIncognita, DomainNet (classification). | prior overlap: none

## P246 | Progressive growing of patch size: Curriculum learning for accelerated and improved medical image segmentation
- id arxiv:2510.23241 | 2026 | Medical Image Analysis | score 48 | bench 35 | dirs D35 | code none found
- mechanism: Start training with small patches and grow them, scaling batch size inversely to keep FLOPs; better convergence on severe foreground imbalance, lower seed variance.
- scout's adaptation: 2D: random crops 128 (batch 128) to 256 (batch 32) to 512 (batch 8), equal steps per stage, crops anywhere on the cell; last stage long because inactive and edge_dark need whole-cell context.
- evidence: R (abstract): +1.28% relative Dice over 15 3D tasks at equal FLOPs, better on all 15, largest on lesion tasks, lower variance. MICCAI 2024 version had code at github.com/compai-lab/2024-miccai-fischer per web search (... | prior overlap: BRIEF section 5: 2x resolution tested, crop curricula never. Open.

## P249 | Fast Trainable Projection for Robust Fine-Tuning (FTP)
- id arxiv:2310.19182 | 2023 | NeurIPS | score 48 | bench 30 | dirs D35 | code https://github.com/GT-RIPL/FTP
- mechanism: Learns per-layer projection radii around pretrained weights via hyper-optimisation; AdamW plug-in.
- scout's adaptation: Encoder only, comparator for SPD.
- evidence: Better OOD robustness on four vision tasks and five pretrained models; in SPD's PASCAL seg table FTP 73.79 ID / 58.45 OOD vs vanilla 66.03 / 44.00. | prior overlap: Partial via PF.

## P279 | Fine-Tuning can Distort Pretrained Features and Underperform Out-of-Distribution (LP-FT)
- id arxiv:2202.10054 | 2022 | ICLR | score 45 | bench 50 | dirs D35 | code none found
- mechanism: A random head distorts features during full fine-tuning; training the head first on frozen features (LP) then fine-tuning (FT) preserves them.
- scout's adaptation: PF already freezes the encoder 1k steps. Open variant: LP phase until the decoder converges (about 5k steps) then full FT at house lr, to separate LP-first from low encoder lr.
- evidence: 10 shift datasets: FT +2% ID, -7% OOD vs LP; LP-FT +1% ID, +10% OOD vs FT. | prior overlap: Largely tested: PF is an LP-FT-like recipe (1k frozen steps plus 0.1x lr) and won E1 inactive. Only the split of LP l...

## P309 | Rethinking "Batch" in BatchNorm
- id arxiv:2105.07576 | 2021 | arXiv | score 45 | bench 30 | dirs D35 | code none found
- mechanism: Review of BN caveats from batch choices (train vs population stats, precise BN, frozen BN in fine-tuning, domain-specific stats) and their fixes.
- scout's adaptation: Batch 8 with 5 mixed sources: test encoder BN frozen at ImageNet stats, precise-BN recompute on train before eval, and both. Required plumbing for EMA, SWAD, WiSE-FT, LiNeS arms.
- evidence: Review with mitigations in visual recognition (abstract). | prior overlap: Partial: per-panel BN adaptation at test time failed; training-time BN choices never varied.

## P316 | DGSAM: Domain Generalization via Individual Sharpness-Aware Minimization
- id arxiv:2503.23430 | 2025 | Qeios (preprint) | score 45 | bench 25 | dirs D35 | code none found
- mechanism: SAM can find flat total loss but sharp per-domain loss; gradual domain-wise perturbation lowers sharpness per domain at less cost than SAM.
- scout's adaptation: Domains = the 5 image sources; source-balanced batches; per-source perturbation steps. Aimed at BMRK weakness and E1 (CSIR-heavy).
- evidence: Beats SOTA DG methods on several benchmarks with less overhead than SAM (abstract). | prior overlap: none

## P338 | Training Beyond Convergence: Grokking nnU-Net for Glioma Segmentation in Sub-Saharan MRI
- id arxiv:2601.22637 | 2026 | Lecture Notes in Computer Science | score 42 | bench 35 | dirs D35 | code none found
- mechanism: Train far past apparent convergence (3,500 vs 200 epochs); small sub-regions improved.
- scout's adaptation: PF at 20k, 80k, 160k steps with EMA, 5 seeds; crack and inactive play the role of small sub-regions.
- evidence: R (secondary summaries, not checked in full text): tumor core / enhancing tumor Dice 86.6/86.3 to 90.1/90.2, whole tumor flat. | prior overlap: BRIEF section 5: longer schedules never varied. Open.

## P353 | Revisiting Fine-Tuning Strategies for Self-supervised Medical Imaging Analysis
- id arxiv:2307.10915 | 2023 | arXiv | score 42 | bench 25 | dirs D35 | code none found
- mechanism: Fine-tuning intermediate layers is better than end-to-end; fine-tuning the first 75% of a network beats end-to-end by up to 5.48%.
- scout's adaptation: Freeze layer4 at its pretrained weights and train the rest; reuse when MIM / DDeP or domain SSL encoders are re-tried.
- evidence: Four medical downstream tasks, several fine-tuning set sizes; up to +5.48% over end-to-end. | prior overlap: none for permanent block freezing; MIM / DDeP + PF n.d. used full-encoder tuning.

## P405 | Why is SAM Robust to Label Noise?
- id arxiv:2405.03676 | 2024 | arXiv | score 40 | bench 20 | dirs D35 | code none found
- mechanism: SAM's label-noise robustness comes mainly from a network-Jacobian regularisation effect and peaks with early stopping; cheaper explicit regularisers recover much of it.
- scout's adaptation: Mechanism reason for the SAM arm on jittered crack labels; if SAM helps, test the cheaper explicit regulariser at 1x cost and read earlier checkpoints.
- evidence: SAM gains of tens of percent under label noise; peak before convergence (abstract). | prior overlap: none

## P430 | Focal-SAM: Focal Sharpness-Aware Minimization for Long-Tailed Classification
- id arxiv:2505.01660 | 2025 | arXiv | score 38 | bench 25 | dirs D35 | code none found
- mechanism: Class-wise sharpness penalties, heavier on tail classes, without extra backpropagations.
- scout's adaptation: Per-class pixel losses over the 24 classes, focal weight on sharpness for inactive, crack, splice, gridline, edge_dark; run only if plain SAM helps.
- evidence: R (abstract): better than ImbSAM and CC-SAM on long-tailed classification with traditional and foundation models. | prior overlap: none; long-tail methods never tried.

