# 19. Feature learning from the unlabelled pool, encoder erasure, and the 100% plan (28 to 30 Oct 2026)

## What this covers
This file covers the session of 28 to 30 Oct, after `18_experiments_trackD_trackM.md`:
- **The user's question (28 Oct):** does learning features from the ~11.7k unlabelled cells, without labels, improve the model trained on all our labels?
- **Three pool-feature methods, run at 5% labels on gaint (29 to 30 Oct):** MIM5 (masked-image pretraining of the encoder), AM (MIM reconstruction error as a crack map), DDeP5 (denoising pretraining of the decoder). Plus CP5 (crack copy-paste onto pool cells), stopped unscored.
- **Encoder erasure (30 Oct):** the house fine-tune erases encoder layer3/4 within its first 2,000 steps, for both inits measured (ImageNet and MIM, ResNet-34 U-Net++).
- **Why 5% was the wrong test,** and when a low-label null carries to full labels (`diag`).
- **protocol_100:** 4 arms × 5 seeds at 100% labels on gaint. Launched 30 Oct 12:05:34 IST on v1.1 (the 15 fine-tunes; CP100 held behind gate 6b). **No results exist yet;** only its design, gates and timing are given here.
- **Label work:** the B1 label audit, scuff label facts, B2 pool mining, B3 scuff as its own class.

The layout follows docs 08 to 10, compressed as in doc 10's SK1 and AL1 sections. Added 30 Oct 2026 (handbook refresh).

**Tags.** E = measured (file), R = literature (Research MCP id), S = judgement. "Clean" / "without noisy" = the 50 test cells without `CSIR_00070_r8_c4`. Rule 1 here is the house rule with divisor 3 (§0).

**Status at writing (30 Oct 2026, ~12:00 IST)**

| Item | Status | Where the results are |
|---|---|---|
| MIM pretraining | done 29 Oct 18:34 IST, 36,500 steps | `team_2026-10-29_features/protocol_mim5.md`, `log.md` |
| MIM5 | done; coach VERIFIED: n.d., closed | `verify_mim5.md`, `results/mim5/` |
| AM | done (val only); KILL confirmed | `verify_mim5.md` §6 |
| DDeP pretraining | done 29 Oct 22:42 IST, 40,000 steps (cv02) | `protocol_ddep5.md`, `log.md` |
| DDeP5 | done; coach VERIFIED: n.d., closed | `verify_ddep5.md`, `results/ddep5/` |
| CP5 | gates passed; stopped 30 Oct 10:50 IST; not scored, no test opened | `protocol_cp5.md`, `spec_cp5.md`, `log.md` |
| Encoder erasure | measured 30 Oct ~10:20 IST; re-derived by runner | `coach_100.md` §0, `protocol_100.md` |
| `diag` analysis | done 30 Oct | `diag_5pct_to_100pct.md` |
| protocol_100 | v1.1 (md5 8dcb231b); all gates pass except gate 6 (CP decoy, FLAG); **launched 12:05:34 IST 30 Oct** (15 fine-tunes); CP100 held behind gate 6b (pending at 12:22 IST) | `protocol_100.md` v1.1, `review_100_v1.md`, `coach_100.md`, `log.md` |
| B1 label audit | done; sheets delivered to the user 11:37 IST | `b1_audit/` |
| B2 pool mining | running on gaint CPU since 12:09 IST (candidates only) | `log.md` 30 Oct 12:09, 12:10 |
| B3 scuff class | spec drafted; runs after protocol_100 | `spec_b3_scuff.md` |

## Sources
- `SESSION_RECORD_2026-10-28_to_30.md` (master for 28 to 30 Oct).
- `team_2026-10-29_features/`:
  - brief `README.md`, append-only `log.md`, `directions.md`;
  - protocols `protocol_mim5.md` (v1.1, md5 70d65d2b), `protocol_ddep5.md`, `protocol_cp5.md`, `protocol_am.md`, `protocol_100.md` (v1, md5 200a6734; v0 kept);
  - reviews `review_mim5_v0.md`, `review_mim5_v1.md`, `review_ddep5_cp5_v0.md`, `review_spec_cp5_v1.md`, `review_100_v1.md`; coach notes `coach_mim5.md`, `coach_100.md`, `coach_strategy.md`;
  - verifications `verify_mim5.md`, `verify_ddep5.md`, `identity_f1.txt`;
  - `diag_5pct_to_100pct.md`, `spec_cp5.md`, `spec_b3_scuff.md`;
  - `b1_audit/` (`b1_coverage.txt`, `b1_flags*.tsv`, `b1_S.tsv`, three panel sheets, `MANIFEST.md5`);
  - `results/{mim5,ddep5,cp5}/` (per-cell raw JSONs, about 240 MB, are local and on gaint with `MANIFEST.md5`, not in git).
- Copies of the markdown files: `sources/teams/team_2026-10-29_features/`; the session record: `sources/session_records/`.

Where a session record and a verify or results file disagree, the verify or results file is used and the discrepancy is noted.

---

## 0. Terms and setup common to this file
- **Team.** `scout` (survey, Research MCP), `runner` (code, servers, runs, scoring), `coach` (settings advice, APPROVED / CHANGES, independent recompute of every primary contrast), `diag` (30 Oct, a one-off analyst). The lead only orchestrates (user, 29 Oct ~12:30).
- **Rule 1 (house).** Δ > max(0.01, 2·sqrt((sd_A² + sd_B²)/3)), divisor 3 even at 5 v 5. Better on one primary, worse on none. Primaries: test crack IoU, crack relF1@2, inactive IoU. Verdict sets: all 50 and without `CSIR_00070_r8_c4` (pass = BETTER on both, or BETTER on one with a same-sign n.d. on the other). Without twins and without both are reported. The team brief first said /n; corrected to /3 before any verdict.
- **A5c-f1.** The 5% supervised baseline re-run on gaint at `el_f1` (603e0d5), 5 seeds, shared by MIM5, DDeP5 and CP5 after identity checks. Test crack IoU 0.300 vs 0.304 for the original A5c on cv02 (cross-machine, descriptive).
- **House optimizer / house fine-tune.** Adam lr 1e-3, coupled L2 weight decay 1e-4, 200-step warmup and cosine, 20k steps, batch 8 (`configs/base.yaml`). Never varied in the P-series or Track M R1 to R5.
- **PF (encoder-preserving fine-tune).** Encoder frozen for steps 0 to 999 (BN in train mode), then encoder lr ramps 0 → 0.1× base over 1,000 steps, encoder weight decay 0. Decoder and head as house. Switch `training.encoder_pf` {freeze 1000, ramp 1000, lr_mult 0.1, wd 0}.
- **MIM.** Masked image modelling: hide image patches, train the encoder to reconstruct them. **SparK:** MIM for CNNs with sparse convolution.
- **DDeP.** Denoising pretraining of the decoder (ε-prediction with a frozen encoder).
- **CP.** Crack copy-paste: labelled crack components pasted onto unlabelled pool cells as an extra training stream.
- **AM.** "Anomaly map": MIM reconstruction error used as a crack map.
- **gaint memory rule.** One RTX PRO 4500 (32.6 GB). Root's `finllm_chat.py` (5.9 GB) must never run out of memory, so ≥ 2 GB stays free at all times. Start gate per run = own measured peak + 2 GB (fine-tune 6.8 GB, CP 9.5 GB). Details in doc 14 §1.2b.
- **cv02.** All 8 GPUs were held by other users for the whole session except the DDeP slot.

---

## 1. Context: the question, and the 5% choice (28 to 29 Oct)
- **28 Oct.** The user asked for a one-paragraph answer to the question above. Answer: never run. Only label propagation (MT, CPS, BsM, ALHVR, SKCDF) and a frozen ImageNet probe had been run; P15's UCF-EL pretraining was n.d. at 5% and worse at 10% (`SESSION_RECORD_2026-10-28_to_30.md` §1).
- **29 Oct ~12:30.** The user asked for a researcher, an executor and a practical critic, with the lead only orchestrating. Team created from `team_2026-10-29_features/README.md`.
- **29 Oct 12:38 to 13:30.** scout's `directions.md` v1 to v3.1 ranked CP, DDeP, MIM5, AM. Coach reviewed; protocols `mim5` v1.1, `ddep5`, `cp5`, `am` APPROVED.
- **The 5% choice.** All three methods were screened at 5% labels (23 cells). This was copied from the 27 Oct synthesis (doc 18 §U, item 3) without checking it against the user's question, which was about 100% labels. The user caught it on 30 Oct (§5; doc 13 C14).

---

## 2. MIM pretraining and MIM5 (29 to 30 Oct, gaint)

**Question.** Does continued MIM of the ImageNet ResNet-34 encoder on the pool beat ImageNet init at 5%?

**Pretraining (E, `protocol_mim5.md` v1.1; session record §3.1)**
- Pool v1.1: **11,690 cells** (list md5 f0a5d74a), plus 256 held-out monitor cells. Excluded:
  - every module of a val, test or E1 cell (−413);
  - 11 ext117 stems;
  - 50 near-duplicates of val/test/ext117 cells (high-pass r ≥ 0.95; v1's 0.85 would have dropped 780 cells, 23% of the pool's ARTS cells);
  - the 7 D7 twins.
- Recipe: SparK-style sparse MIM of the U-Net++ encoder. Mask 0.6, 32 px patches at 512 px, masked-only normalised-pixel L2. Batch 32, 36,500 steps; the encoder is frozen for the first 730 steps (decoder warm-up), then its lr ramps up over 1,000 steps.
- Run 29 Oct 13:08 to 18:34 IST. Monitor loss 0.914 → 0.208, flat from about 26k. `encoder_final` md5 1c3df959.

**Fine-tune and rule.** MIM5 = A5c-f1 with `model.encoder_init=encoder_final`; 5 v 5, house fine-tune, final weights. Kill: n.d. on all three closes MIM ("continued MIM on this pool does not beat ImageNet init on EL at 5%"), with no 100% arm.

**Verdict (E, `verify_mim5.md`): n.d. on all three primaries in both verdict sets; every estimate negative. Closed per protocol.**

| Set (A5c-f1 → MIM5) | Crack IoU | Crack relF1@2 | Inactive IoU |
|---|---|---|---|
| all 50 | 0.3002 → 0.2886, −0.0116 (0.0186) n.d. | 0.7136 → 0.6995, −0.0141 (0.0295) n.d. | 0.2791 → 0.2297, −0.0495 (0.1158) n.d. |
| without noisy | −0.0118 (0.0187) n.d. | −0.0143 (0.0295) n.d. | −0.0513 (0.1200) n.d. |
| without twins | −0.0074 (0.0218) n.d. | −0.0118 (0.0442) n.d. | −0.0477 (0.1215) n.d. |

**Robustness (E, descriptive)**
- MIM5's seed sd is about 3× A5c-f1's on crack (0.015 vs 0.005) and 2.4× on inactive. Only 1 of 5 MIM seeds (s1) is above the A5c-f1 mean.
- Paired image bootstrap, all 50: crack −0.0116 [−0.0181, −0.0043] (cells only, not seeds).
- LA-matched (τ 1): crack 0.3157 → 0.3050, −0.0108 (0.0164), n.d.
- Per source: ARTS crack −0.016, beyond its 0.0125 threshold (descriptive).
- E1 crack recall: 0.0473 → 0.0360; scuff + half-cut (29 cells) 0.0295 → 0.0268; other (77) 0.1009 → 0.0640.
- runner's own analysis matches coach's to 4 decimals.

**Reading at the time (coach, S).** The MIM encoder is a different start, not a better one. [Qualified 30 Oct: §4 showed the house fine-tune erased layer2 to layer4, which is where MIM changed the encoder (MIM5 final vs MIM init cosine 0.000 to 0.139). So MIM5 tested conv1/layer1 transfer only, not MIM features. The protocol's "closes MIM" holds only under the house optimizer and at 5%.]

---

## 3. AM, DDeP5 and CP5

### 3.1 AM: MIM reconstruction error as a crack-recall aid (val only)
- **Rule (`protocol_am.md` v0.1).** Does the map recover components the fine-tuned model misses, at relaxed precision ≥ 0.5?
- **Result (E, `verify_mim5.md` §6): KILL.** Map AP 0.0166, 6.2× the val crack base rate (0.0027). No threshold reaches relaxed precision 0.5, so 0 missed components are recovered (A5c-f1 misses 67 to 71 per run, SUP100 20 to 27). No test number was opened.

### 3.2 DDeP pretraining and DDeP5
**Pretraining (E, session record §3.4; `log.md`).** cv02 A6000, 40,000 steps; encoder frozen, BN in train mode; ε-prediction, γ 0.95. Monitor ε-MSE 1.046 → 0.0465. `decoder_final` md5 dd786ff4, identical on cv02 and gaint after a relay cv02 → laptop → gaint with md5 on each hop. [Discrepancy: the session record's timeline says "15:40 DDeP pretraining starts on cv02 (A6000, GPU 1)". `log.md` (29 Oct 16:26, 19:47) says the GPU 1 slot at 15:40 ran the smoke, GPU 1 was then lost after a gate-parse bug (doc 13 D24), and the full run started on GPU 0 at about 19:43. Both end at 22:42 IST.]

**Verdict (E, `verify_ddep5.md`): n.d. on all three primaries in both verdict sets; small positive estimates. Closed per protocol** ("a denoising-pretrained decoder does not beat a random decoder at 5% on EL").

| Set (A5c-f1 → DDeP5) | Crack IoU | Crack relF1@2 | Inactive IoU |
|---|---|---|---|
| all 50 | 0.3002 → 0.3071, +0.0070 (0.0100) n.d. | 0.7136 → 0.7222, +0.0086 (0.0170) n.d. | 0.2791 → 0.2872, +0.0081 (0.0591) n.d. |
| without noisy | +0.0073 (0.0100) n.d. | +0.0092 (0.0171) n.d. | +0.0084 (0.0612) n.d. |

- **Mechanism (E):** mostly a crack threshold shift. Crack recall 0.365 → 0.384, precision 0.628 → 0.606.
- **LA contrasts (E):** both arms with LA (C2): +0.0045 (0.0100), n.d. DDeP5 vs A5c-f1+LA (C3): −0.0086, i.e. below the free bias.
- **E1:** crack recall 0.0473 → 0.0465; the scuff + half-cut gap untouched.
- **Decoder change (E, descriptive, runner):** final decoder cosine to the pretrained init 0.090, against 0.072 to a random init (seed 0); decoder conv norm falls from 61.5 / 71.1 to 15.8. Fine-tuning overwrote the pretraining, as the protocol predicted.
- **Disclosed:** the `el_f2` `REVISION` file was written after the runs; it matches the checked-out commit.

### 3.3 CP5: crack copy-paste at 5% (stopped unscored)
- **Library (E):** 20 components (11,978 px; CFVS 13, CSIR 4, BMRK 2, ARTS 1). The one ARTS component is `ARTS_00051_r6_c2` (47 px, contrast 42 GL; `protocol_cp5.md` library section), whose crack px are E-SCDD scuff (doc 17 §5.11). So CP5's only ARTS paste was scuff labelled crack.
- **Decoy gate at 2k: PASS (E).** Crack called on decoy spots 0.0049 for CP vs 0.0076 for A5c (flag: > 2× or > 0.05). On real pastes 0.2125 → 0.2334. 245 of 256 cells (11 skipped symmetrically).
- **Stopped.** s1 and s3 finished; s0 (11,800 steps) and s4 (12,350) stopped at 10:50 IST 30 Oct; s2 cancelled. Not scored; no test opened. The automatic per-run rescore files of s1 and s3 exist, unopened.

### 3.4 Test openings so far
2 (MIM5, DDeP5). Before MIM5's opening coach saw A5c-f1 s0's test crack IoU (0.301) while checking a stdout format (disclosed in `verify_mim5.md`).

---

## 4. Key finding: the house fine-tune erases the deep encoder (30 Oct)

**Measurement (E, `coach_100.md` §0; runner re-derived every cosine to 3 decimals, `protocol_100.md`, `el_f3/reports/f100/enc_cosine_rederive.json` md5 89ed1365).** Per-tensor cosine between final (step 20,000) and initial encoder conv weights, averaged per ResNet-34 stage. Read on gaint CPU at about 10:20 IST.

| Stage | MIM moved it: cos(MIM, ImageNet) | A5c-f1: cos(final, ImageNet) | MIM5: cos(final, MIM init) | SUP100 `p6_L3` s0: cos(final, ImageNet) | SUP100 s0 vs s1 (finals) | Norm final/init (SUP100) |
|---|---|---|---|---|---|---|
| conv1 | 0.996 | 0.980 | 0.976 | 0.985 | 0.997 | 0.86 |
| layer1 | 0.859 | 0.379 | 0.327 | 0.396 | 0.623 | 0.75 |
| layer2 | 0.761 | 0.135 | 0.139 | 0.150 | 0.223 | 0.60 |
| layer3 | 0.618 | 0.010 | 0.005 | 0.018 | 0.037 | 0.09 |
| layer4 | 0.533 | −0.001 | −0.000 | 0.001 | 0.007 | 0.06 |

- In every fine-tune, including SUP100 at 100% labels, layer3/4 end orthogonal to their init, and to each other across seeds. Their norms fall to 2 to 9% of init (coach; runner's stage-concatenated L2 gives slightly different ratios by definition).
- Only conv1 and part of layer1 carry any init into the final model. The deep ImageNet features are re-learned from labels, and so were MIM's.
- This explains MIM5's null: MIM changed mostly layer2 to layer4 (cosine to ImageNet 0.53 to 0.76), exactly what fine-tuning wipes.
- **It happens early (E, `protocol_100.md` v1.1 gate table, from `el_f3/reports/f100/smoke/GATES.txt`; coach's re-check in `review_100_v1.md`).** In the house-recipe smoke a1 (SUP100-g s0 at 100%), layer3/4 are already at cosine 0.070 / 0.003 to ImageNet at step 2,000, while their norms are still 0.33 / 0.21 of init (conv1 0.997, layer1 0.731, layer2 0.444). So the direction is lost within the first 2,000 steps (warmup and peak lr), before the norm collapse seen at 20k; it is not a slow drift.
- **Under PF (E, smokes, training only):** layer3/4 cosine to init 0.996 / 0.997 (SUP100-PF) and 0.998 / 0.999 (MIM100-PF) at 2k, and 0.975 / 0.985 and 0.986 / 0.990 at 4k. No test number is involved.
- **Mechanism (S):** conv weights followed by BatchNorm are scale-invariant. The 2k reading says the direction is lost first, during warmup and the peak lr, and coupled L2 shrinks the norms afterwards. coach's first reading ("norm decays, then the direction randomises", `coach_100.md` §0) is superseded on the order of events. Not tested by a one-change arm.

**Consequences (coach, `coach_100.md` §0; `coach_strategy.md` §1)**
- Every "init / pretraining / backbone does not help" result so far was obtained under this one never-varied optimizer: P15 (UCF-EL encoder), MIM5, DDeP5, Track M R3 (ResNet-50; EfficientNet-B4 and ConvNeXt-T pilots). The FINAL members are ResNet-34 SUP100 runs and are erased too (measured on SUP100 s0, s1).
- **Measured vs inferred.** Erasure was measured only on ResNet-34 U-Net++ runs (A5c-f1, MIM5, SUP100). That it also erased P15's UCF-EL encoder and the R3 encoders is likely but not measured (S). For ConvNeXt (LayerNorm, not BatchNorm) the mechanism is not established.
- Dated qualifiers were added next to these claims in docs 00, 01, 05, 10, 11, 13, 15, 16 and 18.
- Track D found frozen ImageNet ResNet-50 / ConvNeXt features rank BMRK crack better than our fine-tuned encoder (doc 18 §D1). PF keeps such features; the house fine-tune does not.
- New house rule proposed by coach (`coach_strategy.md` §3 rule 1): every init or pretraining result reports the final-vs-init encoder cosine per stage.
- The test is protocol_100's SUP100-PF and MIM100-PF arms (§7).

---

## 5. Why 5% was the wrong test (`diag`, 30 Oct)

**The user (30 Oct ~10:45):** "why 5%? I asked about adding the pool to 100% labels." A 5% null need not carry to 100%; it depends on the method. At 5% the defect classes are too scarce. CP5 was stopped at 10:50 and the work replanned at 100% (doc 12 D45).

**What the labels give each method (E, `diag_5pct_to_100pct.md` §1; "recount" = diag's local count)**

| | 5% (23 cells) | 100% (478) |
|---|---|---|
| crack cells (recount / server) | 8 / 9 | 203 / 209 |
| crack components ≥ 20 px (recount) | 37 | 850 |
| CP library after filters | 17 (server 20) | 556 (non-twin) |
| inactive cells | 2 | 41 (server 42) |

[Discrepancy: diag's 556 non-twin components (70 ARTS) come from scout's stats script (`scripts/scout/cp_library_stats_out.txt`). `protocol_100.md` v1 counted 566 (ARTS 68) from the library build at e544133 with only the twins excluded. The frozen v1.1 library, after also excluding the 6 scuff-as-crack cells, has **554 components** (ARTS 67). The v1.1 figure is used in §7.]

**Power (E, §2):** 100% is better powered, not worse. 80%-power MDE, clean: crack IoU 0.012 at 100% vs 0.019 at 5%; inactive 0.032 vs 0.084. Only 2 training cells have inactive at 5%, so the 5% inactive nulls say nothing.

**Per method (§4)**

| Method | Does "null at 5% ⇒ null at 100%" hold? | Main reason |
|---|---|---|
| Copy-paste | No: 5% is the wrong test | Its dose is labels: the library grows from about 20 to about 560 components. Positive at every COCO fraction (R doi:10.1109/cvpr46437.2021.00294) |
| DDeP decoder init | Holds (strong) | The paper's gain falls to +0.3 to +1.3 at full labels (R arxiv:2205.11423), and our fine-tune overwrote the decoder |
| MIM encoder init | Holds only for the house recipe; unknown under an encoder-preserving fine-tune | MIM5 only tested conv1/layer1 transfer, because layer2 to layer4 were erased (diag's addendum after §4) |
| Pseudo-label SSL | Holds for gains; fails for scarcity artefacts | BsM crack +0.029 / +0.012 / −0.006 at 5 / 10 / 20%; joint-BN MT n.d. at 5% but passed at 10% (a handicap that grows as labels shrink) |

**Rule (S, diag §4):** "null at 5% ⇒ null at 100%" is safe only if (1) the method does not consume labels and (2) the 5% estimate is tight on crack. MIM and DDeP met both under the house recipe; CP meets neither; inactive never meets (2) at 5%.

**Addendum (diag, after §4).** The MIM "holds" verdict stands only for plain MIM100 under the house recipe. MIM under PF is unknown at both 5% and 100%. diag retracted its "don't lower the encoder lr" advice; wd 0 is the operative part of PF (S).

**Saved as feedback memory (session record §5):** pool ideas are tested on top of 100% labels unless the user asks otherwise.

**In general: SSL gain falling as labels rise (answer given to the user, session record §6).** A gain shrinking to zero is normal: labels now supply what the pool stood in for. A gain turning negative means the unlabelled signal fights the labels: noisier pseudo-labels, a loss weight tuned at low labels, fewer labelled passes, joint BN, pool vs test mismatch, or pretraining erased by the fine-tune. Diagnose in order: (1) beat seed noise (MDE about 0.012 crack at 100%); (2) the SSL pipeline with the unlabelled loss at 0; (3) sweep the unlabelled weight on val; (4) score pseudo-labels against real labels per class; (5) compare with a matched crack bias (LA); (6) per class and per source; (7) for pretraining, the weight cosine to init.

---

## 6. Coach's strategy for the goal (30 Oct, `coach_strategy.md`)
The user asked coach to lead as a scarce-data expert (log 30 Oct ~11:00).

**Diagnosis (E):**
1. Labels dominate everything measured. Label revision +0.082 crack (P14); 50% → 100% +0.026 on the clean set (0.448 → 0.474); every pool method null from 20% up.
2. The fine-tune discards pretrained deep features (§4).
3. The misses are context, not capacity: E1 half-cut + scuff (75% of crack, 0.13 found); in-split misses concentrate in BMRK and non-twin CFVS.
4. Evaluation: clean MDE crack 0.012, relF1 0.013, inactive 0.032.

**Ranked plan (S):**
- **A. Fix the fine-tune** (in flight: protocol_100 SUP100-PF; R arxiv:2202.10054 on full fine-tuning distorting pretrained features). If SUP100-PF passes or shows a same-sign gain on clean cells: **A2** ResNet-50 and ConvNeXt-T under PF; **A3** a weight average of the 5 PF seeds (model soup, R arxiv:2203.05482). If n.d. or worse: close the init/backbone/pretraining line "with a better reason than before".
- **B. Use the pool to choose what to label.** B1 label audit (§8.1), B2 pool mining (§8.3), B3 scuff policy (§8.4).
- **C. Thin-structure crack loss** (Skeleton Recall, R doi:10.1007/978-3-031-72980-5_13; clDice the alternative) at 100% on the best recipe, for relR@2 ≥ 0.90.
- **D. Inference-only E1 checks:** BN re-estimation on pool half-cells; ResNet-34 + ResNet-50 ensemble members.
- **Stop:** further pool representation learning (contrastive, clustering, diffusion, DDeP), pseudo-label SSL at ≥ 20%, and 5% screens of label-consuming methods.

**Methodology rules coach would add (§3):** report encoder cosine to init for every init/pretraining result; test a method at the label fraction where its mechanism lives; an MDE gate before any 5-seed arm; one best-recipe track combining components that passed alone; human review time is a resource like GPU time.

---

## 7. protocol_100 (design, gates and timing; no results yet)

**Status (E, `protocol_100.md` v1.1, `review_100_v1.md`, `log.md` 30 Oct 12:02 to 12:22).**
- v1 (md5 200a6734) was APPROVED by coach conditional on gates 1 to 7 and one change, G5. v1.1 (md5 8dcb231b, 12:02 IST) adds the gate table, the frozen CP100 library, the launch settings and the two openings.
- Gates 1 to 5, G5, F2-100 and 7 pass (table below); coach re-diffed the identity gates independently. Gate 6 (CP100 decoy) FLAGGED.
- **Launched 30 Oct 12:05:34 IST** on gaint (tmux `f100`): the 15 fine-tunes (SUP100-g, SUP100-PF, MIM100-PF). CP100 jobs come last in the queue and wait for `reports/f100/CP_GO` or `CP_STOP` (gate 6b, below). At 12:22 IST the gate-6b decision was still pending.
- **No arm has a result. Do not quote or predict one.**

**Setup.** All 478 train labels, 20,000 steps, batch 8, final weights, 5 seeds (0 to 4) per arm, all on gaint (cv02 at 10:51 IST: 0 of 8 GPUs qualified). Deploy commit `el_f3` e544133 (suite 285 passed, 3 skipped). Base opts = Track M SUP100 (train.txt md5 842f27c4). Launch settings (v1.1): val only at step 20,000 (`training.val_every=20000`, after gate 4), at most 3 concurrent runs, no expandable_segments (gate 7), start gates 9,000 MiB (fine-tune) / 11,600 MiB (CP) with 120 s spacing under a lock, rc captured before `$(date)`.

| Arm | Change vs SUP100-g | Runs |
|---|---|---|
| **SUP100-g** | none: fresh SUP100 on gaint at the deploy commit (the cv02 seeds are other hardware and commits) | `f3_SUP_100pct_s0..4` |
| **SUP100-PF** | encoder-preserving fine-tune (§0) | `f3_SUPPF_100pct_s0..4` |
| **MIM100-PF** | PF from `encoder_final` (md5 1c3df959) | `f3_MIMPF_100pct_s0..4` |
| **CP100** | house optimizer; copy-paste stream λ 1 from all train cracks onto pool backgrounds | `f3_CP_100pct_s0..4` |

**Contrasts**
1. Pool via the encoder: MIM100-PF − SUP100-PF. The direct answer to the user's question.
2. Recipe: SUP100-PF − SUP100-g.
3. Pool via copy-paste: CP100 − SUP100-g (C1, τ 0), with C2 (both arms LA τ 1) as co-condition for a crack claim; C3 (CP100 τ 0 vs SUP100-g + LA) reported.
4. Reported, not a verdict: MIM100-PF − SUP100-g.
- Rule 1 /3, both verdict sets. Kill: n.d. on all three in both sets, or WORSE on any, closes that contrast at 100%.
- On a pass: the arm's 5-seed mean-softmax ensemble vs its same-machine comparator's ensemble, crack bias by FINAL's rule (max val relF1@2, val precision drop < 0.05, TTA off), paired image bootstrap. FINAL 0.492 is descriptive only.
- Multiplicity: 3 contrasts × 3 primaries × 2 sets (+ CP C2), no correction, disclosed.

**Dropped (S, coach and diag):** DDeP at 100% (fine-tuning overwrites the decoder; the literature gain at full labels is below our MDE); plain MIM100 (it would test only conv1/layer1).

**CP100 library (E, `protocol_100.md` v1 and v1.1; session record §7)**
- 591 components from all train cells, against 20 at 5%. With the 7 D7 twins excluded (their cracks are test cracks; 25 components, 18% of library px): 566 components, 151,993 px (v1).
- On 30 Oct 11:11 to 11:19 coach found 6 train cells whose E-SCDD scuff is labelled crack (doc 17 §5.11). They were added to the exclude list before the CP smokes: 13 stems, list md5 903293c9.
- **Frozen in v1.1:** from 465 cells, 816 candidates, **554 components kept, 151,039 px (CFVS 302, CSIR 164, ARTS 67, BMRK 21)**; kept-list md5 a326dffd (`el_f3/reports/f100/smoke/cp100_library_kept.tsv`). BMRK's 21 is a disclosed limit. The 566 / 151,993 figure is the count before the scuff exclusion.
- The star cell `CFVS_00024_r3_c3` (54 px of E-SCDD "star" labelled crack) stays in the library: meaning undefined, 0.04% of library px; it stays on the review list.
- Measured paste rate (smoke): 516 crack px per pasted image × batch 4 = 2,064 px per step, 0.45 × the labelled 4,549 (≥ 0.4), so cp.batch 4 is confirmed.
- Backgrounds: the pool part of `mim_pool_v11.txt` only (11,219 cells); the 256 monitor cells for the decoy control only. λ 1, cp.batch 4 (labelled stream 4,549 crack px per step, under the 12k trigger), K ~ U{1,2,3}.

**Gates before launch (all at e544133 on gaint)**
1. I1-100: no switch, bit-identical loss/lr/val lines to `el_m` 1be64e1 for 1,000 steps.
2. PF neutral + `encoder_init=mim_step0` identical to no switch.
3. CP λ 0 identical to no switch.
4. Val-off identity (speed-up): loss/lr lines bit-identical for 2,000 steps, house and CP opts.
5. **G5 (coach's change):** SUP100-PF and MIM100-PF smokes to 4,000 steps; per-stage cosine of layer3 and layer4 to their init ≥ 0.8 in both. Fallback, pre-specified and val-blind: lr_mult 0.03, re-smoke to 4k; if that also fails, stop and report that PF is not preserving.
6. MIM encoder md5 in the log; CP smoke and decoy go/no-go at 2k vs SUP 2k.
7. Optional 4th lane: `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` bit-identical for 1,000 steps and reserved memory per fine-tune ≤ 5.5 GB.

**Gate results (E, `protocol_100.md` v1.1 gate table; coach re-diffed gates 1 to 4 and 7 independently, `review_100_v1.md`)**

| Gate | Result |
|---|---|
| 1 to 4 (identity, PF neutral, CP λ 0, val off) | IDENTICAL (22 lines each for 1 to 3; 40 / 40 step lines for 4) |
| 5 (PF at 2k, layer3/4 ≥ 0.5) | SUP100-PF 0.996 / 0.997, MIM100-PF 0.998 / 0.999: PASS |
| G5 (PF at 4k, layer3/4 ≥ 0.8) | SUP100-PF 0.975 / 0.985, MIM100-PF 0.986 / 0.990: PASS; lr_mult 0.1 kept, fallback not needed |
| F2-100 (MIM encoder md5 in the log) | PASS (1c3df959) |
| 6 (CP decoy at 2k vs SUP a1) | SUP 0.0031, CP 0.0076 (2.45×; flag line 2×), both below 0.05: **FLAG** |
| 7 (4th lane) | identity OK, but reserved 6,442 MiB per fine-tune > 5.5 GB: **no 4th lane** |

**Gate 6b (coach's post hoc amendment of gate 6, disclosed as such; `review_100_v1.md`).** One more pre-specified data point, decided before any CP100 run and before opening 1: resume the SUP and CP smokes from 2k to 4k and rerun the same decoy (248 held-out cells, 553 components). CP_GO only if all three hold at 4k:
1. CP decoy ≤ 0.05;
2. CP decoy ≤ 2 × SUP decoy, or CP decoy ≤ 0.0094 (1.25 × its 2k value), i.e. the ratio passes or the rate is not growing;
3. CP decoy / real ≤ 3.6% (the A5c 5% reference; added by coach before the 4k numbers).

Otherwise CP_STOP: CP100 is closed at its gate and opening 2 is not run. The CP100 verdict rule (C1 + C2, two sets) is unchanged. Coach's reasoning: the decoy test is a futility and safety gate (test cells hold no pastes), and at 100% the SUP baseline is more selective (decoy/real 1.1% vs 3.6% for A5c at 5%), which makes the 2× line stricter than at 5%. Status at 12:22 IST: pending.

**Speed-ups (coach, `coach_100.md`).** bf16 autocast is already on everywhere. Val only at start and end, if bit-identical (about 5 to 10%; gate 4 passed, so used). A 4th lane only through the allocator (gate 7: not used). No TF32, channels_last, `cudnn.benchmark` or torch.compile: they would sit under the optimizer contrast.

**Power and pre-stated expectations (S, `protocol_100.md`).** Clean MDE crack 0.012, inactive 0.032.
- SUP100-PF − SUP100-g: crack −0.01 to +0.02, sign uncertain.
- MIM100-PF − SUP100-PF: unknown under PF.
- CP100 − SUP100-g: crack 0 to +0.015 at τ 0, n.d. likeliest after LA; crack precision −0.01 to −0.03.

**Order and timing (`protocol_100.md` v1.1).** Seed-matched waves of the three fine-tune arms first, then CP100 (if CP_GO) two at a time. Launched 12:05:34 IST 30 Oct; the first run (`f3_SUP_100pct_s0`) started 12:08:34. v1.1 ETA: fine-tune waves about 11.5 to 12 h, so opening 1 about 00:00 to 01:00 IST 31 Oct; CP100, if GO, about 6.5 h more, so opening 2 about 07:00 IST 31 Oct. (The session record's earlier estimates, about 01:00 and about 07:30, predate v1.1.)

**Two test openings (pre-registered in v1.1; coach and team-lead, log 30 Oct 11:13, 11:18).**
- Opening 1: the 15 fine-tunes, scored together when all 15 trained with rc 0 (`el_f3/reports/f100/post_opening1/`).
- Opening 2: CP100 (if run) when its 5 runs trained with rc 0, reusing SUP100-g's opening-1 per-cell files unchanged (manifest re-checked), plus the E3b decoy at 20k and crack px on crack-free cells (`post_opening2/`).
- Conditions: no per-run scoring; CP100 is never stopped, re-ordered or re-parameterised on opening-1 numbers; the CP_GO / CP_STOP decision uses the decoy evidence only and is made before opening 1; no protocol_100 change after opening 1.
- v1 and the first review said one scoring pass after all 20 runs; v1.1 replaced that with these two openings.

**Reported, never changing a verdict:** four cell sets, per source, per class, crack capture, mIoU_rob, bootstrap, LA τ 1 for every arm, E1 split scuff + half-cut vs other, crack px on crack-free cells, the CP decoy on the 20k checkpoints, and the encoder cosine table at 2k and 20k for all four arms.

---

## 8. Label work (30 Oct)

### 8.1 B1: label audit of train (done; `b1_audit/`, MANIFEST 10 files md5 OK)
- **Question.** Which train masks might be wrong? Label revision was the biggest effect ever measured (+0.08).
- **Auditors (coach ruling 11:16).** Primary A50: the five 50%-label models `p16_A_50pct_s0-4` (house recipe, `masks_escdd`) on the 239 train cells each never saw, plus the 54 val cells as a base rate. Secondary A20: `sl_20pct_s0-4` (legacy recipe on old `masks_coded`), a column only, because it mostly flags the label revision. (`coach_strategy.md` first proposed `sl_20pct` as primary.)
- **Flag rule.** All 5 auditors confident against GT. Missed-label (ML): all 5 give p ≥ 0.9 where GT says otherwise, components ≥ 20 px crack / 200 px inactive. False-label (FL): a GT component every auditor misses (relaxed recall@2 < 0.1 and mean p < 0.1). Never flagged: frame/padding, scuff/star px, 2 to 3 px edge jitter.
- **Results (E, `b1_audit/b1_coverage.txt`; A50, 239 of 478 train cells)**

  | Flag | Cells (per 100) | Px | Components |
  |---|---|---|---|
  | train crack FL | 15 (6.3) | 4,771 | 26 |
  | train crack ML | 10 (4.2) | 548 | 15 |
  | train inactive FL | 9 (3.8) | 13,725 | 19 |
  | val crack FL (base rate) | 9 (16.7) | 686 | 11 |
  | val crack ML | 2 (3.7) | 57 | 2 |

  Crack flags in 24 cells in all (10.0 per 100). Train is not flagged above the reviewed val set, so many flags will be hard real cracks. The uncovered half of train probably holds about 24 more crack cells and 9 inactive (S, session record §8).
- **Sheets sent to the user (11:37 IST):** `b1_sheet1_crack_top30.png` (24 panels), `b1_sheet2_inactive_top10.png` (9), `b1_sheet3_S_train.png` (15 scuff/star cells). Mark each panel: label error / true hard case / unsure. No mask changes until then; fixes go to a new mask version (`masks_escdd_v2`) with a change list, never to val or test without a separate decision.

### 8.2 Scuff label facts (E, raw E-SCDD vs `masks_escdd`)
Full facts in doc 17 §5.11. In short: 12 train cells carry scuff (3,246 px); our masks label 649 of those px crack in 6 cells, including the 5% "ARTS crack cell" `ARTS_00051_r6_c2`; 2 test cells hold 236 scuff px labelled crack; the star cell `CFVS_00024_r3_c3` has 54 star px labelled crack.

### 8.3 B2: pool mining (running on gaint CPU since 12:09 IST 30 Oct; tmux `b2`)
- The user: candidates only; labelling decided later.
- **Proposer:** the FINAL members (rank-averaged scores: predicted crack, largest component, dark-streak count).
- **Validation first,** on out-of-fold train cells, with positives = train cells whose raw E-SCDD mask has scuff: scored with the A50 models (239 cells) as primary and the A20 models (383) as secondary.
- **Candidates: 100 pool cells** from the pool part of `mim_pool_v11` (11,219 cells):
  - 70 half-cut cells, at most 10 per module. All are CSIR, from 7 modules (297 to 299, 301, 333 to 335): low diversity, disclosed;
  - 30 full cells, at most 3 per module and 40 per source.
- Output: contact sheets for the user.
- Sources: `log.md` 30 Oct 11:12, 12:09, 12:10 (coach's B2 rulings); session record §8.

### 8.4 B3: scuff as its own class (user decision; `spec_b3_scuff.md`)
- **Design.** 25 classes; masks `masks_escdd_s` set the raw scuff px to a new class 24 in the 12 train cells only (the 649 crack px stop being crack; disclosed). Predicted scuff maps to background for the 24-class metrics. BEST vs BEST+S, 5 v 5, after protocol_100 on its winning recipe.
- **Labels.** None new for v0. Thin: 12 cells, 0 half-cut cells. B2 labels would make it a real test.
- **Expected (S, spec §5).** Test primaries n.d.; E1 crack-on-scuff false alarms −20 to −60%; E1 scuff + half-cut recall −0.02 to +0.03; E1 crack precision +0.01 to +0.04. With 20 to 40 mined cells labelled, E1 scuff-group recall +0.03 to +0.12.
- **Open user decision (spec §4).** (a) keep test GT (236 scuff px as crack) for the verdict, coach's recommendation for comparability; (b) also report a test version with those px ignored, descriptively. Test masks are untouched now.

---

## 9. Incidents
Listed in `13_problems_pitfalls_open_issues.md` D20 to D27 and A15: the recurring `rc=$?` after `$(date)` bug, a relative log path, a simultaneous-start memory race, log timestamps ahead of the clock, the cv02 gate-parse bug, the shared HOLD file, the laptop reboot, and gaint test masks differing from cv02 at 2 cells.

---

## Related docs
- `18_experiments_trackD_trackM.md`: Track D, Track M, FINAL, the 27 Oct synthesis.
- `11_results_synthesis_and_claims.md`: rows 22 to 24 (pool feature learning at 5%, encoder erasure, the 5%-to-100% rule).
- `12_decisions_log.md`: D44 to D50.
- `13_problems_pitfalls_open_issues.md`: C14, C15, D20 to D27, E18 to E22.
- `14_code_and_infrastructure.md` §1.2b: gaint worktrees `el_f1`, `el_f2`, `el_f3`; memory rule; run_one locks; two-opening scoring.
- `15_status_remaining_work.md` §1f, §3b, §4b.
- `17_escdd_dataset_audit.md` §5.11.
