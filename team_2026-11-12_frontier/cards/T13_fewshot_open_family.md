# T13 family cards: few-shot, in-context and promptable segmentation; open sweep of 2025 and 2026 venues (13 Nov 2026)

Analyst T13. Tags: R = from the paper or its repository page (fetched this session), E = from our files, S = my judgement. Nothing was run. No server, GPU or sealed set touched.
The Research MCP tools were not available in this session; papers were read through arXiv HTML and GitHub pages with WebFetch.
Read in full (arXiv HTML): P327 GFDS, P503 FSS-SAM3, P410 SANSA (first 100k of 165k characters: method, main tables, ablations). Abstract or repository page only: P548, P557, P456, P070, P137, SAM 2 repository. Everything else: the scout record.
Specs: `T13_fewshot_open_spec.md`. Ledger: `ledger/T13.tsv` (24 papers).

## Family reading (S)

1. **Promptable and in-context models are region tools, not line tools.** Every number in this family is on blob-like objects or industrial defects scored by mIoU. GFDS (R) shows SAM2 at 512 px loses 9.1 mIoU against 1024 px and 24.0 at 256 px; the SAM2 mask decoder emits 256 x 256 logits for a 1024 input. Our cracks are 1 to 2 px labels on a 4 px dark line (E, BRIEF 2). So these models are candidates for **inactive** (blobby, 1 px shift IoU 0.94, E) and maybe the structural classes, and not for crack labels. Crack label refinement stays with T4's ridge_snap.
2. **The best prompt source we own is the house model itself.** PF out-of-fold dumps exist for all 532 cells (E, tonight). Prompting SAM 2 with house inactive components is training-free, label-free, and can be scored paired on the same predictions, which removes seed noise (the argument T10 makes for post-hoc arms, E: inactive IoU SE 0.038 between trained arms). That is arm 1.
3. **Label quality without sealed sets** is measurable only by running the labeller leave-fold-out on the 532 labelled cells (supports from the training folds, queries from the held-out fold), plus F51 (unseen modules, full cells) and the 19 crack-free H36 cells (false alarms). Pool cells have no labels; agreement with the house model there says nothing about correctness. That is arm 2, and its gate decides whether any labeller arm is built.
4. **Pseudo-label SSL with the house teacher on the 11.9k pool was n.d. at 100% labels** (E, BRIEF 5). A foundation in-context labeller is a different teacher (errors possibly decorrelated), so the row does not close it; but it raises the bar: a labeller is worth a GPU arm only if it finds what the house model misses (arm 2 gate G-lab).
5. **T3b** (E, `T3B_PROPOSAL.md`): only about 10 E1 image ids carry the hard crack stratum, so a few-shot rule cannot be tuned on E1. It has to be fixed on a proxy (leave-one-source-out, T7's LOSO-2 roots) and applied once. That is arm 3.
6. **Open sweep:** none of the 13 non-few-shot papers makes a better case than an arm already queued in its own family; each is handed over (ledger notes).

---

## Cards for papers that matter

### P327 GFDS / FM-SAM: few-shot defect segmentation with metric learning and vision foundation models
- Ids: doi:10.1016/j.optlastec.2025.114078; arXiv 2502.01216 (v2 read in full). Code: https://github.com/liutongkun/GFDS (verified to exist).
- Claims (R): 1-shot 1-way over 54 defect categories in 12 industrial products (Tile, Grid, Steel, KolektorSDD, PSPs, DAGM, rubber rings, MSD, Capsules, Macaroni2). Average mIoU: SAM2-s video mode at 1024 px **47.9** (FB-IoU 74.3, 32.3 FPS on a 3090 Ti class GPU); SAM2-t 45.1, SAM2-b 45.0, SAM2-l 43.8 ("a larger model does not always yield better performance"); SAM2-s at 512 px 38.8, at 256 px 23.9. Feature matching FM-l 36.5, FM-l + FastSAM fusion **39.3**. Meta-learning FSS at most 19.2 (PATNet); PerSAM 8.0; Matcher 5.0. SAM2 prompted by points or boxes from FM: 36.5 to 40.2, all below video mode. Fusion ablation: FM-l 36.5, FastSAM masks alone 22.1, union 37.8, their fusion rule 39.3.
- Method details used here (R): video mode = support image and mask as the previous frame, query as the current frame; memory attention then mask decoder. Fusion rule: keep a SAM mask if it overlaps the coarse prediction by more than tau1 = 0.2; replace a coarse component by the SAM mask when the dilated SAM mask (kernel 21) covers it above tau2 = 0.9; keep the other coarse components.
- Evidence check (S): only 1-shot experiments; multi-shot handling is not described. No per-class numbers for cracks or scratches. The 1024 v 512 drop is the strongest fact for us: input scale matters for SAM2, so cells must be upsampled to 1024. Repository holds only the FM code (`MatchingNet_PatchBased.py`, `main.py`), no SAM2 video-mode code and no licence; the SAM2 part is short to write against the SAM 2 video predictor.
- Hypothesis for our data (S): (a) SAM 2 prompted by house inactive components sharpens inactive boundaries and drops spurious blobs (arm 1); (b) SAM 2 video mode with retrieved labelled supports is a usable in-context predictor for inactive and some structure classes, and a T3b row (arm 2). Crack: expected to fail on width (256 x 256 logits).
- Status: **RUN_NOW** (arms 1 and 2).

### P410 SANSA: hidden semantics in SAM 2 for few-shot segmentation
- Ids: doi:10.52202/085713-3969 (NeurIPS 2025); arXiv 2505.21795 (read up to the ablations). Code: https://github.com/ClaudiaCuttano/SANSA (repository named in the paper; licence not stated on the pages read).
- Claims (R): SAM 2 Hiera-L frozen, AdaptFormer adapters in the last two encoder stages (about 10M trainable, strict setting), BCE + Dice, AdamW 1e-4, 5 epochs; references and target as a pseudo-video, memory attention segments the target. 1-shot / 5-shot mIoU: LVIS-92i 48.8 / 53.9, COCO-20i 60.2 / 64.3, FSS-1000 91.4 / 92.1. Frozen SAM 2 in the same pipeline: 16.5 / 32.2 / 73.0 (1-shot). Ablation on COCO-20i: full fine-tuning 51.6, backbone FT 55.2, LoRA 58.0, adapter 59.4, SANSA 60.2; adapters in the late stages 60.2 v early 38.7. Prompt types: mask 60.2, box 54.3, point 53.4, scribble 53.1. Generalist comparison: SegGPT 18.6 LVIS-92i, 56.1 COCO-20i.
- Evidence check (S): natural-image benchmarks only; no industrial, no thin structure. The big jump over frozen SAM 2 (32.2 to 60.2) comes from training adapters on episodes, so on EL it would need episodic training on our train folds (pairs of cells sharing a class).
- Hypothesis (S): if plain SAM 2 video mode (GFDS) already finds PF-missed inactive regions, an EL-trained SANSA adapter would make it a stronger labeller.
- Status: **RUN_AFTER_GATE**, gate G-lab of arm 2.

### P503 Few-shot semantic segmentation meets SAM 3 (FSS-SAM3)
- Ids: arXiv 2604.05433 (read in full). Code: https://github.com/WongKinYiu/FSS-SAM3 (named in the paper; licence not stated).
- Claims (R): frozen SAM 3, support and query composed on one 1008 x 1008 canvas, support instance as a positive box exemplar, optional class-name text. 1-shot mIoU PASCAL-5i 79.6, COCO-20i 66.6 (visual only); with text 81.2 / 75.8. 5-shot (inverse-L layout) 81.2 / 71.8. Forced resize beats aspect-preserving padding (79.6 v 77.5); support on top at about 6:4. Negative exemplars collapse predictions: COCO-20i 66.6 to 54.8 / 46.6 / 44.7 with up to 1 / 3 / 5 negatives. No cross-domain numbers; runtime not reported. The text and tables disagree on several numbers (I quote the tables).
- Evidence check (S): two cells on one canvas give the query about 400 px of height, below native 512; thin cracks are out. Text prompts ("crack", "dark region") are untested on EL. SAM 3 weights need an HF access request (E, T6 family table).
- Status: **BENCH_ONLY** (T3b in-context row, after the user approves SAM 3).

### P548 SegGPT
- Ids: doi:10.1109/iccv51070.2023.00110; arXiv 2304.03284 (abstract page). Code: https://github.com/baaivision/Painter (named on the abstract page; code licence not stated there).
- Claims (R, abstract): in-context colouring with random colour maps; few-shot semantic, VOS, semantic and panoptic segmentation. No numbers on the abstract page. SANSA's tables (R) give SegGPT 18.6 LVIS-92i and 56.1 COCO-20i 1-shot.
- Evidence check (S): canvas splits the input, so each cell is seen at about half size; no thin-structure evidence.
- Status: **BENCH_ONLY** (T3b row via arm 2's harness).

### P557 FSSDINO
- Ids: arXiv 2602.07550 (abstract page). Code: https://github.com/hussni0997/fssdino (named on the page; not opened).
- Claims (R): training-free prototypes on frozen DINOv3 with Gram-matrix refinement, last layer; competitive with specialised FSS on binary, multi-class and cross-domain benchmarks; oracle intermediate layers are better, but no selection rule finds them. No numbers on the abstract page.
- Evidence check (S): GFDS (R) found patch matching with DINOv2 ViT-S/14 at 23.4 mIoU on defects, against 33.9 for DINO ViT-S/8: patch 14 is coarse for small defects.
- Status: **BENCH_ONLY** (cheapest T3b row; DINOv2 ViT-S/14 and DINOv3 ViT-S/16 are local on gaint, E).

### P456 SOFS: small-object few-shot segmentation for industrial inspection
- Ids: doi:10.1109/tii.2025.3538070; arXiv 2407.21351 (repository README). Code: https://github.com/zhangzilongc/SOFS, PyTorch, DINOv2 ViT-B/14, xFormers, released checkpoint; licence **CC BY-NC-SA 4.0** (verified on the README).
- Claims (R, README): segments defects covering less than 0.03% of the image; few-shot segmentation and few-shot anomaly detection; VISION V1, Defect Spectrum, Severstal open-domain test. Scout record: no resize, prototype intensity downsampling, abnormal prior map, mixed normal Dice loss.
- Evidence check (S): the only family member designed for tiny defects, but it needs episodic training; non-commercial licence keeps it out of any WattCycle model.
- Status: **BENCH_ONLY** (trained-FSS T3b row, lowest priority).

### P137 CSWinUNETR (open sweep, handed to T11)
- Ids: arXiv 2606.19824 (MICCAI 2026). Code: https://github.com/labhai/CSWinUNETR, standalone PyTorch 2.5.1, 2D and 3D, binary and multiclass (README verified); no LICENSE file listed.
- Claims (R, scout record): FIVES Dice 90.71 v nnUNetv2 89.26; FFHQ-Wrinkle 64.75 v 63.27; 31M parameters (2D).
- Hypothesis (S): a from-scratch thin-structure transformer row for the method suite; stripe attention along busbar-aligned cracks. Not expected to beat a pretrained encoder with PF on 478 cells (T6 family reading of P089: from-scratch comparisons flatter ViTs).
- Status: **BENCH_ONLY**, owner T11 (licence to clear first).

### P070 DINOv3-IML (open sweep, handed to T6)
- Ids: arXiv 2604.16083. Code: https://github.com/Irennnne/DINOv3-IML, MIT (verified): frozen DINOv3 ViT-S/B/L, LoRA r32 / r64 on QKV (ViT-L r32 = 9.1M trainable), "3-conv head" with bilinear upsampling, 512 px, gradient accumulation 10.
- Claims (R, scout record): +17.0 average pixel F1 over prior SOTA on 4 forensics benchmarks; data-scarce protocol F1 0.774 v 0.530; LoRA beats full FT at all scales.
- Evidence check (S): same mechanism as T6 arm 4 (`hiera_bp_adapter_frozen`: frozen VFM + adapters + light decoder) with public weights. A patch-16 head without a high-resolution path cannot draw 1 to 2 px cracks at 512 px.
- Status: **PARKED** in T6; reopen if T6 arm 4 passes and the user approves DINOv3 ViT-L.

### P588 What makes good examples for visual in-context learning
- Ids: doi:10.52202/075280-0780. Code: none found (scout).
- Claims (R, scout record): retrieved prompts beat random prompts for in-context segmentation and detection.
- Use (S): arm 2 runs retrieved and random supports side by side; T3b declares its support rule before any run.
- Status: **PROTOCOL**.

### P635 KaLOS (open sweep, handed to T12)
- Ids: arXiv 2603.27197 (CVPR 2026). No code found. Abstract-level claim (R, scout): an agreement meta-algorithm for detection and instance segmentation without circular reliance on ground truth.
- Status: **PROTOCOL** (label-noise ceiling row beside T12's `tau_from_annotators`).

## Short notes on the rest (scout record only; details in the ledger)
- P245 FAST, P532 rock joints: T8 (synthesis); PARKED behind `pvddpm_fold_synth`.
- P306 Learn2Synth, P347 DiDA, P421 OFL-SAM2, P530 SegRCDB: T7 (unseen modules, synthesis, UDA); PARKED behind `gin_ipa` / `mic_halfcell`.
- P376 SegFaultLoc, P457 cross-sectional noise: T10 / T3 / T4 label-quality work already queued; PARKED.
- P466 ShiftwiseConv: T11 / T6 encoder rows; PARKED.
- P569 DSE: needs a pool SSL run; PARKED.
- P311 Hummingbird, P541 DIP, P458 FS-CPL, P622 Matcher: this family; PARKED (no code, gated weights, or measured far below SAM 2 video mode on defects).
