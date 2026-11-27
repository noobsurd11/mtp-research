# AUDIT_REC_pseries: independent check of chapters/app_pseries.tex (27 Nov 2026)

Scope: every number, count, date, verdict and interval of the appendix, checked against the primary file, not the NOTES quote.
Primary files read in full: results/{p1,p2,p3_label_versions,p4_feature_probe,p5_region_pl,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,
p17,p18,e1,ema_check}/README.md, results/p6/p6_rules.txt, results/p7/p7_rules.txt, results/p8/p8_rules.txt, results/sk1/sk1_rules.txt,
results/sk1/la_sa.md, team_2026-10-21/alhvr/results.md, team_2026-10-21/data/decision.md, team_2026-10-21/README.md,
results/al1/launch.log, team_2026-10-21/alhvr/log.md; handbook docs 07, 08, 09, 10, 12 only for lock times, protocol content and
items that have no README (audit, SK1 setup, P17 setup). 27 of these files are md5-identical on the server (canonical) and the laptop.
Main-text checks: THESIS_TABLES.md T21 and conventions, ch01, ch04, ch05, abstract.

Line numbers below are of the edited file.

## CHANGES

| file:line | old | new | evidence (path:line, quoted) |
|---|---|---|---|
| app_pseries.tex:16 | "P1 to P5 used the 20211104 masks (v0 ...)" | "P1 to P5 examined models or probes trained on the 20211104 masks (v0 ...)" | results/p5_region_pl/README.md:8 "Crack (14), revised labels"; results/p3_label_versions/README.md:6 "Scored on our own test (50) and val (54) stems" (both versions); P3 to P5 scored on revised masks |
| app_pseries.tex:31 | "threshold in brackets" | "threshold in parentheses" | every table and sentence of the .tex prints thresholds as "(0.0131)"; brackets carry the 95% intervals |
| app_pseries.tex:41-44 | "... the replication arms of P12 and all of P15 used the second machine. Seeds ... never pooled, and a rule never compared arms across machines." | "... the replication and calibration arms of P12 and the six fine-tuning runs of P15 used the second machine (P15's pretraining run used the training machine). ... no verdict rule compared arms across machines; the P12 calibration contrast compared the two machines' supervised arms on purpose and decided nothing." | results/p15/README.md:6 "**Pretraining** (cv02, one run, `p15_ucf_pre_dlv3p_r34`"; :10 "**Fine-tuning** (gaint, RTX PRO 4500): 6 runs"; results/p12/README.md:8 "gaint gA10 (rule 7, calibration): 3 runs"; :49 "gA10 − L3 10% (rule 7, calibration) \| +0.004 (0.010) ... n.d." |
| app_pseries.tex:90-91 | "(47 cells, 2,000 steps, two probe seeds, pooled validation and test cells, revised labels)" | "(trained on 47 cells with the old masks, 2,000 steps, two probe seeds; scored on pooled validation and test cells with revised labels)" | results/p4_feature_probe/README.md:4 "linear 24-class probe on 47 images (`labeled_10pct`, seed 0), old labels" |
| app_pseries.tex:100 | "covered only 8\% of labelled crack" | "covered only 8\% of ground-truth crack" | results/p5_region_pl/README.md:18 "recall of all GT crack 0.08"; :40 "covers only 8% of GT crack" |
| app_pseries.tex:176 | "and the tolerant arm's rare-class pseudo-label share stayed at 0.001 to 0.002" | "and in that seed the tolerant arm's ..." | results/p10/README.md:95 "stays at 0.001–0.002 from step 4,000 in seed 2, against 0.007–0.009 in seeds 0–1" |
| app_pseries.tex:231 | "loss ratio at step 20,000 from 0.46" | "loss ratio at step 20,000 (seed 0) from 0.46" | results/p13/README.md:124 "At step 20,000, s0, the unlabelled / supervised loss ratio is" |
| app_pseries.tex:247 | "the revised-label model still won" | "still scored higher" | results/p14/README.md:65-70 (no rule applied to the old-label scoring: "L3 \| 0.351±0.001", "L3o \| 0.332±0.004") |
| app_pseries.tex:262-263 | "Part A ... locked at 17:28 and Part B ... at 17:35, before any P16 run." | "Part A ... locked at 17:28, before any P16 run, and Part B ... at 17:35, before any P16 SSL run." | results/p16/README.md:3 "Part B (Amendment 1) was locked before any SSL run"; :7 "11 Oct 17:28–22:06 IST" (Part A runs began before 17:35); handbook/10:674, :690 |
| app_pseries.tex:301-302 | caption "label set v1 with four defect types set to ignore" | "the E1 label set of Section~\ref{sec:data-labels} (release 20221008 masks, four defect types set to ignore)" | results/e1/README.md:10 "masks are the release's own (cleaned, like E-SCDD)"; ch04_data.tex sec:data-labels "The E1 set is the release 20221008 masks with class 24 ... mapped to 2 and classes 25 to 28 ... mapped to ignore" |
| app_pseries.tex:331 | "separate-forward SSL lifted inactive on unseen modules most of all." | "... lifted inactive on unseen modules strongly (CsM5 $-$ A5c inactive cell IoU $+0.467$)." | superlative not in any source; handbook/10:1203 "On unseen modules, separate-BN SSL lifts inactive a lot: CsM5 − A5c inactive cell IoU +0.467"; results/p13/README.md:168 |
| app_pseries.tex:359-360 | "a small team in which a reviewer separate from the person running the arms" | "a small team of AI agents in which a reviewer agent, separate from the agent running the arms" | team_2026-10-21/README.md:3 "The leader ... orchestrates four agents"; :27-31 (critic gate); same wording as app_build.tex:309-311 |
| app_pseries.tex:406 | caption "final weights, network A." | "final weights, network A (EMA teacher for BsM5)." | team_2026-10-21/alhvr/results.md:9 "Network A (`model`) for two-network arms and A5, EMA teacher for BsM5" |
| app_pseries.tex:448 | "P10 & 10 to 11 Oct; 5\%; 3; TM" | "...; TM (+SM)" | results/p10/README.md:7 "6 supervised references on gaint (RTX PRO 4500)" |
| app_pseries.tex:485 | "and seven test cells had trained-on twins" | "and the seven test cells of the 21 Oct list had trained-on twins" | team_2026-10-21/data/decision.md:75-88, :103; ch05_legacy.tex:30 gives the later count of 8 same-cell test cells |

NOTES updated: new section "AUDIT 27 Nov" at the end of chapters/app_pseries_NOTES.md lists each edit with its source.

## REMOVED
None as a whole claim. The superlative "most of all" (l331) was replaced by its sourced value (above).

## CONFLICTS (not in my files; for the lead)
1. ch05_legacy.tex:71 reads "SSL helped this model at 5% labels and no gain was detectable from 20% labels up", silent on 10%;
   ch01_intro.tex:70-71 says pseudo-labels "helped only at 5% and 10% labels". The primary record supports a 10% credit:
   results/p11/README.md:38 "Cm − A (rule 3) \| +0.002 (0.012) \| +0.071 (0.067) \| +0.013 (0.012) \| Cm beats supervised (credited:
   rule 2 holds)", with :60-63 "SSL vs supervised is a seed-level pass only" (inactive CI covers 0; relF1@2 robust, :95). The appendix
   (l182-190) matches P11 README and ch01. ch05 is not wrong, only incomplete; T21 has no Cm − A row.
2. Twin test cells: 7 in the 21 Oct list (decision.md:9, :75-88) vs 8 same physical cell + 7 neighbouring crops (ch05:30, from the later
   audit, Section sec:data-split). The appendix now ties "seven" to the 21 Oct list everywhere and points to sec:data-split.
3. E1 extension provenance: the appendix (from results/e1/README.md:47) says the 106 cells come from "67 modules"; ch04 (sec:data-sets)
   counts "71 image ids" / "71 image-id clusters". Different units, no numeric contradiction; left as is.
4. Lock and definition clocks: E1 definitions 12:59 (git, handbook/10:1133) vs "~14:00" (results/e1/README.md:1); amendment 13:16
   (git) vs "~14:15" (README:33). The appendix uses git times, as the handbook does (writer's NOTES conflict 4).
5. Writer's NOTES conflicts 2 (P12 calibration +0.004 vs "within 0.006") and 3 (P6 headroom: results/p6/p6_rules.txt still prints the
   split-mean +0.0256, README:58-61 gives the pooled −0.001 and the correction) confirmed; the .tex is correct on both.

## OPEN
1. main.tex does not \input chapters/app_pseries.tex (only app_t21_note is input after \appendix); the lead must add it.
2. Five \CITE placeholders remain (FixMatch, DINOv2, French et al. 2020, SKCDF, CPS); none of these keys is in references.bib
   (grep: only the DINOv3 entry lists Oquab as a co-author). Listed under MISSING_CITES in NOTES.
3. Machine naming: confirmed. THESIS_TABLES.md:17-19 "Training machine = the RTX A6000 machine ...; second machine = the other machine";
   T21 rows "AL1 (training machine ...)" and "P15 (second machine ...)"; app_build.tex:186 "TM = the training machine (RTX A6000), SM =
   the second machine (RTX PRO 4500)". Sources: cv02 = RTX A6000 (results/p6/README.md:6), gaint = RTX PRO 4500 (results/p10/README.md:7);
   AL1 on cv02 (alhvr/results.md:6), P15 fine-tunes on gaint. The appendix mapping matches T21.
4. Old-pipeline conditions: P1 to P5 carry them in the section paragraph (l59-62: old pipeline, test scored in every run, overlapping
   split as later found, "not valid results") and in the caption of Table pseries-sum1. No pre-7-Oct number is presented as valid.
5. T21 consistency: every value shared with T21 (P3 +0.05 to +0.07; P14 +0.082 [+0.046, +0.129], +0.030 [+0.012, +0.048], −0.004; P6
   +0.020, +0.028, +0.075, +0.135; P11 +0.071 [+0.020, +0.121], +0.018; P12 Dm5 − A5c −0.017 [−0.024, −0.010]; Cs5 − Cm5 +0.084
   [+0.030, +0.143]; P13 +0.117 [+0.042, +0.189], +0.033 [+0.006, +0.055], +0.014 n.d.; BsM5 +0.029 [+0.014, +0.041]; CsM5 − BsM5
   −0.015 (0.018) n.d.; P10 −0.012 [−0.026, −0.001], −0.027; P15 −0.012 / −0.086 / −0.014; P16 n.d. at 20/50/100%; P17 −0.006 / +0.011 /
   −0.008; E1 0.471 → 0.152, 0.80 → 0.41; AL1 −0.0169 / −0.1324 / −0.0312 WORSE in all four sets) agrees with T21, ch05 and the primary
   file. No P-series value appears in the abstract.
6. LaTeX: all 16 \ref targets exist once in the thesis; all 18 labels unique across chapters/*.tex, thesis_tables.tex, main.tex;
   all 10 \citep keys exist in references.bib; no non-ASCII characters, no "--", %/&/_ escaped; array and booktabs are loaded. No host,
   user or path names, no industry partner, no person names other than published authors in \CITE.

Numbers checked against the primary file: all (about 1,000 values: every result, threshold, interval, count, seed set, run count,
date and verdict); lock clock times (P6 11:42, P8 15:43, P11 00:11, P12 01:37, P13 11:51 / 12:51, P14 and P15 12:55, P16 17:28 /
17:35, P17 01:51, P18 17:31, E1 12:59 / 13:16, first commit 7 Oct 23:59, audit 11:24) checked against the handbook's git-commit
records only, since the protocols' own header clocks are known to be early (handbook/10:674, 12 D31). Numbers checked only against
NOTES: none.
