# Mid-term deck outline: training methodology (thesis part 1)

Draft of 10 Oct 2026. There are 17 slides. Every number has a **Source** line. Slide 14 is filled with P7/P8 (scored 10 Oct night); P9–P12 results land 11 Oct. Scope: what existed, what we did, what we propose, further work. This is a mid-term, not the finished project.

---

## 1. Title
- *Learning rare, thin EL defects from few, noisy labels*: semi-supervised segmentation of EL solar-cell images (WattCycle MTP).
- Part 1 of 3: training methodology. Part 2 is architecture; part 3 is real-time deployment and severity.
- Mid-term status: diagnosis done, corrected baseline done, method pilot running.

**Speaker note:** One sentence on why: crack and inactive areas drive power loss, and labels are scarce and noisy.
**Source:** title idea from `to_human/directions_2026-10-10.md` §5.

---

## 2. Problem: rare, thin, noisily labelled classes
- Crack is **0.19%** of train pixels. Its label is a median **1.75 px** wide on a visible line about **4.0 px** wide.
- Crack labels sit within ±1 px of the darkest pixel only **48%** of the time. They are dotted along continuous cracks in 22 images.
- Two annotations of the same image agree at crack IoU **0.257**. A perfect mask shifted by 1 px scores **0.47–0.56**. So strict crack IoU mostly measures label jitter.
- Inactive is the opposite: consistent labels (1 px shift 0.89–0.94) but poor generalisation.
- Deployment: about **0.2 s per cell** available. Severity depends on the **inactive (isolated) area**, not crack pixels.

**Figure:** `data_analysis/figs/duplicate_pairs_masks.png` (same cell, two masks) or `data_analysis/figs/crack_overlays_3.png`.
**Speaker note:** Two classes, two opposite failure modes: crack is limited by label noise, inactive by generalisation.
**Source:** `to_human/situation_report_2026-10-08.md` §0–§2; deployment numbers from `to_human/directions_2026-10-10.md` §1.5 (lit).

---

## 3. Data, and a label-revision finding (P3)
- BenchmarkEL `dataset_20211104`: **478 / 54 / 50** train/val/test at 512×512, **24 classes**. The test set was hand-picked by the original authors.
- The newer BenchmarkEL release `20221008` (695 cells) **cleans the crack labels**: dotted labels joined and widened. E-SCDD (HF, MIT; 903 files) redistributes those masks unchanged for crack and inactive; that is where we downloaded them (audit 12 Oct, `results/escdd_audit/README.md`).
- E-SCDD covers **577 of our 582** images. 34 of our 50 test images have a changed crack mask. Crack IoU between versions on test is **0.745**; relaxed (2 px) agreement is **0.98**.
- Re-scoring the same models on the revised labels moves crack IoU by **+0.05 to +0.07**, more than any SSL effect we had measured. SL-100 test AP goes 0.457 → **0.541**.
- From P6 on, we train and evaluate on the revised masks.

**Figure:** none yet. Suggest an old-vs-revised mask overlay for one test cell (missing).
**Speaker note:**
- P3 is exploratory (no locked protocol).
- The cleaning is BenchmarkEL's own `20221008` correction, and how it was made is undocumented.
- The robust signal is the AP ranking change.
**Source:** `literature/notes/A01_pratt2023_benchmarkel.md`; `literature/notes/F04_el_datasets_census.md` §1a; `results/p3_label_versions/README.md`; `to_human/directions_2026-10-10.md` §1.

---

## 4. What existed: EL segmentation and its evaluation
- **Pratt 2023** (BenchmarkEL): best crack median IoU **0.25**, recall **0.86**. Per-image median, background not scored, one run per model.
- **Torpey 2024** (pretraining on EL): COCO **0.544** ≈ CCT **0.550**; in-domain SimCLR **0.517**; **U2PL 0.448 < random init 0.486**. Full labels only, no label-budget curve.
- **PV-S3 (Jha 2025)**, SSL on UCF-EL: never predicts background; released split leaks test into train (1,769 of 2,289); headline 0.828 vs **0.050** under standard IoU (our reproduction).
- **Fioresi 2022** (UCF-EL): validation = test. Our supervised baseline matches or beats its F1.

**Speaker note:** The field has no label-budget curves with step-matched baselines and loss-off controls on EL. That is the gap in evaluation we fill.
**Source:** `literature/notes/A01_pratt2023_benchmarkel.md`, `A02_torpey2024_pretraining.md`, `A04_jha2025_pvs3.md`, `A03_fioresi2022_ucfel.md`; `to_human/situation_report_2026-10-08.md` §4.

---

## 5. What existed: SSL methods, ALHVR as the inspiration
- **ALHVR (ICCV 2025):**
  - Two networks; pixels split by confidence γ into Ω1 (both sure), Ω2 (one sure) and Ω3 (neither sure).
  - Ω3 gets dynamic competitive pseudo-labels (DTCT); Ω2 gets prototype consistency.
  - Premise: value lies in uncertain regions.
- Designed on few-class, large-structure medical data, with no rare-class analysis.
- **Rare-class SSL with evidence:** AEL (tail +10 to +22 IoU), DARS, DHC (Synapse **33.6 → 48.6** Dice). None combines ALHVR-style routing with class rarity, checked to 2026. DCF (MedIA 2026) is the routing baseline a reviewer will ask for.
- Strong encoders shrink SSL gains: UniMatch V2 is about **+3** on Cityscapes 1/16.

**Speaker note:** Our novelty claim rests on searches, not exhaustive coverage. Read DCF and CaPro before claiming the gap.
**Source:** `literature/notes/B01_alhvr2025.md`; `to_human/situation_report_2026-10-08.md` §5; `literature/notes/B05_core_ssl_baselines.md`; `to_human/directions_2026-10-10.md` §1.3, §7.

---

## 6. What we inherited, and why it did not test SSL (P2, audit)
- Earlier result: "Mean Teacher λ = 1.5 equals λ = 0". The loss-off controls were valid.
- **P2 (locked):** our hypothesis that the gradient was wasted on a softmax-invariant shift was **refuted**. The measured share was **0.041** against the predicted > 0.5.
- The real cause: at **100%** of unlabelled pixels the SemiCE target marks ≥ 2 classes as positive, so it is an incoherent target, not Mean Teacher.
- ALHVR port: λ reaches 0.1 only at the last step, while the learning rate decays to 0.
- Side finding: under a correct confidence rule (≥ 0.95), crack is **0.024%** of confident pixels, about 8× under its labelled share. That is rare-class starvation, measured.

**Speaker note:** We report the refuted hypothesis openly. Earlier "unlabelled losses don't help" results were not a finding about SSL.
**Source:** `results/p2/README.md`; `to_human/situation_report_2026-10-08.md` §0.3, §3.

---

## 7. Diagnosis: why crack is not even fitted on training images (P1)
- The pipeline is exact: masks aligned in 10/10 images, and bf16 equals fp32 over 3 seeds.
- **Training augmentation is the biggest factor.** Blur and ±5° rotation on 1–2 px labels take crack AP **0.929 → 0.587** on the training images.
- CE + soft Dice fits crack to IoU **0.861**, against **0.677** for plain CE.
- Fitting is not generalisation. This motivated the corrected recipe in P6.

**Figure:** `results/p1/overlay_E_CFVS_00031_r4_c4.png` (augmentation: dilated fill) against `results/p1/overlay_C_CFVS_00031_r4_c4.png` (CE+Dice).
**Speaker note:** 10 images, 3,000 steps, one run per arm for A, C and E. Only the large gaps are interpretable.
**Source:** `results/p1/README.md`.

---

## 8. Two probes that shaped the method (P4, P5)
- **P4, frozen-feature linear probe (10% labels):** ImageNet ResNet-50 gives crack AP **0.321** and inactive **0.423**, against random **0.029 / 0.097**. DINOv2 is weak on crack (**0.183**) but on par for inactive (**0.384**).
- **P5, pseudo-labels inside ALHVR regions:** Ω3 holds **72%** of GT crack. Crack pseudo-labels there have strict precision **0.27** but **0.64** within 2 px.
- At the confident end (≥ 0.95): **0.59** strict vs **0.96** within 2 px, but this covers only **8%** of GT crack.
- Per-class γ_c moves crack out of Ω3 (**0.72 → 0.32**) but drops r1 precision (strict 0.53 → 0.42). Thresholds alone do not fix routing.
- **Takeaway:** teacher crack pseudo-labels hit the right crack but the wrong pixels. Offset-tolerant targets keep the signal.

**Figure:** missing. Suggest a strict-vs-2 px precision bar chart per region (data in `results/p5_region_pl/README.md`).
**Speaker note:** Both probes were locked before running. They are offline: one labelled split, 2 runs each.
**Source:** `results/p4_feature_probe/README.md`; `results/p5_region_pl/README.md`.

---

## 9. Experiment 1 (P6): corrected supervised baseline, one change per step
- Ladder at 10% labels on revised masks:
  - **L0** old recipe;
  - **L1** + label-safe augmentation (flips/90° only);
  - **L2** + ImageNet ResNet-34 U-Net++;
  - **L3** + CE+Dice.
- Plus L0 at 100%, and L3 at 20% and 100%.
- **21 runs**: 3 seeds each, 20,000 steps, final-step weights, all on cv02 A6000. Protocol locked before any run.
- Primary metric: test crack AP and inactive AP. Rule: Δ > 0.01 and > 2·SE.

| Arm (test) | crack AP | inactive AP | crack IoU | inactive IoU |
|---|---|---|---|---|
| L0 10% | 0.553 | 0.621 | 0.319 | 0.439 |
| L1 10% | 0.574 | 0.649 | 0.368 | 0.473 |
| L2 10% | 0.519 | 0.477 | 0.392 | 0.383 |
| L3 10% | 0.400 | 0.302 | 0.396 | 0.294 |
| L0 100% | 0.545 | 0.612 | 0.337 | 0.391 |
| L3 100% | 0.593 | 0.420 | 0.471 | 0.429 |

**Figure:** `results/p6/fig_ladder.png`.
**Speaker note:** Means over 3 seeds; the sds are in the README, max 0.051 (L0 crack IoU).
**Source:** `protocols/P6_corrected_baseline.md`; `results/p6/README.md`; `results/p6/p6_rules.txt`.

---

## 10. P6 takeaway 1: label-safe augmentation helps; AP is not comparable across losses
- **L0 → L1 (label-safe augmentation) helps both classes:** crack AP **+0.020**, inactive AP **+0.028**. It passes the locked rule.
- **L1 → L2 → L3 "hurts" AP** (crack −0.054, then −0.119), but at the argmax operating point crack IoU rises 0.368 → 0.392 → 0.396 and relaxed precision@2 rises 0.80 → 0.84 → 0.91.
- **Why:** the ImageNet and Dice models score **42%** of GT crack pixels and **65%** of GT inactive pixels below 0.001 (L3 10%). L0 scores 3% and 19%. There they tie with ≥ 98.5% of the background, so AP cannot rank them.
- **The inactive drop shows at every operating point** (IoU 0.473 → 0.383 → 0.294), but it is carried by 3 test cells. Without them it is −0.005 and −0.019. Source: `results/p6/README.md`, exploratory 5.
- **Crack effects survive resampling the test cells:** label-safe crack IoU +0.048, 95% image-bootstrap CI [+0.003, +0.097].

**Figure:** `results/p6/fig_saturation.png`.
**Speaker note:** The metric choice drives the conclusion here. That is why P8 fixes IoU and relaxed F1 as primary before running.
**Source:** `results/p6/README.md` (rule 1 table, exploratory 1); `results/p6/hist_analysis.txt`.

---

## 11. P6 takeaway 2: the old recipe does not use labels; L3 does
- **L0, 10% → 100% labels:** pooled AP **−0.001**; inactive IoU *falls* **0.439 → 0.391**.
- **L3, 10% → 100%:** pooled AP **+0.159**, crack IoU **+0.075**, inactive IoU **+0.135**.
- L3 100% is the best crack model: IoU **0.471**, relaxed F1@2 **0.876**.
- **Apparent puzzle, resolved:** L1 at 10% has a higher inactive IoU (0.473) than L3 at 100% (0.429). Without the top 3 inactive cells the order flips (L3 100% ahead by **+0.088**), so this is not a finding.
- **What survives resampling the cells:** L3's gain from more labels, crack IoU **+0.075** [+0.029, +0.128] and inactive IoU **+0.135** [+0.049, +0.205]. Source: `results/p6/README.md`, exploratory 5.
- **Inactive pixels sit in a few cells** (Source: `results/p6/README.md`, exploratory 4):
  - test: 16 of 50 cells have any; the top 3 hold **59%**; one cell (BMRK_00073) holds **23%**;
  - val: 6 of 54 cells have any; the top 3 hold **89%**;
  - so any inactive difference is effectively decided by about 3 cells (overlay row 3).
- **Inactive is also few-shot on the label side:** only **4 of the 47** labelled cells at 10% contain inactive, and **2 of 23** at 5% (crack: 19/47 and 9/23). Source: `results/p10/labelled_set_counts.txt`.
- Implication: SSL can only close a gap that exists, and only L3 has one.

**Figure:** `results/p6/fig_label_scaling.png`.
**Speaker note:** One split, 50 test images, and the inactive class is dominated by few images.
**Source:** `results/p6/README.md` (exploratory 2, 3); `results/p6/hist_analysis.txt`.

---

## 12. Proposed method: rarity-routed, offset-tolerant pseudo-labels
- A Mean Teacher student on the label-safe strong view; the teacher on the weak view; EMA 0.999.
- **Per pixel of the teacher's prediction:**
  - **Rare class (crack, inactive) argmax, confident or not:** credit the student if p_s[r] is high **anywhere within 2 px**. Loss −p_t[r]·log(max-pool₅ₓ₅ p_s[r]).
  - **Confident (≥ 0.95) head-class pixel outside a 2 px band around rare targets:** ordinary CE.
  - **Everything else:** no loss.
- One mechanism serves both kinds of noisy target: ±1–2 px human jitter and 1–2 px teacher offset (P5).
- Guard against fattening: always report relaxed precision@2 next to any gain.

**Figure (to draw):**
- Left: teacher crack line offset by 1 px from the student's.
- Middle: hard CE penalises both lines.
- Right: max-pool tolerance gives full credit.
- Bottom: three-way pixel routing (rare → tolerant term, confident head → CE, rest → ignored).

**Speaker note:** This is the minimal version (P7 arm C). Full ALHVR two-network region routing is further work.
**Source:** `protocols/P7_tolerant_pl_pilot.md` (arms, "How C routes each pixel"); `to_human/directions_2026-10-10.md` §5.

---

## 13. Experiment 2 design: P7 (pilot) and P8
- **Setup:** 10% labels (**47** images) + **431** unlabelled train images; 20,000 steps; λ ramp 0 → 1 over steps 2,000–4,000; 3 seeds; 9 runs each.
- **Arms:**
  - **B** = hard pseudo-label CE (≥ 0.95);
  - **C** = tolerant (proposed);
  - **D** = C with λ = 0, the loss-off control;
  - **A** = P6 supervised reference.
- **P7:** base chosen by P6 rule 2 on val, which was **L0** (val score 0.480 against L1 0.414, L2 0.396, L3 0.296). Primary: test AP. **Reported as a pilot by locked rule:** L0 headroom is −0.001.
- **P8:** the same arms on **L3**, where the gap exists. The base was chosen after seeing P6, and this is disclosed; the choice applies equally to all arms. Primary: test crack IoU, inactive IoU and crack relaxed F1@2, fixed before running. Report the share of the gap closed, (C − D) / (L3@100% − D).
- **Rules:** C helps if C − D > 0.01 and > 2·SE. C must also beat B, or the claim reduces to "a correct pseudo-label loss helps". Flag C if relaxed P@2 falls > 0.05 against D.

**Speaker note:** The loss-off arm D isolates the unlabelled loss from pipeline changes (stream mixing, BatchNorm). That was our earlier "4+4" confound.
**Source:** `protocols/P7_tolerant_pl_pilot.md`; `protocols/P8_tolerant_pl_on_l3.md`; `results/p6/README.md` (rules 2–3).

---

## 14. Experiment 2 results: no detectable SSL gain at 10% labels, and why
- **Table:** test, revised labels, mean ± sd over 3 seeds. Primary metrics in bold.

| P8 (L3 base, primary: IoU / relF1) | **crack IoU** | **inactive IoU** | **crack relF1@2** | crack AP |
|---|---|---|---|---|
| A: supervised L3 10% | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.400 |
| D: Mean Teacher, loss off | 0.383±0.003 | 0.194±0.034 | 0.796±0.008 | 0.402 |
| B: hard PL (≥ 0.95) | 0.389±0.007 | 0.219±0.081 | 0.806±0.015 | 0.430 |
| C: tolerant PL (ours) | 0.392±0.006 | 0.253±0.109 | 0.811±0.012 | 0.421 |
| L3 100% labels | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.593 |

- **P8 locked verdict:**
  - C − D is +0.009 / +0.059 / +0.015, and no primary passes the threshold. B − D: none passes. C does not beat B.
  - Over test cells, C − D is small but consistent: crack +0.009, CI [+0.002, +0.015]; inactive +0.059, CI [+0.020, +0.109]. Over training seeds it is not separable: seed 0 collapses on inactive with and without the loss.
- **P7 (L0 base, pilot because L0 has no label headroom):**
  - C − D: crack AP +0.000, inactive AP −0.032 (worse).
  - B − D: worse on both (−0.024 / −0.097).
  - **C beats B** on both. On inactive IoU, +0.056, CI [+0.022, +0.086], robust to the choice of cells.
- **Finding 1 (why hard PL hurts on L0):** pseudo-labels push real defect pixels to "certain background". Share of GT pixels scored < 0.001: D 6%/21% → C 9%/28% → B 13%/35% (crack/inactive). This is confirmation bias where the teacher misses a defect. Tolerant routing halves the damage.
- **Finding 2 (an obstacle on L3):** the SSL pipeline with the loss *off* (D) is below plain supervised training (A): crack IoU −0.013, CI [−0.028, −0.001]; inactive −0.10.
  - The cause is not the EMA teacher: the student scores the same.
  - Candidates: the SSL labelled view (stronger jitter plus Gaussian noise), and BatchNorm over mixed batches.
  - C only wins that back, ending where A is: crack IoU −0.004 vs A.
- **Figure:** `results/p8/fig_p8_bars.png` (main); `results/p7/fig_p7_bars.png` (backup).
- **P9, 12k external pool (10% labels), scored 11 Oct:**
  - tolerant PL − its loss-off control passes the locked rule on inactive IoU (+0.056, threshold 0.046); crack shows no difference;
  - same effect size as P8, now with less seed noise;
  - not robust to the choice of cells: +0.026 without the top-3 cells, CI [−0.013, +0.117];
  - tolerant does not beat hard PL; the 28× larger pool does not amplify the effect.
- **P10, 5% labels (23 cells), scored 11 Oct:** no loss passes.
  - In-domain: seed 2 collapses under **both** hard and tolerant PL (crack ≈ 0.13, inactive ≈ 0). Its rare-class pseudo-label share stays about 5× lower from step 4,000, so the collapse is visible in training logs.
  - The two healthy seeds lift the control about +0.06 crack and +0.12 inactive (post hoc).
  - External pool: tolerant PL loses crack (−0.012, CI [−0.026, −0.001]) with wider predictions, concentrated on the pool's own sources (CSIR+ARTS −0.065).
  - The pipeline handicap grows to D5 − A5 = −0.055 crack IoU.
  - Swapping only the unlabelled pool with the loss off moves the control (P9 inactive +0.094; P10 crack +0.032). So batch mixing is part of the handicap.
- **Running now:**
  - P11: matched labelled view at 10%;
  - P12: matched view at 5%, with a cv02 supervised 5% reference and a gaint replication on fresh seeds.
  - First gaint replication seed (tolerant vs loss-off control, 5%, seed 3): crack 0.337 vs 0.270, inactive 0.400 vs 0.249. **One seed; not a result.**
- **Figures:** `results/p9/fig_p9_bars.png`, `results/p10/fig_p10_bars.png` (backup slides).

**Speaker note:**
- The honest result is "no detectable SSL gain at 10% labels with 431 unlabelled cells".
- Two things are learnt: (1) how to use pseudo-labels for rare classes (tolerant beats hard, robustly); (2) a concrete pipeline handicap that the literature's SSL gains may hide.
- The locked rules made both visible.

**Source:** `results/p7/README.md`; `results/p8/README.md` (rules, bootstrap, student-vs-teacher); `results/p9/README.md`; `results/p10/README.md`; `results/p7/p7_rules.txt`; `results/p8/p8_rules.txt`; `protocols/P9_external_pool.md`, `P10_ssl_5pct.md`, `P11_matched_pipeline.md`, `P12_matched_5pct.md`.

---

## 15. Research discipline (and one correction)
- **Every confirmatory experiment's protocol is committed before running:**
  - P1/P2 `f9708c0`, P5 `fdc7198`, P4 `855b130`;
  - P6 `db76a8c`, P7 `37985d6`, P8 `da3d941`;
  - P9 `be69ace`, P10 `9a85958` (amendment `bf745e0`, before its runs), P11 `38de062`, P12 `7320bd4`.
- Loss-off controls, 3 seeds, step-matched runs, final-step checkpoint, base selected on **val**, reported on **test**. Exploratory results are labelled as such (P3, P6 diagnostics).
- Hypotheses refuted and reported: P2 (wasted-gradient), P1 H1 not met as written and H3 refuted, P5 rule 3 not met.
- **Correction:** an interim P6 headroom of **+0.026** averaged per-split APs. The locked rule says pooled pixels, which gives **−0.001**, so P7 is a pilot. Earlier corrections are also on record (the Fioresi 57.3% mIoU claim).

**Speaker note:** With 50 test images and noisy labels, discipline is what makes small effects interpretable at all.
**Source:** `git log -- protocols/`; `results/p6/README.md` (rule 3 correction); `results/p1/README.md`; `results/p2/README.md`; `results/p5_region_pl/README.md`; `literature/notes/A03_fioresi2022_ucfel.md`.

---

## 16. Further work
- **Method:**
  - full ALHVR-style two-network routing with rarity-aware Ω regions;
  - labelled anchoring in Ω3 (the BUR direction);
  - baselines DCF, BUR, DHC and ALHVR.
- **Rivals and ground:**
  - MIM pretraining of the small encoder (no pseudo-labels);
  - train on old labels, test on revised (noise-aware loss);
  - UCF-EL physical-module-disjoint re-split. 25–44% of UCF test cells have the same cell in train, and UCF's label gap is 0.54 → 0.23 from 100% to 1%;
  - ≥ 2 labelled splits.
- **Collapse safeguard (from P10):** rare-class pseudo-label share is a training-time collapse signal. Candidates: per-class quotas or adaptive thresholds that keep it from vanishing, and per-class logging, since the aggregate missed P8's inactive-only collapse.
- **Unlabelled-pool hygiene (from P9/P10):** the external CSIR/ARTS pool hurts crack on same-source benchmark cells. Check capture and preprocessing match before adding a pool.
- **Evaluation for the inactive class:** 16 of 50 test cells and 6 of 54 val cells carry inactive pixels. Inactive needs more cells before any per-recipe claim: a larger test pool, or cross-validated splits. The E-SCDD audit (12 Oct) found that its extra cells add only 10 inactive cells with little inactive area (`results/escdd_audit/README.md` §8).
- **Part 2, architecture:** a ≈5M-parameter CNN student; large models only as teachers. Per P4, a CNN teacher for cracks and DINO-type features for region classes only.
- **Part 3, deployment and severity:** about 0.2 s per cell; severity from inactive area; reward crack connectivity.

**Speaker note:** Each item gets a locked protocol before it runs, as so far.
**Source:** `to_human/directions_2026-10-10.md` §4–§6; `to_human/situation_report_2026-10-08.md` §6.5, §9; `results/p6/README.md` (exploratory 3); `results/p4_feature_probe/README.md`.

---

## 17. Timeline
- **Done (to 10 Oct):**
  - data and label analysis; P1–P5 probes; directions review (literature plus institutional PDFs);
  - P6 corrected baseline (21 runs);
  - P7/P8 SSL at 10% labels (18 runs, scored).
- **Overnight 10–11 Oct (cv02 8 GPUs + gaint):**
  - P9, external pool (9 runs);
  - P10, 5% labels × pool (15 runs, plus 6 supervised references on gaint);
  - P11, pipeline-matched control (12 runs, starts as GPUs free);
  - P12, matched pipeline at 5% (12 SSL + 3 supervised on cv02, after P11; 6 SSL replication + 3 calibration runs on gaint from ~04:00).
- **11 Oct:** apply the locked rules to P9–P12 as each lands (P12 last, evening); fill slide 14's "running now" line; update the overlays with the best SSL arm.
- **12–13 Oct:** deck and rehearsal. **Mid-term:** about 14 Oct (confirm the date).
- **After mid-term:** in order, MIM rival → old→revised label experiment → UCF re-split → full routing method → parts 2–3.

**Speaker note:** The order is cheapest falsifying test first.
**Source:** `results/*/README.md` dates; `to_human/directions_2026-10-10.md` §4 ordering.

---

### Figures
Made on 10 Oct; the source script is in brackets:
- `results/p6/fig_overlays.png` (`scripts_gaint/overlay_figure.py`):
  - 3 test cells chosen by a fixed rule (top-2 by GT crack area, top-1 by GT inactive area);
  - columns: image, old label, revised label, then L0 10%, L1 10%, L3 10% and L3 100% (seed 0);
  - serves slides 3 (old vs revised), 10 and 11.
- `results/p5_region_pl/fig_p5_offset.png` (`scripts/midterm_figures.py`): slide 8.
- `results/figures/fig_method_routing.png` (`scripts/midterm_figures.py`): slide 12. Panel (c) is a toy illustration with student p = 0.9 on its line and 0.05 elsewhere; it is not measured.

Still missing:
- P7/P8 result bars: slide 14, after tonight.
