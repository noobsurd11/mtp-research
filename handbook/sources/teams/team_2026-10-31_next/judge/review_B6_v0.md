# judge review: protocol_B6 v0 (md5 d90323de), 1 Nov 2026 ~18:50 IST

judge (respawned 18:40). Adversarial review before lock. Tags E / S. Verdict: **NOT READY to lock.** One blocking leak (B6-1), one blocking engineering gap (B6-4), one blocking honesty item (B6-2, power). The rest are fixes to the rule text.

Code: `judge/b6_audit.py` (8fa1106d), `judge/b6_groups.py` (d35b9359). Data: el_f3 `labeled/masks_escdd` + `labeled/images` (pulled read-only), train / val lists md5 842f27c4 / 9dcccf00 (= splits_benchmark). Outputs `judge/out/b6_cells.tsv` a0ed4a13, `b6_neardup.tsv` 2a1dee00, `b6_groups.tsv` 5ff33e20, `b6_twin_montage.png` 42993953. No test or E1 mask, image or prediction read for B6-1. B6-2 re-analyses PF2's already-opened per-cell files (`results/pf2/raw/m0`); this is not a new read.

## B6-1 BLOCKING: the module key leaks the same physical cell across folds
- **The flaw:** "source + image id" is not a module for CFVS. CFVS images are a time series of the same modules (`team_2026-10-21/data/decision.md` D6). The same physical cell therefore appears under several image ids, and v0's key would place those copies in different folds.
- **E: twins inside train + val.** Each was screened as same source, same (r, c), different image id, then checked on mask IoU and visually (montage):

  | Chain | Split | Inactive mask IoU between copies |
  |---|---|---|
  | `CFVS_00013/15/16_r7_c4` (+ 00009, 00010, 00012 earlier stages) | 10 train + 2 val | 0.82-0.97 |
  | `CFVS_00037_r8_c4` ~ `CFVS_00046_r8_c4` (+ 00032) | train ~ val | 0.979 |
  | `CFVS_00020/22/31_r4_c4` (+ 00017) | train (00017 val) | 0.46-0.70 |
  | `CFVS_00139_r4_c3` ~ `CFVS_00143_r4_c3` | train ~ val | 0.22 (crack IoU 0.30; visually the same cell) |
  | `CFVS_00102`/`00103` | train | – |
  | `CFVS_00114`/`00130` (r8_c2 neighbourhood) | – | 0.33 (probable) |
  | `ARTS_00005_r4_c5` ~ `ARTS_00097_r4_c5` | train ~ val | crack IoU 0.37 |

  - The 512 px crops include the neighbouring cells, with their labels. So the whole image must move together, not only the matching cell.
- **E: size of the leak.** Linking those image ids (connected components) gives 334 physical groups instead of v0's 354 keys.
  - **47.6% of all train + val inactive px** (135,595 of 285,020) and 17 of the 48 inactive cells sit in 8 multi-image groups.
  - With 5 folds, each cross-image pair lands in different folds about 80% of the time. About 38% of inactive px would then be "held out" while their physical twin is in training.
- **E: the leak is not neutral (it favours PF).** These numbers re-analyse opened PF2 s5-9 per-cell files; they are descriptive, with small n.

  | Cells | n | SUP100-g | SUP100-PF | Δ |
  |---|---|---|---|---|
  | val, all | 54 | 0.423 | 0.509 | **+0.086** |
  | val, without the 7 val cells that have a train twin | 47 | 0.501 | 0.472 | **−0.029** |
  | test, all | 50 | | | +0.0173 |
  | test, without the 7 D6 twins | 43 | | | +0.0145 |

  - **S:** the whole in-distribution val gain sits on the 2 val inactive cells whose twin is in train (`CFVS_00046_r8_c4`, `CFVS_00143_r4_c3`).
  - On test, 2 of the 3 twin inactive cells go up under PF (`CFVS_00027_r4_c4` 0.654 → 0.817).
  - So v0's key risks a **false PASS driven by twin recall**.
- **Fix (required):**
  - Folds by physical group. Edges: same image id; OR same source + same (r, c) + different image id with inactive or crack mask IoU ≥ 0.2; OR (CFVS only) 128-px high-pass r ≥ 0.90; plus D6's listed twins and early stages.
  - BMRK / SDLE get no screen edges. D6 rejected their high scores, and I checked `BMRK_00222` / `BMRK_01660` visually: they are different cells.
  - My grouping is `judge/out/b6_groups.tsv` (phys_group column). coach should freeze its own version, md5 it and show a montage of every edge.
  - The bootstrap clusters and leave-top-3-out must use the same groups.
  - Disclose that the ARTS r1_c6 near-identical clean cells (high-pass r 0.96-0.99, no defect px) are left ungrouped. They do not affect the inactive primary.

## B6-2 BLOCKING (honesty): power is far below §5's claim, so state the MDE before spending the GPU
- **E: power inputs.**
  - Test (PF2 s5-9, opened files): 16 inactive cells, px-weighted effective n 7.2 (top-3 0.588).
  - The paired module-cluster bootstrap SE of Δ inactive is **0.025**, with 95% CI [−0.022, +0.076].
  - B6 pool with physical groups: 35 inactive groups, **effective n 13.3** (top-3 0.388). v0's key gives 20.7, which overstates independence.
- **S: what that means for B6.**
  - Cell-sampling SE ≈ 0.025 · sqrt(7.2 / 13.3) ≈ **0.018**.
  - Seed noise is not in a fixed-prediction bootstrap. With 2 seeds it adds roughly 0.008 (test per-run sd 0.014 / 0.021, diluted over 5 fold models).
  - Total SE ≈ 0.020. CI half-width ≈ 0.04, about 0.8× test's, not "1/2 to 1/3".
  - **Power to exclude 0 at the expected +0.017: about 13%. 80%-power MDE: about 0.055.**
  - §5's own expectation is +0.01 to +0.03, so the likeliest outcome is n.d., and an n.d. says little.
  - What B6 can deliver is an upper bound ("in-distribution inactive gain < ~0.05"), which may still be worth 16 h. That decision belongs to the user, made with these numbers.
- **Ask:**
  - Replace §5's "1/2 to 1/3" with a computed MDE (coach recomputes my scaling).
  - Pre-register the reading of n.d. as "in-distribution effect below ~0.05 not excluded / not detected".
  - team-lead should put the MDE in front of the user before B6 takes 16 h of gaint.

## B6-3: the verdict rule
1. **Seed noise.** The paired cluster bootstrap with predictions fixed holds the 2 training runs fixed. Use a two-stage bootstrap: resample groups, and for each (fold, arm) draw the seed from {5, 6} with replacement. Or move to 3 seeds (30 runs). Keep "same sign in each seed pair", defined as PF sK − house sK for K = 5, 6. Say that it is weak (with 2 seeds, both positive by chance is ~25% under the null).
2. **Add rule 1's floor:** PASS also needs Δ ≥ 0.01. As written, a CI excluding 0 with Δ +0.006 would pass.
3. **Pooling:** pooled OOF IoU mixes 5 fold models per arm-seed. Fine, but report per-fold Δ, and a fold-level sign count (x / 10 fold-seed pairs).
4. **Name the pass wording now:** "PF raises in-distribution inactive IoU on held-out physical modules (train + val pool)", and the fail and n.d. wording to match.

## B6-4 BLOCKING (engineering): e544133 cannot run "train = 4 folds incl. val cells" as written
- **E** (gaint el_f3 `scripts/train.py`, e544133):
  - With `labeled_fraction ≥ 1` the trainer reads `<root>/splits/train.txt`.
  - `data.labeled_list` needs frac < 1, and it refuses any stem not in train.txt, so val cells raise `contains non-train images`.
  - So v0's "only data change: the train list" is not possible at e544133 without one of two routes:
    - (a) a per-fold `data.root`: symlinked `labeled/`, with `splits/train.txt` = 4-fold list and `val.txt` = held-out fold;
    - (b) a code change, which means a new commit, which breaks §3's "same commit e544133".
- **Ask:** route (a), with:
  - a CPU identity check that a fold root carrying the original train.txt is bit-identical to e544133 (5 steps, as builder's checks);
  - per-run log assert "Labelled: N" = fold size;
  - CE class weights follow the fold list (they come from the labelled subset in use: `train.py` l.273). Assert they differ from the full-train weights.
- **Scorer guard (blocking):** `m0_audit` scores val / test / ext by default. Twenty new models scored that way would produce **unregistered test and E1 reads**.
  - B6 scoring must take an explicit stem list (the held-out fold only).
  - Assert that the output cell set = that fold, and that no test / E1 stem appears.
  - Do no end-of-training eval on test.

## B6-5: smaller items
- **Val reuse:** val (54) enters the pool. It was the selection set for B5 OPs and bias rules, though not for PF's settings, which are a priori (handbook 19 §54). Disclose. It is acceptable because B6 picks no threshold (argmax, final weights).
- **Test / E1 exclusion:** OK as designed. The 7 D7 train twins of test cells may stay in, because B6 never scores test. CSIR_00300: 0 cells in train + val (checked).
- **Stratification:** the largest inactive group (the CFVS r7_c4 chain, 12 cells, 44,278 px = 15.5%) fixes its fold's inactive load. Report per-fold inactive px. Greedy balance on px, not only on cell counts.
- **Data regime:** about 425 cells per run vs 478, at the same 20,000 steps, so ~12% more epochs per cell. Same for both arms; disclose.
- **cv02 option:** OK if the whole experiment stays on one machine type. Add a 2-run cross-check (one fold, both arms, s5) of the A6000 vs gaint 1,000-step identity, as stated.
- **The "[count to fill]" line in §2:** E counts:
  - 532 cells, 48 inactive cells (train 42, val 6), 285,020 inactive px; top-1 / 3 / 10 share 0.107 / 0.255 / 0.597.
  - Per source (cells / B6 keys / inactive cells / inactive px):

    | Source | Cells | B6 keys | Inactive cells | Inactive px |
    |---|---|---|---|---|
    | ARTS | 182 | 107 | 2 | 1,150 |
    | BMRK | 50 | 50 | 6 | 29,704 |
    | CFVS | 169 | 104 | 29 | 222,994 |
    | CSIR | 114 | 76 | 11 | 31,172 |
    | SDLE | 17 | 17 | 0 | 0 |

  - CFVS holds 78% of the inactive px, so the B6 claim is mostly a CFVS claim. Say so, and report per source.

## Bottom line (S)
- Fix B6-1 (physical groups) and B6-4 (fold root plus scorer guard) before any run.
- Fix B6-3 (rule text) before lock.
- B6-2 is a user decision: about 16 GPU-h for a design with ~13% power at the expected effect and an MDE of ~0.055. If the user still wants the upper bound, run it. Otherwise park B6 behind HC and A8.

## Sign-off on v1 (judge, 1 Nov 18:54 IST): SIGNED
Checked file: `protocol_B6.md` as on disk, md5 **09d74b4c**. coach's message cited 518e277e; I signed the version on disk.

**E** (own check of `results/b6/b6_folds.tsv` e2cafce1 against my `b6_groups.tsv` 5ff33e20 and the el_f3 lists):
- 532 unique stems, exactly train ∪ val;
- 0 test stems, 0 E1 stems (`e1_context.tsv`);
- the phys_group column equals my groups for all 532;
- **0 of 334 groups split across folds**;
- per fold (cells / inactive cells / inactive px): 107 / 10 / 56,753; 107 / 8 / 57,565; 106 / 7 / 57,142; 106 / 15 / 56,785; 106 / 8 / 56,775. These match §2's table.

Items 1-7 are applied:
- two-stage bootstrap;
- Δ ≥ 0.01 floor;
- per-fold root with val = test = held-out fold;
- the scorer guard;
- asserts on "Labelled" / CE weights / config re-diff;
- disclosures.

Power arithmetic checked: SE 0.020 gives 13% at +0.017, 32% at +0.03, and 80% at about +0.055.

Notes, none blocking:
1. With val = fold k, the step-20000 val pass writes best.pth at step 20000. The scorer must load the final-step weights. They are the same step, but assert step 20000 in the m0 JSON.
2. cv02: before each wave, re-check that no other user holds more than 4 GB on the chosen GPUs. The 18:50 snapshot is not a standing guarantee.
3. Before launch, the user decision on spend (§8.4) stands. Likeliest outcome: n.d.
