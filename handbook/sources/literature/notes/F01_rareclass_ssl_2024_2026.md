# F01: ALHVR lineage and rare-class SSL segmentation, 2024–2026 (what is new beyond B01–B06)

Scout pass on 10 Oct 2026, about 09:35–10:00 IST. Sources:
- OpenAlex citation graph: works citing ALHVR, BUR, MCF, ABD, DARS, AEL since 2024, keyword-filtered.
- Semantic Scholar: citations of DHC (78 citing works). Semantic Scholar otherwise rate-limited.
- WebSearch, and arXiv abstract pages.

Read scope per row: T = title, A = abstract, S = sections (pdftotext grep of method and ablation), F = full.
Open-access PDFs are in `literature/pdfs/<slug>/`. Nothing here was run on our data; "fit" lines are inferences from our measured facts.

## 1. ALHVR / BUR successors (citation graph, OpenAlex, 10 Oct 2026)

- **ALHVR** (OpenAlex W7160025859) has 5 citing works:
  - Wan et al., "Breaking error coupling via divergent–convergent coordination", MedIA 2026, [doi](https://doi.org/10.1016/j.media.2026.104236) (T, paywalled)
  - Zhu et al., "Uncertainty-discrepancy collaborative learning", BSPC 2026, [doi](https://doi.org/10.1016/j.bspc.2026.110871) (T, paywalled)
  - "Learning Beyond Pixels: Structured Knowledge Topology Consistency …", LNCS (MICCAI 2026), [doi](https://doi.org/10.1007/978-3-032-38069-2_32) (T, paywalled)
  - "Hierarchical Disentangled Consistency Learning …", LNCS 2026 (T)
  - a cardiac unsupervised paper (T, irrelevant)
- **None of the five has a class-imbalance or rare-class title.** No ALHVR successor targets tail classes (bounded: titles only, abstracts not deposited).
- **BUR** (arXiv 2502.07457; OpenAlex W4407424873) has 0 citing works. Re-read (S):
  - its uncertainty mask is **class-agnostic**: a global entropy percentile (95th during supervision, 99th during self-training);
  - datasets are ACDC (4 classes), LA (binary) and PROMISE12 (binary);
  - no rare-class analysis.
- **Earlier precedent for BUR's allocation:** "Uncertainty-aware deep co-training", CBM 2022, [doi](https://doi.org/10.1016/j.compbiomed.2022.106051) (T + search snippet). Supervised loss focuses on ambiguous pixels; unsupervised loss on reliable ones.
- **Same masking idea in natural images:** CSL, "When Confidence Fails" (ICCV 2025, [arXiv 2509.16704](https://arxiv.org/abs/2509.16704), A).
  - Fixed confidence thresholds fail under over-confidence: correct and wrong predictions overlap at high confidence.
  - Sample-specific decision boundaries in confidence-feature space.
  - **Randomly masks reliable pixels** so the network learns from low-reliability regions.
  - Natural-image counterpart of ALHVR Table 1. Class-agnostic.

## 2. New rare-class / class-imbalanced SSL segmentation (2024–2026)

| Paper | Venue | Mechanism | Rare-class evidence | Read | Fit to us |
|---|---|---|---|---|---|
| **DCA**, Divide, Conquer, Aggregate: asymmetric experts ([CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_Divide_Conquer_and_Aggregate_Asymmetric_Experts_for_Class-Imbalanced_Semi-Supervised_Medical_CVPR_2026_paper.html), [code](https://github.com/PHPJava666/DCA)) | CVPR 2026 | Log-gap split of classes into head/medium/tail; 3 expert decoders (the tail one is detail-oriented); unlabelled pseudo-label = **logit stitching** across experts; aggregation decoder | Ablation: experts alone take Es 0→46.3, RAG 0→39.1, LAG 0→48.0 Dice (Synapse); label-split adds +14.5 avg Dice | S | Class-group routing of *who makes the pseudo-label*. Not region routing. 3D organs, size imbalance rather than label noise |
| **CGS**, Collaborative Generalist and Specialists ([arXiv 2504.00862](https://arxiv.org/abs/2504.00862)) | TMI 2025 (per S2 venue) | Generalist head plus one **one-vs-rest specialist head per class**; cross-consistency; inter-head error detection cleans pseudo-labels; specialists dropped at inference | Small targets (esophagus, aorta) improved on ACDC/SegTHOR/Synapse | S | One-vs-rest crack/inactive heads avoid the 24-way softmax competition with busbar/gridline. Zero deployment cost |
| **SKCDF**, Semantic Knowledge Complementarity Decoupling ([CVF](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_A_Semantic_Knowledge_Complementarity_based_Decoupling_Framework_for_Semi-supervised_Class-imbalanced_CVPR_2025_paper.html)) | CVPR 2025 | **Decouples data flow:** unlabelled data trains the encoder (semantic features); the decoder is protected from noisy pseudo-labels; labelled-guided pseudo-labels; auxiliary class-balanced head | Synapse, AMOS small organs | S | Matches our P2 finding that rare-class pseudo-labels are near-empty or wrong; also the "loss-off 4+4 inactive gain" via encoder/BN path |
| **DINO-Mix** ([arXiv 2602.07819](https://arxiv.org/abs/2602.07819)) | arXiv 2026 | Frozen **DINOv3** as an external, unbiased feature teacher (feature distillation on mixed images) + **Progressive Imbalance-aware CutMix** (class-balanced patch sampling, curriculum toward class-agnostic) | Synapse 20%, AMOS 5% minority organs | S | "Inward-looking" self-training starves minorities, which is our 0.024% crack share of confident pixels. DINOv3 patch 16 is likely too coarse for 1–2 px cracks [inferred] |
| **SCDL**, Semantic Class Distribution Learning ([arXiv 2603.05202](https://arxiv.org/abs/2603.05202)) | arXiv 2026 | Learnable class proxies aligned bidirectionally with embeddings; labelled-data anchors | low-frequency organs, Synapse/AMOS | A | Labelled-GT-anchored prototypes: the only prototype variant our audit left open |
| **VCDP** ([arXiv 2607.07416](https://arxiv.org/abs/2607.07416)) | arXiv 2026 | Gaussian class distribution + variation prototypes; training-only | small, ambiguous organs | A | as SCDL |
| **STAC**, shape transformation by active contour ([arXiv 2410.14210](https://arxiv.org/abs/2410.14210)) | BIBM 2024 | SDF-based **enlargement of small organs** as augmentation | Synapse, AMOS | A | Dilating thin cracks in training is the opposite of what our metric wants. Precision is already about 0.3 |
| **TAK**, textual anatomical knowledge ([arXiv 2501.13470](https://arxiv.org/abs/2501.13470)) | TMI 2026 | GPT-4o text priors → CLIP → segmentation-head params | multi-organ | A | low fit (no anatomy prior for defects) |
| **Beyond Random Sampling** ([arXiv 2607.04249](https://arxiv.org/abs/2607.04249)) | arXiv 2026 | VFM-based **choice of which images to label** (Density-K-Center) + memory-guided copy-paste for imbalance | PROMISE 1/16: +5.3 DSC over UniMatch V2 | A | Relevant to WattCycle's labelling choice and to the "single labelled subset" weakness |
| CaPro, class-aware prototype + cross-view contrast ([doi](https://doi.org/10.1016/j.patcog.2026.115032)) | Pattern Recog. 2026 | class-aware prototypes | ? | T | **Paywalled. Possible partial counterexample to the gap; verify** |
| Dynamic Category Preference Learning, long-tailed SSL seg in remote sensing ([RG](https://www.researchgate.net/publication/397697575)) | TGRS 2025 | class preference / tail-aware | ? | T | non-medical long-tail SSL seg; verify |

Older items surfaced, not new mechanisms:
- U2PL, UPC (ICCV 2024: patch-level replacement of uncertain patches with labelled patches).
- BLV (CVPR 2023: logit variation; also an SSL Cityscapes setting).

## 3. Thin / tubular structures: is there a skeleton- or tolerance-aware *unlabelled* loss?

| Paper | What the unlabelled loss is | Read |
|---|---|---|
| **SemiCurv** ([arXiv 2205.08706](https://arxiv.org/abs/2205.08706)), TIP 2022 | Geometric strong augmentation with a **differentiable inverse transform** before pixel consistency; **N-pair consistency** because MSE collapses to all-background under heavy imbalance. 6 curvilinear datasets incl. road cracks; ≤5% labels → about 95% of full | S |
| **ITC/CTC**, coronary plaque ([arXiv 2501.07850](https://arxiv.org/abs/2501.07850)), 2025 | Dual-task head (mask + **skeleton-aware distance transform**) with consistency between the two on unlabelled data | A |
| **HAIC-NET** ([doi](https://doi.org/10.1016/j.patcog.2024.110429)), Pattern Recog. 2024 | Per the search snippet: "topological connectivity consistency" on **centerline maps** against GT or pseudo-labels | T + snippet, **paywalled, verify** |
| Semi-ECNet ([doi](https://doi.org/10.1109/isbi56570.2024.10635703)), ISBI 2024 | Sobel edge-map consistency for vessels | A (catalogue) |
| SSFA ([PMC11783301](https://europepmc.org/article/PMC/PMC11783301)), Bioinformatics 2025 | CPS with Dice. The skeleton enters only as a **fracture-attention input map**, not in the loss | S |
| ESRVS ([arXiv 2607.24453](https://arxiv.org/abs/2607.24453)), 2026 | 1 labelled image + DINOv3 prototypes + physics prior → pseudo-labels. Reports clDice | A |
| Concrete crack SSL: [AutCon 2023](https://doi.org/10.1016/j.autcon.2023.105181) (OA); EAAI 2024 (mutual consistency + boundary loss); DiffEncoderCrack (ESWA 2026); cross-teacher (AEI 2023) | generic consistency / pseudo-labels. AutCon: 2% labels within 2.6 / 4.7 mIoU of full | A / T |
| Road UDA with topology ([doi](https://doi.org/10.1016/j.isprsjprs.2023.10.020)), ISPRS 2023 | skeleton-based **pseudo-label refinement via connectivity** (UDA, not SSL) | snippet |

**Verdict on our claim "no skeleton- or tolerance-aware SSL objective":**
- Partly refuted. Skeleton/centerline-aware unlabelled consistency exists in the medical-vessel line (ITC 2025; HAIC-NET 2024, pending verification).
- Still unrefuted, in what we found:
  - no unlabelled loss is **tolerant to ±1–2 px offsets** between teacher and student or pseudo-label;
  - none is **multi-class / rare-class aware**;
  - none on EL.
- Reword the gap: "tolerance-aware, class-aware unlabelled consistency for thin rare classes", citing ITC, HAIC-NET and SemiCurv as the nearest work.

## 4. EL-specific SSL segmentation since PV-S3

- None found (WebSearch, 10 Oct). PV-S3 (EAAI 2025) is still the only EL SSL segmentation paper.
- Neighbours: SeMaCNN (anomaly, HJT) and STC-Net (supervised).

## 5. Verdict on the "region routing × class awareness" gap

Still unoccupied in what we found. Nearest neighbours:
- **Class-aware without region routing:** DCA (class-group experts + logit-stitched pseudo-labels), CGS (per-class specialists), DHC/GA (weights), DINO-Mix/AEL (class-aware mixing).
- **Region routing without class awareness:** ALHVR, BUR, CSL, CoraNet, deep co-training 2022.
- **Unverified (paywalled):** CaPro (PR 2026) and the two ALHVR citers in MedIA / BSPC 2026. Read them before claiming novelty.
- **Caution:** a gap is not a contribution by itself. Our own measurements say the teacher is right on only about 62% of Ω3 crack pixels, so the routing target in Ω3 is the bottleneck, not the routing rule.

## PAYWALLED_FOR_PARENT (fetch through institutional access)

1. Wan et al., MedIA 2026, Breaking error coupling (ALHVR successor): https://doi.org/10.1016/j.media.2026.104236
2. Hu et al., Pattern Recog. 2026, CaPro (class-aware prototypes; gap check): https://doi.org/10.1016/j.patcog.2026.115032
3. Zhu et al., BSPC 2026, Uncertainty-discrepancy collaborative learning (ALHVR citer): https://doi.org/10.1016/j.bspc.2026.110871
4. Learning Beyond Pixels, topology consistency (MICCAI 2026, cites ALHVR): https://doi.org/10.1007/978-3-032-38069-2_32
5. Shen et al., HAIC-NET, Pattern Recog. 2024 (centerline consistency on unlabelled?): https://doi.org/10.1016/j.patcog.2024.110429
6. Uncertainty-aware deep co-training, CBM 2022 (BUR-allocation precedent): https://doi.org/10.1016/j.compbiomed.2022.106051
7. Crack SSL, mutual consistency + boundary loss, EAAI 2024: https://www.sciencedirect.com/science/article/abs/pii/S0952197624018414
8. Road UDA with topology, ISPRS 2023: https://doi.org/10.1016/j.isprsjprs.2023.10.020
9. Dynamic Category Preference Learning, TGRS 2025 (long-tail SSL seg): https://www.researchgate.net/publication/397697575
10. Semi-ECNet, ISBI 2024: https://doi.org/10.1109/isbi56570.2024.10635703
