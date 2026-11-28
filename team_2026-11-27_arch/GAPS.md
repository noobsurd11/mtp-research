# Gaps of the 27 Nov sweep

Sources: section NOT_FOUND (or "Gaps") of each `scouts/<id>/REPORT.md`, and each report's tool-status notes.

## 1. Search tools that failed
- **Semantic Scholar was rate-limited for the whole session in all 8 family scouts.** Effects: `search_snippets` failed every time it was tried (general 2 attempts, every other scout 1); `get_citations` worked only through the other indexes (dg); S2-only hits are missing (med, recipe); citation contexts, for example critiques of PV-SAM or nnSAM, were not checked (vfm).
- **arXiv timed out on most queries** (thin, dg, data, recipe, unsup, med "frequent time-outs", vfm "some calls"). Two arXiv-only queries returned nothing (data q27 "synthetic data thin structure segmentation diffusion", q28 "electroluminescence solar cell segmentation"); med q37 (nnU-Net 2D thin curvilinear benchmark) returned 0. **Preprints from Oct to Nov 2026 are probably under-covered** (thin, dg).
- Scopus answered only sometimes (data, unsup, vfm). OpenAlex and ScienceDirect did most of the work.
- **Full-text fetches that timed out or had no open copy:** WireSegHR, RPCANet++ (first try; worked later) (thin); EVP (vfm); D2ADA, the IJCV 2025 AL study, Shim 2025 (dg); arXiv 2407.08209 curvilinear dataset expansion, vesselFM first try (data); Cellpose3, Touchstone, Omnipose, MedFormer (med). `fetch_fulltext` timed out for recipe, which read arXiv copies instead.
- **Index records without an abstract:** tqdm (dg, kept at fit 0); Minimum Strip Cuts (recipe, same gap as D26); Masked Generative Distillation (recipe); the 2026 retinal input-resolution study doi:10.1007/s10278-026-02135-3 (data); HCFNet abstract truncated (vfm); SSRN preprint of PV-SAM (vfm); arxiv:2609.13232 "What Does the Encoder Actually Decide?" has template placeholders in its abstract and was not used (general).
- **Code not verified:** GMMSeg, RPL, CSST, PyramidFlow, ContrastSeg (unsup); FACS-net repo URL not captured (thin, general). **Licences not verifiable:** Dhimish data, PSCDE, Akram Hugging Face weights, vesselFM, Preserve-the-Hard and DIDEX repos (data).

## 2. Classic or expected papers the tools never returned (NOT_FOUND)
- **general:** Swin Transformer; PSPNet, UPerNet, FPN, DeepLabv3+ originals; RepLKNet; LocalMamba; Visual Attention Network; PoolFormer / MetaFormer; MaxViT; CMT; BEiT; BiSeNet V1/V2 originals; Dite-HRNet; PP-LiteSeg, SeaFormer, TopFormer; ESPCN pixel shuffle.
- **thin:** CT-CrackSeg, CrackSeU, CrackSegNet (query 42, no results); CFD dataset paper (Shi et al. 2016) and CrackTree (Zou et al. 2012).
- **vfm:** Painter; iBOT; MAE (He et al.); MobileSAM; DDP (Ji et al. 2023); VPT (Jia et al. 2022); SAM-Med2D (not searched by name).
- **med:** Swin-UNETR original; SegMamba (D25 holds it); KiTS23, BraTS 2023 and FLARE 2022 winners' reports.
- **recipe:** "When do flat minima optimizers work?" (Kaddour et al., NeurIPS 2022); trainable weight averaging (TWA), PAPA, hierarchical weight averaging; Logit Standardization in KD (CVPR 2024).
- **dg:** original RandConv, SAR, CoTTA, TENT were not searched again (MASTER holds RandConv note P369, CoTTA P573, TENT P619, SAR P594).
- **unsup:** RbA and PEBAL not searched by name; DINO-Mix in D29.
- **data:** AnyStar not searched (not relevant).

## 3. Topics where the search returned nothing (evidence gaps, not tool failures)
- Any segmentation paper on EL half-cut, shingled or multi-busbar **layout shift**; any paper isolating pure geometric layout shift (dg). Geometric layout synthesis for structured industrial images (data q30).
- A public EL set with half-cut cells and pixel masks (only Dhimish 2026, on request); an open physics simulator of EL crack images (data).
- An AD prior fused into a supervised multi-class pixel segmenter at full labels with per-class gains; contrastive or prototype losses evaluated on thin structures; self-training at full labels on a thin or defect task with an unseen-domain test (unsup).
- A training loss with an explicit pixel tolerance matching relF1@2 (relaxed / buffered precision-recall); layer-wise LR decay studies for CNN segmentation; SAM+SWA or GSAM on dense prediction (recipe).
- Any VFM against a well-tuned CNN on 1 to 2 px lines with a tolerance metric (vfm). PV-SAM is the only EL + VFM pixel paper and uses a random split.
- 2D ablations of deep supervision, foreground oversampling and CE + Dice on thin structures (med; same gap as D25).
- Controlled sliding-window vs whole-image inference for thin structures; elastic or grid distortion validated on 1 to 2 px labels; super-resolution preprocessing for EL cracks (data).
- Active learning or cold-start selection for PV/EL defect segmentation; thin-structure evidence for active DA beyond RIPU's 'pole' row (dg).

## 4. What a second pass should cover
1. **Re-run the S2-dependent calls** once the rate limit lifts: the failed `search_snippets` claims (HRNet vs U-Net on thin structures; dynamic upsampler on thin structures; tolerant thin-structure loss; AD map as an input channel), and `get_citations` on FACS-net, nnSAM, PV-SAM, CAPS, MIRO and CSST to find critiques and replications.
2. **arXiv sweep for Oct to Nov 2026** in every family, by date, since arXiv timed out.
3. **Full text for every wave-1 paper that is abstract only** before its readout is interpreted: Kervadec boundary loss, focal Tversky, CWD, EoA, FADE, SAPA, BlurPool, GIN+IPA (numbers for our ledger), plus U-HRNet, EVP, D2ADA, Shim 2025, WireSegHR and arXiv 2407.08209.
4. **Code and licence checks** for the arms going to builders (GMMSeg, CSST, FACS-net repo, SUPER has none) and for the data sources (Dhimish, PSCDE).
5. **Families no scout owned:** interactive or human-in-the-loop labelling tools for new layouts; topology-preserving post-processing beyond Curvi-Tracker; super-resolution and restoration front ends; mask-transformer heads on thin structures (D23 was the last look); test-time adaptation since D31.
6. **The classic originals in section 2** only for thesis citations; none of them is a candidate arm.
