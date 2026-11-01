# Build: HC (idea 5), synthetic half-cut loader transform `data.synth_halfcut`

builder, 31 Oct 2026 (v3: coach's rule_p and dose; v4 1 Nov: found's code review PASS answered in §8, §5 E1 row corrected; v5 1 Nov: GPU smokes H0 IDENTICAL, H1 PASS in §9; build final). Code only. No test or E1 read. **The user approved HC (via team-lead, 1 Nov) to run after THIN-B3.** GPU smokes H0 (p = 0 identity) and H1 run through runner (§6; results §9). Spec: `protocol_HC.md` §3 and §8. Simulator design: domain (`ideas/idea05_synthetic_halfcut.md`; `ideas/scripts/dom_synth_val.py` = SHV1, md5 6e702c36; `dom_synth_halfcut.py`). Tags: E = measured (file named), S = judgement.

## 0. Summary
- **Code:** gaint worktree `/home/noob/work/el_hc`, branch `hc` from e544133 (independent of el_thin). Commits:
  - 226967c code + tests;
  - 6b6dd6b smoke script;
  - 09cc856 the first source rule;
  - **c2e6973 = deploy**: rule_p and the per-eligible dose; stamp `reports/hc/DEPLOY`; `scripts/hc/smoke_hc.sh` md5 **5a5c707b**.
- **Switch:** `data.synth_halfcut={p, pool, jitter}`, opt-in, absent = house. **HC arm opts** = SUP100-PF opts + `data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv` (jitter default 0.08).
- **Eligibility (rule_p, coach, before any HC number):**
  - raw 512 × 512;
  - both centre-cell gaps found;
  - gap band ≤ 20 px;
  - padding (class 7) fraction of the band < 0.4.
- **Dose:** p applies per eligible sample. E: 353 / 478 train cells eligible, so the synthetic share ≈ 0.35 × 0.74 ≈ **0.26** of labelled views.
- **Identity (E, CPU, 5 real steps vs the e544133 export, at c2e6973):** switch absent (house, PF) **IDENTICAL**; switch present with p = 0 **IDENTICAL**.
- **Tests (E):** 14 HC tests, including domain's cross-implementation check (pixel-equal to SHV1 on all 80 eligible SHV1 images); suite 299 passed, 3 skipped, CPU only.

## 1. What the transform does (`src/data/synth_halfcut.py`; port of SHV1 + the training jitter)
Per labelled training sample, before the house label-safe ops (Resize 512, flips, rot90, brightness / contrast):
1. **Eligibility** (deterministic from image and mask; draws nothing): rule_p above. Not eligible → unchanged (code 2).
2. **Dose:** an eligible sample draws u from the object's own generator; synthesized if u < p (code 1), else unchanged (code 0). p = 0 draws nothing.
3. **Split:** at the centre-cell midline, inserting a copy of the image's own top gap band (image and mask rows).
4. **Rescale:** sx = 342/256 · U(0.92, 1.08), sy = 163/(128 + g) · U(0.92, 1.08). Image bilinear, mask and content mask nearest (`ndi.zoom` order 1 / 0, same mapping).
5. **Crop:** 512 × 512 centred on the top or bottom half (uniform), clamped inside the rescaled source as in SHV1 (pads 255 / class 7 only if the source is smaller; 0 cases under rule_p).
6. **Intensity:** content px (not white padding rows / columns, not class 7) linearly mapped to a (mean, sd) pair drawn uniformly from the 1,008 pool half-cells.
   - Pool file: `data/splits/synth_halfcut_pool_ap.tsv` = domain's `ap_pool.tsv`, md5 **a78a2d2a**, CSIR_00300 excluded, the file SHV1 used.
   - Rounded and clipped to uint8.

**Draw order of a synthesized sample:** u, x jitter, y jitter, half, pool index.

**Determinism**
- `SynthHalfCut` is an empty Albumentations Compose stored on the dataset after the house transform. The batch stream seeds it per sample, so it is deterministic, resumable and independent of the worker count.
- E: `SeedSequence.generate_state` is prefix-consistent, so the house transforms keep their seeds. Every unsynthesized sample equals the house sample (test).

**Log:** an own line per log window and in total, `synth window: made a eligible_not_drawn b not_eligible c | total: ... (share, eligible, p_eff) at step N`. The step line is unchanged. Totals restart after a resume (logging only).

**Refused:** non-supervised methods, non-labelsafe augmentation, cp, absh; p outside [0, 1]; missing p or pool.

**Differences from domain's scripts (protocol_HC §3):**
- training jitter;
- ineligible samples pass through (SHV1 used a 128 / 384 fallback on all 54 val cells);
- half and pool pair drawn per sample.

**Disclosed:** the training sources are narrower than the SHV1 / V4 readout set (80 of SHV1's 108 images come from eligible val cells; domain's SHV1-c subset lists them).

## 2. Diff (`git diff e544133 c2e6973`)
| File | Change |
|---|---|
| `src/data/synth_halfcut.py` | new: pool loader, content mask, gap rows, `gap_geometry`, `find_source` (rule_p), `synthesize`, `SynthHalfCut` |
| `src/data/benchmark_el.py` | +7: optional `synth` (stored last), applied before `transform` in the labelled path, sample key `synth` |
| `scripts/train.py` | +26: `check_synth_halfcut`; `SynthHalfCut` for the labelled train dataset only; pool md5 logged |
| `src/trainers/trainer.py` | +16: code counts; own log line |
| `data/splits/synth_halfcut_pool_ap.tsv` | frozen pool (1,008 rows, md5 a78a2d2a) |
| `scripts/hc/hc_source_stats.py` | real-data build check (§4) |
| `scripts/hc/smoke_hc.sh` | runner's GPU smoke (§6) |
| `tests/test_hc_synth.py` | 14 tests (§3) |

## 3. Tests (E; `el_hc/reports/hc/suite_v2.txt`: 299 passed, 3 skipped; CPU only, F1_IMAGENET=1)
- **Pool file:** md5 a78a2d2a, 1,008 pairs, no CSIR_00300.
- **Toy cell:**
  - gaps within 6 px of 128 / 384; flat and 256-px images are not eligible (same objects returned);
  - band padding ~20% stays eligible, ~51% is excluded; a 40-px band (g > 20) is excluded and returns code 2.
- **Real train list (house masks):**
  - asserts 353 sources (ARTS 132, CFVS 122, CSIR 99), 466 found, 411 with g ≤ 20, 58 excluded by padding;
  - kept padding fraction ≤ 0.25, excluded ≥ 0.49, so the 0.4 cut sits in an empty gap;
  - excluded = BMRK 42 + SDLE 16 exactly.
- **SHV1 equivalence (domain's request):**
  - jitter off with SHV1's recorded half and pool index: `synthesize()` reproduces `dom_synth_val.py`'s image and mask exactly on every SHV1 image whose val cell is eligible (80 of 108);
  - E (one-off): my eligibility agrees with domain's `rule_p_pass` (SHV1-c subset) on all 108.
- **Synthesized cell:** 512 × 512 uint8; labels a subset of the source's, ≤ 23; crack CNR > 1; ≥ 2 spacing-label bands.
- **Pixel alignment, image drawn from the mask (8 seeds):** every crack-level dark px is within 1 px of a crack label; ≥ 95% of crack labels sit on dark px.
- **Determinism:** same seed gives the same output.
- **Dose:** p = 0.35 on eligible draws gives a share within 0.28-0.42. **An ineligible sample leaves the generator state untouched.**
- **Stream:** p = 0 = house stream bit for bit, never synthesized; at p = 0.5 a sample equals the house sample iff not synthesized; resume = uninterrupted.
- **Other:** switch checks; trainer log line (counts, share 0.5000, eligible 0.7500, p_eff 0.6667 on the fixture); switch absent from `configs/*.yaml`.

## 4. CPU identity and real-data checks (E)
**Identity at c2e6973:** harness `el_thin/scripts/thin/identity_cpu.py` (md5 962379a6), CPU fp32, 8 threads, nice 19, `CUDA_VISIBLE_DEVICES=""`, 5 real steps; reference = the e544133 export records. Records in `el_hc/reports/hc/idchk_c2e6973/`.

| Run | vs e544133 |
|---|---|
| house, switch absent | **IDENTICAL** 5/5 (md5 c5393f9f) |
| SUP100-PF, switch absent | **IDENTICAL** 5/5 (md5 08d51539) |
| SUP100-PF, switch present, p = 0 | **IDENTICAL** 5/5: loss repr, lr, sha of all params + buffers, fixed-batch logits, image / mask bytes, init state, class counts (md5 964e72c1) |
| SUP100-PF, p = 0.35 | differs as designed (md5 83950e21) |

(Identity also held at 226967c and 09cc856.)

**Real train set under rule_p** (`scripts/hc/hc_source_stats.py`; `el_hc/reports/hc/source_stats_rulep.json` md5 367a5848; fixed seeds; train cells only):
- **Sources:** 353 / 478.

  | Group | Sources / cells |
  |---|---|
  | ARTS | 132 / 162 |
  | CFVS | 122 / 146 |
  | CSIR | 99 / 111 |
  | BMRK | 0 / 42 |
  | SDLE | 0 / 17 |
  | multi | 137 / 165 |
  | mono | 92 / 106 |
  | unknown | 123 / 206 |

- **Reconciliation with domain's 349:** domain counted on raw E-SCDD masks with the 24 → 2 / 29 → 1 / 25-28 → 0 mapping. Re-run that way on gaint, it gives 349. The 4 extra house sources are train cells with no raw E-SCDD mask: ARTS_00057_r2_c5, CSIR_00178_r7_c1, CSIR_00179_r12_c4, CSIR_00179_r6_c1 (BMRK_02125_cell1223 also has no raw mask but is ineligible). No cell differs where both masks exist. Training uses the house masks, so 353.
- **CPU:** 27.2 ms per synthetic cell (median 25.9, p95 41.6, single thread, gaint under load). At p 0.35, about 2 per batch of 8, so ≈ 55 ms per step over 4 workers (S: no step-time cost).
- **Labels:** 0-23, a subset of the source's; padded outputs 0.
- **Inserted band (the source's gap-row labels, as SHV1):** background 31%, sp_mono 28%, sp_multi 26%, padding 6% (module-edge margins, kept by rule_p), edge_dark 3%, border 2%, ribbons 1.4%, inactive 0.2%, crack 0.07%.
- **Alignment on real cracks:**
  - local contrast synthetic / source median 0.84 (p10 0.38, n 144);
  - crop CNR ratio 0.83;
  - domain's 0.95 was on train multi only; domain agrees the drop is bilinear smoothing at ×1.3.
  - A best-shift test is inconclusive: sources already show > 1 px for 75 / 147.
- **Montage:** `ideas/figs/hc_build_montage_train_rulep.png` (md5 8948d90d; ARTS, CFVS, CSIR rows; source | synthetic | crack red / inactive blue).

## 5. Label mapping of a gap px (judge condition 4; one table)
| Where | Gap px label |
|---|---|
| HC training, inserted band | the source's own gap-row labels (coach and domain: keep; one spacing class would mislabel ribbons): background, sp_mono, sp_multi, padding (module margins), edge_dark, border, ribbons, as in §4. House train masks hold no raw 24 / 29, so a multi source inserts 1 and a mono source inserts 2 (E, found `review_hc.md` §5: band has 1 only 173, 2 only 179, both 0, neither 1 = CSIR_00062_r9_c6, §8 F2) |
| Hanifi `_rf` | E-SCDD 29 → 1 (calib's build; E, found: 556,400 / 556,400 raw-29 px are 1) |
| E1 scoring (ext117) | **E1 (20221008 masks): multi half-cut gaps are already 1 (class 29 exists only in E-SCDD); 24 (sp mono halfcut) → 2** (4 cells). Sources: handbook 17 §5.2, `results/e1/README.md`, found's review F1. E1 masks not re-read (sealed; not needed). *Corrected 1 Nov (found F1); v3 wrongly said "29 → spacing"* |

(E + S) A gap px is the same class in all three uses: multi half-cut gap = 1, mono half-cut gap = 2 (found's review §5). Gap px are non-defect (crack 0.07% and inactive 0.2% of band px come from defects crossing the gap rows). Nothing to disclose for gap px.

## 6. GPU smoke (runner; after the user's GPU OK and coach's line)
`el_hc/scripts/hc/smoke_hc.sh H0 H1` at deploy **c2e6973** (md5 **5a5c707b**):
- **Gate:** sources runner's `gpu_gate.sh`; start gate 9,000 MiB; one job at a time; rc before `date`; `--exit_after_step 2000`.
- **H0:** SUP100-PF s0 + `synth_halfcut.p=0`, 2,000 steps, val off. 80 step + PF lines vs `f3_SUPPF_100pct_s0.stdout`; this is the shared-baseline gate. It does not depend on the source rule.
- **H1:** p = 0.35, 2,000 steps: finite loss; `synth window` lines (expected share ≈ 0.26, eligible ≈ 0.74, p_eff ≈ 0.35); peak_reserved from latest.pth + nvidia-smi; steps/s.

## 7. History of the source rule (before any HC number)
| Version | Rule | Sources |
|---|---|---|
| 226967c | gaps found | 466 |
| 09cc856 | + g ≤ 20 + no padding in the band | 231 |
| **c2e6973** | rule_p: + g ≤ 20 + padding fraction < 0.4; p per eligible sample, p 0.35 | **353** |

All before any HC number; superseded stats are kept on gaint (`source_stats.json`, `source_stats_v2.json`).

## 8. Code review by found (`review_hc.md` md5 d7ba9db8, 1 Nov): answers
**Verdict PASS, no blocker, no code change.** el_hc stays at deploy **c2e6973** (no new commit, so no identity re-run needed). found's independent checks agree with §3-§4: identity house / PF / PF + p 0 IDENTICAL 5/5 vs found's own e544133 records; eligibility 353 = domain's verbatim gap code (0 disagreements; cut gap 0.248 / 0.494); ineligible samples move no RNG (0 / 125); p 0 = house 120 / 120; resume identical; SHV1-p 80 / 80 byte-equal; diff read, no defect.

| # | found's point | builder's answer |
|---|---|---|
| F1 | Wording: E1 masks (release 20221008) have no class 29; multi half-cut gaps are 1, only 24 → 2. build_hc §5 and protocol_HC §3 said "29 → spacing" / "29 to sp mono" | **Accepted.** §5 corrected (E1 row and summary line). protocol_HC §3 is coach's file: sent to coach. No code or number changes: the transform never reads E1 and the scorer is not part of el_hc |
| F2 | CSIR_00062_r9_c6 (g 17) is the one source whose band has neither 1 nor 2: sp_dogbone (3) 5,962 px + background 2,742 px | **Accepted, disclosed; no change.** E (builder re-check on gaint, `find_source` at c2e6973, house mask): yt 133, band rows 124-140, g 17, band_pad 0; band = {0: 2,742, 3: 5,962} exactly. The cell is a dogbone cell (whole mask: class 3 21,805 px, no 1 / 2), so its own gap label is correct under the "source's own labels" rule (coach, domain). It is the 0.34% class-3 share in §4's band composition (`source_stats_rulep.json`, which §4's text had rounded away) |
| F3 | House train masks keep P6's old labels on raw scuff / star px (raw 25 → 0 / 13 / 14: 1,207 / 1,390 / 649 px; raw 28 → 0 / 1 / 14: 176 / 8 / 54); `_rf` and E1 ignore 25-28 | **Accepted, disclosed; no change.** Shared by both arms (house masks unchanged by HC; the training mask set is `labeled/masks_escdd` in both). The 703 crack px = handbook 17 §5.3 (649 scuff + 54 star). Not a gap-px issue (band crack share 0.07%). An HC synthetic view inherits these labels wherever its source has them, as any house view does |
| F4 | CE class weights come from the real masks in both arms (class-count sha equal at p 0.35) | **Agree, by design** (one change per arm): `count_class_pixels` runs on the stem list, before and independent of the transform. Synthetic views change the sample stream, not the weights |
| §8 | Pool hygiene: 0 CSIR_00300; the pool's 7 module images share 0 of E1's 71 source images | Agree; nothing to do |
| §10 | Remaining gates: GPU H0 / H1 (runner), queue + opening (runner), coach APPROVED | H0 running at gaint since 18:42 (step 1,350 at 18:52; live eligible share 0.7386). Results go in §9 when runner sends them |

## 9. GPU smokes (runner, el_hc c2e6973, `smoke_hc.sh` 5a5c707b; gaint, shared gate 9,000; log `el_hc/reports/hc/smoke/smoke.log`)
**H0, p = 0 identity (the shared-baseline condition, protocol_HC §3 / §9.2): PASS.**
- Run `hc_h0_p0`: SUP100-PF s0 + `data.synth_halfcut.p=0` + pool, 2,000 steps, val off; 18:42:24-18:57:18, rc 3 (planned `--exit_after_step 2000`, a hard exit before the trainer's TEST block).
- Script verdict: `H0 p=0 identity to step 2,000: IDENTICAL (80 ref lines, 80 hc lines)`; `H0_ref.lines` = `H0_hc.lines` md5 **8645b979** (cmp equal).
- E, builder's own extraction (grep of `step N/20000` and `PF encoder lr=` lines only, timestamps and steps_per_sec stripped, step ≤ 2,000; the stdouts were not read in full): 80 lines each (40 step + 40 PF lr), identical (md5 of the joined lines 6c537a2a both); step 2,000 line `loss=0.6201 loss_sup=0.6201 lr=0.0009797` in both, vs `el_f3/experiments/f3_SUPPF_100pct_s0.stdout`.
- Synth lines: 40, made 0 throughout; total at step 2,000: eligible_not_drawn 11,818, not_eligible 4,182 of 16,000 samples → **eligible 0.7386** (353 / 478 = 0.7385). p = 0 draws nothing, as designed.
- Peak: nvidia-smi 6,826 MiB, `peak_reserved` 6.35 GiB; 2.26 steps/s beside 2 THIN runs + finllm (not a clean speed reading).
- So HC's commit with p = 0 is bit-identical to e544133 on SUP100-PF opts for 2,000 GPU steps: **PF2's `pf2_SUPPF_100pct_s5..9` serve as HC's shared baseline** (protocol_HC §3).

**H1, p = 0.35 (protocol_HC §9.2): PASS.**
- Run `hc_h1_p035`: SUP100-PF s0 + `data.synth_halfcut.p=0.35` + pool a78a2d2a, 2,000 steps, val off; 18:57:19-19:12:09, rc 3 (planned exit); `smokes done: H0 H1` 19:12:11.
- **Loss finite:** 40 step lines, 0 nan / inf; 0.9212 at 1k, **0.7466 at 2k** (H0 0.6201: higher, as expected with ~26% synthetic views; lr lines equal H0's, e.g. 0.0009797 at 2k).
- **Synth counts** (E, builder's grep of the 40 `synth window` lines only): total made **4,102**, eligible_not_drawn 7,716, not_eligible 4,182 of 16,000.

  | Measure | Measured | Expected |
  |---|---|---|
  | synthetic share (made / all) | **0.2564** | 0.35 × 353/478 = 0.2585 |
  | eligible share | **0.7386** | 0.7385 |
  | p_eff (made / eligible) | **0.3471** | 0.35 (binomial sd over 11,818 eligible 0.0044: −0.7 sd) |
  | per-window (400 samples) share, min-max | 0.210-0.300 | sd 0.022 |
  | per-window p_eff, min-max | 0.280-0.407 | |

- **Cross-check:** not_eligible 4,182 in H1 = H0 exactly (same seed, same stream; eligibility is deterministic per sample and draws nothing).
- **Memory:** nvidia-smi peak 6,826 MiB, `peak_reserved` 6.35 GiB, **= H0**: synthesis runs in the CPU workers, no GPU cost. Gate = 6,826 + 2,048 = 8,874 → **train gate 9,000 stays** (runner).
- **Speed:** 2.264 steps/s vs H0 2.26, both beside 2 THIN runs + finllm (+ a CPU job in H1): no measurable step-time cost (S; not a clean reading, as §4's 27 ms per synthetic cell predicted).

**Both smokes pass; HC build final.** Remaining before APPROVED (protocol_HC §9.3): runner's queue + opening build, coach.
