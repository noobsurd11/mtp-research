# D32: Self-supervised pretraining for dense prediction in a narrow domain

Scout for D32. Session 1: 12 Nov 2026, about 19:55 to 20:15 IST. Session 2 (resume): 13 Nov 2026.
Labels: R = what a paper reports, E = what our files report, S = my judgement.

## Tool log
- Session 1: Research MCP returned HTTP 502 from 14:30 to 14:36 UTC, then worked; Semantic Scholar rate-limited throughout (no snippets). WebSearch budget ran out after 2 calls; ids were verified by WebFetch of arXiv pages.
- Session 2: Research MCP worked through OpenAlex (and arXiv on some calls). Scopus and ScienceDirect returned HTTP 401, Semantic Scholar stayed rate-limited, so search_snippets failed again. 18 search_papers, 1 get_citations, 1 similar_papers, about 10 get_paper, 2 fetch_fulltext (both open access: the SEM paper and LeJEPA), 3 WebSearch.

### Queries run
| # | Session | Tool | Query | Result |
|---|---|---|---|---|
| 1 | 1 | search_papers 2020+ | domain-specific self-supervised pretraining semantic segmentation small dataset | 502 |
| 2 | 1 | search_papers 2022+ | SparK sparse masked modeling convolutional networks pretraining | 502 |
| 3 | 1 | search_papers 2023+ | continued pretraining DINOv2 domain adaptation self-supervised | 502 |
| 4 | 1 | WebSearch | SparK "Designing BERT for Convolutional Networks" github | 2301.03580, keyu-tian/SparK |
| 5 | 1 | WebSearch | continual SSL pretraining DINOv2 domain-specific 2025 segmentation | 2604.10609, 2509.17816, 2509.06990, 2511.04288 |
| 6 | 1 | search_papers 2020+ | dense contrastive learning self-supervised visual pretraining | DenseCL, VADeR, SPARC 2026 |
| 7 | 1 | search_papers 2021+ | in-domain self-supervised pretraining versus ImageNet transfer segmentation | dermoscopy study 2026, LOCA, surgical SSL |
| 8 | 1 | search_papers 2022+ | self-supervised pretraining industrial surface defect segmentation | DINOv3 vs ImageNet industrial 2026, X-ray SSL 2024, AGSSP |
| 9 | 1 | search_papers 2022+ | masked autoencoder pretraining crack segmentation | nothing on MIM for cracks |
| 10 | 1 | search_papers 2025+ | continual self-supervised pretraining DINOv2 domain-specific images | RAD-DINO, DIET-CP, MammoDINO |
| 11 | 1 | search_papers 2021+ | self-supervised learning electroluminescence photovoltaic solar cell | no EL SSL beyond Torpey |
| 12 | 1 | search_papers 2023+ | self-supervised pretraining thin curvilinear structure segmentation vessels fibers | nothing new |
| 13 | 1 | search_papers 2022+ | masked image modeling auxiliary loss during fine-tuning semantic segmentation multi-task | HPM only |
| 14 | 1 | search_papers 2025+ | self-supervised dense representation learning convolutional network segmentation 2025 | Fault-SGS (no abstract) |
| 15 | 1 | search_papers 2024+ | masked image modeling pretraining convolutional networks hierarchical sparse | Frepa, SS-UNet, FreMIM |
| 16 | 1 | search_snippets | domain-specific SSL gain disappears with full labelled data | rate-limited |
| 17 | 1 | get_citations | NeCo arxiv:2408.11054 | 5 citers, none narrow-domain |
| 18 | 1 | similar_papers | VasoMIM + AOI-SSL + dermoscopy study | inpainting SSL for medical seg |
| 19 | 2 | search_papers 2025+ | domain-specific self-supervised pretraining semantic segmentation small dataset | Selective masking 2512.06981, Subimage overlap 2601.01781, aerial road inpainting 2503.24326, RS pretraining study (Sensors 2026) |
| 20 | 2 | search_papers 2023+ | SparK sparse masked modeling convolutional networks pretraining | SparK; SparK mask-pattern note 2505.08819; Wolf 2023 small medical sets |
| 21 | 2 | search_papers 2024+ | continued pretraining DINOv2 domain adaptation self-supervised | DINOv2 for concrete cracks (MIR 2026), Efficient SSA (ICCVW 2025), STRADAViT |
| 22 | 2 | search_papers 2022+ | masked image modeling auxiliary loss jointly with supervised segmentation training | TTT-MAE only; still no joint MIM + supervised segmentation paper |
| 23 | 2 | search_papers 2023+ | self-supervised pretraining crack segmentation unlabeled images | FreeCOS (covered by D11 / D06), crack UDA; no crack SSL pretraining |
| 24 | 2 | search_papers 2025+ | dense self-supervised learning pixel-level representation 2025 | LeJEPA, JEM 2610.10013, MatSSL, patch kernel alignment |
| 25 | 2 | search_papers 2025+ | self-supervised pretraining industrial defect segmentation unlabeled images | AGSSP, patch-sampled CL for metallography |
| 26 | 2 | search_papers 2024+ | in-domain self-supervised pretraining outperforms foundation model transfer small dataset | plant MAE FM 2609.32183, Virchow2 |
| 27 | 2 | search_papers 2023+ | pretraining whole encoder-decoder U-Net self-supervised reconstruction segmentation | masked U-Net pretraining (ultrasound), STU-Net |
| 28 | 2 | search_papers 2023+ | test-time training masked autoencoder segmentation distribution shift | Continual-MAE, ConvNeXt V2 |
| 29 | 2 | search_papers 2024+ | frequency masked autoencoder high-frequency fine structures pretraining segmentation | Frepa, FreMIM |
| 30 | 2 | search_snippets | in-domain pretraining on small dataset outperforms DINOv2 transfer LeJEPA | rate-limited |
| 31 | 2 | search_papers 2024+ | benchmark self-supervised learning medical segmentation CNN masked autoencoder nnU-Net OpenMind | OpenMind (ICCV 2025), FOMO25 |
| 32 | 2 | WebSearch | Frepa high-frequency components medical visual foundation model github code | github.com/arturia-pendragon-iris/frepa |
| 33 | 2 | WebSearch | LeJEPA in-domain pretraining small dataset outperforms DINOv2 DINOv3 Galaxy10 | Galaxy10 claim; Mine-JEPA 2604.00383 |
| 34 | 2 | search_papers 2025+ | self-supervised pretraining thin structures roads vessels cracks representation small objects | PEPA 2606.23486 (adapter, not SSL), UCS |
| 35 | 2 | get_citations | LeJEPA arxiv:2511.08544 | 40 citers, almost all world models; no dense in-domain follow-up |
| 36 | 2 | similar_papers | Frepa + DINOCell + plant MAE FM | FreMIM, CUPre, plant FMs; nothing closer |
| 37 | 2 | search_papers 2024+ | self-supervised pretraining infrared grayscale images segmentation in-domain | IR fusion only; low-data SSL comparison 2404.17202 |
| 38 | 2 | search_papers 2024+ | ConvNeXt V2 FCMAE domain-specific pretraining segmentation fine-tuning | SEM particle SSL (npj Comp Mat 2025), SARATR-X |
| 39 | 2 | search_papers 2025+ | dense contrastive learning pixel-level self-supervised segmentation narrow domain medical industrial | ConPro (DSA vessels), counterfactual pixel CL |
| 40 | 2 | search_papers 2024+ | how much unlabeled data in-domain self-supervised pretraining scaling dataset size segmentation | FFPN Frangi pretraining (MedIA 2025) |
| 41 | 2 | fetch_fulltext + read_paper | SEM SSL (doi:10.1038/s41524-025-01802-3), LeJEPA (arxiv:2511.08544) | numbers below |
| 42 | 2 | search_papers 2025+ | DINOv3 continued self-supervised pretraining domain-specific dense features segmentation | V-pretraining 2601.22108, DINOv3 medical / dental benchmarks |
| 43 | 2 | WebSearch | 2026 in-domain self-supervised pretraining industrial inspection segmentation beats ImageNet DINOv3 grayscale | confirms 2605.23472 and 2605.12430 findings |

## What our own runs already closed (E, from BRIEF section 5 and handbook docs 11 / 19)
- SparK-style MIM of the ImageNet ResNet-34 U-Net++ encoder on the 11.9k pool (mask 0.6, 32 px patches at 512 px, normalised-pixel L2 target, batch 32, 36,500 steps), then PF fine-tune at 100% labels, 5 v 5: crack IoU +0.0048 (MDE 0.0113), relF1@2 +0.0035, inactive -0.0118, E1 crack recall -0.024. Encoder kept by PF. n.d., closed. DDeP (decoder denoising) on the same setup: n.d.
- Closed: continued pixel-target MIM and decoder denoising of ResNet-34 from ImageNet on the 11.9k pool, PF, 100% labels.
- Open: other backbones (ConvNeXt V2, hybrid conv-ViT, ViT), other targets (frequency, gradient, ridge-filter maps), joint-embedding objectives (DINO / iBOT / JEPA / SIGReg), structure-guided or hard-patch masking, from-scratch in-domain pretraining, the 159k pool, E1-directed evaluation, fold-based measurement.
- Pool facts (E): the 159k HF pool is CSIR + ARTS only, 84% of new rows ARTS mono 5-busbar, no BMRK / CFVS / SDLE, no E1 module family, and it contains 21 of our 50 test cells by ID plus about 2,400 byte-identical pairs. De-duplicate against test, val and E1 before any pretraining.

## Evidence on "in-domain SSL vs ImageNet / general FM"
R (what papers measured):
- Hamda et al. 2026 (dermoscopy): ResNet-34 U-Net, ImageNet init beat in-domain masked reconstruction at every label budget; ImageNet then in-domain SSL lowered Dice at 4 of 5 budgets. Same architecture and same result as our MIM null.
- Rettenberger et al. 2025 (SEM particles, greyscale, 25k unlabelled images, new in session 2, full text read): ConvNeXt V2 FCMAE trained in-domain from scratch beat the official ImageNet ConvNeXt V2 weights at every model size, by +0.8 to +1.5 AJI+ (low magnification, scores around 85 to 87) and +1.9 to +5.9 (high magnification, fuzzier images). DenseCL on the same images was below ImageNet. Best size was Pico (8.6M params); larger models did not help. In-domain FCMAE passed ImageNet with only about 1,000 pretraining images on the low-magnification task. Cost: 15,000 epochs, 640 px random crops (no rescaling, to keep small details), 32 px mask patches, 50% mask, 33 to 188 h on 80 A100s. Downstream was Mask R-CNN, 10 repeats.
- LeJEPA 2025 (full text section 6.3 read): with default settings and 400 epochs on Galaxy10 (11k images), in-domain LeJEPA on ResNet-18 / ResNet-34 / ConvNeXt V2-Nano / LeViT beat DINOv2 ViT-S and DINOv3 ViT-S transfer, both frozen and full fine-tune, 3 seeds. Classification only; also works on Flowers102 (1k images).
- Mine-JEPA 2026 (sonar, 1,170 images): in-domain SIGReg SSL F1 0.935 vs fine-tuned DINOv3 0.922; applying in-domain SSL on top of a foundation model lowered results by 10 to 13 points.
- Gharbage et al. 2026: DINOv3 helps ConvNeXt only after full fine-tune on RGB defects; supervised ImageNet better on X-ray (greyscale modality shift).
- AOI-SSL 2026: on 7k monochrome AOI images, MAE beat DINO and iBOT; in-domain SSL beat scratch and ImageNet ViT; hybrid conv-ViT kept thin wires (wire IoU 66.7 vs 43.0).
- Guo et al. 2026 (plant imaging, 10M tiles): in-domain MAE ViT beat a natural-image MAE by +0.069 mean Dice; gains grew with pretraining scale.
- Selective masking 2025 (weeds): masking the highest-reconstruction-loss patches beat random masking and ImageNet by about +2.5% on weed sets, mostly on the weakest classes; same-dataset pretraining was best under a low budget.
- MedDINOv3: domain continued pretraining +1.87 Dice; multi-scale token aggregation (+2.10) and resolution (+2.06) each gave more.
- DINOCell: continued domain SSL on DINOv2 "changed little" in-distribution.
- Weed VFM (2511.04288): domain SSL gains larger on unseen conditions than in-distribution.
- FFPN (MedIA 2025): Frangi-filter pseudo targets on 1,510 unlabelled MRA volumes as multi-task pretraining raised clDice by about 2 to 3 points over recent semi- and self-supervised methods on 4 vessel sets.
- VasoMIM: structure-guided masking over plain MAE only +0.35 to +1.1 Dice.
- Frepa: frequency-aware MAE-style pretraining, up to +15% Dice on retinal vessels.

S (judgement):
1. Continued SSL on top of a strong init gives about zero or hurts (our MIM null, Hamda, Mine-JEPA, DINOCell). Gains appear when (a) SSL is the init itself, trained in-domain, on a backbone whose pretraining recipe matches (FCMAE for ConvNeXt V2, SIGReg for small CNNs), (b) under domain shift (E1), and (c) the target emphasises fine high-frequency or ridge structure (Frepa, FFPN).
2. The SEM paper is the closest positive evidence for us: greyscale, 25k images, small particles, CNN, in-domain from scratch beats ImageNet, the bigger gap on the fuzzier images. Its cost is the problem (thousands of GPU-h); a shorter schedule on a 1-ch Pico / Nano at 512 px is the affordable version.
3. Plain reruns on R34 with more pool images are not worth GPU time. The live bets are: in-domain FCMAE ConvNeXt V2 (from scratch and continued), ridge- or frequency-targeted pretraining that also trains the decoder, and SIGReg in-domain as the bold bet. Judge every arm on folds and E1, and always against the same backbone's ImageNet init.

## Selected papers
score = value for raising our numbers; bench = value for the benchmark suite / protocol.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2301.00808 ConvNeXt V2 (FCMAE) | 2023 | CVPR 2023 | github.com/facebookresearch/ConvNeXt-V2 | Fully convolutional MAE (sparse conv on visible patches) + GRN so ConvNets gain from MIM | Two arms on the de-duplicated pool, 1-ch stem, 512 px random crops without rescaling: (a) continue FCMAE from ImageNet V2-Nano/Tiny weights; (b) from-scratch FCMAE on Pico/Nano, as in the SEM paper. Mask 0.5, 32 px patches. Encoder in smp U-Net++ with a stride-2 skip. PF fine-tune. Baseline = same backbone with ImageNet FCMAE+FT weights | 52 | 60 |
| 2 | doi:10.1038/s41524-025-01802-3 Rettenberger et al. (SEM) | 2025 | npj Comput. Mater. | github.com/lrettenberger/ConvNeXt-V2 (from paper) | Evidence and recipe: in-domain from-scratch FCMAE on 25k greyscale images beats ImageNet by +0.8 to +5.9 AJI+, best at small sizes; DenseCL loses to ImageNet | Use their modified repo and settings (crop, no rescale, 32 px patches, 50% mask, pick checkpoint by val reconstruction loss) for arm 1b; scale epochs down about 20x to fit 8 A6000; Pico/Nano only | 45 | 45 |
| 3 | arxiv:2407.14651 Frepa | 2024 | IEEE TMI 2025 | github.com/arturia-pendragon-iris/frepa (web search; ViT-B, Swin-B, ConvNeXt checkpoints listed; not opened) | MAE-style pretraining with high-frequency masking + low-frequency perturbation + embedding consistency | Cracks are high-frequency dark lines; scuffs, contrast and source style are low-frequency. Frepa's ConvNeXt variant on the pool at 512 px, 1-ch; low-frequency perturbation doubles as source / scuff invariance aimed at E1. PF fine-tune. Shares baseline with #1 | 50 | 40 |
| 4 | arxiv:2312.15273 FFPN (Frangi pretraining) | 2025 | Medical Image Analysis | github.com/shigen-StoneRoot/FFPN (from abstract) | Unlabelled images preprocessed with a Frangi vesselness filter; a multi-task pretraining predicts the filter maps (plus reconstruction), so the whole network, decoder included, learns thin-structure outputs | Dark-ridge filter (Frangi on inverted EL, sigma 1 to 2 px, plus black top-hat) on the de-duplicated pool; pretrain the full U-Net++ R34 (encoder and decoder) to regress the ridge map and reconstruct the image; then house PF fine-tune. Differs from our MIM / DDeP: the target is a crack-like structure map, and the decoder is pretrained toward it. Watch busbar / finger ridges: suppress them with the house model's structural-class predictions | 50 | 30 |
| 5 | arxiv:2511.08544 LeJEPA (bold bet) | 2025 | arXiv | github.com/rbalestr-lab/lejepa (from abstract) | JEPA prediction loss + SIGReg (push embeddings to an isotropic Gaussian); one hyperparameter, no teacher, stable on ResNets and ConvNeXts; in-domain on 11k images beats DINOv2/v3 transfer | Train R34 and ConvNeXt V2-Nano from scratch on the 11.9k pool with LeJEPA at 256 to 512 px crops, 1-ch, crop scales kept small so 1 to 2 px cracks survive; add SIGReg on per-patch features (a dense variant, untested in the paper) as a second arm. Then U-Net++ PF fine-tune. Baseline = ImageNet init of the same backbone. Risk: evidence is classification only | 40 | 55 |
| 6 | arxiv:2508.10794 VasoMIM | 2025 | AAAI 2026 | project page dxhuang-casia.github.io/VasoMIM (repo unverified) | Masking guided by a Frangi map + consistency through a frozen segmentor | Ridge-filter-guided masking at ratio 0.5 and consistency through frozen house crack / inactive logits, on top of #1 or #3. Paper's own gain over MAE is small (+0.35 to +1.1) | 38 | 30 |
| 7 | arxiv:2605.12430 AOI-SSL | 2026 | CVPR-W 2026 | none listed | MAE beats DINO / iBOT on 7k monochrome industrial images; hybrid conv-ViT keeps thin wires; patch-retrieval kNN head adapts to a new device with tens of labels | (a) MAE on a hybrid conv-ViT on the pool, PF; (b) a kNN patch-retrieval head on house encoder features with a memory from a few labelled half-cut cells (E1 few-shot track). (b) is cheap and aimed at E1 | 38 | 55 |
| 8 | arxiv:2601.18619 Scale-aware SSL | 2026 | arXiv | none | Small-window crops in SSL so pretraining sees fine sparse structures; +13% seismic faults, +5% cells, no gain on large regions | 32 to 96 px crops resized up, half near dark ridges, in the DINO / LeJEPA arms (#5, #10). Report crack and inactive separately (the paper predicts inactive will not move) | 40 | 30 |
| 9 | arxiv:2408.11054 NeCo | 2024 | ICLR 2025 | github.com/vpariza/NeCo (from project page) | Post-pretraining with patch-neighbour ranking consistency; about 19 GPU-h; +5.5 to +7.2 on dense probes | NeCo on DINOv2-reg / DINOv3 ViT-B with pool cells at 448 to 518 px, 1-ch repeated to 3, before the D24 VFM fine-tune. Arm vs the same VFM without NeCo | 40 | 45 |
| 10 | arxiv:2509.02379 MedDINOv3 | 2025 | arXiv | github.com/ricklisz/MedDINOv3 | Continued DINOv3 (DINO + iBOT + KoLeo, Gram anchoring, high-res) + multi-scale token aggregation | Cheap part first: multi-scale aggregation + 512 to 768 px on DINOv3 ViT-B with no pretraining change; then the continued run on the pool. Their ablation says the first part gave more | 40 | 55 |
| 11 | arxiv:2512.06981 Selective masking | 2025 | arXiv | none found | Iterative MIM that masks the patches with the highest reconstruction loss; helps the weakest classes most; same-dataset pretraining best at low budget | Apply to #1 or #4: mask the hardest-to-reconstruct patches (on EL these are cracks, splices, gridline breaks, edges). Targets problem 4 (gridline, splice, edge_dark) as well as crack | 35 | 25 |
| 12 | arxiv:2405.09365 SARATR-X | 2025 | IEEE TIP | github.com/waterdisappear/SARATR-X (from abstract) | Foundation model for noisy greyscale SAR on 0.18M unlabelled images; MIM with multi-scale gradient features as targets instead of raw pixels, to avoid learning speckle | Cheapest variant of our closed run: repeat the R34 SparK setup but replace the normalised-pixel target with multi-scale gradient / HOG targets. EL sensor noise and source contrast differ; gradient targets keep edges and ridges. Baseline = our pixel-target MIM checkpoint and the house PF | 30 | 25 |
| 13 | arxiv:2604.10609 DINOCell | 2026 | arXiv | github.com/kadenstillwagon/DINOCell | Continue DINOv2 ViT-B (DINO + iBOT) on 130k domain images with patch size 14 to 8 | Patch 8 at 512 px gives 64 x 64 tokens; continue on the de-duplicated pool. Their ablation found little in-distribution gain, so judge on E1 and folds. Expensive | 33 | 45 |
| 14 | arxiv:2405.15613 SSL data curation | 2024 | arXiv | github.com/facebookresearch/ssl-data-curation | Hierarchical k-means + balanced sampling over clusters gives better SSL features than uncurated data | The 159k pool is 84% ARTS mono 5-busbar (E). Cluster pool embeddings, draw a balanced 30 to 50k subset (mono / multi / half-cell, CSIR / ARTS, dark-streak cells) after de-duplication. Add-on to any pretraining arm | 33 | 40 |
| 15 | arxiv:2301.03580 SparK | 2023 | ICLR 2023 | github.com/keyu-tian/SparK | MIM for any CNN: sparse conv on visible pixels + hierarchical decoder | Already run on R34 (n.d.). Keep as the benchmark's CNN in-domain MIM row | 12 | 60 |
| 16 | doi:10.64898/2026.10.14.26365443 Hamda et al. | 2026 | medRxiv | none | Controlled study: in ResNet-34 U-Net, ImageNet beats in-domain masked reconstruction; ImageNet then SSL hurts | No arm. Independent replication of our MIM null; reason to stop R34 + pool-MIM variants | 15 | 60 |
| 17 | arxiv:2605.23472 Gharbage et al. | 2026 | arXiv | none | ConvNeXt with DINOv3 vs ImageNet init on industrial RGB and X-ray; ImageNet better under X-ray modality shift | Benchmark design: include ConvNeXt-T ImageNet and ConvNeXt-T DINOv3 rows under the same fine-tune; prior that a general FM is not automatically better on 1-ch EL | 20 | 65 |
| 18 | arxiv:2604.00383 Mine-JEPA | 2026 | arXiv | none found | In-domain SIGReg SSL on 1,170 sonar images beats fine-tuned DINOv3; in-domain SSL applied on top of an FM loses 10 to 13 points | Supports #5 (in-domain from scratch) and argues against continued SSL on DINOv3 as the default; for the benchmark, pretraining rows must separate "from scratch in-domain" from "continued" | 22 | 45 |

Other evidence rows kept from session 1 (no standalone arm): arxiv:2406.10973 ExPLoRA (cheaper continued DINOv2 with LoRA, only if #10 or #13 shows a sign), arxiv:2511.04288 Weed VFM (gains largest under shift: make E1 the primary SSL metric), doi:10.3390/app14072785 Intxausti (in-domain SimSiam / SimMIM beat ImageNet on 27.9k X-ray images, detection), arxiv:2212.04690 Kang (pathology SSL benchmark template), arxiv:2305.13456 Corley (match input size and normalisation to pretraining; ImageNet must always be a row), arxiv:2509.17816 GLARE (adapter-only continual dense SSL), arxiv:2609.32183 Guo (in-domain MAE beats natural MAE by 0.069 Dice; scales with data), doi:10.1109/iccv51701.2025.02213 OpenMind (ICCV 2025: a fixed SSL benchmark on one pretraining set and two architectures against a strong from-scratch nnU-Net; protocol template for the benchmark's pretraining section).

## Minimum experiments
Shared rules (S): de-duplicate the pool against test, val, E1 (ID and bytes) first; compare against the same backbone's ImageNet init under PF, never R34 alone; report per-stage encoder cosine to init; screen 2 seeds on the cv5v2 folds (out-of-fold) + E1, 5 seeds only on pass. Pretraining runs go on cv02 in parallel, fine-tunes reuse one baseline per backbone.

1. ConvNeXt V2 FCMAE (#1, #2): arm A = continued FCMAE from ImageNet V2-Nano on 11.9k (about 40 GPU-h); arm B = from-scratch FCMAE on Pico/Nano, 11.9k then 50k curated (100 to 300 GPU-h); baseline = V2-Nano ImageNet weights, PF. Metrics: out-of-fold crack relF1@2, E1 crack recall, inactive IoU. Kill if all three below +0.01.
2. Frepa (#3): ConvNeXt arm with Frepa pretraining, same baseline as 1. Kill as 1.
3. FFPN ridge-target pretraining (#4): arm = U-Net++ R34 pretrained to predict ridge maps + reconstruction on 11.9k (about 20 GPU-h), then house PF; baseline = house PF and our MIM checkpoint. Kill if out-of-fold relF1@2 < +0.005 and E1 crack recall < +0.02.
4. LeJEPA (#5): arm = R34 and ConvNeXt V2-Nano from scratch, 400 epochs on 11.9k (about 40 GPU-h each), then PF; baseline = ImageNet init of the same backbone. Kill if both below ImageNet on out-of-fold relF1@2 (no gain needed to keep the benchmark row, but a gain is needed to keep it as a model arm).
5. VasoMIM masking (#6) and selective masking (#11): add to the winner of 1 to 3; kill if relF1@2 out-of-fold < +0.005 and E1 recall < +0.01; for #11 also check gridline and splice IoU on folds.
6. AOI-SSL kNN head (#7b): house encoder features + memory from a few labelled half-cut cells; baseline house PF ensemble; metric E1 crack recall at matched precision; kill if < +0.02. About 2 GPU-h.
7. Scale-aware crops (#8): inside 4 or 8; kill if relF1@2 out-of-fold < +0.005.
8. NeCo (#9): D24's DINOv3 ViT-B arm after NeCo on pool (about 20 GPU-h) vs without; kill if E1 crack recall and out-of-fold relF1@2 both < +0.01.
9. MedDINOv3 (#10): step 1 aggregation + resolution only; step 2 continued pretraining (about 200 GPU-h); kill step 2 if < +0.01 relF1@2 and < +0.02 E1 recall over step 1.
10. SARATR-X gradient targets (#12): rerun the closed R34 SparK job with HOG / multi-scale gradient targets (about 15 GPU-h pretrain + fine-tunes); kill if crack IoU < +0.012 (MDE) and E1 recall < +0.02.
11. DINOCell (#13): only if 8 or 9 shows a sign.
12. Curation (#14): winning arm on curated 30k vs random 30k; kill if n.d.
13 to 18: evidence or benchmark rows.

## Rejected (one line each)
- arxiv:2509.06990 DIET-CP: datum-index objective, classification-only evaluation, negative on fine-grained in-domain sets.
- arxiv:2203.05573 Self pre-training MAE: MAE on the target training set on a plain ViT; superseded by pool-scale MIM, which we ran.
- arxiv:2408.05815 HySparK and doi:10.1016/j.radonc.2025.110711 SS-UNet: 3D medical whole-network MIM; 2D analogues are #1 and our closed run.
- doi:10.1109/cvpr52729.2023.01000 Hard Patches Mining: learned hard-patch masking; #11 is the simpler 2025 version, keep HPM as a fallback.
- arxiv:2210.01571 VICRegL, doi:10.1109/cvpr46437.2021.00304 DenseCL, doi:10.1109/wacv57701.2024.00019 LOCA: dense joint-embedding SSL for natural images; the SEM paper found DenseCL below ImageNet on greyscale in-domain data.
- arxiv:2401.10815 RAD-DINO: greyscale control only.
- arxiv:2209.00314 Kalapos: counter-evidence only.
- arxiv:2210.00923 Masked Supervised Learning: augmentation, belongs to D21.
- arxiv:2610.10013 JEM (Meta, 2026): patch-level SSL at 300M to 7B params; natural-image scale, no small-domain evidence; reference for the benchmark's FM rows when weights appear.
- arxiv:2601.22108 V-pretraining: continued pretraining with a downstream-guided view / mask designer; interesting but no code found and evidence is ADE20K / NYUv2 with DINOv3.
- arxiv:2503.24326 Aerial road inpainting SSL: inpainting pretraining for thin roads; same mechanism family as our closed MIM / DDeP, abstract gives no numbers.
- arxiv:2312.12480 Continual-MAE and arxiv:2209.07522 TTT-MAE: test-time MAE adaptation; belongs to D30 (DG / UDA for E1).
- arxiv:2606.23486 PEPA: post-encoder adapter for curvilinear segmentation, not pretraining; belongs to D09 / D22.
- arxiv:2307.07245 FreeCOS: fractal synthesis for curvilinear segmentation; covered by D06 / D11.
- doi:10.1007/s11633-025-1553-5 DINOv2 for concrete cracks: uses DINOv2 features, no in-domain SSL; covered by D14.
- Torpey et al. (arxiv:2402.17611): covered by D07.

## Gaps
- Joint SSL + supervised training (MIM or ridge-target loss kept on during fine-tuning, so the fine-tune cannot erase the pretraining) still has no paper (queries 13 and 22). Cheap to test anyway as an extra loss head; worth its own search.
- No SSL pretraining paper on cracks of any kind (queries 9, 23); no EL SSL beyond Torpey (query 11).
- No dense (segmentation) evidence for LeJEPA / SIGReg; the in-domain wins are all classification. A dense SIGReg variant would be new.
- Semantic Scholar snippets were unavailable in both sessions; for most 2026 entries numbers come from abstracts. Full text read only for the SEM paper and LeJEPA.
- Fault-SGS (doi:10.1016/j.eswa.2026.135052) has no abstract in the index; read when publisher access returns.
- E1-directed SSL on unlabelled E1 images is a transductive track decision for the lead / benchmark design.
- The 159k pool is not on disk and is narrow (E). Download only if arm 1, 3, 4 or 5 shows a sign at 11.9k.
