# MTP setup: summary (2026-10-02)

The environment is set up. CUDA works on the RTX PRO 4500 Blackwell and the 20-iteration smoke test ran clean. I stopped at step 5: there's no record of how the ~12k unlabelled images were picked. No training, no commits, and no repo code changes.

## What passed
- **Repo and data:** the code uses BenchmarkEL `dataset_20211104`. The official folders give exactly 478 / 54 / 50 images and the class list has 24 classes.
- **Data layout:** the 582 images are symlinked into `data/labeled/images`. `data/splits/{train,val,test}.txt` come from the official split folders.
- **Torch:** the stable cu130 wheel worked, no nightly needed (torch 2.14.1). `get_arch_list()` includes `sm_120`. A conv2d forward+backward on CUDA matched the CPU result to within 1e-6.
- **BenchmarkEL checks:** every image has a mask, all masks are uint8 with values 0–23 only, and no cell ID is in more than one split (with or without the augmented copies).
- **UCF checks:** every image has a mask and no cell is in both train and test.
- **Smoke test:** all 20 losses were finite (4.29 → 2.12). Peak GPU memory was 11.9 GiB allocated / 14.3 GiB reserved, alongside the other user's ~6 GiB.
- **Augmentation:** masks stay aligned in every panel of `reports/aug_check.png`.

## What failed or was not done
- **Unlabelled set (step 5):** there's no manifest, `unlabeled.txt` or `_inventory.json` anywhere. `download_unlabeled.py` only describes the method, and an exact rebuild would need the cached Dropbox listing, the original arguments and a Dropbox API token. None of those are here, so nothing was downloaded.
- **UCF val split → 957:** this can't be checked. The clone has only train and test, the 2,289-image test set doubles as val, and there's no seed or val list anywhere. 957 is 10% of 9,562, but the code that made it isn't on this box.
- **50/20/10% splits:** they were never committed (`data/splits/` is gitignored), and `prepare_splits.py` reshuffles everything into 466/58/58, so they can't be rebuilt. `class_pixel_counts.csv` covers the full 478-image train set only.
- **GaussNoise (step 4):** neither use of it in `src/data/augmentations.py` (lines 94 and 183) uses `std_range`. Albumentations 2.0.8 silently drops `var_limit`, so both fall back to the default, which is about 10–15× stronger noise than intended, applied to 30% of samples. You can see it in the grid. I didn't fix it.

## Things you should know
- **Masks:** the shipped masks are class indices, but the loader expects colour masks. Symlinked as they are, every class except background becomes "ignore" (24.6% of pixels). So `data/labeled/masks` holds 582 colour masks I generated (3.6 MB) — the conversion the README describes but `download_data.sh` doesn't do. They're new derived files, not copies, and each one decodes back to the original exactly. The originals are symlinked in `data/labeled/masks_coded`.
- **Test leakage in the loss weights:** the class frequencies hard-coded in `class_info.py` match all 582 images (train+val+test) to 5e-7. Recomputed on train only, the weight ratio is 615:1, not 313:1.
- **Silent fallback to all images:** if a split file is missing, `train.py` trains on every image in the folder, test set included. Running a 50/20/10% config right now would do exactly that.
- **UCF masks:** 573 of them contain the value 128, which is UCF's own "ignore" label (3.9% of pixels).
- **Rotation:** it can crop up to 81% of a crack out of frame, and the reflect border adds mirrored copies at the corners.
- **Shared modules:** splits share whole modules (train and test have 22 in common), though no cell repeats. This only matters if you want module-disjoint evaluation.

## Decisions for you
1. Unlabelled data: find the old `_inventory.json` or file list, or approve a new subset (I'd need a Dropbox token).
2. 50/20/10% splits: define a new seeded subset of the 478 train images, or recover the old lists.
3. Noise level: switch to `std_range≈(0.0124, 0.0277)` (what was intended), or keep the current strength the past results may have been trained with.
4. Loss weights: recompute from the 478 train images only, or keep the current values to match the reported numbers.
5. UCF val split: point me to the code and seed that produced 957, or approve a new seeded 10% hold-out from train.
6. UCF masks: whether to keep 128 as ignore or remap it before use.
7. Colour masks: keep the generated ones, or change the loader to read the original masks (a small code change).

## Files
- `sa-unetpp-ssl-el/reports/`: `setup_check.md` (full details), `class_pixel_counts.csv`, `aug_check.png`, `summary.md` (this file)
- Helper scripts: `/home/noob/work/setup_tools/` (outside the repo)
