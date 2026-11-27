# Review: severity track S0 to S4

Independent reviewer, 16 Nov 2026, 12:06 to 12:30 IST, on gaint (CPU only, nice 19). I built none of it. Tags: E = measured by me (file given), R = paper or dataset page, S = judgement.
My check files: `/home/noob/work/bench_reads/severity/review/` (`rv_*.py` scripts, `rv_*.out` outputs, `rv_s4_pred_sheet.jpg`, `rv_s3_cells_sheet.jpg`). I changed no tool, no data and no other file.

**Verdict: no item fails. S0 to S4 are PASS WITH NOTE.** Every headline number reproduces from the raw files or the stored outputs. Two readings need a wording fix before they go into the thesis: S4-Q3 (F4.1) and the pooled ELPVPower rho (F3.3).

## Checks common to all items (E)
- Branch bench_sev, 24aa039..f2c795d: 22 files added, 0 changed or deleted; every commit carries the Co-Authored-By trailer; no remote branch; tree clean.
- No `.backward(`, optimizer, `.step()` or `torch.save` in the added code. Nothing was trained.
- No reference to legacy test, E1 or test lists in the added code. S1 reads cv5v2 OOF dumps through `w1read.discover`.
- No external image in the research tree: the only images newer than 15 Nov 21:40 there are split_integrity sheets (our own cells). External crops and sheets stay in `bench_reads/severity`.
- No `bench_sev_*` tmux session is still running.
- Frozen rule copies: the md5 of each frozen file equals its name (S2 971d46d2, S3 cb61fc95, S4 86862318). Sections 0 and 1 of each result file are byte-identical to that copy.

## S0 downloads and licences: PASS WITH NOTE
- E (`rv_s0_md5.out`): `md5sum -c` passes for Polenghi (260 of 260) and ELPVPower (721 of 721). Each set has a README with source, DOI, date, licence as found and file list, plus a publisher sha256 list. Free space on / is now 151 GB, above the 120 GB floor.
- E, licence fields re-read from the stored repository records:
  - Mendeley `data_licence`: short_name "CC BY 4.0". `LICENSE.txt` starts "Legal Disclaimer (CC-BY 4.0)".
  - Dataverse `latestVersion.license` = "CCBY", termsOfUse empty, version 1.3. The README quotes both correctly.
- Notes:
  - (a) The ELPVPower CC BY version is unverified, because the landing page sits behind a bot check. S3 carries the label "analysis only, terms unverified", as it must.
  - (b) The downloads ran with the Bash sandbox off, through the permission system. This is disclosed. The sources (Mendeley, Juelich DATA API, the paper's GitHub) are all allowed.
  - (c) Polenghi's CITATION.txt still holds a placeholder DOI. Cite 10.17632/pxyzzkbs4b.1.
  - (d) The A3 licence (CC BY 4.0) comes from the 4 Nov fact check (`team_2026-11-04_thermal/check/factcheck.md` D-15, figshare API, R). It was not re-read on 15 Nov. Acceptable.

## S1 t5_post_eval on our cells: PASS WITH NOTE
- **Rule before numbers.** BUILD_LOG 21:53:18 has the rule written. The tool commit 637e2ce is 21:56:38 and the run 21:56 to 21:59. There is no frozen copy, so the ordering rests on the log and the md5 statement alone (note). The rule follows T12 section 6 in substance: primary MAE, bands, detection at 0.5%, the D1 thresholds 0.75 / 0.5, the D2 conditions (a) / (b), and the critic's fix (c_phys rule, D1 also on predicted maps).
- **Recomputed (E, `rv_s1_d1.out`):**
  - D1 on GT from T8's own `c_phys.json`, a file independent of `post_eval.py`: 229 crack cells, 48 inactive, AUROC 0.8292, Spearman 0.577. This equals the builder's figure.
  - D1 predicted, cv02 PF, mean of 5 seeds: AUROC 0.708, Spearman 0.394. Equal.
  - Primary, cv02 PF: MAE 0.1224 pp. Equal.
- **Statistics.** Groups are the 330 cv5v2 groups, then seeds. A naive cell bootstrap gives [0.075, 0.178] (`rv_s1_boot.out`), narrower than the builder's [0.066, 0.188], as it should be.
- Notes:
  - (a) The 532-cell MAE is mostly zeros (484 inactive-free cells). The file says so, and the 1.25 pp on inactive cells is labelled post hoc.
  - (b) The rows "contradiction" is a trigger the builder fixed in advance, and it fired inside noise (all |z| <= 0.88). I agree with the builder's reading: keep T5 as an appendix. The lead decides.
  - (c) S1 says nothing about power. The file says so.

## S2 Polenghi staged damage: PASS WITH NOTE
- **Rule before numbers.** The frozen copy is from 22:34:21. The P1 gate text was written at 22:49, before any power number, and P1 is the preparation that is read.
  - Note: section 2 says the P2 gate text of 23:24 was written "before the power step". But `power.json` has mtime 23:23:17, earlier than 23:24 (E). P2 decides nothing, so no number changes. Fix F2.1: reword it to "written after power.json existed; P2 is descriptive".
- **Recomputed (E, `rv_s2.out`, from the raw `ELPV_DATA_FULL.CSV`):**
  - Analysis set: 67 stages (32 + 35), the same as the builder's. L matches the loss column with 0 mismatches.
  - rho(a, L) 0.557, rho(crack, L) 0.647, within-device a 0.306 / 0.715. All equal.
  - My own device-then-stage bootstrap (another seed) gives [0.149, 0.793] and SE of the difference 0.315.
  - The EL images of 0.2_D27 and 0.2_D28 are pixel-identical (confirmed).
- **Statistics.** The unit is the device, n = 2. The file says plainly that intervals are optimistic and stages are dependent. Outcome NULL by the rule.
- **Item 5.** I looked at `gate_sheet_P1.png`. Cracks are drawn, but large dark strips are not called inactive (0.1_D11, D22, D32). The file says this before the power step and in its reading, so it does not read the null on a as evidence against inactive area.
- Open for the lead: the V x I at one low-light operating point substitution (rule 1.1).

## S3 ELPVPower (T12 item 8): PASS WITH NOTE
- **Rule before numbers.**
  - The frozen copy is from 23:32:51. The eye calls of both pilots are from 23:39:42, inference started 23:48:42 and the stats ran 16 Nov 12:04.
  - The decision rule is T12 section 8 in substance: rho >= 0.6 and D > SE(D). Bootstrap over instances.
  - The S137 subset (one first high-excitation row per instance) is a deviation from "per measurement". It was fixed in the rule for CPU budget, with the full set prepared and not armed. Acceptable, because it gives exactly one row per independent unit.
- **Recomputed (E, `rv_s3.out`, S137 and L from the raw `data.csv`, A and C summed from `infer/rows/*.tsv`):**
  - 129 rows, after the 8 auto-fail rows 619 to 644.
  - rho_A 0.873, rho_C 0.885, D -0.013, SE(D) 0.017 (seeds 20261115, 1, 2 give 0.017). All equal. **NULL by the rule.**
  - A Fisher-z check for n = 129 gives about [0.82, 0.91]. The bootstrap [0.80, 0.91] is not narrower.
- Notes:
  - (a) **Gate (b).** The cutter was revised after the rule, while the builder looked at pilot 1. The fresh pilot 2 gives 94.3%, under the 95% line. This is disclosed, and the pooled figure is 96.0%. Every eye-called mis-cut row also fails the automatic check, so the row filter removes them. Acceptable, but the lead should record the gate as "passed on a pilot that was seen while the cutter was tuned".
  - (b) **8 rows dropped against the 7-row line.** Disclosed. A post hoc run with the rows back in gives the same NULL. Lead decision.
  - (c) **Pooled rho is mostly module type.** E (mine): the type order alone (T1 < T2 < T3) gives rho 0.834 with L. The n-weighted mean of the within-type rhos is 0.44 for A and 0.46 for C. The file says "mostly a between-type contrast". **Fix F3.3:** section 3.3 should not say "the PF model's outputs ... carry power information" without adding "pooled, largely by telling heavily cracked T3 from near-clean T1; within T1 rho_A is 0.02". The T3-only D +0.105 is a beside figure seen after the fact, not a result, and the file says this.
  - (d) **Item 5 (transfer before power).** The domain check and the extremes sheet came out of the same stats run as the correlation, so prediction quality was not judged before power. That run was the rule's design. I looked at both, and my own cell-level sheet (`rv_s3_cells_sheet.jpg`: T3 median-A row 525, T3 lowest-A row 579, the two T1 rows with the highest L, worst 4 and 4 fixed cells each). What I saw (S):
    - On T3, dark, fragmented regions are marked inactive and the cracks run along their edges. Mid-grey fragments are often marked inactive too, so the size of a is probably over-called on T3. Rank order is plausible.
    - On T1, dark multicrystalline grain is not called inactive, which is correct. The T1 rows with 13% loss show nothing an EL model should mark, so the T1 null reads as "loss not visible as damage", not as a transfer failure.
    - Under this transfer the correlation measures severity, not only transfer.
  - (e) The licence label is present.

## S4 DTU A3, thermal and power: PASS WITH NOTE (reading fix required before reuse)
- **Rule before numbers.**
  - The frozen copy is from 22:34:02. Discovery ran at 22:37, the QA calls at 22:41:42, inference from 22:43 and the stats at 23:03:41.
  - The QA calls came before any I-V or prediction value was read. The EL dark fractions existed but were not read, as disclosed.
  - The rule keeps pick3b v1's label and bars, and the amendment is dated.
- **Recomputed (E, `rv_s4.out`):**
  - FF from the raw I-V files with my own parser: 31 modules, median FF 0.7633, max difference from the builder 5e-7.
  - The 16 usable non-diode modules give rho(A_seg) 0.903, rho(EL dark) 0.444 and Δrho +0.459. All equal.
  - On all 24 non-diode modules, rho(EL dark) is 0.636. Equal.
- **Statistics.** The unit is the module, which is right. n is small and the file says so.
- **F4.1, the S4-Q3 reading.** The verdict "tracks better" follows the frozen rule, but it is fragile in three ways:
  - (i) **Seed.** The lower bound of the Δrho interval is +0.009 at the fixed seed. On 3 of 8 bootstrap seeds it is <= 0 (-0.009, -0.000, -0.013). An analytic Zou interval with the Bonett-Wright Spearman SE gives [+0.108, +0.982], so the sign is probably real, but the bar is met by a hair.
  - (ii) **Selection tied to the outcome.** Cutting failed on exactly the modules where both FF loss and EL darkness are highest: interconnects M2, M3, M6, M8 (FF loss 3.2 to 11.0%, EL dark 0.023 to 0.045). On all 24 non-diode modules EL dark reaches 0.636. The comparison therefore removed the range where the EL proxy works.
  - (iii) **Narrow label range.** Nine of the 16 modules have FF loss between -0.75% and +0.04%, likely within I-V repeatability (S). The rho of 0.90 is largely crack modules (FF loss about 1 to 2%, A_seg 0.2 to 1.4) against PID and mild interconnect modules (loss about 0). Within cracks, n = 8, it is 0.79 (post hoc).
  - **Exact fix:** in section 4, replace "predicted inactive area per module ... is the better-supported quantity on the one public set where we could test it" with: "On the 16 modules that could be cut (a subset that excludes the four highest-loss interconnect modules, where the EL darkness proxy is strongest), predicted inactive area ranked FF loss better than EL darkness; the interval's lower bound is at 0 and depends on the bootstrap seed. This is a borderline result on a selected subset, not evidence that segmentation beats EL darkness in general."
- **F4.2, item 5 (transfer before power).** The rule had no prediction-quality gate, only a cutting QA (geometry). No prediction sheet existed before the stats. I made one (`rv_s4_pred_sheet.jpg`: the worst cell and cell r2_c5 of each of the 18 cut modules). What I saw (S):
  - On crack modules, cracks are drawn well and isolated dark fragments are marked inactive. Good transfer.
  - On edge and bottom-row cells, inactive leaks in from the black background outside the module: cracks_M7 r5_c0 0.3%, PID_M2 r5_c6 3.9%, PID_M3 r5_c4 3.7%, diode_M4 r3_c0 0.4%. This adds a small false A_seg, mostly to the low-loss PID modules.
  - PID-darkened (shunted) cell regions are partly labelled inactive, which is not the meaning of "isolated".
  - Add these three lines to S4 section 4. They do not change the verdict, because they inflate A_seg on low-loss modules, which works against the observed rho.
- **F4.3.** The cutting QA calls are single-signed (owed item 2). My look at the overlays was not blind, because I had read the calls first, so it is not a co-sign.
- 3b-R1 and 3b-R2 follow their bars:
  - EL dark proxy: label-valid on the non-diode set.
  - S_IR: not a proxy; ΔR2 "in between" with an interval spanning 0.
  - The FF label misses the bypass-diode loss. This is said plainly.
- The LOO ΔR2 interval on all 31 modules (-67.7) shows that OLS is unstable with the diode modules. It decides nothing.

## Final table
| Item | Number (E, reproduced) | Rule | Outcome | May the lead rely on it |
|---|---|---|---|---|
| S0 | 260/260 and 721/721 md5 OK; Polenghi CC BY 4.0; ELPVPower "CCBY", no version | fetched = all files pass publisher checksum; licence quoted from the record | done | Yes. ELPVPower only as "analysis only, terms unverified" |
| S1 primary | PF per-cell inactive MAE 0.121 / 0.122 pp (gaint / cv02) | T12 s6, descriptive | descriptive | Yes, as a descriptive error on cv5v2 pool cells; mostly zeros; 1.25 pp on inactive cells (post hoc) |
| S1 D1 | GT AUROC 0.829, Spearman 0.577; predicted 0.708 / 0.394 (cv02 PF) | >= 0.75 and >= 0.5 on GT and on predicted (both machines) | isolation risk DROPPED | Yes |
| S1 D2 | HOUSE v PF: dMAE z -0.45, dIoU z +0.65 | T12 s6 value test | FAIL: appendix; rows trigger fired inside noise | Yes. Lead rules on the rows note (my reading: appendix) |
| S2 primary | rho(a, L) 0.557 [0.152, 0.795]; crack 0.647; diff -0.09, SE 0.31; 67 stages, 2 devices | rho >= 0.6, low > 0, beats crack by > SE | NULL | Yes as a null on n = 2 that cannot separate measures (stage number 0.91); not evidence against inactive area |
| S3 primary | rho_A 0.873 [0.803, 0.914]; rho_C 0.885; D -0.013, SE 0.017; 129 rows | T12 s8: rho >= 0.6 and D > SE(D) | NULL: severity stays parked | Yes. Pooled rho is mostly module type (type alone 0.834); T3-only D +0.105 is post hoc, not a result |
| S4 3b-R1 | rho(EL dark, FF loss) +0.636 [+0.236, +0.872], 24 non-diode | pick3b v1: >= 0.5 and low > 0 | label-valid | Yes, module level, FF label (misses diode loss) |
| S4 3b-R2 | rho(S_IR, FF loss) +0.192; ΔR2 +0.102 [-0.177, +0.401] | proxy >= 0.5; adds if ΔR2 >= 0.10 and low > 0 | not a proxy; in between | Yes: drone thermal not shown to track or add for these defects; it flags diode and soiling |
| S4-Q3 | Δrho +0.459 [+0.009, +0.991], rho(A_seg) 0.903, 16 modules | Δrho >= 0.10 and low > 0 | "segmentation tracks better" by the rule | Only as "borderline, on a selected subset, seed-fragile" (F4.1). Not as a general finding |

## Fixes and decisions
- Builder fixes (wording only, no number changes): F2.1 (S2 P2 gate timing sentence), F3.3 (S3 section 3.3 sentence), F4.1 (S4 section 4 reading), F4.2 (S4 transfer lines).
- Lead decisions already listed by the builders, which I support:
  - T5 placement: appendix.
  - The S2 electrical substitution.
  - The S3 8-row drop: accept, since the post hoc result is the same.
  - Arming the S3 full set: it adds load stages of 10 T1 instances, not new instances, so it cannot change the reading. Low value.
  - A blind co-sign of S4's cutting QA.
  - A pre-registered within-type test (T3) on fresh rows.
- Reviewer's addition (S): any later "inactive beats crack length" test must be stratified by module type or damage class and pre-registered, because on all three public sets the pooled contrast is driven by which kind of module is damaged.
