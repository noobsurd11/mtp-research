# Review: HC code (el_hc deploy c2e6973 vs e544133), protocol_HC §9 gate 1

found, 1 Nov 2026 (started 14:34 by the previous found session; finished 18:50 by this one). Independent of builder: own scripts, own reference records, builder's identity harness used read-only. CPU only (gaint nice 19, CUDA hidden; laptop for the raw E-SCDD pixel check). No test cell, no E1 pixel, no model score read. Tags: E = measured (file named), S = judgement.

## Verdict
**PASS, no blocker.** The code does what protocol_HC §3 and build_hc.md say:
- house path unchanged with the switch absent and with p = 0;
- eligibility = rule_p (353 sources);
- no RNG shift for ineligible samples;
- SHV1 reproduced pixel for pixel;
- the gap px label is the same class in training, `_rf` and E1.

One wording fix is needed in protocol_HC §3 and build_hc §5 (finding F1). It changes no code and no number. Three disclosures follow (F2-F4).

## 1. What I ran (records: gaint `/home/noob/work/found/hc_review/`, local copy `ideas/found_scripts/hc_review/`)
| Check | Script (md5) | Output (md5) |
|---|---|---|
| CPU identity, 4 runs × 5 real steps | `hc_review_idchk.sh` c995ee13; builder harness `identity_cpu.py` 962379a6 (read-only) | `HCa..HCd_*.json`; batch.log: 14:32:50-14:38:55, rc 0 × 4, el_hc HEAD c2e6973, 0 tracked changes |
| Identity compare | `hc_idcmp.py` a6c2cebb (own) | `idcmp.txt` e1182468 |
| Eligibility, seeding, band labels, SHV1 | `hc_review_checks.py` 6999e2b3 (own) | `hc_checks.json` 575aa386 |
| Label map vs raw E-SCDD | `hc_labelmap_check.py` e843dd78 (own; laptop `datasets/escdd_full`) | `hc_labelmap.json` 5e6da23e |
| Diff read | `git diff e544133 c2e6973` (8 files, +1,766 / −1) | §7 |

Reference records for identity: found's own e544133 export runs from the el_f8 review (`found/f8_idchk/A_e544133_house.json` 4fe80d0a, `C_e544133_pf.json` c8f910ba; same harness, same machine), not builder's.

## 2. CPU identity (E, `idcmp.txt`)
Compared: loss class, n params, init state, class-count sha, fixed-batch stems + image / mask bytes, and per step: loss repr, lr, sha of all params + buffers, logits hash and shape.

| el_hc c2e6973 run | vs e544133 | Note |
|---|---|---|
| house, switch absent | **IDENTICAL** 5/5 | |
| SUP100-PF, switch absent | **IDENTICAL** 5/5 | |
| SUP100-PF + `synth_halfcut.p=0` | **IDENTICAL** 5/5 | only change: the batch carries the extra key `synth` (outcome code; by design, benchmark_el.py +7) |
| SUP100-PF + p = 0.35 | differs (fixed batch image / mask, all 5 steps) | as designed; init state and class-count sha equal, so CE weights still come from the real masks |

Agrees with builder's records (build_hc §4).

## 3. Eligibility (E, `hc_checks.json` → eligibility)
- builder's `find_source` vs my re-implementation from domain's reference gap code (`gap_rows` copied verbatim from `dom_synth_val.py` 6e702c36) + band padding fraction: **353 = 353, 0 per-cell disagreements** on the 478 train cells (house masks).
- Split: ARTS 132, CFVS 122, CSIR 99, BMRK 0, SDLE 0. Gaps found 466; g ≤ 20: 411; excluded by padding 58 = BMRK 42 + SDLE 16 exactly.
- Cut: kept padding fraction max **0.248**, excluded min **0.494**. The 0.4 cut sits in an empty gap.
- Live (E, runner's H0 at 18:47, `el_hc/experiments/hc_h0_p0.stdout`): eligible share 0.7375 over 5,200 samples, vs 353/478 = 0.7385.

## 4. Per-sample seeding and RNG (E, `hc_checks.json` → eligibility, seeding; code §7)
- An ineligible sample leaves the object's generator unchanged (**0 of 125 changed**). The global numpy and torch RNG are untouched by the transform.
- `SeedSequence.generate_state` is prefix-consistent (seeds 0-199, n 1-11). `_flatten` puts the empty `SynthHalfCut` Compose last (stored after `transform`), so the house transforms keep their seeds.
- p = 0 equals the house sample on **120/120** random (index, seed) keys. At p = 0.35, every not-made sample equals the house sample (**90/90**); 30 were made (0.25; expected 0.35 × 0.74 ≈ 0.26).
- BatchStream resume (`iterate(3)`) equals the uninterrupted stream (images, masks, codes; 3 batches, workers 0).

## 5. Label mapping (judge condition 4; E unless tagged)
**Raw E-SCDD spacing classes** (`ListOfClassesAndColorCodes_20221008.csv` in the E-SCDD download):
- 1 sp multi; 2 sp mono; 3 sp dogbone;
- 24 sp mono halfcut; 29 sp multi halfcut;
- 25-28: scuff, corrosion cell, brightening, star.

| Use | Where a half-cut gap px goes | Evidence |
|---|---|---|
| HC training (inserted band) | the source's own gap-row labels, copied verbatim | 706/706 made masks ⊆ source labels, max 23, 0 padded outputs. Band spacing class per source: **1 only 173, 2 only 179, both 0, neither 1**. House train masks hold **no** raw 24 or 29 (0 of 473 cells with a raw mask), so a multi source inserts 1 and a mono source inserts 2 |
| Hanifi `_rf` (calib's 106-cell build) | 29 → **1** | pixel check vs raw E-SCDD: raw 29 → 1 on **556,400 / 556,400 px** (36 cells); 25-28 → ignore (207,371 px = the 255 marker, 0 outside ignore); raw ≤ 23 unchanged (0 px); raw 24: none in `_rf` |
| E1 scoring (m0_audit; ext117 = release 20221008 masks) | **no class 29 exists in E1's masks**: a multi half-cut gap is already **1** (sp multi); 24 → **2** (4 cells) | handbook 17 §5.2 (E-SCDD vs 20221008: the only mask changes are 62 masks sp multi → sp multi halfcut and 4 spacing swaps; crack / inactive px changed 0); `results/e1/README.md` (24 → 2; 25-28 → ignore). E1 masks not re-read (sealed; not needed) |

- **Result:** multi half-cut gap = 1 and mono half-cut gap = 2 in all three uses. No difference to disclose for gap px.
- **F1 (should-fix, wording only):**
  - protocol_HC §3 says "E1 scoring maps 29 to sp mono as m0_audit does today". E1 masks carry no 29: their multi gaps are sp multi (1), and only class 24 (sp mono halfcut) maps to sp mono (2).
  - build_hc §5 says "29 → spacing" for E1. Suggested text: "E1 (20221008 masks): multi half-cut gaps are 1 (class 29 exists only in E-SCDD); 24 → 2".
  - domain's idea05 line 78 already states it correctly.

## 6. SHV1 equivalence (E, `hc_checks.json` → shv1)
- `synthesize()` with jitter off and SHV1's recorded half and pool index reproduces domain's stored SHV1 files: **80 / 80 images and 80 / 80 masks byte-equal** on the SHV1-p list (md5 7f651fc7, 80 names). 0 problems.
- domain's own code path (copied into my script) regenerates the stored files 4 / 4, so the files are the reference output.

## 7. Diff read (S unless tagged)
- **Scope** (E): new `src/data/synth_halfcut.py`. Integration is small:
  - `benchmark_el.py` +7: `synth` applied to (raw image, mask) before the house transform, labelled path only;
  - `train.py` +26: switch check, labelled train dataset only, pool md5 logged;
  - `trainer.py` +16: outcome counts, own log line, step line unchanged.
  - Val, test and scoring loaders are untouched.
- **Switch check:** refuses SSL, cp, absh, non-labelsafe augmentation, and a missing p or pool. It passes on the real HC opts (E: runner's H0 started through `train.py` with the switch, 18:42).
- **Draw order:** u, then for made samples x jitter, y jitter, half, pool index. p = 0 draws nothing. Matches build_hc §1.
- **Output:** uint8 (H, W, 1), so the house transform gets the same type as a raw sample.
- **Totals:** the trainer's synth totals restart on resume (logging only; disclosed in build_hc).
- **No defects found.**

## 8. Data hygiene (E, names only)
- Pool `data/splits/synth_halfcut_pool_ap.tsv`: md5 a78a2d2a, 1,008 half-cells, 0 CSIR_00300.
- The pool's 7 module images (CSIR_00297, 00298, 00299, 00301, 00333, 00334, 00335; 144 half-cells each) share **0** of E1's 71 source images (ext117 manifest, `in_external_pool` = 0). The 11 ext117 cells from those images are the ones E1 already drops.
- No intensity target comes from an E1 module.

## 9. Disclosures (no action needed)
- **F2.** 1 of 353 sources (CSIR_00062_r9_c6, g 17) inserts a dogbone gap: band = sp dogbone (3) 5,962 px + background 2,742 px. This is class 3 in band composition (0.34%).
- **F3.** House train masks put P6's old labels on raw scuff / star px (raw 25 → 0 / 13 / 14: 1,207 / 1,390 / 649 px; raw 28 → 0 / 1 / 14: 176 / 8 / 54). `_rf` and E1 put 25-28 in ignore.
  - The 703 crack px match handbook 17 §5.3 (train 703).
  - Both arms share this. It is not a gap-px difference: band crack share is 0.07%.
  - domain's "25-28 → 0" for the house masks is approximate.
- **F4.** Builder's CE class weights come from the real masks in both arms (class-count sha equal at p = 0.35). Synthetic views do not change the weights (S: correct for a one-change arm).

## 10. Remaining gates (not part of this review)
- §9.2: runner's GPU H0 (p = 0 vs `f3_SUPPF_100pct_s0.stdout`, step + PF lr lines, 2,000 steps) and H1 (p = 0.35: share ≈ 0.26, eligible ≈ 0.74, peak memory, steps/s). H0 has been running since 18:42.
- §9.3: queue + opening build. coach's APPROVED follows.

## Addendum (18:58): independent re-check of runner's H0 (E)
- H0 `hc_h0_p0` (p = 0, GPU, 2,000 steps; trained 18:57:18, rc 3 = planned exit) vs `el_f3/experiments/f3_SUPPF_100pct_s0.stdout`.
- Script: `found/hc_review/stepcmp.py` 6d0fc019. It reads only step lines and PF lr lines, ≤ step 2,000, with timestamps and steps/s stripped. Output: `h0_stepcmp.txt` b2a857cf.
- Result: **step lines 40/40 IDENTICAL and PF encoder lr lines 40/40 IDENTICAL.** The shared-baseline condition holds on my read too. Runner's gate record is the official one.
- Runner's parse: peak_reserved 6.35 GiB, nvidia-smi max 6,826 MiB, 2.26 steps/s, eligible share 0.7386 over 16,000 samples (353/478 = 0.7385), 0 made.
