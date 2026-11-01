# SHV1: frozen synthetic half-cut validation set (domain, 31 Oct 2026)

- **What:** all 54 val cells cut by the idea-5 simulator, both halves of the centre cell: 108 images, 512 x 512, grey (L).
- **Generator:** dom_synth_val.py (copy in this folder; md5 6e702c36 = team_2026-10-31_next/ideas/scripts/dom_synth_val.py), seed 20261031. Run 31 Oct 17:34 IST on gaint CPU (CUDA hidden, nice 19, 1 thread); log ../logs/shv1.log rc=0.
- **Inputs:**
  - el_f3/data/splits/val.txt (md5 9dcccf00);
  - images el_f3/data/labeled/images;
  - masks el_f3/data/labeled/masks_escdd (house 24-class GT);
  - intensity pairs ../out/ap_pool.tsv (md5 a78a2d2a; 1,008 pool half-cells, CSIR_00300 excluded).
- **Geometry** (deterministic, no jitter): centre cell split at its midline; its own gap band inserted (image + mask rows); sx = 342/256, sy = 163/(128 + g); 512 crop centred on the half, clamped inside the source. Gap found in 54/54 cells.
- **Intensity:** content px (F6 white rule, mask != 7) are linearly mapped to one (mean, sd) pair per image, drawn from the pool pairs with the frozen seed (index in shv1_context.tsv, column pool_idx).
- **Labels:**
  - Masks are transformed with the image (nearest).
  - The inserted gap gets the source spacing class (sp multi 1 / sp mono 2). That is the same convention as calib's _rf build (29 -> 1, 24 -> 2) and E1 scoring (release masks: half-cut multi gap = 1, class 24 -> 2).
  - ignore/ is all zero (layout as calib data/rf).
- **Content:** 40 images with crack >= 20 px (from 21 of 23 val crack cells), 88,272 crack px; 11 images with inactive (6 of 6 val inactive cells), 26,529 px; 68 crack-free images.
- **Appearance vs the 1,008 pool half-cells** (medians):

  | | SHV1 | pool |
  |---|---|---|
  | mean | 153 | 154 |
  | sd | 25.6 | 23.7 |
  | mean abs Laplacian | 3.15 | 2.84 |
  | x pitch (px) | 343 | 342 |
  | row pitch (px) | 158 | 163 |
  | gap width (px) | 11 | 10 |
  | gap depth | 0.31 | 0.33 |

- **NOT matched:**
  - busbar count (source 2-5 vs 9);
  - multi texture (source grain vs CSIR dislocation clusters);
  - histogram shape (0.69 vs 0.79; a linear map keeps val's shape);
  - scuff (none);
  - BMRK sources (8 val cells) are single cells in a white frame, so their synthetic halves are single half-cells in white.
- **USE:** a non-E1 selection / readout set. Examples: a half-cut-specific crack bias, or the idea-5 mechanism readout (oracle-b shift V0 -> SHV1).
  - NEVER score E1 or test with it.
  - It is derived from val, so anything chosen on it is chosen on val.
- **Files:**
  - images/, masks/, ignore/ (108 each);
  - stems_eval.txt (108 names, <val_stem>__h0|h1);
  - shv1_context.tsv;
  - README.md;
  - dom_synth_val.py;
  - MANIFEST.md5 (md5 of every file here except itself).
