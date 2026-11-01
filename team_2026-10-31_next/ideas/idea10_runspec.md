# Idea 10 run spec: S10-inactive (found, 31 Oct 2026)

Design: `idea10_ai_labelling.md` v2.1 (§6), judge PASS-to-protocol (low priority). The user OK'd the separate sam2 venv and the SAM2.1 Hiera-T weights (team-lead, log.md).

## 1. Status of the environment (E, done 31 Oct; details in log.md)
- **venv:** `/home/noob/work/venv_sam2`, created with `/usr/bin/python3.12 -m venv` (pip 24.0 bundled; nothing downloaded for pip itself).
  - `torch` 2.14.1+cu130, torchvision, numpy, pillow, tqdm and PyYAML are **reused read-only** from `el-fault-detection/.venv` through the path file `zz_reuse_el_venv_readonly.pth`. No torch was downloaded. The training venv is not modified: torch `__init__.py` md5 4feada30 before and after; 0 of the new packages appear in its `pip list`.
- **pip install** (into venv_sam2 only):
  - `pip install --no-deps --no-build-isolation --require-hashes -r found_requirements.txt`;
  - packages: hydra-core 1.3.2, omegaconf 2.3.0, antlr4-python3-runtime 4.9.3, iopath 0.1.10, portalocker 2.10.1, all sha256-pinned (`found_scripts/venv_sam2_requirements.txt` md5 15dd6898). About 0.4 MB downloaded.
- **sam2 code:** Meta's `facebookresearch/sam2` at commit `2b90b9f5ceec907a1c18123530e92e794ad901a4` (Apache-2.0).
  - Source: one codeload tarball (55,645,345 B, sha256 1f2fbfad…, deleted after extraction).
  - Kept: `sam2/` + LICENSE files + setup.py + pyproject.toml (43 entries, 393 KB) in `/home/noob/work/venv_sam2_src/sam2_2b90b9f`.
  - Every file was verified against the GitHub tree's git blob sha1 (39 files, plus 4 config symlinks verified on their link blobs).
  - Imported via the path file `found_sam2_src.pth`, with no build. The optional CUDA post-processing extension `_C` is not built; SAM2 skips it.
  - The PyPI package named "sam2" is a third-party upload, so it is **not** used.
- **Weights:** `/home/noob/work/weights/sam2.1_hiera_tiny.pt`, 156,008,466 B.
  - From `facebook/sam2.1-hiera-tiny` @ de431c40; sha256 7402e0d8… matches the HF LFS oid; **md5 6aa6761c9da74fbaa74b4c790a0a2007**.
- **Smoke** (`found_scripts/sam2_smoke.py` md5 08dcf014; CPU, CUDA hidden, 8 threads):
  - build 0.4 s, 39.0M params;
  - `set_image` 1.4 s per 512-px cell; predict 0.07 s;
  - masks (3, 512, 512). "SMOKE OK".

## 2. The run: **CPU only, no GPU slot requested**
SAM2.1 Hiera-T takes 1.4 s per cell on CPU, so S10's ~293 cells need ~7 min of SAM time. The GPU queue is not needed. If team-lead still wants the GPU, runner starts the same command with CUDA visible behind its gate and logger; peak memory **unknown**, smoke first.
- **Code:** `ideas/scripts/s10_inactive.py` (not written yet). Two stages:
  1. **Model stage** (`el-fault-detection/.venv` python, CUDA hidden): the A50 5-seed ensemble = `/home/noob/work/cv02_noob_el/el_p13/experiments/p16_A_50pct_s0..4` (step 20,000 asserted; loaded with el_f3 code read-only, as B1's audit did).
     - Cells: the 239 train cells outside `el_f3/data/splits/seed0/labeled_50pct.txt` (B1's OOF set, 3 D7 twins included) + the 54 val cells.
     - Writes per cell the argmax-inactive mask, and prompts per component ≥ 100 px (bounding box + its deepest interior point by EDT).
  2. **SAM stage** (`/home/noob/work/venv_sam2/bin/python`, CUDA hidden): SAM2.1 Hiera-T, one box + point prompt per component, `multimask_output=True`, the mask with the highest predicted IoU, union per cell.
  - Scoring (CPU): per-cell inactive IoU and boundary F1 at 2 px vs `labeled/masks_escdd` (Pratt 20221008 inactive labels).
    - Variants: (a) model, (b) SAM, (c) intersection.
    - Paired cell bootstrap over the 22 OOF inactive cells (2,000 resamples).
    - The rule is in `idea10_ai_labelling.md` §6: two comparisons, disclosed; the 6 val cells are report-only.
- **Commands (template):**
  ```
  CUDA_VISIBLE_DEVICES="" nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -I s10_inactive.py model --code /home/noob/work/el_f3 --runs <5 A50 dirs> --labeled /home/noob/work/el_f3/data/splits/seed0/labeled_50pct.txt --out /home/noob/work/found/s10/
  CUDA_VISIBLE_DEVICES="" nice -n 19 /home/noob/work/venv_sam2/bin/python -I s10_inactive.py sam --ckpt /home/noob/work/weights/sam2.1_hiera_tiny.pt --cfg configs/sam2.1/sam2.1_hiera_t.yaml --out /home/noob/work/found/s10/
  CUDA_VISIBLE_DEVICES="" nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -I s10_inactive.py score --out /home/noob/work/found/s10/
  ```
- **Writes:** per-cell masks (npz, ~20 MB) and a JSON summary. **No model checkpoints, no training.**
- **Time:** S: model stage ~5 min (B1: 293 cells × 5 members in ~5 min on CPU); SAM stage ~7-10 min; scoring ~2 min.
- **Data read:**
  - el_f3 `data/labeled/images`, `labeled/masks_escdd` (239 OOF train + 54 val), `splits/seed0/labeled_50pct.txt`, `splits/val.txt`.
  - No test, no E1, no `_rf` (SAM-made labels; judge).
- **Weights (md5):**
  - `sam2.1_hiera_tiny.pt` 6aa6761c9da74fbaa74b4c790a0a2007;
  - A50 checkpoints: `latest.pth` step 20,000; md5s recorded by the script at run time.
- **Approval:** CPU-only descriptive work, so per team-lead's T9 precedent, judge approves the pre-registration (the §6 rule + this spec), not coach. **Runner is not involved unless the GPU route is chosen.**

## 3. Open
1. `s10_inactive.py` (≈ 0.5 day) and its pre-registration note. Judge's OK before any number.
2. It runs after T9's dumps finish, or beside them at ≤ 8 threads (gaint has 48 cores).
