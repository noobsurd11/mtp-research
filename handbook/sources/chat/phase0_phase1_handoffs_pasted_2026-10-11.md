

=== user message 2026-10-11T06:46:04.320Z (line 5252) ===
sir, I had worked something earleir as well, you need to know: phase0: 

<pasted_content id="1ebd">
Here's what I have. Part 1 is on record from earlier sessions, Part 2 is what we did in this chat.

## Part 1: Project state on record

**Setup**
- Dataset: BenchmarkELimages (582 labeled, ~12k unlabeled, 512x512, 24 classes), plus UCF-EL.
- Mandate: WattCycle wants detect, grade severity, estimate power loss. Your advisor wants a paper with a ~2M-param model.
- Core model: SA U-Net++ ported to PyTorch, Mean Teacher + SemiCE.

**Results and findings**
- Old SA ablation ("removing SA helps", 0.2028 vs 0.1792) and the SSL sweep (20%: 0.2580, 10%: 0.1323) are **invalid**. They predate the GaussNoise fix (albumentations 2.x ignored `var_limit`, noise erased cracks). Rerun before using any of it.
- Defect mIoU (crack + inactive) is the headline metric. Gridline (class 15) is noisy and excluded.
- SSL vs SL must match optimizer steps. An 8x step mismatch fake-produced a +7.4 gain.
- Reproduction gaps were metric-convention mismatches (Fioresi includes background, Pratt uses per-image median, PV-S3 ignores background-GT pixels).
- UCF-EL 20% labels, equal steps: SL 48.9 / 60.8 (PV-S3 metric), PV-S3 reimplementation SSL 46.4 / 58.9, FSL 100% 50.2.
- Class weights: sqrt-inverse-frequency (~310:1), not raw (98,000:1).
- Topology mask for Subpath A: `{1,2,3,4,9}`, so busbars and ribbons don't create fake isolated gaps.

**ALHVR port (Lei et al., ICCV 2025), second experiment**
- Eq. 22 sharpening breaks at C=24, so use softmax temperature sharpening.
- Cosine-logit ceiling at C=24 is ~0.24 max softmax, so use τ≈0.1.
- Eq. 15 prototype problem is NaN from division by zero on rare classes.
- Top risk: DTCT teaching background over cracks. Only thin-crack recall shows it.

**What was lost**
- The `noob` user on gaint was reset. Reproduction code, UCF val split, Subpath A code (57 tests), label splits and predictions are gone.
- Surviving: private repo `noobsurd11/el-fault-detection` (rebuilt foundation), and `sa-unetpp-ssl-el` (tag `v0-sa-failed`, failed SA experiment only).
- Second server `cv02@10.8.1.106` is being set up, with files to copy over from gaint.

## Part 2: This chat

**Decisions**
- Keep Mean Teacher. Add class-adaptive thresholding (FlexMatch style), decoupled from UniMatch's dual-stream.
- Architecture work comes before further SSL method changes.
- Goal order: (1) something WattCycle can pilot, with the quantification pipeline as core claim, (2) paper with accuracy contribution.
- No paired I-V data, so power loss relies on published correlations. Köntges A/B/C: power loss tracks **isolated (Type C) area**, not total crack pixels.
- Open check: does the BenchmarkEL taxonomy distinguish isolating cracks?

**Findings**
- The SA block is `sigmoid(Q+K)*V`, an elementwise gate, not dot-product attention (I confirmed this in `blocks.py`).
- Param counts from the repo code (my recomputation, not your logs):
  - SA U-Net++: 4,589,880
  - SA blocks: 88,000 (1.9%)
  - no-SA: 4,501,880
  - base-20: 1.79M
  - base-24: 2.58M
- No single base width gives exactly 2M. Report base-20 and base-24 as bracketing controls.
- Jetson has no FP8. Use INT8 + TensorRT.
- Stage-2 architecture ideas: true non-local attention at a coarse level, axial/strip attention, thin-structure-preserving downsampling. Check first whether cracks survive the encoder pooling.

**Subpath A plan (post-processing)**
Per-class connected components, `regionprops`, boundary-truncation flag, skeleton length, isolation detection, mm calibration, fixed output schema, manual check on 10-15 images.

**Subpath B plan (compression)**
1. SA vs no-SA ablation on uncompressed models.
2. Native-narrow controls (base-20, base-24).
3. Latency harness (CUDA events, on the Jetson).
4. Torch-Pruning to ~2M.
5. INT8 + TensorRT.
6. Rerun Subpath A on every compressed model.
7. Pareto plot.

**Paper links**
- UniMatch: arxiv.org/abs/2208.09910
- UniMatch V2: arxiv.org/abs/2410.10777
- CorrMatch: arxiv.org/abs/2306.04300
- AllSpark: arxiv.org/abs/2403.01818
- CCVC: arxiv.org/abs/2303.01276
- Sliced-Wasserstein (CVPR 2025): par.nsf.gov/biblio/10601309
- NREL crack-to-power-loss: osti.gov/servlets/purl/2999405
- EL to module power: arxiv.org/abs/2009.14712
- Dhimish & Hu 2022: ncbi.nlm.nih.gov/pmc/articles/PMC9288437
- Kropp et al. 2018: mdpi.com/1996-1073/11/5/1172

## One conflict to resolve

My record says the Mean Teacher and ALHVR presentations were already prepared (11-slide deck, ALHVR practiced aloud). You just said neither is presented yet. Which is right? Also, the ALHVR port is the live second experiment, so UniMatch and SegFormer are probably not the right slide picks anyway.
</pasted_content id="1ebd">

 phase1: 

<pasted_content id="1ebd">
# MTP handoff: semi-supervised PV defect segmentation (EL images)

Written Oct 11 2026 from conversation history and memory, because the on-box files were lost.
Status snapshot inside this doc = **00:04 IST, Tue Oct 6 2026**. Anything running then has probably finished: re-check both machines first.
Numbers come from CC (Claude Code) reports pasted into chat and from the poster. They are not re-verified against files. Items marked **[unverified]** need a check.

---

## 0. TL;DR (read this if nothing else)

1. **Project:** semi-supervised segmentation of defects in electroluminescence (EL) images of solar cells. Datasets: UCF-EL-Defect and BenchmarkELimages. Proposal: small U-Net + ALHVR-inspired SSL + severity grading.
2. **Deliverables:** (a) CV course poster (EE511, projector format): done, content now partly outdated. (b) **MTP progress report in LaTeX: not started.** Needs: reproductions, SA-UNet++ rerun, ALHVR as-is pilot, proposal.
3. **Reproduction:** Fioresi and Pratt reproduce once metric conventions are matched. Jha et al. (PV-S3) does not reproduce as published. **Jha's released code sets `ignore_index = 0` (background) in training and scoring, so it never models background**: 0.050 standard vs 0.828 on its own metric (public UCF-EL split).
4. **UCF-EL, 20% labels:** our PV-S3 reimplementation shows no gain over step-matched supervised (0.491 +- 0.009, 3 seeds). It collapses to ~0.28 (rare-class pseudo-label over-prediction).
5. **BenchmarkEL, 20% labels (95 images):** ALHVR and Mean Teacher beat supervised by ~0.02-0.03 defect mIoU, but **the unlabelled loss does nothing**: MT with lambda=0 equals MT; EMA adds nothing. Likely cause: BatchNorm sees 4+4 images in SSL arms vs 4 in SL. ALHVR loss-off control and batch-8 SL runs were still running.
6. **Real bottleneck:** crack over-prediction from class-weighted CE (crack precision 0.22-0.35 at recall ~0.70). A crack-logit shift picked on val gives +0.03 for SL and erases arm differences.
7. **Dead ends:** prototype-based fixes (EMA prototypes, prototype relabelling) and clDice. Closed by measurement.
8. **gaint was reset once** (all earlier on-box work lost). Rebuilt repo `el-fault-detection`. Rule: push after every step.
9. **Second server cv02** (8x A6000, shared) works and doubled throughput. Never compare arms across machines; only within a machine.
10. **Style the user wants:** terse, concise, no em-dashes, no buzzwords. Treat questions as tests, not confirmations. Don't assume; follow the code.

---

## 1. Context and people

- User: Om (memory also calls them Yash). Memory profile says B.Tech IT, RGIPT, 2nd year. The poster lists **Yash Vijay Patil, IIT Mandi, course EE511 Computer Vision, supervisor Dr. Dinesh Singh**. Identity/institute is inconsistent across sources: **confirm which institute and template the MTP report uses** (the question "do you have a template or page limit?" was never answered).
- Project is an MTP with WattCycle (solar asset-management company). Dual mandate: WattCycle wants a deployable detect, grade-severity, estimate-loss pipeline; faculty advisor wants a submittable paper with a lightweight model. Advisor directives pending: **reproduce a prior paper** (done), **explore Mixture of Experts** (gated, see section 12), lightweight model (~2M params in memory, ~4M on the poster).
- CV course also required two paper presentations: Mean Teacher (Tarvainen and Valpola 2017) and ALHVR (Lei et al., ICCV 2025). Both done. Slips found in the ALHVR practice run: gamma vs lambda confusion, module-to-region routing, dataset conflation.

## 2. Domain basics (for explaining)

- **EL imaging:** current through the cell makes it glow in infrared; damaged areas look dark. Defects: crack, contact/gridline interruption, interconnect, corrosion, inactive area.
- **Segmentation** labels every pixel; needed for severity. Labels are expensive, hence SSL.
- **IoU** = TP/(TP+FP+FN). Per class, **IoU = F1/(2-F1)** exactly. **Precision** = TP/(TP+FP), **recall** = TP/(TP+FN).
- **Imbalance:** UCF-EL pixel shares: background 92.2%, crack 5.57%, contact 2.06%, interconnect 0.093%, corrosion 0.052% (about 1761:1, from 0.92225668/0.00052361 = 1761.3). BenchmarkEL: background+padding ~86%, crack ~0.22%, rarest defects <0.001%.
- **Seed:** training seed controls init, data order, augmentation, dropout. Our split seed is fixed (split seed 0); only the training seed varies. At 95 labelled images, seed noise is about +-0.03-0.04 defect mIoU.
- **Epoch vs step:** an SSL loop iterating over the unlabelled set does many more optimizer steps per "epoch" than SL over the labelled set. Always match optimizer steps.

---

## 3. Machines, tools, access

### gaint
- RTX PRO 4500 Blackwell, 32 GB (another user holds ~6 GiB). torch 2.14.1+cu130 (nightly line; sm_120), torchvision 0.29.1, smp 0.5.0, albumentations 2.0.8, timm 1.0.30, Python 3.12, `.venv` inside the repo.
- Repo: `/home/noob/work/el-fault-detection`, remote `github.com/noobsurd11/el-fault-detection` (private). Old repo `sa-unetpp-ssl-el` holds only the failed SA experiment, tagged `v0-sa-failed`.
- Datasets: `/home/noob/work/datasets/BenchmarkELimages` (release `dataset_20211104` = CSB-S1, 582 images), `/home/noob/work/datasets/UCF-EL-Defect/training` (311 MB). **`data/labeled` in the repo is symlinks** to the BenchmarkEL folder (1,164 files = 582 images + 582 masks). `data/ucf_el` is a symlink to the UCF folder.
- Papers: `/home/noob/work/docs/papers`. Disk was 97% full before the reset; 935 GB free after.
- Last git head seen: `79571ae` (Oct 5 22:45). Earlier: `d920cd6`, `fe79e19`.
- Git push was blocked at one point by expired tokens: fix `gh auth login` then `git push origin main`.

### cv02
- `cv02@10.8.1.106`. 8x RTX A6000 48 GB, 64 cores, 1 TB RAM, driver 580 / CUDA 13.0. **Shared by ~186 users; other users' jobs load the GPUs** (speeds varied 2x).
- Access: via `noob_herald` exec (or `Yugma_Herald`) with **`ssh -i ~/.ssh/amlc_cv02 -o IdentitiesOnly=yes -o BatchMode=yes cv02@10.8.1.106 '...'`**. Default keys are refused.
- **Home `/usershome` is 100% full (9.2 GB free for everyone).** Everything lives in `/tmp/noob_el` (local NVMe, 1.3 TB, wiped on reboot). `/tmp/noob_el/env.sh` redirects XDG/PIP/UV/TORCH/HF/MPL/TMPDIR caches. Never write large files under `~`.
- Persistent copies of results: `~/noob/el_results/<run>/` (small files only, keep <50 MB). Working copy: `/tmp/noob_el/el-fault-detection`, results staging `/tmp/noob_el/results_to_sync`, report `reports/cv02.md`.
- tmux sessions on the shared account: `amlc` (the user's AMLC team, do NOT touch), `main`, `el` (our jobs). Jobs survive logout. Run tmux on the server, not locally.
- Setup facts: code tarball built from gaint HEAD (REVISION `fe79e19`), excluding `.venv`, `experiments`, `.git`, `data/labeled`, `data/ucf_el`. BenchmarkEL shipped as dereferenced `bench_labeled.tgz` (103 MB, 1,164 files). `stringzilla` pinned 5.1.2. Checksums of splits verified. 167 tests pass.
- Rules for jobs on cv02: pick GPUs with memory.used <1 GiB and util <10%; cap concurrent jobs (3, later 6, later stacked 2 per idle GPU); `CUDA_VISIBLE_DEVICES` per job; watchdog resumes once; latest+best checkpoints only; push nothing from cv02.
- Jha's released code lives under `/tmp/noob_el/pvs3/PV-S3` (+ `glue/PATCHES.md`).

### Tool quirks (MCP)
- `Gaint_Herald` exec: silently drops commands >~60 s; **blocks** `tmux`, standalone `cd`, output redirects, `sh`, `xargs`, `for` loops, `whoami`, sometimes `nvidia-smi`. Workarounds: pass `cwd`; run `python3 -c` with `subprocess`; detach long jobs with `nohup`/`start_new_session`; or put the task in a prompt for the user to paste into Claude Code.
- `noob_herald` exec worked for ssh to cv02 (earlier had authorization errors). `Yugma_Herald` is a fallback.
- CC model routing (memory): sonnet tier for basic work, opus tiers escalated by criticality.
- The user pastes prompts into CC on each machine themselves. Prompts should be self-contained code blocks.

---

## 4. Datasets and splits (new pipeline)

### UCF-EL-Defect (Fioresi et al. 2022)
- 9,562 train / 2,289 test (official, via `train_images.csv`/`test_images.csv`; filenames contain spaces and `+`, so use the CSV, not extension swaps).
- Masks: single channel class indices 0=background, 1=crack, 2=contact, 3=interconnect, 4=corrosion, **128=unknown, ignore** (4.79% of pixels).
- No val split exists upstream (upstream validates on test). We carved **957 val (10%, stratified by defect-presence signature, seed 0)** and a **20% labelled subset (1,912 images) drawn from train minus val**, stratified the same way, seed 0. Unlabelled pool for SSL = the other 7,650 official-train images (this **includes the 957 val images**, so val is not clean for reproduction arms; fix before any method work: rebuild labelled/unlabelled from train minus val).
- Average over the **4 defect classes** for Jha-style comparisons.
- Crack annotation width: **15.2 px median (4.92% of image side)**; mean image side 302 px.

### BenchmarkELimages (Pratt et al. 2023), "CSB-S1" in Jha
- Splits 478 / 54 / 50 = 582 images (paper text says 593: discrepancy is paper vs its own repo, not Jha). 24 classes (12 defect), 512x512.
- Releases: `dataset_20211104` (24 cls, CSB-S1), `dataset_20220723` (28 cls, ~2109 imgs, CSB-S2), `dataset_20221008` (29 cls, ~2282 imgs, CSB-S3). S2/S3 not downloaded (only needed for Jha Table 5).
- Crack annotation width: **2.0 px median (0.39% of side)**.
- Evaluation classes: **crack (14) and inactive (11)**; headline = **defect mIoU = mean(crack IoU, inactive IoU)**. Gridline (15) is a noisy class, excluded from headline. Pratt's own eval uses crack, gridline, inactive.
- Class-ID facts: ribbons=4, busbars=9. Topology mask for isolation = {1,2,3,4,9}; intensity cross-check = {1,2,3}.
- Class weights: hard-coded sqrt-inverse-frequency in `src/data/class_info.py` (max:min ~312.8). **They were computed over train+val+test (582 images): a leak** (matches to 5e-7). 6 zero-weight classes: sp_dogbone, clamp, rings, dead_cell, belt_mark, jbox.
- **20% subset (seed 0): 95 labelled images** (`data/splits/seed0/labeled_20pct.txt`); **unlabelled pool in current runs = 383 held-out train images with masks hidden** (`unlabeled_20pct.txt`). The earlier planned ~12k genuinely unlabelled set is NOT on gaint now.
- Genuine unlabelled set (earlier session): ~12k EL images on a Dropbox share. Selection method: DFS walk, per-leaf cap 2500, `random.seed(42)`, round-robin, `--count 12000` gave 11,993 after failures. No manifest survives. Found that the pool **leaks labelled train/val/test images by filename**: must filter by cell ID. App-key:secret Basic auth worked against Dropbox shared-link endpoints. Obtainable again; not yet re-downloaded **[unverified]**.
- Splits: **never rerun a split script that reshuffles**. Committed splits live in `data/splits/`, `seed0/`, `seed1/`, `seed2/`.

---

## 5. Metric conventions (the central lesson)

| name | definition | where used |
|---|---|---|
| **standard** | one global confusion matrix over all pixels (ignore label respected); mean over defect classes | our default, Fioresi 4-class |
| **Fioresi 5-class** | same but includes background class | Fioresi abstract 57.3 |
| **PV-S3 metric** | drop every pixel whose ground truth is background, then build the confusion matrix. **Recall is unchanged**, only background false positives vanish | Jha's code |
| **Pratt median** | IoU per image per class, median over test images, average over crack/gridline/inactive; **absent class scores 0 (rule B)** | Pratt 2023 |

- Pratt absent-class rules (we scored all): **A** exclude absent images, **B** absent scores 0 (**primary, reproduces Pratt**), **C** absent and unpredicted scores 1. Under B, any class present in <50% of test images has median 0 by construction (inactive present in 17/50).
- PV-S3 metric proof of recall invariance: TP and FN are defect-GT pixels; dropping background-GT pixels touches neither.
- On BenchmarkEL we also report **val+test pooled (104 images)** as secondary. **Final-step weights are primary** (54 val images are too noisy for best-val selection; it flips comparison signs). UCF has no val, so all UCF numbers are final-step.
- A metric that improves when predictions are dilated or when the background threshold is raised rewards false alarms.

---

## 6. Papers

| paper | what | key facts |
|---|---|---|
| Fioresi et al., IEEE J. Photovoltaics 12(1) 2022 | creates UCF-EL; DeepLabv3-R50 | abstract mIoU 57.3 (5-class). Table II F1 without sim: .80/.55/.20/.76 (contact/crack order: crack .80, contact .55, interconnect .20, corrosion .76); with sim: .81/.58/.33/.78. lr 0.005, threshold 0.54 in paper (code uses 0.52), aux loss. Validated on test set. 16,808 imgs (17,064 with 256 simulated) vs public 11,851 |
| Pratt et al. 2021 / 2023 | BenchmarkEL, 12 models = 4 archs x 3 weight sets | U-Net_12 16.00 (12,333,720 params, Gupta VGG16-UNet), U-Net_25 13.33 (25,858,887, Tomar), PSPNet 58.0M, DeepLabv3+ 22.4M (their best ~0.28). Weighted CE. Weight sets: A all 1.0; B inverse median pixel %; C custom (bg 0.2, ribbons 3, gridline 10, inactive 10, crack 20, others 1). Aug: 180 rot, mirror, flip (478 to 1912). **No epochs/LR/optimizer stated.** Set A band 0.04-0.24 |
| Jha et al., EAAI 160:111790 (2025), PV-S3 | mean-teacher SSL on UCF-EL | Table 1 SSL(20%) 67.00/72.50/88.90/78.17 (per class 89/49/40/90); SL(20%) 8.76; FSL(100%) 70.84; Table 3 SSL100% 74.75; Table 4 compares to Fioresi 57.30/59.00/59.75/57.75; seed std +-1.35; stated recipe: 30 ep, lr 1e-3, batch 16, crop 224. Code `github.com/abj247/PV-S3` (built on PS-MT) |
| Gangopadhyay et al., IEEE TETCI 9(2):1502 (2025) | SA-UNet++ | "SA" block is **sigmoid gating**, not dot-product self-attention; no spatial mixing |
| Lei et al., ICCV 2025, pp 21450-21459 | ALHVR | see section 10 |
| Others cited | Chen CPS (CVPR 2021), Oliver et al. (NeurIPS 2018, realistic SSL evaluation), Kontges et al. (2011, crack modes), MetaSSL (arXiv 2509.01144, per-class adaptive thresholds), FlexMatch/FreeMatch, Kang et al. ICLR 2020 (classifier bias) | |

Jha's own CSB-S1 crack results are 50-58 on the same 2 px annotations where Pratt gets 13-16: annotation width is **one of three confounders** (width, metric, absent-class rule), not "the" explanation.

---

## 7. Reproduction results

### 7a. Records from the first (lost) pipeline, used on the poster
| baseline | published | ours | note |
|---|---|---|---|
| Fioresi FSL 4-class / 5-class | 48.15 / 57.30 | 50.21 / 59.42 | per class IoU ours 66.89/44.43/33.20/56.35; P/R/F1 67.57/67.11/65.90 vs 59.00/59.75/57.75 |
| Pratt U-Net (rule B) | 13.33-16.00 | 15.01 | rule A 29.22, C 26.87; Set A under B 8.48 (inside paper's 0.04-0.24 band); our model 23,751,576 params |
| Jha SL 20%, 30 ep | 8.76 | 13.13 (PV-S3 metric), 10.83 standard | same undertrained regime |
| Jha SL 20%, 12.0k steps | n/a | 56.61 / 39.00 | converged |
| Jha SSL 20% (our reimpl), 95.7k steps | 67.00 | 58.85 / 46.40 | 8.15 short on their metric |
| SL 20% step-matched, 95.8k steps | n/a | 60.79 / 48.90 | beats SSL |
| FSL 100%, 59.8k steps | 70.84 | 65.84 / 50.21 | |
| FSL 30 ep / lr 1e-3 vs 100 ep / lr 5e-3 | n/a | 20.70 vs 50.22 | rare classes 0.00 to 33.20 (interconnect), 56.35 (corrosion) |
- Probes (records): all-crack predictor 10.50 (PV-S3) vs 0.45 standard (23x); 3 px dilation +8.92 vs -7.63; background-threshold sweep on SSL: argmax 58.85/46.40, t=0.52 59.57/46.44, 0.70 64.25/45.19, **0.90 67.99/38.41**; weighted-CE 30-ep model 68.36 PV-S3 vs 27.70 standard (ranking inversion).
- Pre-fix-of-metrics early claim "SSL doubles performance 10.83 to 21.19" is invalid (both runs undertrained).

### 7b. Re-run in the new pipeline (Oct 2026)
**UCF-EL** (defect mean, standard / PV-S3 metric), final-step, DeepLabV3+ R50 smp, bf16:
| run | steps | result |
|---|---|---|
| SL 20%, 30 ep, lr 1e-3 | 3,585 | 0.185 / 0.230 (interconnect, corrosion ~0) |
| SL 20%, lr 5e-3 | 12,000 | 0.448 / 0.559 |
| FSL, 30 ep, lr 1e-3 | 17,930 | 0.364 / 0.434 |
| **FSL 100 ep, lr 5e-3 poly** | 59,760 | **0.497 / 0.636** (Fioresi 4-class 0.482: reproduced) |
| **SL 20% step-matched, seeds 0-2** | 95,760 | **0.491 +- 0.009** |
| SL 20% strong-view-only diagnostic | 12,000 | about -0.045 vs normal SL |
| PV-S3 v1, s0 | 95,700 | 0.200 / 0.379 (collapse, precision 0.325 vs SL 0.646) |
| PV-S3 v2 (weak-view supervised loss), s0, s1 | 95,700 | 0.276, 0.283 (PV-S3 metric 0.568, 0.436) |
| PV-S3 v2 + per-class pseudo-label share cap | 95,700 | corrosion IoU 0.067 to 0.631; overall 0.418 standard **[figure labelled ambiguously in chat; verify]** |
- Probes (new): dilation +8.1 PV-S3 / -4.1 standard; threshold 0.9 on SSL 37.9 to 44.9 (PV-S3 metric).
- **The old record "SSL 46.4" is not reproduced** by v1 or v2 (old code lost). State this plainly in the report.
- Why PV-S3 v1/v2 collapses (no-training diagnostic on v2 s0 teacher, 7,650 unlabelled images): teacher predicts corrosion on **0.96% of unlabelled pixels, 23x the labelled share, 16x the truth**; **99.4% of pixels clear the 0.6 threshold**, so false corrosion labels feed back. PV-S3 metric hides it: corrosion 0.067 standard vs 0.879 PV-S3.
- Original diagnosis "supervised loss on strong view only" was **wrong as the main cause** (only -0.045).

**Pratt on BenchmarkEL, new recipe** (not stated in paper, so we chose: Adam 1e-3, cosine, 20k steps, batch 4, 512 input; smp U-Net VGG16 ~23.75M; weighted CE; rot180/flips):
- Rule B: **Set C 0.116, Set A 0.145** (paper U-Nets 0.133-0.160): **approximately reproduced** (about 2 points under). Rule A Set C 0.283. Global IoU Set A 0.331 beats Set C 0.284 (paper ranks C first): weight-set ranking is not stable across recipes. Records' 15.0 superseded.
- **Wrong claim to avoid:** "rule A Set C 0.283 is the paper's best 0.28"; paper's 0.28 is DeepLabv3+ under rule B.

### 7c. Jha's released code, run on cv02 (finished Oct 5 23:31 IST)
- Setup: DeepLabV3+ R50 deep stem, one student + two EMA teachers (keep rate 0.996), 125.3M params total; 30 epochs x 479 = **14,370 steps**; batch 16 + 16; lr from `saved/ssl_el/config.json` = **1e-2** (paper and CLI default say 1e-3).
- Their split is not the public split: 1,769 of 2,289 public test images are in their train lists; 5,194 of their image names are not in the public release. Their supervised-only mode crashes in the released code.
- **`ignore_index = 0` everywhere** (`main/train.py:30`, `main/DataLoader/pvs3.py:68` with `num_classes = 5`, `Model/Deeplabv3_plus/EntireModel.py:51,63`, `Utils/metrics.py:73-76`, `configs/config_deeplab_v3+.json:7`, `saved/ssl_el/config.json`). UCF-EL encodes background as 0. Our glue maps ignore label 128 to 0 (9,976,044 px).
- Result (eval295 grid = comparable to our runs): **standard defect mean IoU 0.050; PV-S3 metric 0.828** (native resolution 0.0503 / 0.791). **Background predicted on 0 pixels.** Crack precision 0.1176 / recall 0.946; corrosion predicted 3.33M px vs 102,570 GT (32x). Above Jha's published 67.0 on the public split.
- Assumption: their private data encodes background as 0 as in the public release. State this in the report.
- Also: our reimplementation (which trains background) was never faithful on this point, so its collapse is a finding about our version only.

### 7d. SA-UNet++ (Gangopadhyay)
- Old claim "removing SA improves defect mIoU 0.2028 vs 0.1792 / gating hurts" is **invalid** (predates GaussNoise fix; all 11 runs checked, all before the fix).
- Corrected rerun on BenchmarkEL (current code), test defect mIoU: SA-SL-20 gaint s0 0.338; cv02 3 seeds 0.341 +- 0.013; pooled 4 seeds 0.3399 +- 0.0104 (val+test 0.2926 +- 0.0201). SL-20 pooled 0.3435 +- 0.0329. **No effect** (p 0.78 test, 0.135 val+test). SA-SL-100 s0 (gaint) 0.320. SA-MT-20 was queued; result **[unverified]**.

---

## 8. Bugs and traps found (all silently corrupted results)

1. **GaussNoise 16x too strong:** albumentations 2.x renamed `var_limit` to `std_range` and silently ignores the old kwarg. Measured sigma ~68 instead of ~4 (0-255). Erases cracks. `var_limit=(10,50)` equals `std_range=(0.0124, 0.0277)`.
2. **fp16 autocast NaN** in DeepLabV3+/R50 within ~2 SGD steps (forward overflows; GradScaler cannot help). Use **bf16**.
3. Metrics code indexed a 5-class tensor with 24-class defect indices (CUDA device assert).
4. Runner-script self-deadlock: a `pgrep -f "run_x.sh"` guard matched its own parent (80 min idle GPU). Use `[r]un_x.sh` patterns; never create and launch a guard in one call.
5. smp needs H,W divisible by 16 (Fioresi crop 250 becomes 256).
6. **Strong augmentation applied without the paired mask** collapsed an earlier SSL sweep. Geometry must be shared; strong aug photometric only.
7. **Coupled augmentations** in the pilot code (H and V flips fired together; blur and noise together). Fixed; **pilot-era numbers are not comparable** to current-code runs.
8. Worker-seed bug found in the Phase 0 rebuild (confirmed old results doubly invalid).
9. Class weights computed over test labels (leak). Fioresi upstream validates on test. UCF has no val.
10. Full deterministic mode made training 5x slower; use the pilots' faster mode.
11. Resume: tested bit-exact for all 7 trainers; watchdog resumed under `kill -9`.
12. `scikit-image` 0.26: `remove_small_objects` semantics inverted.
13. Disk: `ENOSPC` breaks tools; keep `save_every == total steps`.

---

## 9. BenchmarkEL experiments in `el-fault-detection` (current code)

Common setup: U-Net++ 4.98M params, 512 input, 20,000 steps, lr 1e-3 (cosine), labelled batch 4, class-weighted CE, split seed 0, training seeds vary, final-step weights, bf16. Dropout2d 0.2. SSL arms run 4 labelled + 4 unlabelled per step; MT lambda 0 for 2,000 steps warmup, linear ramp to 1.5 over steps 2,000-3,999; EMA alpha 0.999 for MT (evaluated model = EMA teacher); ALHVR lambda max **0.1**, evaluated on network A. Speeds on gaint: SL 8.3 it/s, MT 3.5, ALHVR 0.72 (0.574 on cv02 alone; 0.25 when GPUs were contended).

### 9a. Pilot (older code, coupled augmentation): do not mix with current numbers
Test defect mIoU final: SL-100 34.4, SL-20 33.6, MT-20 35.2. ALHVR died silently at step 13,600 (machine shut down cleanly at 21:34 Oct 2; cause unknown, no admin logs); interim `best.pth` at 13,500: test 0.3295 vs SL-20 0.3306.

### 9b. Current-code results, both machines (test = 50 images; v+t = val+test 104 images)
| arm | n (gaint+cv02) | test | val+test |
|---|---|---|---|
| SL-20 | 8 (3+5) | 0.3435 +- 0.0329 (gaint s0 0.306, s1 0.368, s2 0.379) | 0.3137 +- 0.0195 |
| SL-100 | 4 (1+3) | 0.3383 +- 0.0060 | 0.2956 +- 0.0107 |
| SA-SL-20 | 4 (1+3) | 0.3399 +- 0.0104 | 0.2926 +- 0.0201 |
| MT-20 | 6 (3+3) | 0.3662 +- 0.0061 | 0.3415 +- 0.0059 |
| ALHVR-20 | 6 (2+4) | 0.3724 +- 0.0103 | 0.3472 +- 0.0108 |
| MT-20, lambda 0 (EMA control) | 3 (cv02) | 0.365 +- 0.018 | |
A later table in the other chat (more cv02 seeds) shows SL-20 0.339 +- 0.033, SL-100 0.340 +- 0.006, MT 0.365 +- 0.007, ALHVR 0.374 +- 0.013, MT lam0 0.365 +- 0.018. Use whichever `results_consolidated.md` is current.

Two-sample tests (pooled, no multiplicity correction; seeds not fully independent): ALHVR vs SL-20 test +0.0289 (Welch p 0.045, MW 0.108), v+t +0.0335 (p 0.002); MT vs SL-20 +0.0227 (p 0.095), v+t +0.0279 (p 0.004); ALHVR vs MT +0.0062 (p 0.24); SL-100 vs SL-20 -0.0052 (p 0.68), v+t -0.0181 (p 0.066); SA vs SL-20 -0.0036 (p 0.78), v+t -0.0211 (p 0.135). Both machines separately point the same way.

### 9c. What these mean (this chat first over-read them)
- Early claim "SSL beats supervised (p about 0.05, 0.004)" was premature. **MT with its unlabelled loss off (lambda 0) scores the same as MT**: unlabelled-loss effect on the student -0.0050 +- 0.0207 (test), -0.0006 +- 0.0162 (v+t), n=3. **EMA adds nothing**: teacher minus student +0.0000 +- 0.0019 inside MT (cosine LR ends at 0 so teacher averages a still student); at lambda 0 teacher minus student -0.0048 +- 0.0048.
- `arm_differences.md` (12 items): supervised and MT share the same labelled images, order, class weights, loss, geometric augmentation. Differences: **MT student sees 8 images through BatchNorm (4 labelled + 4 unlabelled) vs 4**; evaluated model is the EMA teacher; photometric RNG draws are shifted (SL and MT labelled images are bitwise equal in only ~70-87 of 400 samples); dropout masks for 8 vs 4 images. MT labelled view is **strong** in all six MT runs; a weak-view run was stopped and archived (`mt_20pct_s0_weakview_stopped`). The SL arms already use that same augmentation, so "SL with the MT strong view" is moot.
- Leading hypothesis (**not yet shown**): the SSL gain is BatchNorm batch composition. The **batch-8 SL runs also double labelled images per step**, so they do not isolate BatchNorm; MT lambda-0's student (4 labelled + 4 unlabelled through BN, no unlabelled loss, no EMA) is the cleaner BN control (~0.37 vs SL-20 ~0.344).
- **SL-100 equals SL-20** (more labels do not help), so at 20% there is no label gap for SSL to close.
- ALHVR vs MT: +0.006, inside noise, at about 4x the compute.

### 9d. Precision diagnostic (gaint checkpoints, 14 runs, provisional n = 3/3/2 per arm)
- Confusion of `alhvr_20pct_s1` on test: crack precision 0.35, recall 0.70, 70,626 true vs 143,570 predicted px; gridline P .33/R .74; material P .38/R .65; inactive P .67/R .55 (under-predicted); background P .98/R .91. Under PV-S3-style scoring crack IoU rises 0.30 to 0.585: the gap is background painted as crack (85% of false crack pixels are true background). **25-51% of predicted crack pixels lie >2 px from any true crack**, so it is not only a halo.
- Crack precision 0.22-0.35 at recall ~0.70 in every weighted run: class weights (background cheap to get wrong) make thin classes swell.
- **Crack-logit bias shift picked on val** (subtract ~1.25-1.75): SL-20 0.351 to 0.382 (+0.031), MT-20 0.368 to 0.387 (+0.019), ALHVR-20 0.369 to 0.381 (+0.013). After the shift arms are within 0.005 of each other. SL-100: no gain (-0.005). Val defect mIoU is much lower than test (0.17-0.27 vs 0.31-0.38), so shift sizes are noisy.

### 9e. ALHVR region diagnostics (pilot `regions.csv`, run died at 13.6k)
- Global gamma rose 0.64 to 0.87. Omega1 grew 50% to 64% of all pixels. **73-76% of crack pixels sit in Omega3, 6-7% in Omega1.** DTCT's chosen teacher predicts **background on 55% falling to 35%** of the crack pixels it supervises. Pseudo-label accuracy by region: Omega1 97%, Omega2 ~88%, Omega3 ~66%. Prototype loss stalls ~2.4 (cosine ceiling). lambda had only reached 0.06 at death. At step 13.5k val 0.230 vs SL 0.227.

### 9f. Prototype diagnostic (cv02, no training): prototypes are dead
- Cross-network prototypes label **4.6% of Omega3 crack pixels correctly** (two independently trained networks do not share a feature space). Own-network prototypes (43-49%) are worse than the classifier head (62%) on crack in every region. The relabel rule recovers ~6,600 crack pixels and wrecks **12.5M background pixels**. No EMA or temperature fix rescues this. **Report as a negative result with evidence.**

---

## 10. ALHVR: exactly what the code does (read from `github.com/ziziyao/ALHVR`, `train_ALHVR/code/train_ALHVR_acdc.py`)

- Two independently trained networks, **no EMA, no cross-pseudo-supervision term**. (An earlier explanation here said "CPS base, Omega1 gets cross pseudo-labels": **wrong**. Omega1 receives **no unlabelled loss**.)
- Per batch: `con = (conf_A + conf_B)/2` on the perturbed predictions; `gamma = mean of the lowest beta*N values of con`, beta = 0.8 ("proportion"), over all unlabelled pixels in the batch. Recomputed every batch.
- Regions use `max(softmax)` vs gamma only: **Omega1** both above gamma; **Omega2** exactly one; **Omega3** neither.
- **CG-CPCL (Omega2):** per-batch class **prototypes** from decoder features (each network's clean features grouped by its own argmax, i.e. predicted labels); cosine similarity of the unconfident network's perturbed features to the confident network's prototypes gives class scores; cross-entropy toward the confident label. A class absent from a batch gets an **all-zero prototype** (the code adds epsilon; it does **not** NaN, a correction to earlier statements).
- **DTCT (Omega3):** per pixel the more confident network's clean prediction is the teacher; sharpened with T = 0.1; other network's perturbed prediction trained to match with MSE plus an entropy penalty.
- Perturbation on features (dropout/noise), not image geometry.
- Mandatory EL fixes (implementation corrections, not contributions): Eq. 22 sharpening breaks at C = 24 (use softmax temperature); cosine ceiling: top softmax prob caps at e/(e+(C-1)/e) = 0.65 at C = 5 and **0.24 at C = 24**, so divide cosine scores by tau about 0.1; skip classes absent from a batch.
- Reported by Lei et al.: ACDC at 20% labels matches full supervision; AbdomenCT-1K +17 Dice at 5%. Medical, roughly balanced classes.
- Region taxonomy lock: **Omega1 dominates by raw pixel count; Omega3 dominates conditioned on defect pixels.** Keep both statements explicit in writeups.
- Memory notes the ALHVR port runs on top of two networks; the unlabelled pool there is a 383-image set; the "second experiment" is the ALHVR port itself, not plain CPS (user objected to putting CPS on the critical path). Plain CPS was never run.

---

## 11. Proposal history (what is alive, what is dead)

Poster version (3 parts):
- **(a) Backbone:** ~4M-param U-Net, pretrained light encoder (MobileNetV3/EfficientNet-B0 class), reduced decoder, **full-resolution skip** (two 3x3 convs, 16 ch, <3k params) for 2 px cracks. Report params, FLOPs at 512^2, latency. Baseline reference U-Net/VGG16 23.8M. Advisor earlier wanted ~2M.
- **(b) SSL (ALHVR-inspired):** M1 defect-aware sampling of unlabelled images; M2 per-class confidence thresholds gamma_k (EMA-smoothed, floor/ceiling); M3 EMA prototype memory (m about 0.99, per network, init from labelled data) + cosine temperature. Two branches in training, one at inference.
- **(c) Severity grading** (BenchmarkEL only; needs inactive, busbar, ribbon classes): instances (`src/postprocess/instances.py`, 57 tests, lost), crack skeleton via `skan` (length, medial-axis width, tortuosity), electrical isolation via topology mask (crack pixels as walls, flag components not touching a busbar), **Kontges modes**: A crack with no isolated area; B isolated area still glowing; C isolated area dark/inactive. Grade agreement (accuracy, confusion matrix, Cohen's kappa, GT masks vs predicted masks) as a metric.

Later modification ideas, with current status:
| idea | status |
|---|---|
| Mandatory fixes (tau, softmax sharpening, skip absent classes) | needed if CG-CPCL used; CG-CPCL itself now looks inert |
| **M2' class-prior-aligned routing** (per-class gamma_k + two-sided pseudo-label share control 0.5x-2x of labelled share) | **strongest evidenced**: UCF corrosion collapse fixed by a one-sided cap (0.067 to 0.631 IoU); crack is under-labelled on BenchmarkEL (route went the other way) |
| **M3 EMA prototypes / prototype-guided DTCT** | **DEAD** (section 9f) |
| **M4 asymmetric DTCT** (background label needs both networks to agree; defect needs only the more confident) | untested; targets the 35-55% crack-erasing channel; risk of false alarms |
| **M5 clDice topology loss** | **dropped**: bottleneck is over-prediction, not recall |
| M1 defect-aware sampling | deprioritised: BenchmarkEL pool is only 383 images (mostly defective); returns with a real unlabelled set |
| MoE (advisor) | **gated** on a specialist diagnostic (thin-defect specialist crack+contact, area specialist corrosion+interconnect, generalist, equal steps, 3 seeds, ~2 GPU hours). Standard load balancing balances pixel counts, i.e. background; routing would need to be supervised by defect group. Not worth building if specialists do not beat the generalist by more than seed noise |
| Plan attribution runs: ALHVR without CG-CPCL, without DTCT, lambda 0 | only lambda-0 ran (cv02, pending) |
| Pretrained backbone (SegFormer/DINOv2), pruning/INT8 for Jetson (Torch-Pruning, TensorRT; FP8 unavailable) | future work; re-run Subpath A on every compressed checkpoint |

**Current direction (set by the data):** fix the supervised recipe first (class-weight over-prediction, normalisation, batch composition), then test SSL only where a label gap exists (SL-10%, UCF-EL at 1-5%, or a genuine ~12k unlabelled set). Success criterion fixed in advance: full method beats step-matched SL by more than seed noise (Welch p < 0.05 at >=5 seeds, and rare-class IoU), at <=5% labels.

---

## 12. Poster (done; content partly outdated)

- Title: "Label-Efficient Segmentation of Rare Defects in Electroluminescence Images of Solar Cells". Author Yash Vijay Patil, supervisor Dr. Dinesh Singh, EE511, IIT Mandi.
- Projector format 128 x 72 cm (16:9), `poster.pdf`, `poster_1080.png`, `poster_4k.png` backup, `speaker_notes.md`. LaTeX (beamerposter-based template compiled offline with latexmk), numbers via `numbers.tex` macros with `% src:` comments. Sections: 1 Introduction, 2 Motivation, 3 Datasets (Table 1), 4 Method (Fig. 3 three-panel: backbone, SSL training, severity; solid = implemented, dashed = proposed; M1-M3 in accent), 5 Reproduction (Fig. 4 arms chart, Table 2, three findings), 6 Conclusion, 7 References (8 entries in footer). Fig. 1 pixel-share bars; Fig. 2 qualitative strip was pending.
- **Needs updating:** (i) Fig. 3 caption cites CPS: wrong, ALHVR has no CPS term; (ii) M3 prototype memory is dead; (iii) new step-matched number 0.491 +- 0.009 (3 seeds) in new code; (iv) Jha released-code finding; (v) Gangopadhyay row; (vi) crack-width claim wording; (vii) numbers moved to final-step new-pipeline values.
- Presenting line: "At equal compute, SSL (our reimplementation, one seed then three) showed no gain; Jha's published SL baseline (8.8) is undertrained; his code ignores background."
- Do **not** say: "SSL doesn't work", "Jha is wrong", "we beat Fioresi", "attention hurts", "we reproduced Jha".

---

## 13. Corrections log (errors made along the way: do not repeat)

By Claude (this chat):
1. "Fioresi shortfall of 7.1 is real": was 4-class vs 5-class mixing.
2. Said 0.54 vs 0.52 threshold was a slip: paper says 0.54, code 0.52 (both right).
3. "Width explains Pratt 13-16 vs Jha 67-88": overclaim (Jha's own CSB-S1 results contradict it).
4. "All four baselines reproduce": SL 20% compared across metrics; Jha gap partly budget not only metric.
5. "SL best over budgets": withdrawn (selection on test).
6. Hypothesis "threshold explains Jha's operating point": falsified (PV-S3 eval is plain argmax).
7. "SSL gain disappears" stated before seeds; "reverses" was too strong at one seed.
8. Methodology said ALHVR is built on CPS and Omega1 gets pseudo-labels: wrong.
9. "Prototype per-batch divides by zero / NaN": the code produces **zero vectors**, no NaN.
10. "EMA prototypes in Omega3 could be the most important change", and "add clDice (M5)": both refuted by measurement.
11. "SSL beats supervised p about 0.05 / 0.004": premature; unlabelled loss has no measured effect.
12. "PV-S3 collapse caused by strong-view supervised loss": only -0.045; real cause is rare-class pseudo-label over-prediction.
13. Told CC to switch MT labelled view to weak: wrong rule; the rule is "labelled loss gets the augmentation of the matching SL arm".
14. "ALHVR +0.064 over SL-20": was measured against the worst SL seed.
15. "The 12k unlabelled set cannot be reconstructed": it can be re-downloaded (method documented).

By CC (caught in review): "we beat Pratt 2x" (empty-image rule); "equal budget" off by 8x in steps; "UCF val stays clean" (FSL trains on all 9,562, SSL pool contains val); "rule A Set C is the paper's best figure"; "every run far below Jha's 67-71" compared unlike arms; "8.15 gap genuinely unexplained" (four unmatched differences: labelled count 2,614 vs 1,912, lr, crop 224 vs 256, PS-MT vs our mean teacher, plus possible class weights).

Meta-lesson: every "the method differs" explanation turned out to be a comparison-convention or control mistake. Check conventions, steps, and controls before believing a method difference.

---

## 14. Status snapshot (00:04 IST Tue Oct 6; re-check)

| machine | job | state then | ETA then |
|---|---|---|---|
| gaint | batch-8 night queue: SL-20 b8 x3, SL-100 b8 x3, SL-20 b8 no class weights (seed 0), SL-10 b8 x3; two at a time, ~2.0 it/s each | first pair at ~9,400/20,000 | SL-20/100 ~07:00; all ~12:45 |
| gaint | step 3: add new arms to consolidated table + tests (vs SL-20, MT-20, ALHVR) | waits for queue | |
| cv02 | ALHVR lambda-0, training seeds 1-3 (unlabelled loss weight 0, forward pass unchanged; log shows all unlabelled terms exactly 0) | ~900/20,000, 0.25 it/s | ~21:00 Oct 6 |
| cv02 | SL-20 b8 (seeds 0-2; used 0-2 instead of 3-5, pairs with batch-4 runs of the same seed) then SL-100 b8 x3 | SL-20 s0/s1 ~5,500/20,000 | morning |
Reports written on gaint: `arm_differences.md`, `precision_diagnostic.md` (+ `diagnostics/`), `stats_tests.md`, `results_consolidated.{md,csv,json}`, `numbers.tex`, `figures/`, `day1.md`. On cv02: `cv02.md`, `prototype_diagnostic`, PV-S3 results block.

### How to read the batch-8 results
| result | meaning | next |
|---|---|---|
| SL-20 b8 reaches about 0.365 | gains were BatchNorm batch size / labelled throughput | batch 8 becomes baseline; ALHVR must beat it |
| SL-100 b8 still equals SL-20 b8 | no label gap at 20% | move SSL tests to 10%, UCF-EL, or real unlabelled data |
| SL-20 b8 without class weights changes crack precision | weights drive over-prediction | fix loss first, benefits every arm |
| ALHVR lambda-0 equals ALHVR | ALHVR's unlabelled terms do nothing here | DTCT/CG-CPCL fixes only if a gap exists |
| SL-10 b8 shows a gap vs MT/ALHVR | SSL has a regime | M2'/M4 test there |
Because batch 8 also doubles labelled images per step, read it as "BatchNorm plus 2x labelled throughput". Cleaner BN test: MT lambda-0 student vs SL.

---

## 15. Report plan (MTP progress report, LaTeX)

Outline (target ~25-35 pages, institute template unknown):
1. Introduction (EL inspection, label cost, imbalance, objectives, contributions so far)
2. Background (EL defect segmentation: Fioresi, Pratt, Jha; SSL: MT, CPS, UniMatch, ALHVR; imbalance-aware thresholds: FlexMatch, FreeMatch, MetaSSL; U-Net, U-Net++, SA-UNet++)
3. Data and evaluation (both datasets, pixel shares, crack width 2 vs 15 px, formal definitions of the three metrics, protocol: equal steps, final-step reporting, seeds, val carved from train)
4. Experiment 1: SA-UNet++ with MT (setup, the GaussNoise and SSL bugs, corrected rerun: no effect)
5. Experiment 2: reproduction (four papers, convention findings, probes, step-matched result, Jha's released code finding)
6. Experiment 3: ALHVR as-is (code-vs-paper differences, baselines, region diagnostics, MT lambda-0 and EMA controls, precision diagnostic, prototype negative result)
7. Proposed method (backbone, supervised recipe fix, M2'/M4 candidates, mandatory fixes, severity grading)
8. Plan (label-ratio sweep, seeds, genuine unlabelled set, MoE diagnostic, timeline)
9. Conclusion
- **Integrity note (mandatory):** reproduction code and logs were lost in the account reset; numbers come from run records and the poster; artifacts are being rebuilt. New-pipeline reruns exist for UCF-EL arms, Pratt, Jha's code (cv02), and all BenchmarkEL arms.
- Open by design: the old "SSL 46.4" record (not reproduced), batch-8/BN question until results land, MoE, M1-M5 (proposed, not implemented).
- Claims allowed: "at equal compute, our PV-S3 reimplementation showed no gain on UCF-EL"; "published SSL gains depend on baseline training and metric"; "on BenchmarkEL, unlabelled-loss effects are not detectable at 95 labels (MT lambda-0 control)"; "released PV-S3 code never models background".

---

## 16. Standing rules for any new session / CC prompts

- **Match optimizer steps** across arms; log total steps in `metrics.json`.
- bf16 autocast; GaussNoise via `std_range` only; paired geometric aug; strong aug photometric only.
- Report **final-step** numbers; best-val only as a secondary and flagged noisy. Never select checkpoints on test.
- Report standard metric as headline; PV-S3 and Pratt metrics only for comparison with those papers, always labelled.
- Don't mix pilot-era (coupled augmentation) numbers with current-code numbers; keep separate tables.
- Never compare arms across machines. Within a machine only. cv02 calibration: its SL-20 s0 should land inside gaint's SL-20 range (0.306-0.379).
- Seeds: >=3 per arm minimum, 5-8 for effects <0.05; claim a difference only beyond seed spread. Splits fixed (split seed 0); train seed varies.
- Run one change per arm relative to an existing arm.
- Rebuild labelled/unlabelled splits from train minus val before any method work (UCF).
- Commit and push after each step; commit splits and manifests, never checkpoints; `git add -f` was needed for `data/splits` (now `!data/splits/` in `.gitignore`).
- Memory guard before every GPU launch (free memory + 2 GiB), watchdog resume, no silent fallbacks (missing split file = hard error), keep latest+best checkpoints only, check `df`.
- Questions are tests, not confirmations: report findings that contradict the framing; follow the code when it contradicts the prompt.
- Style: terse, concise, no em-dashes, no buzzwords; poster style is stated measurements, not accusations.

## 17. Open items

1. Pull gaint batch-8 results, cv02 lambda-0 and batch-8 results; update `results_consolidated`, `stats_tests`, tables and `numbers.tex`.
2. Decide direction from the decision table in section 14.
3. Re-download the genuine unlabelled set (filter labelled leakage by cell ID) if SSL is pursued on BenchmarkEL.
4. Rebuild UCF splits from train minus val for method work.
5. Postprocessing (Stages 1-3 and Kontges grading) must be rebuilt: lost with the reset.
6. Run `SA-MT-20` and verify its result; rerun nothing old.
7. Poster fixes listed in section 12; optional per-class SSL vs SL on UCF-EL.
8. Optional CPU task already specified: document the PV-S3 `ignore_index` file:lines and the background-encoding assumption in `cv02.md`.
9. MoE specialist diagnostic (optional, only if time).
10. Get the institute's MTP report template and page limit.
11. Fix memory discrepancies below.

## 18. Memory notes that are stale or wrong (fix on next memory update)

- Memory calls the user "Honey" in project files; profile name is Om.
- "~2M param lightweight model" (memory) vs "~4M" (poster).
- "582 labelled + ~12,000 unlabelled" is the full dataset; current experiments use 95 labelled + 383 hidden-mask unlabelled.
- "Missing baseline: plain CPS must run first" is superseded (ALHVR itself is the second experiment; ALHVR has no CPS term).
- "EMA prototype issue is NaN in eq. 15": actual behaviour is zero prototype vectors.
- "SA gating hurts": retired. "Stage 1 postprocess complete (57 tests)": code lost.
- "Task `herald-ada8eb38` (Stage 2)": status unknown, probably lost.
- "Active repo `sa-unetpp-ssl-el`": now `el-fault-detection`.
</pasted_content id="1ebd">

 unfortunately most of the codes and results we lost coz of user reset, but you mmight get much help from this, first we tried SA SSL on unet++ and then we reproduced all the paers and figured out the results and deviations from papers, now tell me if we are wrong at something now


=== user message 2026-10-11T07:02:25.312Z (line 5404) ===


<pasted_content id="1ebd">
I'll answer only what I worked on. For the rest I say so, and I'd rather leave a gap than guess.

**1. "SA SSL raised IoU".** I never reported that. I can't tell which of (a), (b), (c) was meant, but (b) looks like a misreading of a table I relayed on Oct 4:
- That table listed **SA SL-20% seed 0** only: final-step test 0.338, best-val-step test 0.301. Both numbers belong to one arm; they are not sa_mt vs sa_sl.
- (a) is the old SA ablation (0.2028 vs 0.1792 defect mIoU, SSL-20% 0.2580). It predates the GaussNoise fix and is invalid.
- Later in the same table, SA-SL-20% pooled over 4 seeds showed no effect (test 0.3399 vs SL-20 0.3435).
- I never saw an sa_mt result and flagged it unverified. Check `results_consolidated` on gaint for the real sa_mt number.
- I know nothing about (c), the TF-era code.

**2. SemiCE source.** I don't know where your original port got it. I wasn't in that session.
- Jha et al.'s PV-S3 describes SemiCE as cross-entropy on pseudo-labels with two thresholds (t_pos, t_neg). Our UCF reimplementation took t_pos 0.6 and t_neg 0 from that description.
- My notes also link SemiCE with Gangopadhyay's SA-UNet++ (Mean Teacher + SemiCE).
- I have no record of an advisor suggesting it.
- To check the port against the original, read Jha's released code, which is on cv02 at `/tmp/noob_el/pvs3/PV-S3`. The unsupervised term in `main/Model/Deeplabv3_plus/EntireModel.py` (around line 89) uses `reduction="none"` with an `inverse_prob` weight. I did not verify that this is exactly SemiCE.
- That released code is no use as a reference for the idea itself, since it never models background (`ignore_index = 0`).
- I don't know what "P2" is.
- On UCF, our reimplementation failed through rare-class pseudo-labels: at t_pos 0.6, 99.4% of pixels pass, and corrosion is over-predicted 23x. A per-class share cap fixed corrosion (IoU 0.067 to 0.631). That points at the thresholding, not necessarily the SemiCE idea.

**3. 6 to 8 Oct gap.** I have no record of the 7 Oct UCF Mean Teacher runs at 1% and 5% labels, and I know of no decisions made from them. My last MTP session ended at 00:04 IST on Oct 6, and I can't say whether other MTP sessions existed in that window.
- "All below supervised" is consistent with the failure we diagnosed on UCF.
- I can't say whether those runs used any class-aware control.

**4. Phase 0 decisions.** I don't know of those decisions or the P-numbering.
- What I know of the goals: a dual mandate. WattCycle wants a deployable detect, grade, estimate-loss pipeline; the advisor wants a paper. The stated resolution was to report full-accuracy results as the headline, with a lightweight variant as a secondary point.
- I have no record of "WattCycle pilot first, paper second".
- I know a three-way architecture comparison was dispatched earlier (SA-UNet++, UNet++ R34, DeepLabV3+ R50), and I never saw its results.
- The audit finding is relevant: the old code trained from scratch with no pretrained encoder, and published work reports much higher crack IoU with pretrained encoders. I don't know if the current models are pretrained.
- Data from this chat supports "supervised and architecture before SSL changes":
  - SL-100 equals SL-20.
  - MT with its unlabelled loss off equals MT.
  - Crack over-prediction is the measured bottleneck.

  Whether the original order still holds is your decision.

**5. Unlabelled data.** I can't answer the cell-type or low-contrast questions.
- What I know: the share held about 12k images, and our selection method (walk the folders, cap 2,500 per leaf, round-robin) gave 11,993 images after failures. I never saw 11,938, so your count is presumably post-filtering.
- The share leaks labelled images by filename, so it needs filtering by cell ID.
- Because of the per-leaf cap and round-robin, a pool with only CSIR/ARTS suggests a listing or capping effect, or that the share lacks other cell types. I can't tell which.
- The cheap test is to re-walk the share listing with no downloads and count images per leaf folder. `_inventory.json` was lost, so it has to be regenerated.

**6. Advisor directives.** Not sure; these are the facts I have.
- My notes say the advisor wanted a lightweight model of about 2M params. The ~4M figure on the poster came from your own thinking, and I don't know why it changed. I have no deadline for either.
- On MoE: my notes list it as an advisor directive. In this chat you called it a suggestion you weren't sure about. I don't know if it's required.
- My position: gate it on a specialist-vs-generalist diagnostic (about 2 GPU hours) before building anything.
- The report due date was never given to me either.
</pasted_content id="1ebd">

 only these i remember, now its time to revsiit our approach, think of whats going on, how shall a 11years experienced scientist should direct frther, and move smartly, not just another worker, but a scientist, we did some really ogod things, some mistakes, but now lets see it from new perspective, lets revisit the problem itself, like very broad vision, assume youve got this ps right now, and someone shared you all this context we know now, how would you classify the problem, what would be your goal, appraoch, and see we will get lead on this project, coz one part of presentation is the proposal, not driven by intuitions but the existing knowledge on the project, dataset, basically everything we now aware of
