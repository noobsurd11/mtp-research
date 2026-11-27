export const meta = {
  name: 'frontier-paper-discovery',
  description: 'Sweep 2020-2026 literature across 44 directions for methods that can raise EL solar-cell defect segmentation scores, then dedupe and rank a shortlist',
  phases: [
    { title: 'Canary', detail: 'check Research MCP and web search from a subagent' },
    { title: 'Scout', detail: 'one scout per research direction' },
    { title: 'Critic', detail: 'three completeness critics hunt for missed papers' },
    { title: 'Judge', detail: 'two-lens scoring of every deduped paper' },
  ],
}

const ROOT = '/home/yugma/mtp/research/team_2026-11-12_frontier'
const MCP = 'select:mcp__claude_ai_Research_MCP__search_papers,mcp__claude_ai_Research_MCP__search_snippets,mcp__claude_ai_Research_MCP__get_paper,mcp__claude_ai_Research_MCP__similar_papers,mcp__claude_ai_Research_MCP__get_citations,mcp__claude_ai_Research_MCP__get_references,mcp__claude_ai_Research_MCP__fetch_fulltext,mcp__claude_ai_Research_MCP__read_paper'

const PRE = `You are a member of a research team whose goal is the highest-scoring model for electroluminescence (EL) solar-cell defect segmentation (cracks, inactive areas, other defects, balanced mIoU), with one month left.

FIRST read ${ROOT}/BRIEF.md in full with the Read tool. It holds the project facts, the numbers to beat, what was already tried and under which conditions, and the team rules (section 7). Follow those rules exactly.

Tools: load the Research MCP tools with ToolSearch, query "${MCP}" (max_results 10). Load web search with ToolSearch, query "select:WebSearch". In search_papers use limit 15 to 20 and abstract_chars 250 to keep results small. If a tool call fails or is rate-limited, wait a little and retry up to 3 times, then continue with the other tool. Never invent a paper, an id, a number or a repository URL.`

const RUBRIC = `Score rubric (0 to 100) = expected gain on OUR metrics x probability it works on OUR data x feasibility within one month on 8 RTX A6000 + 1 32 GB GPU.
90+: strong, direct evidence on a near-identical problem (thin 1-2 px structures, few hundred labelled images, label jitter, or EL itself), code available, days of work.
70-89: solid mechanism matched to one of the five problems in BRIEF section 4, plausible gain, code or simple to implement.
50-69: plausible, needs real adaptation or the evidence is from a distant domain.
30-49: long shot or expensive, but a distinct idea worth one cheap test.
below 30: reference value only.
Do not lower a score only because something with a similar name failed in BRIEF section 5; lower it only if the same mechanism was tested under the same conditions.
Second number, bench_score (0 to 100), is separate: how much the paper matters for the user's benchmark vision (BRIEF section 1). High if it is a widely used recent method that a credible EL benchmark must include as a baseline, or if it shapes how the benchmark is split, scored or extended to severity. A paper can be low on score and high on bench_score, or the reverse.`

const PAPER = {
  type: 'object',
  properties: {
    paper_id: { type: 'string', description: 'doi:... or arxiv:... exactly as a tool returned it' },
    title: { type: 'string' },
    year: { type: 'integer' },
    venue: { type: 'string' },
    url: { type: 'string' },
    code_url: { type: 'string', description: 'official code repository if you verified it, else empty string' },
    mechanism: { type: 'string', description: 'the one idea, 1 to 2 sentences' },
    evidence: { type: 'string', description: 'what the paper measured: numbers, datasets, training-set size' },
    targets: { type: 'array', items: { type: 'string', enum: ['crack', 'inactive', 'e1_unseen', 'other_classes', 'measurement', 'deployment', 'benchmark', 'severity'] } },
    adaptation: { type: 'string', description: 'how it must be changed for our data (1-channel EL, 512 px, 478 cells, 1-2 px jittered crack labels, 24 classes, 5 sources)' },
    min_experiment: { type: 'string', description: 'cheapest decisive experiment: arm, baseline, metric, kill line' },
    gpu_hours: { type: 'number', description: 'rough GPU-hours for that experiment' },
    prior_overlap: { type: 'string', description: 'none, or the BRIEF section 5 row it overlaps and why it is still open (or truly closed)' },
    bet: { type: 'string', enum: ['safe', 'medium', 'moonshot'] },
    score: { type: 'integer', description: '0 to 100 by the rubric: value for raising OUR scores' },
    bench_score: { type: 'integer', description: '0 to 100: value for the benchmark (a method the suite should include as a strong recent baseline, or guidance on benchmark design, scoring, or severity post-evaluation)' },
  },
  required: ['paper_id', 'title', 'year', 'mechanism', 'adaptation', 'min_experiment', 'score'],
}

const SCOUT_SCHEMA = {
  type: 'object',
  properties: {
    direction_id: { type: 'string' },
    queries_run: { type: 'integer' },
    papers: { type: 'array', items: PAPER },
    gaps: { type: 'array', items: { type: 'string' }, description: 'things you could not find, or sub-directions that deserve their own search' },
    file: { type: 'string', description: 'path of the markdown file you wrote' },
  },
  required: ['direction_id', 'papers'],
}

const DIRS = [
  { id: 'D01', slug: 'el_segmentation', title: 'EL solar-cell defect semantic segmentation methods, 2020 to 2026', focus: 'Every paper that segments defects in EL images at pixel level: U-Net variants, attention, transformers, Mamba, lightweight models. Especially work on BenchmarkEL, E-SCDD, UCF-EL, PVEL-S, MultiSolSegment. Record their reported per-class numbers, splits, tricks (losses, augmentation, resolution, pretraining) and anything that beats a ResNet-34 U-Net++.', seeds: 'electroluminescence solar cell defect segmentation; EL image crack segmentation photovoltaic; E-SCDD; BenchmarkEL; UCF-EL; PV-S3; SEiPV-Net; STC-Net; MultiSolSegment' },
  { id: 'D02', slug: 'el_detection_datasets', title: 'EL defect detection / classification ideas and a census of public labelled EL datasets', focus: 'Two jobs. (a) Detection and classification papers on EL images whose ideas transfer to segmentation (attention to thin cracks, multi-scale, background suppression of busbars and fingers, few-shot, long-tail). (b) A census of every public EL dataset with labels (pixel masks, boxes, image labels) released 2020 to 2026, with size, label type, licence and access, so the 478-cell training set can be enlarged.', seeds: 'PVEL-AD; ELPV; photovoltaic electroluminescence dataset; solar cell defect detection YOLO electroluminescence; EL dataset pixel annotation release 2024 2025 2026' },
  { id: 'D03', slug: 'el_citation_snowball', title: 'Forward-citation snowball of the core EL dataset papers', focus: 'Use get_citations (with_contexts where useful) on the core papers and list every citing paper that proposes a segmentation or detection method, a dataset, a label revision or an evaluation critique. Core papers: Pratt 2021 (Renewable Energy, U-net EL defect quantification), Pratt 2023 (BenchmarkEL, Systems and Soft Computing), Fioresi 2022 (UCF-EL, IEEE JPV), Hanifi 2025 E-SCDD (arXiv 2511.09604), Su 2023 PVEL-AD, Deitsch 2019 ELPV, Sanghi MultiSolSegment (arXiv 2603.13337), Jha PV-S3 (arXiv 2404.13693), Torpey 2024 (arXiv 2402.17611). Be exhaustive rather than selective here, then score.', seeds: 'find each core paper with get_paper by title or arXiv id, then get_citations' },
  { id: 'D04', slug: 'pv_multimodal', title: 'Multi-modal PV inspection: EL with thermal IR, photoluminescence, UV fluorescence, visible', focus: 'Fusion and cross-modal learning for PV modules: EL + IR, EL + PL, EL + UVF, registered multi-modal datasets, cross-modal distillation or learning with privileged information, translation between modalities, physics that links modalities to inactive area and cracks. Also lock-in thermography and outdoor / daylight EL or PL.', seeds: 'electroluminescence infrared thermography fusion photovoltaic; multimodal PV module inspection dataset EL IR; photoluminescence electroluminescence deep learning; UV fluorescence cracks deep learning' },
  { id: 'D05', slug: 'pv_thermal_segmentation', title: 'Thermal (IR) PV fault detection and segmentation from drones, 2020 to 2026', focus: 'A possible second deliverable: the partner company owns a drone thermal camera. Find public thermal PV datasets with labels (image level, boxes, masks), the best methods, hot-spot and module segmentation, fault classification, and how thermal findings map to EL findings. Note dataset sizes, licences and what a one-month project could deliver.', seeds: 'photovoltaic infrared thermography dataset fault classification; PVF-10; InfraredSolarModules; UAV thermal solar panel defect segmentation; hot spot segmentation deep learning' },
  { id: 'D06', slug: 'el_synthesis', title: 'Synthetic EL data: physics simulation and generative models', focus: 'Physics-based simulation of EL images of cracked cells and isolated (inactive) regions (finite-element or SPICE network models of fingers and busbars), GAN and diffusion generation of EL defects, synthetic image-mask pairs for EL, and any measured downstream gain in detection or segmentation. E-SCDD itself contains 93 diffusion images.', seeds: 'electroluminescence image simulation crack finite element; synthetic electroluminescence images GAN; diffusion model solar cell defect generation; EL image generation data augmentation photovoltaic' },
  { id: 'D07', slug: 'pv_pretraining_anomaly', title: 'PV / EL self-supervised pretraining, foundation models and unsupervised anomaly detection', focus: 'Self-supervised or foundation-model pretraining on EL / PV imagery; unsupervised or weakly supervised anomaly detection and localisation on EL cells (normal-only training); what localisation quality they reach for cracks versus dark areas.', seeds: 'self-supervised electroluminescence; anomaly detection electroluminescence solar cell; foundation model photovoltaic inspection; contrastive pretraining EL images' },
  { id: 'D08', slug: 'el_physics_preprocessing', title: 'EL image formation, preprocessing and physics priors', focus: 'Cell registration and perspective correction, template or golden-cell subtraction, removal of busbar and finger patterns, vignetting and exposure normalisation, denoising, deblurring, super-resolution for EL, multi-bias EL, classical crack detectors (vesselness, anisotropic diffusion) usable as input channels or priors; half-cut cell and multi-busbar layouts; what scuff or scratch marks look like in EL.', seeds: 'electroluminescence image preprocessing cell segmentation perspective; EL image enhancement solar; half-cut cell electroluminescence defects; micro-crack detection anisotropic diffusion electroluminescence; scratch electroluminescence' },
  { id: 'D09', slug: 'crack_architectures', title: 'Crack segmentation architectures (pavement, concrete, steel), 2021 to 2026', focus: 'Transformers, Mamba, hybrid CNN models and universal crack segmenters and benchmarks. What transfers to 1 to 2 px cracks on a textured, patterned background with a few hundred labelled images. Note which papers use tolerance metrics.', seeds: 'crack segmentation transformer; crack segmentation Mamba; SCSegamba; CrackFormer; OmniCrack30k; CrackSeg9k; thin crack segmentation high resolution' },
  { id: 'D10', slug: 'topology_losses', title: 'Topology- and connectivity-aware losses', focus: 'Beyond clDice and Skeleton Recall (both run here): cbDice, Betti matching, Topograph, persistent-homology losses, warping loss, centerline cross-entropy, connectivity-preserving post-processing. Find evidence on when they help strict overlap versus only topology, their effect on predicted width, and cheap implementations.', seeds: 'topology preserving segmentation loss; cbDice centerline boundary; Betti matching; Topograph; skeleton recall loss follow-up; tubular structure loss' },
  { id: 'D11', slug: 'curvilinear_formulations', title: 'Alternative output formulations for thin lines', focus: 'Distance-transform or centerline heat-map regression, orientation and direction fields, connectivity maps, graph or polyline extraction (roads, lanes, vessels), line-segment set prediction, implicit or sub-pixel representations. Which are robust to 1 px label jitter and can be rasterised at a chosen width.', seeds: 'centerline distance transform regression segmentation thin structures; directional connectivity segmentation DconnNet; road graph extraction; orientation learning road connectivity; deep distance transform tubular' },
  { id: 'D12', slug: 'vessel_road_modules', title: 'Vessel, neuron and road segmentation modules', focus: 'Dynamic Snake Convolution, deformable, strip and directional convolutions, full-resolution networks (FR-UNet), detail branches, attention for curvilinear structures, results on DRIVE / CHASE / Massachusetts Roads / DeepGlobe at small training sizes, and what ablations say matters.', seeds: 'dynamic snake convolution tubular; retinal vessel segmentation full resolution; curvilinear structure segmentation; strip convolution road; thin vessel segmentation capillaries' },
  { id: 'D13', slug: 'edge_detection_noisy', title: 'Learned edge detection with crisp outputs and inconsistent annotations', focus: 'Edge detection faces the same problem as our cracks: thin targets, annotator disagreement, thick predictions, tolerance-based evaluation. Find crisp-edge methods, label refinement for edges, uncertainty-aware edge detection, ranking losses, diffusion edge detectors and lightweight edge networks.', seeds: 'crisp edge detection noisy labels refinement; uncertainty-aware edge detector multiple annotations; RankED; DiffusionEdge; TEED; PiDiNet' },
  { id: 'D14', slug: 'crack_foundation_models', title: 'Foundation models for crack and thin-structure segmentation', focus: 'SAM, SAM 2, SAM 3 and DINOv2 / DINOv3 adapted to cracks or other thin structures: adapters, LoRA, prompt-free decoders, zero- and few-shot results, failure modes on 1 to 2 px structures (patch size), high-resolution tricks.', seeds: 'segment anything crack segmentation fine-tuning; CrackSAM; SAM adapter thin structures; DINOv2 crack; SAM 2 medical thin vessel; SAM 3 concept segmentation' },
  { id: 'D15', slug: 'noisy_label_segmentation', title: 'Segmentation from noisy, misaligned or incomplete pixel labels', focus: 'Boundary and offset noise, thin-structure jitter, missing annotations (positive-unlabelled segmentation), early-learning correction, robust losses, co-teaching, confident learning for segmentation, spatial label smoothing, noise-transition models. Evidence on thin structures matters most.', seeds: 'noisy label segmentation boundary; ADELE early learning segmentation; T-Loss robust segmentation; learning from noisy annotations medical segmentation; partial annotation missing labels segmentation; label noise thin structures' },
  { id: 'D16', slug: 'label_refinement_alignment', title: 'Automatic label correction and alignment to image evidence', focus: 'Methods that move or reshape imprecise labels onto the visible structure: aligning misregistered road or map labels, snake and active-contour refinement, model-in-the-loop relabelling, SAM-assisted mask refinement, self-correcting pseudo-labels, learned label offsets. The aim here: snap 1 to 2 px crack labels to the dark ridge and learn each source\'s label width.', seeds: 'label alignment misregistered annotations road; noisy map labels alignment deep learning; mask refinement segment anything noisy labels; self-correction label refinement segmentation; active contour label refinement' },
  { id: 'D17', slug: 'annotator_style', title: 'Annotator-style, multi-rater and dataset-conditioned segmentation', focus: 'Models that represent how a given annotator or dataset draws labels: probabilistic and style-conditional segmentation, crowd models, dataset-ID conditioning, universal models with dataset prompts. Here the five image sources have different crack label widths (1.5 to 3.25 px), so a source-conditional output could raise strict IoU.', seeds: 'annotator style segmentation; multi-rater medical segmentation; Pionono; learning from multiple annotators segmentation; dataset conditioned segmentation label convention; probabilistic U-Net' },
  { id: 'D18', slug: 'iou_soft_label_losses', title: 'Metric-aligned and soft-label losses', focus: 'Lovasz losses, Jaccard Metric Losses and Dice Semimetric Losses (soft labels), boundary label smoothing, Tversky and focal families, compound losses, loss choice studies (which loss for which metric), calibration and operating-point selection when the metric is IoU on thin classes.', seeds: 'Jaccard metric losses soft labels; Lovasz softmax; Dice semimetric losses; boundary label smoothing segmentation; unified focal loss; loss functions segmentation benchmark study' },
  { id: 'D19', slug: 'longtail_segmentation', title: 'Long-tailed and class-imbalanced semantic segmentation with full supervision', focus: 'Balanced softmax and logit-adjusted training, region rebalance, seesaw, class-balanced and rare-class sampling, pixel contrast and prototypes, hard-pixel mining, decoupled training, class-specific thresholds. Our weak classes: gridline (IoU 0.28), splice (0.00), edge_dark, material.', seeds: 'long-tailed semantic segmentation; region rebalance; logit adjustment segmentation; class imbalance segmentation rare class sampling; pixel contrastive learning segmentation; balanced loss dense prediction' },
  { id: 'D20', slug: 'small_object_losses', title: 'Small-structure and instance-wise losses', focus: 'Blob loss, lesion-wise or component-wise Dice, size-inverse weighting, recall-oriented and count-aware losses, small-lesion strategies from medical imaging (MS lesions, microbleeds, metastases), tiny-object tricks. 76 to 88% of our crack components are under 20 px.', seeds: 'blob loss instance imbalance segmentation; lesion-wise loss small lesions; component-wise dice; small object semantic segmentation loss; tiny lesion segmentation detection sensitivity' },
  { id: 'D21', slug: 'defect_augmentation', title: 'Defect and rare-class augmentation', focus: 'Copy-paste with blending and context awareness (our plain crack copy-paste gave no gain and more decoys), CutPaste / DRAEM / NSA style synthetic anomalies, class-aware mixing, inpainting-based augmentation, procedural crack synthesis, elastic or geometric augmentation that is safe for thin lines, rare-class oversampling evidence.', seeds: 'copy-paste augmentation segmentation blending context; synthetic anomaly generation natural synthetic anomalies; defect augmentation industrial segmentation; procedural crack synthesis; rare class augmentation semantic segmentation' },
  { id: 'D22', slug: 'highres_detail_architectures', title: 'Detail-preserving and high-resolution architectures', focus: 'HRNet / OCR, UNet 3+, full-resolution stems, dual-branch networks, PointRend, super-resolution auxiliary heads, small-stride or small-patch ViTs, ViT-Adapter and similar, tiling at native resolution. The question: how to keep 1 to 2 px lines through the encoder and decoder.', seeds: 'high resolution representation segmentation thin; ViT-Adapter dense prediction; dual super-resolution learning segmentation; PointRend; patch size vision transformer small objects segmentation; UNet 3+' },
  { id: 'D23', slug: 'mask_transformers', title: 'Transformer segmenters and mask classification', focus: 'SegFormer, Mask2Former, OneFormer, Mask DINO, SegNeXt, EoMT and later; evidence on small datasets, rare and thin classes, greyscale or industrial data; per-pixel versus mask classification for long-tailed classes; training recipes that work with a few hundred images.', seeds: 'Mask2Former small dataset; SegFormer defect segmentation; EoMT encoder-only mask transformer; SegNeXt; mask classification rare classes; transformer segmentation data efficiency' },
  { id: 'D24', slug: 'vfm_peft_dense', title: 'Vision foundation backbones with parameter-efficient tuning for dense prediction in low-data regimes', focus: 'DINOv2 / DINOv3 (ViT-L and larger, ConvNeXt), SAM encoders, RADIO, Perception Encoder, SigLIP 2 and similar, tuned with LoRA, adapters, Rein or frozen with a light decoder; results on datasets of a few hundred images (medical, industrial, remote sensing), on greyscale non-natural images and under domain shift. Our only test so far was a tiny ConvNeXt at 4k steps.', seeds: 'DINOv3 dense prediction fine-tuning; Rein vision foundation model domain generalized segmentation; LoRA DINOv2 segmentation medical; frozen foundation model segmentation few labels; foundation model industrial defect segmentation' },
  { id: 'D25', slug: 'medical_seg_pipelines', title: 'Self-configuring and modern medical segmentation pipelines', focus: 'nnU-Net and nnU-Net Revisited, residual-encoder presets, U-Mamba, Swin-UMamba, VM-UNet, MedNeXt, STU-Net, TransUNet, U-KAN; what actually beats a tuned U-Net on small 2D datasets; foreground-oversampled patch sampling, deep supervision, long schedules, ensembling by cross-validation folds.', seeds: 'nnU-Net revisited; U-Mamba; MedNeXt; Swin-UMamba; 2D medical segmentation benchmark small dataset; self-configuring segmentation' },
  { id: 'D26', slug: 'refinement_stages', title: 'Refinement stages and coarse-to-fine cascades', focus: 'SegRefiner and other diffusion refiners, CascadePSP, boundary patch refinement, SAM-based refiners, CRF layers, error-correction networks, two-stage detect-then-refine at high resolution. Aim: fix width and alignment of thin predictions, recover missed faint segments.', seeds: 'SegRefiner; segmentation refinement diffusion; CascadePSP; coarse-to-fine thin structure segmentation; SAMRefiner; error correction network segmentation' },
  { id: 'D27', slug: 'multitask_structured', title: 'Multi-task and structured outputs', focus: 'Joint region and boundary heads, multi-label (sigmoid) segmentation for overlapping classes, hierarchical heads, auxiliary image-level classification to suppress false positives, constraints between related classes (here: inactive regions are bounded by cracks; cracks are also labelled inside inactive regions), panoptic formulations.', seeds: 'multi-label semantic segmentation overlapping classes; boundary aware multi-task segmentation; classification guided segmentation false positive; hierarchical semantic segmentation; region boundary joint learning' },
  { id: 'D28', slug: 'frequency_priors', title: 'Frequency, wavelet and filter priors; patterned-background defect detection', focus: 'Wavelet U-Nets, frequency-domain learning, Gabor / steerable / learnable vesselness layers, Hessian ridge features as inputs, and defect detection on periodic textures (fabric, LCD, wafers, PCB) where the regular pattern is suppressed. EL cells have periodic fingers and busbars.', seeds: 'wavelet segmentation network thin; frequency domain defect detection periodic texture; learnable Frangi vesselness; Gabor convolution crack; XNet wavelet; periodic pattern defect LCD fabric deep learning' },
  { id: 'D29', slug: 'semisupervised_recent', title: 'Semi-supervised segmentation, 2023 to 2026, at high label fractions or with foundation models', focus: 'Our pseudo-label SSL was null from 20% labels up. Find what is different in recent work: foundation-model teachers, SemiVL, UniMatch V2, AllSpark and later, noisy student at full labels, SSL when the pool is out-of-distribution, SSL for thin structures. Only keep papers with a mechanism that differs from Mean Teacher with pseudo-labels on a ResNet.', seeds: 'UniMatch V2; SemiVL; semi-supervised semantic segmentation foundation model; self-training full labels improves segmentation; semi-supervised vessel segmentation; semi-supervised crack segmentation' },
  { id: 'D30', slug: 'dg_uda', title: 'Domain generalisation and unsupervised domain adaptation for segmentation', focus: 'The unseen-module gap (crack IoU 0.47 to 0.15) is a layout and confounder shift: half-cut cells, scuff streaks. Find single-source DG and UDA methods (DAFormer, HRDA, MIC, Rein, DGInStyle and later), style, texture and frequency randomisation, multi-site medical DG, shape or layout shift, and what works for rare thin classes.', seeds: 'domain generalized semantic segmentation; masked image consistency domain adaptation; single source domain generalization medical segmentation; style randomization segmentation; DGInStyle' },
  { id: 'D31', slug: 'test_time_adaptation', title: 'Test-time adaptation and test-time augmentation for segmentation', focus: 'Beyond BN statistics (which failed here): entropy and consistency based TTA, continual TTA, test-time training with masked reconstruction, adapter or prompt TTA, source-free adaptation, plain flip / rotation / multi-scale TTA; known failure modes on rare classes.', seeds: 'test-time adaptation semantic segmentation; test-time training masked autoencoder; continual test-time adaptation segmentation; test-time augmentation segmentation; source-free domain adaptation segmentation' },
  { id: 'D32', slug: 'dense_ssl_pretraining', title: 'Self-supervised pretraining for dense prediction in a narrow domain', focus: 'In-domain pretraining with 10^4 to 10^5 unlabelled images: DINO / iBOT / DINOv2 continued pretraining, MAE and SparK, dense contrastive methods, domain-specific foundation models (radiology, pathology, remote sensing, industrial), and when in-domain SSL beats ImageNet or a general foundation model. Our MIM test on ResNet-34 with 11.9k images was null; 159k images are available.', seeds: 'domain-specific self-supervised pretraining segmentation; SparK masked convnet; DINOv2 continued pretraining domain; dense contrastive learning; self-supervised pretraining industrial inspection; pretraining small domain data vs ImageNet' },
  { id: 'D33', slug: 'generative_data', title: 'Generative data for segmentation', focus: 'Diffusion-generated image-mask pairs (DatasetDM, DiffuMask, FreeMask, SegGen, Dataset Diffusion and later), mask- or layout-conditioned ControlNet or LoRA fine-tuned on a few hundred images, few-shot defect generation (Defect-Gen, AnomalyDiffusion, DefectFill, DualAnoDiff, SeaS and later), unpaired translation for domain gaps (full-cell to half-cut style), with measured downstream segmentation gains. A mask-conditioned generator would also give labels that are aligned by construction.', seeds: 'diffusion synthetic data semantic segmentation; mask conditioned image generation segmentation training; few-shot defect generation diffusion; anomaly generation diffusion segmentation; ControlNet data augmentation segmentation small dataset' },
  { id: 'D34', slug: 'distill_ensemble_averaging', title: 'Ensembles, distillation and weight averaging', focus: 'A 5-seed ensemble is our only clear win. Find: ensemble-to-single distillation for segmentation, self-distillation, SWA, EMA, model soups, heterogeneous ensembles, test-time augmentation, uncertainty-weighted fusion, and distillation into small students (2 to 5 M parameters) for deployment.', seeds: 'knowledge distillation semantic segmentation; ensemble distillation segmentation; model soups; stochastic weight averaging segmentation; self-distillation dense prediction; heterogeneous ensemble segmentation' },
  { id: 'D35', slug: 'recipe_finetuning', title: 'Training recipes and fine-tuning for small-data segmentation', focus: 'Our fine-tune erased the pretrained encoder; the optimizer was never varied. Find: feature-preserving fine-tuning (LP-FT, L2-SP, layer-wise lr decay, surgical fine-tuning), AdamW and schedules, sharpness-aware minimisation, EMA, normalisation choices at batch 8, augmentation policies safe for thin structures, crop and multi-scale strategies, schedule length studies.', seeds: 'fine-tuning distorts pretrained features; layer-wise learning rate decay segmentation; sharpness-aware minimization segmentation; L2-SP; data augmentation segmentation small dataset study; training recipe semantic segmentation' },
  { id: 'D36', slug: 'weak_multidataset', title: 'Weak and heterogeneous supervision; multi-dataset training', focus: 'Use the other EL datasets together with BenchmarkEL: UCF-EL polygons with a different taxonomy, MultiSolSegment multi-label masks, PVEL-AD boxes, ELPV image labels. Find multi-dataset training with different taxonomies and partial labels, label-space unification, box / scribble / point / image-level supervision turned into masks (with SAM), mixed supervision for defects.', seeds: 'multi-dataset semantic segmentation different taxonomies; partial label segmentation multiple datasets; box supervised segmentation SAM; mixed supervision surface defect; image-level labels weakly supervised defect segmentation' },
  { id: 'D37', slug: 'data_centric', title: 'Data-centric methods: label error detection, relabelling, selection', focus: 'Label error detection for segmentation, automated relabelling, data valuation and pruning, active learning with tiny budgets, annotation with VLMs or SAM without humans, dataset auditing. The user avoids manual labelling, so automatic or model-assisted routes rank higher.', seeds: 'label error detection semantic segmentation; confident learning segmentation; automated relabeling segmentation; active learning semantic segmentation small budget; data valuation segmentation' },
  { id: 'D38', slug: 'incontext_promptable', title: 'In-context, few-shot and promptable segmentation as a labeller', focus: 'SegGPT, Painter, SAM 2 memory propagation across similar images, SAM 3 concept prompts, Matcher, PerSAM, dense-correspondence label propagation with DINO features. Use: label the 12k to 159k unlabelled cells or new contexts (half-cut cells) without parametric self-training; few-shot adaptation to a new module type.', seeds: 'in-context segmentation SegGPT; few-shot segmentation foundation model; SAM 2 propagation few-shot medical; label propagation dense correspondence DINO; one-shot segmentation Matcher PerSAM' },
  { id: 'D39', slug: 'anomaly_detection', title: 'Industrial anomaly detection and segmentation as a prior', focus: 'PatchCore, EfficientAD, Dinomaly, SimpleNet, DeSTSeg, AnomalyCLIP, AnomalyDINO, MuSc and later, supervised-with-few-anomalies methods; anomaly maps as priors or extra inputs to a supervised segmenter; performance on textured and patterned surfaces and on thin defects. We have about 12k unlabelled cells, many defect-free.', seeds: 'Dinomaly; EfficientAD; anomaly detection few labeled anomalies segmentation; zero-shot anomaly segmentation CLIP; anomaly map prior supervised defect segmentation; texture anomaly detection thin scratches' },
  { id: 'D40', slug: 'surface_defect_segmentation', title: 'Industrial surface defect segmentation, state of the art', focus: 'Steel, magnetic tile, KolektorSDD2, wafers, PCB, fabric, rail: architectures, losses, few-shot defect segmentation, mixed supervision, tiny-defect tricks and benchmark-winning recipes that could transfer to EL cells.', seeds: 'surface defect segmentation state of the art; KolektorSDD2 segmentation; few-shot defect segmentation; steel surface defect segmentation transformer; tiny defect segmentation industrial' },
  { id: 'D41', slug: 'evaluation_methodology', title: 'Evaluation with small, noisy test sets and thin structures', focus: 'Metrics for thin structures under label uncertainty (tolerance metrics, NSD, boundary IoU, clDice as a metric), annotation-uncertainty-aware evaluation, statistical comparison of segmentation models with small test sets, cross-validation versus hold-out, reporting practice. We need an instrument that can detect gains of 0.01 to 0.02.', seeds: 'Metrics Reloaded; evaluation thin structure segmentation tolerance; statistical significance segmentation comparison small test set; label noise test set evaluation segmentation; confidence intervals segmentation benchmarks' },
  { id: 'D43', slug: 'benchmark_design', title: 'How trusted segmentation and inspection benchmarks are built', focus: 'The user wants to set a new benchmark for EL defect segmentation because published numbers are not comparable. Find benchmark and methodology papers that show how to do it well: group-wise (module-wise) splits and leakage audits, hidden or sealed test sets, cross-validation protocols, standard baseline suites, label-noise handling and multi-annotator test labels, reporting with confidence intervals, datasheets and model cards, lessons from benchmarks in small domains (Medical Segmentation Decathlon, nnU-Net Revisited style critiques, MVTec AD / VisA, KolektorSDD, crack benchmarks such as CrackSeg9k and OmniCrack30k, WILDS for distribution shift), and critiques of benchmark practice (leakage, test-set overfitting, unfair baselines). Also any existing comparative study or benchmark attempt on EL / PV images and its flaws.', seeds: 'benchmark design semantic segmentation rigorous validation; data leakage train test split group; nnU-Net revisited call for rigorous validation; WILDS benchmark distribution shift; pitfalls benchmarking medical image segmentation; photovoltaic electroluminescence benchmark comparison deep learning models' },
  { id: 'D44', slug: 'severity_power', title: 'Severity grading and power-loss estimation from EL (post-evaluation)', focus: 'What comes after the masks, and whether it adds value to a benchmark: crack mode classification (Koentges A / B / C), inactive or disconnected area fraction, crack length and orientation statistics, cell- and module-level power or I-V prediction from EL, fill-factor loss from defect maps, public datasets that pair EL with I-V or power (UCF DPV sets, DTU, Pratt 680 modules, others), standards (IEC TS 60904-13) and defect criticality criteria, and task-level metrics that score a segmentation model by the severity it implies rather than by pixels.', seeds: 'electroluminescence power loss prediction deep learning; crack severity classification solar cell inactive area; EL image I-V curve prediction module power; cell crack criticality electroluminescence; fraction of inactive area power loss photovoltaic module; IEC TS 60904-13' },
  { id: 'D42', slug: 'recent_venue_sweep', title: 'Open sweep of 2025 and 2026 venues', focus: 'No fixed topic. Scan CVPR, ICCV, ECCV, NeurIPS, ICLR, MICCAI, WACV, TPAMI, TMI, IJCV and strong arXiv work from 2025 and 2026 for segmentation papers on thin structures, tiny defects, small-data regimes, label noise, foundation-model adaptation, synthetic data, or any new idea that fits the five problems in the brief and that topic-specific searches may miss because it is recent or oddly named.', seeds: 'use year_from 2025 on many varied queries; use WebSearch for accepted-paper lists and for recent arXiv listings' },
]

const scoutPrompt = d => `${PRE}

Your role: literature scout for direction ${d.id}: ${d.title}.
Focus: ${d.focus}
Seed queries and names (hints from memory, verify each with a tool before using it): ${d.seeds}

What to do:
1. Run at least 12 distinct searches (search_papers with year_from 2020; repeat the best ones with year_from 2025 to catch recent work; search_snippets for evidence questions). Snowball from the 2 or 3 strongest papers with similar_papers and get_citations. Use WebSearch for 2025 and 2026 work and to verify code repositories. Older foundational papers are fine when they are the method itself.
2. Select the 8 to 18 papers with a distinct, testable mechanism that could raise our scores on at least one of the five problems in BRIEF section 4. Prefer recent work, public code, evidence on small data or thin structures or a close domain, and feasibility within a month. Include one or two bold bets if you find them. Think about what the method would do on OUR data, not on the paper's benchmark.
3. For every selected paper fill all fields. "adaptation" must be specific to our data. "min_experiment" must name the arm, the baseline (the house model or its PF variant), the metric and a kill line. "prior_overlap" must say honestly whether BRIEF section 5 already tested the same mechanism under the same conditions.
4. Write ${ROOT}/directions/${d.id}_${d.slug}.md: the queries you ran, a table of the selected papers (id, year, venue, code, mechanism, adaptation, score), a short list of notable papers you rejected with one-line reasons, and gaps. Plain English, no em-dashes.
5. Return the structured result. direction_id is "${d.id}".

${RUBRIC}`

// ---------- helpers ----------
const norm = s => (s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
const idKey = p => {
  let id = (p.paper_id || '').toLowerCase().trim()
  id = id.replace(/^https?:\/\/(dx\.)?doi\.org\//, 'doi:').replace(/^https?:\/\/arxiv\.org\/abs\//, 'arxiv:')
  id = id.replace(/^(arxiv:\d{4}\.\d{4,5})v\d+$/, '$1')
  return id
}
function dedupe(list) {
  const byTitle = new Map(), byId = new Map(), out = []
  for (const p of list) {
    if (!p || !p.title) continue
    const tk = norm(p.title), ik = idKey(p)
    let e = (tk && byTitle.get(tk)) || (ik && byId.get(ik))
    if (e) {
      const dirs = Array.from(new Set(e.directions.concat(p.directions)))
      const ss = e.scout_scores.concat([p.score])
      const code = e.code_url || p.code_url || ''
      if ((p.score || 0) > (e.score || 0)) Object.assign(e, p)
      e.directions = dirs; e.scout_scores = ss; e.code_url = code
    } else {
      e = Object.assign({}, p, { directions: p.directions.slice(), scout_scores: [p.score] })
      out.push(e)
    }
    if (tk) byTitle.set(tk, e)
    if (ik) byId.set(ik, e)
  }
  return out
}
const tag = (res, id) => (res && Array.isArray(res.papers) ? res.papers : []).map(p => Object.assign({}, p, { directions: [id] }))

// ---------- Canary ----------
phase('Canary')
const canary = await agent(`Tool availability check, keep it short. (1) Call ToolSearch with query "${MCP}" and max_results 10, then call mcp__claude_ai_Research_MCP__search_papers with query "electroluminescence solar cell crack segmentation", year_from 2023, limit 3, abstract_chars 0. (2) Call ToolSearch with query "select:WebSearch" and run one web search for "DINOv3 segmentation fine-tuning". (3) Check that you can read ${ROOT}/BRIEF.md and write a file ${ROOT}/log/canary.txt containing the word ok. Report what worked.`,
  { label: 'canary', phase: 'Canary', effort: 'low', schema: { type: 'object', properties: { research_mcp_ok: { type: 'boolean' }, websearch_ok: { type: 'boolean' }, file_io_ok: { type: 'boolean' }, note: { type: 'string' } }, required: ['research_mcp_ok', 'websearch_ok', 'file_io_ok'] } })
if (!canary || !canary.research_mcp_ok) {
  return { aborted: true, reason: 'Research MCP not reachable from a workflow subagent', canary }
}
log(`canary: research_mcp=${canary.research_mcp_ok} websearch=${canary.websearch_ok} file_io=${canary.file_io_ok}`)

// ---------- Scout ----------
phase('Scout')
const scoutRes = await parallel(DIRS.map(d => () =>
  agent(scoutPrompt(d), { label: `scout:${d.id}:${d.slug}`, phase: 'Scout', model: 'opus', effort: 'high', schema: SCOUT_SCHEMA })
    .then(r => ({ d, r }))))
let okScouts = scoutRes.filter(x => x && x.r)
let failed = DIRS.filter(d => !okScouts.some(x => x.d.id === d.id)).map(d => d.id)
if (failed.length) {
  log(`retrying failed scouts: ${failed.join(',')}`)
  const retry = await parallel(DIRS.filter(d => failed.includes(d.id)).map(d => () =>
    agent(scoutPrompt(d) + '\n\n(Second attempt: an earlier scout for this direction did not finish. Write your file early and keep the result compact.)', { label: `scout-retry:${d.id}:${d.slug}`, phase: 'Scout', model: 'opus', effort: 'high', schema: SCOUT_SCHEMA })
      .then(r => ({ d, r }))))
  okScouts = okScouts.concat(retry.filter(x => x && x.r))
  failed = DIRS.filter(d => !okScouts.some(x => x.d.id === d.id)).map(d => d.id)
}
let raw = okScouts.flatMap(x => tag(x.r, x.d.id))
const gaps = okScouts.flatMap(x => (x.r.gaps || []).map(g => `${x.d.id}: ${g}`))
let pool = dedupe(raw)
log(`scouts ok ${okScouts.length}/${DIRS.length}; raw ${raw.length}; deduped ${pool.length}; failed: ${failed.join(',') || 'none'}`)

// ---------- Critic ----------
phase('Critic')
const listing = pool.map(p => `${p.year} | ${p.title} | ${p.directions.join(',')}`).join('\n')
const dirList = DIRS.map(d => `${d.id} ${d.title}`).join('\n')
const CRITICS = [
  { id: 'C1', lens: 'Missing mechanisms. Go through the five problems in BRIEF section 4 one by one and through the "never tried at all" list in section 5. For each, ask what a strong researcher from another field (medical imaging, remote sensing, document analysis, materials inspection, astronomy, seismology, biology microscopy) would try that is absent from the list below. Then search for the best papers on those absent mechanisms.' },
  { id: 'C2', lens: 'Recency. The list below may miss work from 2025 and 2026. Sweep recent venues and arXiv (use year_from 2025 and WebSearch) for high-impact segmentation, defect-inspection, thin-structure, label-noise, foundation-model-adaptation and synthetic-data papers that are not in the list. Also check for newer versions or successors of the listed methods.' },
  { id: 'C3', lens: 'EL and PV domain coverage. Check that no relevant electroluminescence / photovoltaic inspection paper from 2020 to 2026 is missing: methods, datasets, label revisions, benchmarks, multi-modal work, half-cut and multi-busbar specific work, scuff / scratch defects, severity or power-loss prediction from EL. Use forward citations of the dataset papers and many keyword variants (also Chinese-group journals: Solar Energy, IEEE JPV, Progress in Photovoltaics, Measurement, IEEE TII, IEEE TIM, Energies, Sensors).' },
]
const criticRes = await parallel(CRITICS.map(c => () =>
  agent(`${PRE}

Your role: completeness critic ${c.id}. ${okScouts.length} scouts searched these directions:
${dirList}

Their notes on gaps:
${gaps.slice(0, 120).join('\n') || 'none reported'}

Papers found so far (year | title | directions):
${listing}

Your lens: ${c.lens}

Find up to 20 papers that are NOT in the list above and that carry a distinct, testable mechanism for our problems. Run at least 12 searches. Fill every field for each paper as a scout would ("adaptation" specific to our data, "min_experiment" with arm, baseline, metric and kill line, honest "prior_overlap"). Write ${ROOT}/directions/${c.id}_critic.md with your queries, the papers and what you judge is still missing. Return the structured result with direction_id "${c.id}".

${RUBRIC}`, { label: `critic:${c.id}`, phase: 'Critic', effort: 'high', schema: SCOUT_SCHEMA }).then(r => ({ c, r }))))
const okCritics = criticRes.filter(x => x && x.r)
raw = raw.concat(okCritics.flatMap(x => tag(x.r, x.c.id)))
pool = dedupe(raw)
log(`after critics: raw ${raw.length}; deduped ${pool.length}`)

// ---------- Judge ----------
phase('Judge')
const CLUSTERS = ['label_refine', 'noise_robust_loss', 'annotator_style', 'soft_iou_loss', 'topology_loss', 'thin_arch', 'line_formulation', 'edge_det', 'vfm_backbone', 'sam_family', 'mask_decoder', 'medseg_pipeline', 'refinement_stage', 'multitask_multilabel', 'longtail', 'small_object', 'defect_aug', 'gen_data', 'physics_sim', 'multi_dataset_weak', 'ssl_semi', 'dg_uda', 'tta', 'dense_pretrain', 'distill_ensemble', 'recipe', 'anomaly_prior', 'freq_prior', 'preprocess', 'multimodal_thermal', 'thermal_task', 'promptable_labeller', 'data_centric', 'eval', 'benchmark_design', 'severity_power', 'el_domain_method', 'other']
const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    scores: {
      type: 'array', items: {
        type: 'object',
        properties: {
          idx: { type: 'integer' },
          score: { type: 'integer' },
          bench: { type: 'integer' },
          tier: { type: 'string', enum: ['A', 'B', 'C', 'X'] },
          cluster: { type: 'string', enum: CLUSTERS },
          reason: { type: 'string' },
        }, required: ['idx', 'score', 'bench', 'tier', 'cluster', 'reason'],
      },
    },
  }, required: ['scores'],
}
const sorted = pool.slice().sort((a, b) => (b.score || 0) - (a.score || 0) || norm(a.title).localeCompare(norm(b.title)))
const NCH = Math.max(1, Math.ceil(sorted.length / 28))
const chunks = Array.from({ length: NCH }, () => [])
sorted.forEach((p, i) => chunks[i % NCH].push(p))
const LENSES = [
  { id: 'upside', text: 'Upside lens. You are an ambitious senior researcher. Ask: if this works on our data, how much does it move the numbers in BRIEF section 3, and which of the five problems does it attack at the root? Reward ideas that change the instrument, the data or the formulation rather than tune the house model. Still be honest about probability.' },
  { id: 'realism', text: 'Realism lens. You are a careful experimentalist with one month and a 50-cell test set. Ask: is the evidence real (dataset size, leakage, tuned baselines), is the code public, how many days to a decisive result, and can a gain of the claimed size be detected here? Penalise methods whose evidence is far from thin 1 to 2 px structures or few-hundred-image regimes. Do not penalise an idea only because a similar-sounding one failed in BRIEF section 5.' },
]
const fmt = (p, i) => `[${i}] ${p.title} (${p.year}, ${p.venue || 'venue n/a'}; ${p.paper_id}; code: ${p.code_url || 'none found'}; from ${p.directions.join(',')}; scout score ${p.score}, scout bench ${p.bench_score == null ? 'n/a' : p.bench_score}, bet ${p.bet || 'n/a'})
  mechanism: ${p.mechanism}
  evidence: ${p.evidence || 'n/a'}
  targets: ${(p.targets || []).join(',') || 'n/a'}
  adaptation: ${p.adaptation}
  min experiment: ${p.min_experiment} (about ${p.gpu_hours == null ? '?' : p.gpu_hours} GPU-h)
  prior overlap: ${p.prior_overlap || 'n/a'}`
const judgeJobs = []
chunks.forEach((ch, ci) => LENSES.forEach(l => judgeJobs.push({ ch, ci, l })))
const judgeRes = await parallel(judgeJobs.map(j => () =>
  agent(`You are a judge on a research team whose goal is the highest-scoring model for electroluminescence (EL) solar-cell defect segmentation, with one month left.
FIRST read ${ROOT}/BRIEF.md in full. You may verify a doubtful claim with the Research MCP tools (ToolSearch query "${MCP}") but you do not need to search otherwise.

${j.l.text}

Score each of the ${j.ch.length} candidate papers below.
${RUBRIC}
Tier: A = run in the first week; B = run after an A result or a cheap gate; C = keep as reference or a late option; X = void, allowed ONLY if BRIEF section 5 shows the same mechanism was already tested under the same conditions (say which row in "reason").
Cluster: pick the mechanism family, so that papers testing the same idea can share one experiment.
Give both numbers for every paper: score (value for raising our scores) and bench (value for the benchmark, as the rubric defines).
Use the whole score range; spread your scores. Return one entry per paper with its idx.
Also write your scores as JSON (idx, paper_id, title, score, bench, tier, cluster, reason) to ${ROOT}/rank/chunk_${String(j.ci).padStart(2, '0')}_${j.l.id}.json.

Candidates:
${j.ch.map(fmt).join('\n')}`, { label: `judge:${j.ci}:${j.l.id}`, phase: 'Judge', effort: 'high', schema: JUDGE_SCHEMA }).then(r => ({ j, r }))))

for (const x of judgeRes) {
  if (!x || !x.r || !Array.isArray(x.r.scores)) continue
  for (const s of x.r.scores) {
    const p = x.j.ch[s.idx]
    if (!p) continue
    p.judge = p.judge || {}
    p.judge[x.j.l.id] = { score: s.score, bench: s.bench, tier: s.tier, cluster: s.cluster, reason: s.reason }
  }
}
for (const p of pool) {
  const js = Object.values(p.judge || {})
  p.final = js.length ? Math.round(js.reduce((a, b) => a + b.score, 0) / js.length) : (p.score || 0)
  p.bench = js.length ? Math.round(js.reduce((a, b) => a + (b.bench || 0), 0) / js.length) : (p.bench_score || 0)
  p.cluster = (p.judge && (p.judge.realism || p.judge.upside) || {}).cluster || 'other'
  p.tiers = js.map(j => j.tier).join('/')
}
const ranked = pool.slice().sort((a, b) => b.final - a.final)
const compact = p => ({ id: p.paper_id, t: p.title, y: p.year, f: p.final, b: p.bench, u: p.judge && p.judge.upside ? p.judge.upside.score : null, r: p.judge && p.judge.realism ? p.judge.realism.score : null, tier: p.tiers, cl: p.cluster, d: p.directions.join(','), code: p.code_url ? 1 : 0 })
return {
  n_scouts_ok: okScouts.length, failed_directions: failed, n_critics_ok: okCritics.length,
  n_raw: raw.length, n_dedup: pool.length, n_judged: ranked.filter(p => p.judge).length,
  top: ranked.slice(0, 150).map(compact),
  bench_extra: ranked.slice(150).filter(p => (p.bench || 0) >= 70).slice(0, 40).map(compact),
}
