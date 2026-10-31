# D (inference only): pre-registration, written before any D number exists

runner, 30 Oct 2026 12:33 IST. Coach's D (coach_strategy.md §4) with coach's 4 changes (30 Oct). **Val + E1 only; no test cell is read, no test opening.** Descriptive; any follow-up needs its own protocol with a test opening.

## Target and read (stated now)
- **Target:** E1 crack recall on the **29 scuff + half-cut cells** (`scripts/e1_context.tsv`: scuff=1, halfcut=1), 5-member mean-softmax ensemble at FINAL's crack bias **+0.75**, variant − FINAL (same members, same bias).
- **Must not hurt:** E1 crack recall on the **29 half-cut cells without scuff** (scuff=0, halfcut=1; FINAL recall about 0.55).
- **Kill (27 Oct item-4 rule):** no variant gains **≥ +0.05** on the target recall at an **E1 crack-precision cost < 0.05** → killed.
- **Sanity:** val crack relF1@2 drop ≤ 0.01.
- **Reported with every variant (bias +0.75 and 0):** E1 crack recall per group (target / must-not-hurt / 48 full cells), E1 crack precision, crack IoU, relF1@2, crack px on the 74 crack-free E1 cells, inactive IoU (E1 and val); val crack IoU, relF1@2, inactive IoU.

## Variants
- **FINAL (reference):** p6_L3_100pct_s0-2 (cv02 824fab0) + p16_A_100pct_s3-4 (cv02 bac5264), final weights (step 20,000 asserted), mean softmax, crack bias as Track M m9 (`scripts/m9_final.py`).
- **D(c) routed BN-HC (primary D(c)):** each member copied, BN running statistics re-estimated (reset, cumulative average) by one train-mode, no-grad pass over the **986 pool half-cells** (mim_pool_v11 pool part, CSIR 297-299, 301, 333-335; R1-R4 filtered), batch 8, no augmentation. The BN-HC members score **only the 58 E1 half-cut cells** (halfcut=1); the original members score every other cell (val has no half-cells).
- **D(c) global (labelled as such):** the BN-HC members on every cell.
- **D(a):** R34-5 (= FINAL), **RN50-5** alone (Track M R3 Part B `m_r3_rn50_s1-5`: house L3 recipe, ImageNet ResNet-50 U-Net++, cv02, el_mt commit; step 20,000 asserted; recipe and commit stated in the results), **R34-5 + RN50-5** (10-model mean softmax).
- **Size-matched control (added after opening 1, not before):** R34-10 = FINAL 5 + SUP100-g 5 (gaint f3), val + E1 only.

## Checks first
- The scorer reproduces FINAL's val numbers (Track M `final/final_tables.txt` / `final_val_decisions.json`) before any variant is scored; masks and ext cells as m0_audit (labeled/masks_escdd; ext117 eval list, 106 cells).
