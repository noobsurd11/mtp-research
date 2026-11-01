# Session record, 31 Oct to 1 Nov 2026: Om's 11 ideas validated, PF2 and PF2E, THIN-B3, HC / A8 / B6 armed

Covers the session after `SESSION_RECORD_2026-10-30_to_31.md` (which stops at 31 Oct ~07:30 IST). Status as of 1 Nov ~20:30 IST.
Team folder: `team_2026-10-31_next/` (brief `README.md`, append-only `log.md`, ledger `e1_openings.md`). Tags: E = measured (file), R = literature (id), S = judgement. "Clean" = the 50 test cells without `CSIR_00070_r8_c4`. Rule 1 = house rule, divisor 3.

## 0. In one screen
- **The ask (31 Oct ~13:45):** the user pasted Om's answers and 11 new ideas (`om_2026-10-31.md`) and said: "read and launch agents to review validate and work on this direction further, no budget boundaries, we have 2 more months to work on this project. but id refrain from manual labelling unless very much needed". Om's diagnosis (S): the remaining failure is domain generalisation to unseen panels (E1), not data quantity.
- **PF2 (replication of PF on new seeds 5-9; E1 opening #1): PASS** (coach `verify_pf2.md`, runner CONFIRMED to 4 dp):
  - E1 inactive IoU 0.0481 → 0.2371 (+0.1890, thr 0.0433) BETTER: **replicated on new seeds, same E1 cells**. E1 crack recall +0.0271 (thr 0.0370) n.d.: **not replicated**.
  - Test crack relF1@2 BETTER in both sets, **narrowly** (+0.0117 / +0.0120 vs floor 0.0100; leave-top-3-out +0.0015). Crack IoU and inactive IoU n.d.
  - **RN50-PF − SUP100-PF: FAIL** (test inactive WORSE both sets, −0.0289, thr 0.0251). RN50 is closed under PF. BEST stays SUP100-PF.
- **PF2E (5-member ensembles, E-PF vs E-g; E1 opening #4): PASS on the E1 inactive co-primary** (+0.2141, module-cluster CI [+0.030, +0.382]); test n.d. (relF1@2 +0.0121, CI includes 0). judge's wording: "fewer false inactive calls on module edges plus twice the inactive recall on E1"; E1 inactive GT is 10 cells in 7 images; borderline under Bonferroni; not an independent replication. **No "matches FINAL" claim** (E-PF 0.4920 clean crack only at a b the pre-registered val width flag rejected).
- **The 11 ideas (judge reviewed all):** PASS to protocol: 5 (synthetic half-cuts → HC), 7 (metrics, in every protocol), 8 (foundation encoder → A8 screen). PARK: 3 + 4 jointly (structure channel), half-cut routing (idea 1). DROP: 2 (intensity; the "brighter E1" is a white letterbox), 6 (high resolution; a repeat of R5), 11 (no appearance arm), TENT (idea 9), label-free per-panel thresholds (idea 1), SAM on cracks (idea 10). Closed by result: **TTA (T9 FAIL)**, **half-cut routing pre-check FAIL**. Method note: **S10** (SAM fills inactive regions, passes its rule at A50).
- **Data facts found:** E1 crack labels are about 1.5x wider than train; Hanifi `_rf` half-cut crack labels are unusable (no labelled half-cut crack set exists outside E1); within E1 strata the failure is ranking, not threshold.
- **User decisions:** E1 = second test set (31 Oct ~15:00); idea 8 weights + screen; idea 10 S10; HC; PF2E with E1 co-primaries; DINOv3 route B with the user's licence acceptance; B6 only on cv02 (1 Nov). §3.
- **Now:** THIN-B3's opening is running (E1 opening #2; results §8, pending verify). Armed behind it: the nq queue (A8 screen + HC runs), A8 scoring, HC opening. B6 locked for cv02 only.

## 1. Timeline (IST)
| When | Event |
|---|---|
| 31 Oct 13:51-13:54 | New team started (`README.md`); builder, calib, domain, found, judge spawned; runner and coach respawned |
| 31 Oct 13:57 | runner commits handbook a076e54 (fix 5: Hanifi B2 cells redacted in sources) |
| 31 Oct 13:58-14:28 | coach writes `protocol_PF2.md`; runner builds and smokes (14:03-14:27); APPROVED 14:28 (md5 58cbc5e2) |
| 31 Oct 14:12-14:15, 14:32 | builder's pytest opens a CUDA context on gaint (254 MiB), §10 |
| 31 Oct 14:13-14:31 | judge reviews ideas 6, 8, 9, 10; Hanifi H36 crack labels ruled unusable (14:23) |
| 31 Oct 14:27 | T9 launched (gaint CPU) |
| 31 Oct 14:29:15 | **PF2 launched** (3 lanes); 14:36 runner commits handbook 4156be7 |
| 31 Oct 14:40-14:53 | ideas 1, 3, 4, 5, 7, 11 reviewed; coach finds a defect in `pf2_post.sh` (gate in a comment), fixed 14:41 |
| 31 Oct 14:46-14:54 | builder's CPU batch computes test and E1-scuff numbers outside an opening; quarantined unread (§10) |
| 31 Oct 14:54-17:30 | usage cap: all agents paused |
| 31 Oct ~15:00 | **User decisions:** E1 = second test set; idea 8 weights + screen; idea 10 S10 (logged 17:31) |
| 31 Oct 17:34-17:38 | ideas 2 and 5 judged; SHV1 synthetic half-cut val set frozen; routing pre-check rule written before any number |
| 31 Oct 17:37 | `e1_openings.md` ledger started |
| 31 Oct 17:41-17:44 | SAM2 weights + sam2 venv on gaint; S10 launched |
| 31 Oct 18:03-18:05 | **routing pre-check FAIL**; PF2 §13 void; S10 PASS (method note) |
| 31 Oct 18:15-18:28 | domain's half-cut detector R1 FAIL, R2b frozen then PARKED; its feature runs included the 50 test images (structure only) |
| 31 Oct 18:04-18:41 | HC built (el_hc), rule_p sources (353), p 0.35 |
| 31 Oct 18:12-20:19 | P8 probe run 1 (CPU) |
| 31 Oct 21:13-21:16 | **T9 FAIL: TTA closed** (judge confirmed) |
| 31 Oct 22:37:43 | PF2 gate 6 PASS (RN50-PF s5 4k cosine) |
| 31 Oct 23:32-1 Nov 00:22 | side queue: B5 bf16 self-check exact (B5 FROZEN 23:35); THIN smokes S0-S4 |
| 1 Nov 00:25-00:38 | protocol_thin_b3 v1 locked; APPROVED 00:38; **THIN-B3 armed 00:38:42** |
| 1 Nov 06:32:22 | PF2 ALL TRAINED (15 rc 0); opening 06:33:18-08:26:14; THIN starts 06:32:46 |
| 1 Nov 07:45:13 | PF2 LA scoring peak 7,758 MiB; min free 2,635 (floor held) |
| 1 Nov 08:30 | **PF2 VERIFIED** (coach); 08:30 THIN opening gate raised to 9,900 |
| 1 Nov 08:34-08:49 | RN named secondary (ensembles at +0.75, val + E1) run and recomputed |
| 1 Nov ~13:15 | **User decisions:** HC yes; PF2E yes with E1 co-primaries; DINOv3 route B; B6 designed (logged 14:27) |
| 1 Nov 14:28-14:30 | PF2E v1, HC v1, A8 screen v1 locked; DINOv3 fetched; P8 run 2 started; B6 v0 |
| 1 Nov ~14:36-18:40 | usage cap: all agents ended; THIN ran unattended on gaint; respawned 18:40 (calib, domain not) |
| 1 Nov 18:42-19:12 | HC smokes H0 (identity 80/80) and H1 |
| 1 Nov ~18:49 | judge tails THIN stdouts (test numbers on screen, not recorded) (§10) |
| 1 Nov ~18:49-18:54 | judge: B6 v0 NOT READY (CFVS twins, power); B6 v1 design locked at judge's sign-off (~18:54) |
| 1 Nov ~19:00 | **User decision:** B6 only if cv02 frees up (logged 19:01); 19:02 never-tail rule broadcast |
| 1 Nov 19:02:04-19:13:10 | **PF2E run** (E1 opening #4); 19:04:56 verdict-b clarified with `out/` empty |
| 1 Nov 19:10-19:15 | laptop memory critical (544 MB available); local watchers stopped; found, builder stopped |
| 1 Nov 19:18-19:21 | **PF2E VERIFIED** (coach) and CONFIRMED with qualifications (judge) |
| 1 Nov 19:20-19:26 | A8 / A8c smokes (300 steps); 19:24 ruling: no test via data root |
| 1 Nov 19:39:03 | THIN-B3 ALL TRAINED (15 rc 0); **THIN opening started 19:40:18** |
| 1 Nov 19:43:42 | nq queue (A8 + HC) armed; 19:54 A8 scoring armed; 20:22:33 HC opening armed |
| 1 Nov 20:19 | `set -e` chained-check finding (runner's helper) |

## 2. Team, rules, infrastructure (changes this session)
- **Roles** (`README.md`): `team-lead` (orchestrates), `runner` (gaint GPU owner, the only agent starting GPU jobs), `coach` (protocols, APPROVED, independent recompute), `builder` (code), `calib` (ideas 1, 2, 7), `domain` (ideas 3, 4, 5, 11, item-13 close-out), `found` (ideas 6, 8, 9, 10), `judge` (adversarial review of every idea, recomputes E claims). calib and domain finished their work 31 Oct and were not respawned after 1 Nov's cap.
- **Pipeline:** idea report in `ideas/<idea>.md` → judge verdict appended → coach protocol → GPU only on coach's APPROVED; non-Om-approved GPU work needs the user's OK (batched by team-lead).
- **Primaries** stay crack IoU / relF1@2 / inactive IoU. Every protocol also pre-registers component recall at component precision ≥ 0.90 and relR@2 at relP@2 ≥ 0.90 (val-chosen bias; Om B5). Cell-level metrics reported.
- **E1 policy (user, 31 Oct ~15:00):** E1 is a second test set. A protocol may pre-register E1 co-primaries, read once at its single opening, never for tuning, selection or thresholds; the paper reports every E1 opening (§9).
- **Selection sets:** val (54) and Hanifi `_rf` after hygiene (117 − 7 CSIR_00300 − 4 val/test-module = 106). Its F51 (51 unseen-module full cells, 12 crack cells, 36 modules) is the `_rf` crack decision set; H36 (36 half-cuts) is for false alarms only (§6.1).
- **gaint:** shared `gpu_gate` (flock, free ≥ peak + 2 GB, ≥ 120 s spacing, HOLD file); per-queue gpumem loggers (10 s, 1 s while scoring); FROZEN.md5 per opening (coach writes it; no file changes after); CPU jobs of other agents pause in runner-declared critical windows (PF2 opening, announced 06:30-08:30; THIN opening, announced ~19:45-22:15, in effect from 19:40:18 until runner's 'window over', ~22:00). Scoring gate GS raised to 9,900 MiB after PF2's measured LA peak (§10).
- **Never tail / cat a training stdout** (team-lead 19:02 1 Nov): the trainer prints an end-of-run TEST block (§10). Grep step lines only.
- **The trainer's end-of-run test pass:** for runs that must read no test cell (A8 screen, B6), a per-run `data.root` whose `splits/test.txt` is a copy of the held-out list (A8: val; B6: the held-out fold). No code change.

## 3. Decisions by the user (and Om), with dates
| When | Decision | Logged |
|---|---|---|
| 31 Oct ~13:45 | Om's answers (protocol_100 verdicts accepted, BEST = SUP100-PF, PF2 / thin-crack arms / B3 approved, vetter §6 Q1-11) and 11 new ideas; the user: no budget limit, 2 months left, avoid manual labelling unless really needed | `om_2026-10-31.md`; handbook 12 D60, D61 |
| 31 Oct ~15:00 | **E1 = second test set** (pre-registered co-primaries, read once per opening, never for selection; paper reports every opening) | log 17:31 team-lead |
| 31 Oct ~15:00 | **idea 8:** weights (DINOv3 ConvNeXt-T, ViT-S/16, SAM2 Hiera-T) + 2-seed 4k PF screen after PF2; the user accepts the DINOv3 licence and runs any login-gated step | log 17:31 |
| 31 Oct ~15:00 | **idea 10:** S10 inactive check; separate sam2 venv on gaint + ~156 MB weights | log 17:31 |
| 1 Nov ~13:15 | **idea 5 / HC: yes**, GPU after THIN-B3 | log 14:27 |
| 1 Nov ~13:15 | **PF2E: yes**, with E1 crack relF1@2 and E1 inactive IoU as co-primaries (module-cluster bootstrap); E1 opening #4 | log 14:27 |
| 1 Nov ~13:15 | **DINOv3 route B**, verbatim "B: I accept, fetch timm" (the user accepts the DINOv3 License; found fetched the two timm mirrors with sha256 check) | log 14:27, 14:30 |
| 1 Nov ~13:15 | **Om B6** (module-grouped CV for a powered inactive claim): coach designs it now | log 14:27 |
| 1 Nov ~19:00 | **B6 only if cv02 frees up** (≥ 3 qualifying GPUs, one whole experiment there), otherwise skip; never on gaint; reported as low-powered. team-lead 19:02: cv02 had 5 qualifying GPUs, so 2 seeds / 20 runs on cv02 | log 19:01, 19:02 |
| 31 Oct ~13:45 (reading) | **B1 / B2 marks: optional (team-lead's reading of the user's 31 Oct ~13:45 line '…refrain from manual labelling unless very much needed', which overrides Om B4's 'now'); not done; not re-asked.** Not a separate user ruling: team-lead's reading; the team uses proxies instead (Hanifi AUROC check, synthetic half-cuts) | `om_2026-10-31.md` header (the user's line); team-lead to scribe 1 Nov |
- team-lead (1 Nov 19:46): builder's B6 cv02 setup yes, with a fresh `labeled/` holding only the 532 stems (no test / E1 file on cv02).

## 4. PF2 (`protocol_PF2.md` v1.1, md5 at APPROVED 58cbc5e2; `verify_pf2.md`)
### 4.1 Design and run (E)
- Arms SUP100-g / SUP100-PF / RN50-PF, seeds 5-9, 20k steps, all 478 labels, gaint e544133 (RN50 needed no code change; 1-ch stem = RGB sum of smp-hub resnet50.imagenet). Seeds 0-4 never pooled for a verdict (they generated the hypothesis).
- Co-primaries: PF2 contrast 5 (3 test with the two-set rule + E1 crack recall + E1 inactive IoU, direction PF > house stated); RN contrast 3 (test). Uncorrected, disclosed.
- Reported: B5 OPs (calib's frozen scorer), cell-level, scuff-ignored test, E1 strata, E1 width-robust checks (judge: E1 GT crack area/skeleton 3.66 px vs train 2.41, about 1.5x wider), E1 oracle relF1@2 (ranking only).
- Gates: smoke 14:03-14:27 (SUP / SUPPF IDENTICAL to the protocol_100 s0 stdouts; RN50-PF layer3/4 cosine 0.975 / 0.983 at 4k); R34 start 9,000 MiB, RN50 13,234 (peak 11,186 + 2,048), scoring GS 7,900 (RN50 LA val peak 5,824 + 2,048).
- Ran 31 Oct 14:29:15 to 1 Nov 06:32:22 (15 rc 0, 0 Tracebacks; min free during training 4,802 MiB). Gate 6 (RN50-PF s5 4k) PASS 22:37:43. Opening 06:33:18-08:26:14 (MANIFEST 3827f7c0, 290 files; 45/45 B5 self-checks exact).
### 4.2 Verdicts (E, `verify_pf2.md`, coach; runner CONFIRMED to 4 dp)
| Contrast | Metric | Δ (thr) | Read |
|---|---|---|---|
| PF2 | E1 inactive IoU | 0.0481 → 0.2371, **+0.1890 (0.0433)** | BETTER |
| | E1 crack recall | 0.1715 → 0.1986, +0.0271 (0.0370) | n.d. |
| | test relF1@2, all 50 / clean | +0.0117 / +0.0120 (0.0100 / 0.0100) | **BETTER, narrow** |
| | test crack IoU | −0.0011 / −0.0009 | n.d. |
| | test inactive IoU | +0.0173 / +0.0171 (~0.029) | n.d. |
| RN | test inactive IoU | 0.4557 → 0.4269, **−0.0289 (0.0251)**; clean −0.0289 (0.0249) | **WORSE: FAIL** |
| | test crack IoU / relF1@2 | −0.0056 / −0.0028 | n.d. |
- Same at tau 1. Bottom (RN50-PF − SUP100-g): n.d.
- **Robustness:** relF1@2 paired bootstrap +0.0117 [−0.0034, +0.0292], P(Δ > 0) 0.93; leave-top-3-out +0.0015. B5: test relR@2 at relP@2 ≥ 0.90 +0.034 both sets (thr 0.0155). judge (descriptive): part of it is bought with 0.02 relP (pooled rel OP: SUPPF test relP 0.900 vs SUP 0.920).
- **E1 inactive gain** stable: PF 5/5 seeds 0.207-0.279 vs house 0.025-0.089; half-cut 58: 0.162 → 0.537; full 48: 0.025 → 0.097. E1 width-robust crack: relR@2 +0.051 (n.d. by 0.0007), component recall +0.055 (BETTER by 0.0002). 10-seed pooled (descriptive): E1 crack recall 0.170 → 0.206, inactive 0.044 → 0.241.
- **RN named secondary:** E1 scuff + half-cut recall 0.1378 → 0.1153 (−0.0225). Ensembles at +0.75 (addendum, val + E1, recomputed by coach): SUPPF_5 vs RN50PF_5 target recall 0.168 → 0.143 (−0.025); D's house RN50 +0.060 did not carry over under PF.
- **Anomaly (descriptive):** RN50-PF s5 layer4 cosine 0.998 / norm ratio 1.00 at 20k (s6-9 0.907-0.919, 1.10-1.12); PF lr lines identical to s6; seed-specific; not an inactive outlier.
- **Decides (S, coach):** BEST stays SUP100-PF (better on test relF1@2 narrowly, much better on E1 inactive, no test cost). RN50 closed under PF. Pre-registered follow-ups: the ensemble (PF2E, §5) and Om B6 (§7.4).

## 5. PF2E (`protocol_PF2E.md` v1, locked 14:28; `verify_pf2e.md`)
- Inference only, gaint CPU fp32: E-PF (pf2_SUPPF s5-9) vs E-g (pf2_SUP s5-9), mean softmax. Bias by FINAL's D2 rule on val; headline b = 0 if the D2 b trips the val width flag (crack precision drop > 0.05). Test: paired image bootstrap; E1: paired module-cluster bootstrap (71 clusters = source images).
- **Verdict b:** protocol §2 said "the chosen b", the approved scorer "headline b"; judge flagged it; coach clarified "headline b" at 19:04:56 with `out/` empty; val decisions written 19:05:49; test / E1 files 19:13:09. D2 chose b 1.25 (E-g) and 1.5 (E-PF); both tripped the val flag (val crack precision drop +0.0543 / +0.0753), so **the verdict is at b 0 for both**.
| Primary | E-g | E-PF | Δ [CI] | Read |
|---|---|---|---|---|
| test crack IoU | 0.4788 | 0.4815 | +0.0027 [−0.0146, +0.0159] | n.d. |
| test relF1@2 | 0.8821 | 0.8942 | +0.0121 [−0.0048, +0.0309], P>0 0.92 | n.d. |
| test inactive IoU | 0.4376 | 0.4613 | +0.0237 [−0.0310, +0.0971] | n.d. |
| E1 crack relF1@2 | 0.3990 | 0.4345 | +0.0355 [−0.0232, +0.0912] | n.d. |
| **E1 inactive IoU** | 0.0665 | 0.2807 | **+0.2141 [+0.0303, +0.3820]**, P>0 0.99 | **PASS** |
- **PF2E PASS (E1 inactive co-primary); test n.d.; no FAIL.** Clean set same pattern. coach's own-RNG CIs give the same verdicts.
- **judge's 5 qualifications** (appended; coach re-checked the main ones):
  1. E1 inactive GT is 9,158 px in 10 cells, 7 source images, n_eff 3.3 (top-3 clusters 87%).
  2. The gain is half detection, half false alarms removed: TP 2,782 → 5,746 (recall 0.304 → 0.627); false inactive px 32,654 → 11,315, mostly module-border / frame-edge / ribbon px of edge cells in three consecutive CSIR images (CSIR_00391 / 00394 / 00395).
  3. Leave-one-cluster-out Δ [+0.138, +0.277]; consecutive-id CSIR families as clusters (37 or 16) keep LB > 0 (+0.023 / +0.024).
  4. Bonferroni 99% LB ≈ 0.000: borderline under correction.
  5. E1 crack precision falls (P 0.547 → 0.495, relP@2 0.626 → 0.588); crack px on 74 crack-free E1 cells 2,138 → 2,528 (+18%).
- **Wording (judge, coach agrees):** "fewer false inactive calls on module edges plus twice the inactive recall on E1", on 10 E1 cells / 7 images; borderline under Bonferroni. Not a broad unseen-panel inactive capability. Not independent of E1 opening #1 (same member models, same E1 cells).
- **No "matches FINAL" claim:** E-PF clean crack IoU 0.4846 at b 0; 0.4920 (= FINAL's 0.492) only at its D2 b 1.5, which the pre-registered val width flag rejected (val crack precision drop +0.0753 > 0.05; on test, crack precision 0.670 → 0.584). FINAL is cv02, other commits: descriptive only.
- **B5 addendum (reported, coach 19:39):** b 0 self-checks exact 6/6. At val OPs: test component recall at P ≥ 0.90 0.8307 → 0.8624 (+0.032), relR@2 at relP@2 ≥ 0.90 0.8655 → 0.9035 (+0.038); clean +0.032 / +0.038. E1 at the val OP (descriptive): comp R +0.125, relR@2 +0.098, with E1 relP@2 0.498 / 0.451 (far below 0.90 for both). Cell-level (test_clean, b 0): recall 0.936 both, FA 0 both, AUROC 0.968 → 1.000.
- **Recommendation (S, coach and judge):** E-PF is the better deployable candidate than E-g; its D2 operating point is argmax here.

## 6. The 11 ideas: validation and verdicts (`ideas/*.md`, judge verdicts appended)
| # | Idea (owner) | Key evidence (E) | judge verdict |
|---|---|---|---|
| 1 | E1 threshold / calibration (calib) | E1 PR curve below val at every bias (at relP@2 ≥ 0.70: val relR@2 0.954, E1 0.226); per-module label-oracle bound FINAL relF1@2 0.432 → 0.610; label-free rules (per-module quantile, tail shift) lose on F51 and E1; cell-type two-bias oracle FINAL 0.432 → 0.518 (b +5.4 half-cut / −0.8 full), SUPPF5 0.445 → 0.490 | DROP label-free per-panel thresholds; diagnostic KEEP; half-cut routing PARKED (pre-check FAIL, §6.2) |
| 2 | Per-module intensity normalisation (calib) | E1 content brightness = train (median 143 vs 138, AUROC 0.52); the whole-image gap is the white letterbox of 55/58 E1 half-cuts; house jitter reaches 98% of E1; recall vs brightness ρ −0.03; three test-time mappings lower val relF1@2 by 0.02-0.06 and fail the pre-stated GO rule | DROP |
| 3 | Neighbour-reference channel (domain) | 50% of E1 cells (62% of E1 half-cuts) have no same-module file in any source; no module images; FINAL val crack FPs 90% plain background, 2% ribbons, 0% spacing; no crack-vs-scuff separation | Om's version DROP; in-crop variant PARK (jointly with 4) |
| 4 | Periodic-structure removal (domain) | suppresses busbars, keeps oblique cracks, but the model already ignores busbars; crack vs scuff AUROC ≤ 0.45; axis-parallel 480 px lines keep 0.50-0.54 | DROP standalone; 3 + 4 jointly PARKED (channel by a pre-set val rule if ever run) |
| 5 | Synthetic half-cuts (domain) | val cells turned into half-cuts: FINAL recall 0.706 → 0.606 (gap + scale) → 0.563 (+ pool intensity), relR@2 0.887 → 0.774; matches E1 half-cut without scuff (0.552), not scuff + half-cut (0.126); no non-E1 scuff example to simulate | **PASS-to-protocol (narrowed)** → protocol_HC (§7.2) |
| 6 | Higher resolution / HR branch (found) | 2x was run (Track M R5): n.d., val EXCLUDE, 4x compute; stride-2 skip keeps the crack signal; E1 cracks labelled ~1.5x wider | DROP (HR stem kept inside idea 8's wrapper) |
| 7 | Cell-level and operating-point metrics (calib) | scorer `el_metrics.py` validated (backfill exact); b_comp wanders across seeds (sd 1.1-2.8) → arm-level pooled OP; GPU bf16 needed for the exact self-check | PASS (in every protocol since PF2) |
| 8 | Foundation encoder (found) | P8 probe (§6.4); wrapper `hrstem_unetpp` in el_f8 | **PASS-to-protocol** (probe descriptive; 2-seed 4k PF screen A8 vs A8c is the kill gate) → protocol_A8screen |
| 9 | Test-time adaptation (found) | BN-HC's mid-precision gain is mostly a calibration shift; TENT predicted to move crack the wrong way | TENT DROP; T9 per-panel AdaBN PASS to a CPU check → **T9 FAIL, TTA closed** (§6.3) |
| 10 | AI-assisted labelling with SAM (found) | Hanifi `_rf` crack labels: 75% of components < 5 px vs 4% Pratt; SAM fails on cracks | crack SAM DROP, trust-region cleanup PARK; scuff PARK until B3; inactive S10 PASS-low → **S10 PASS** (method note, §6.3) |
| 11 | Appearance augmentation (domain) | E1 brightness / contrast inside house-jitter reach (96-100%); histogram shape outside train p2.5-97.5 for 60% of E1 half-cuts (descriptive) | no standalone arm (geometry → idea 5) |
- judge's final ranking (31 Oct 17:33): 7, 1-routing (conditional), 5, 8, 9, 10, 2; 3 / 4 / 6 / 11 parked or dropped.
- **Item 13 closed** (`team_2026-10-29_features/pool_large/CLOSED.md`, domain; judge correction applied): no download; Use A (the 159k pool holds no E1 module family or new cell type: a thesis negative result), Use B (provenance, leakage, licence note).

### 6.1 Data facts (E)
- **E1 crack labels are ~1.5x wider** than train: area / skeleton 3.66 px vs train 2.41 (judge `judge/crack_width.py`); val 2.46 (judge recompute 1 Nov, log 21:1x; train / val masks only). Pixel E1 crack recall is partly a width readout; protocols report width-robust E1 metrics.
- **Hanifi H36 half-cut crack labels are unusable** (judge 14:23, coach): 1,792 px over 17 cells, 48% within 10 px of spacing / border / cut line; FINAL relR@2 0.036 (1/17 cells). F51 is the `_rf` crack decision set; H36 is for false alarms on its 19 crack-free cells. **There is no labelled half-cut crack set outside E1.**
- 75% of E1 crack px sit in the 29 scuff + half-cut cells, 5% in the 40 plain full cells (judge, SUP s0 m0 GT rows).
- **Letterbox (ideas 2, 11):** E1's "brighter" whole-image statistic is the white letterbox (padding fraction 0.40 vs train 0.17); on content px E1 matches train (mean of cell means 137.3 vs 136.5).

### 6.2 Routing pre-check (`ideas/routing_precheck.md`; rule and R1 cross-fit term written before any number): FAIL
| Model | b_V0 | b_SHV1 | Δb (≥ 1.0) | G (≥ 0.02) | G_cf (≥ 0.01) | max relR@2 at relP@2 ≥ 0.90, V0 vs SHV1 |
|---|---|---|---|---|---|---|
| FINAL | +1.1 | +1.5 | +0.4 | +0.008 | +0.002 | 0.892 vs 0.730 |
| SUP100-PF s0-4 pooled | +2.9 | +3.8 | +0.9 | +0.001 | −0.003 | 0.876 vs 0.694 |
- SHV1 = domain's frozen synthetic half-cut val set (108 images from the 54 val cells, MANIFEST 63dd5469). judge reproduced it exactly (own folds G_cf ≈ −0.001). On simulated half-cuts the models lose ranking, not calibration; E1's large half-cut offset is not produced by geometry + intensity alone. **PF2 §13 void; routing PARKED** behind a labelled half-cut set with E1-like context.

### 6.3 T9 and S10 (CPU, pre-registered)
- **T9 (per-panel BN on `_rf`; `t9_prereg.md`): no variant passes for either family; TTA CLOSED** (judge reproduced exactly).
| Family | Variant | ΔAP on P (36 cells) | H36 crack-free FA px |
|---|---|---|---|
| FINAL | V2 per-panel, all BN | +0.010 | 580 → 1,769 |
| FINAL | V3 shallow | +0.015 | 580 → 427 |
| SUPPF5 | V2 | −0.000 | 31 → 2,214 |
| SUPPF5 | V3 | +0.016 | 31 → 319 (> bound 231) |
  Every variant fails term 1 (+0.03). Thesis line (judge): test-time BN adaptation, global (D BN-HC) or per panel (T9), does not improve unseen-panel crack ranking and raises false alarms.
- **S10 (SAM inactive masks vs model masks, A50 out-of-fold, 239 cells, 22 GT-inactive): b (SAM) PASS** (pooled IoU 0.4925 → 0.5653, +0.073, paired bootstrap [+0.013, +0.135]); c (model AND SAM) FAIL (−0.006). Recall 0.542 → 0.669 at P 0.842 → 0.785; boundary F1 flat; FA px on no-GT cells +28%; val (6 cells, report-only) −0.039. Method note only: "SAM fills partially found inactive regions on unseen cells; it does not sharpen boundaries and it adds false area where the model is already loose." A50 only; 2 comparisons uncorrected.

### 6.4 P8 probe (frozen features + linear probe; descriptive; no test, no E1; `idea08_foundation.md` §4c-4d)
| Encoder (2 probe seeds) | F51 crack AP | val crack AP | H36 crack-free FA px |
|---|---|---|---|
| IN R50 (torchvision) | **0.444** | 0.36 | 3-11 |
| DINOv3 ConvNeXt-T (run 2) | 0.363 | 0.35 | 216-282 |
| IN-1k ConvNeXt-T (= A8c weights) | 0.310 | 0.33 | 95-167 |
| SUP100-PF s0 encoder | 0.295 | 0.27 | 1,030-1,097 |
| SUP100-g s0 encoder | 0.274 | 0.25 | 352-495 |
| DINOv3 ViT-S/16 at 1024 | 0.212 | 0.31 | 53-143 |
| SAM2 Hiera-T | 0.198 | 0.25-0.26 | 698-921 |
| DINOv2-S/14 | 0.173 | 0.17 | 0 |
| IN R34 (house init) | 0.158 | 0.20 | 1,432-1,700 |
| DINOv3 ViT-S/16 at 512 | 0.147 | 0.19-0.21 | 0 |
- Pick rule (bar = 0.444 − 0.02 = 0.424): no candidate qualifies; SAM2 Hiera-T out (no A8h arm); ViT-S/16 out; DINOv3 ConvNeXt-T enters by rule only (Om's named encoder). Screen = A8 vs A8c. DINOv3 CNX-T beats IN-1k CNX-T by +0.053 AP (seed ranges disjoint) but with 20-90x R50's H36 false alarms. judge reproduced both runs exactly.

## 7. Protocols written and armed
### 7.1 THIN-B3 (`protocol_thin_b3.md` v1, locked 1 Nov 00:25; APPROVED 00:38, md5 5a625987; later dated edits)
- Arms on SUP100-PF, seeds 5-9, one change each: SKR (Skeleton Recall, w 1, r-2 tube: covers 99.2% of train crack px, so a soft crack-recall term), CLD (soft-clDice, w 1, k 10), B3 (scuff as class 24, 25-ch head; 12 train cells, 3,246 px). Comparator: PF2's pf2_SUPPF s5-9 reused (shared-baseline condition met: smoke S0 IDENTICAL over 2,000 steps).
- Co-primaries: test 3 (two-set rule); SKR / CLD also test component recall at P ≥ 0.90 and relR@2 at relP@2 ≥ 0.90 at the arm-level pooled val OP; all arms **E1 crack relF1@2** (thr ~0.042). Multiplicity: SKR / CLD 6, B3 4, uncorrected, disclosed.
- B3 mechanism risk stated before the runs: scuff IoU 0.0 at 2k; if the 5-seed mean at 20k is < 0.10, B3 is reported as "scuff class not learned; the effect is the relabelling of 649 train crack px". Distance-map third arm costed, not recommended (inside distance 1 px for 75.5% of crack px).
- Deploy el_thin c9bbb02; gates SKR 9,100 / CLD 10,500 / B3 9,000; GS 7,900 → **9,900** (1 Nov 08:30, before any THIN number). Armed 00:38:42; 15 runs 06:32:46 to 19:39:03, all rc 0, config OK 15/15; opening started 19:40:18.
### 7.2 HC (`protocol_HC.md` v1 locked 1 Nov 14:29; v1.1 erratum 18:54; queue APPROVED 19:43, opening FROZEN 20:22)
- HC − SUP100-PF, seeds 5-9: opt-in loader transform `data.synth_halfcut`, p 0.35 per eligible sample (~26% of views synthetic); sources by rule_p (gap found, band ≤ 20 px, band padding fraction < 0.4): 353 train cells (ARTS 132, CFVS 122, CSIR 99; BMRK, SDLE excluded). Not simulated: 9-busbar layout, CSIR texture, scuff.
- Co-primaries: test 3 + E1 crack relF1@2 + E1 inactive IoU. Mechanism kill (non-E1): SHV1 relR@2 at relP@2 ≥ 0.90 gain < +0.05. Harm guard: F51 crack AP worse (module bootstrap upper bound < 0) → FAIL.
- Build el_hc c2e6973 (builder); found's independent review PASS (`review_hc.md`: house / PF / p0 IDENTICAL 5/5, eligibility 353, SHV1-p 80/80 byte-equal; wording fix F1). Smokes: H0 p 0 IDENTICAL to f3_SUPPF s0 (80/80 lines), H1 share 0.2564, peak 6,826 MiB → gate 9,000.
### 7.3 A8 screen (`protocol_A8screen.md` v1 locked 1 Nov 14:30; v1.1 erratum 19:24; scoring FROZEN 19:53)
- A8 = DINOv3 ConvNeXt-T-PF vs A8c = IN-1k ConvNeXt-T-PF, seeds 0-1, complete 4k schedule (cosine to 0), wrapper `hrstem_unetpp` (el_f8 c280e8c2; builder's review `review_f8_wrapper.md`: no blocker). No test, no E1.
- GO rule: F51 crack AP A8 − A8c > 0 with module-bootstrap LB > 0; val crack AP ≥ A8c − 0.02; false alarms ≤ max(1.5x, +200 px). Validity: encoder stage 2-3 cosine ≥ 0.5. KILL closes "foundation encoder" for the thesis.
- Smokes 300 steps: peak 9,254 MiB both → gate 11,400. Weights: DINOv3 ConvNeXt-T md5 abf90463 (strict timm load, forward identical), IN-1k fcc1480a.
- No-test ruling: `data.root=/home/noob/work/a8_root` with `splits/test.txt` = a copy of val.txt (9dcccf00); 0 real test stems.
### 7.4 B6 (`protocol_B6.md`: v1 design locked at judge's sign-off 1 Nov 18:54 (signed md5 09d74b4c); v1.0.1 (md5 e1f1c894) adds builder's --stems assert and judge's two non-blocking notes, no design change)
- PF − house inactive IoU on held-out physical modules: 5-fold module-grouped CV on train + val (532 cells; test and E1 excluded), 2 seeds → 20 runs. Groups = judge's physical-module groups (`b6_groups.tsv` 5ff33e20; CFVS time-series twins merged: 47.6% of inactive px in 8 multi-image groups); folds `b6_folds.tsv` e2cafce1 (inactive px 19.9-20.2% per fold).
- judge's v0 review (NOT READY): image-id folds leak CFVS twins and favour PF (val inactive +0.086 → −0.029 without the 7 twin val cells, descriptive).
- Verdict: two-stage bootstrap (groups + seed); PASS = CI LB > 0 and Δ ≥ 0.01. **Power (stated before any run): ~13% at Δ +0.017, ~32% at +0.03, 80% needs ~+0.055.** n.d. is the likely outcome.
- Per-fold `data.root` with val.txt = test.txt = the held-out fold (the trainer's end-of-run test pass then sees only that fold). cv02 only, ≥ 3 qualifying GPUs re-checked per wave. Open: builder's roots + held-out scorer, runner's jobs, coach's APPROVED.

## 8. THIN-B3 results (pending verify)
[Placeholder: filled after runner's and coach's verification tonight (E1 opening #2). Verdicts per arm (SKR, CLD, B3) on the test co-primaries, the B5 co-primaries (SKR, CLD), the E1 crack relF1@2 co-primary; B3 scuff readouts; judge's check.]

## 9. E1 openings ledger and multiplicity (`e1_openings.md`)
| # | Protocol | Models | E1 co-primaries | Opened | Result |
|---|---|---|---|---|---|
| 1 | PF2 | pf2_{SUP,SUPPF,RN50PF} s5-9 | E1 crack recall, E1 inactive IoU (PF contrast) | 1 Nov 06:33-08:26 | inactive +0.189 BETTER; crack recall n.d. (addendum: RN secondary ensembles, descriptive) |
| 2 | THIN-B3 | SKR / CLD / B3 s5-9 (+ PF2 SUPPF s5-9 reused) | E1 crack relF1@2 | started 1 Nov 19:40:18 | pending (§8) |
| 3 | HC | HC s5-9 (+ SUPPF s5-9 reused) | E1 crack relF1@2, E1 inactive IoU | not yet (armed) | |
| 4 | PF2E | E-PF vs E-g (PF2 s5-9 members) | E1 crack relF1@2, E1 inactive IoU (71-cluster bootstrap) | 1 Nov 19:02-19:13 | inactive +0.214 PASS; relF1@2 n.d. |
- **Multiplicity note:** within each protocol the co-primaries are uncorrected and disclosed (PF2 5, THIN SKR / CLD 6, B3 4, HC 5, PF2E 5 primaries). Across openings nothing is corrected either. #4 is not independent of #1 (same member models and cells). PF2E's E1 pass is borderline under Bonferroni (LB ≈ 0.000). Reusing PF2's already-opened SUPPF files as a comparator in #2 and #3 is not a new E1 read. Reading E1 for a pre-declared no-op adds multiplicity for no information, so the routing readout was dropped (judge).
- **Before the policy:** E1 was read many times (P13 on, Track M, 27 Oct diagnostics, D, protocol_100, 31 Oct idea backfills, builder's quarantined batch). FINAL and protocol_100 seeds 0-4 are not blind on E1; their later E1 numbers enter no conclusion.

## 10. Incidents and disclosures
- **PF2 LA scoring peak (1 Nov 07:45:13):** rescore_logit_adjust over 15 runs (test + val) peaked at 7,758 MiB beside THIN SKR s5 + CLD s5 + finllm; the gate (GS 7,900) assumed the smoke's 5,824 (RN50 LA, val only, one run). **Min free 2,635 MiB** (< 3,000 for ~30 s): the 2 GB floor held by 587 MiB; finllm (PID 6206) unaffected. Fix: measured peaks replace smoke peaks; THIN's opening GS 9,900 (7,758 + 2,048), before any THIN number. Rule for new scoring passes: max(smoke peak, last real peak) + 2 GB.
- **builder's 31 Oct test / E1-scuff read (14:46-14:54, CPU):** `m0_audit_b3 --ext-scuff --test-scuff` on the already-opened f3_SUPPF s0 and p6_L3 s0 (and a scorer-identity pair recomputing test cells), before coach's ruling reached builder. Not used for any choice; values not reported. Outputs quarantined unread on gaint (`builder_scratch/quarantine_test_reads_2026-10-31`, chmod a-r, MANIFEST.md5 e367b101). Neither run belongs to any new contrast.
- **builder's GPU-context slip (31 Oct ~14:12-14:15, 14:32):** pytest on gaint without `CUDA_VISIBLE_DEVICES=""` opened a CUDA context (runner read 254 MiB; margin then 7.2 GB; finllm unaffected). Since then every gaint command runs with CUDA hidden, nice 19, ≤ 8 threads.
- **judge's tail of THIN stdouts (1 Nov ~18:49; first logged as ~18:52):** printing the last ~150 chars of 13 trained THIN stdouts showed the trainer's end-of-run TEST block (crack / inactive IoU, mIoU per run). No comparator computed, nothing written or recorded; judge's verification uses only the opening's files. **New rule (team-lead 19:02): never tail / cat / less a training stdout; grep step lines only.** builder (18:52) and runner disclosed `tail` reads of HC smoke stdouts: smokes exit at 2,000 steps before any TEST block, so no test number was possible.
- **The trainer's unconditional end-of-run test pass** (trainer.py l.857-880, e544133 and el_f8): every run evaluates the test split at its last step. For A8 and B6 this is neutralised by per-run data roots (test.txt = held-out list), no code change (found's flag 19:23; judge B6 item 7).
- **Test images touched for structure:** domain's half-cut detector R1 / R2b feature runs included the 50 test images (structure only, no labels or scores; coach told domain to drop them 18:21; disclosed in idea05 §1.10); calib read test images for appearance statistics and the max class id of the 50 test masks (00:27); judge's `intensity_stats.py` read test masks for padding class 7 only. None chose anything. Rule since: mask-format checks on train / val only.
- **Usage caps and respawns:** 31 Oct 14:54-17:30 (all agents paused); 1 Nov ~14:36-18:40 (all agents ended; runner, coach, found, builder, judge respawned from disk state; calib and domain not). THIN ran unattended on gaint meanwhile; the HC / A8 smoke slot after THIN's last dispatch was missed and PF2E's build was finished after the respawn.
- **Laptop memory pressure (1 Nov 19:10):** 544 MB available of 15.6 GB, swap full (mostly the user's own apps). Claude Code stopped all 4 of runner's local background tasks (THIN and cv02 watchers, H1 and PF2E waits); found and builder stopped by team-lead after logging state; watchers moved to gaint (one event watcher `rwatch.sh`, tmux rwatch, 19:28; v2 19:54); one local waiter (`lwait.sh`) kept for the cv02 polls (gaint cannot reach cv02); at most one helper agent at a time. gaint jobs unaffected.
- **`set -e` chained checks (1 Nov 20:19, runner's helper):** `[ a ] && [ b ]` under `set -e` does not stop on an early failing term, so integrity checks in `thin_post.sh` / `pf2_post.sh` could pass silently. runner re-verified THIN directly (HEAD = DEPLOY = REVISION c9bbb02, 0 tracked changes, comparator MANIFEST 3827f7c0, scorer md5s hold); coach's verify re-checks independently.
- **Other slips (all caught before any number):** `pf2_post.sh` a82ad566 had the extra-pass `gate_wait` inside a comment (coach, 14:40; fixed 14:41); hand-written timestamps ahead of the clock: coach (14:10) and runner (14:13), corrected in place; found's version headers, corrected to log.md times; judge (31 Oct 14:30, verdict headers corrected to log.md times; 1 Nov four lines stamped 18:51 / 18:58 / 19:20 / 19:36 for events at ~18:49-18:54, the furthest ~42 min ahead: the lines stand as written, followed by a correction line at 18:55; only the sign-off header in `judge/review_B6_v0.md` was corrected in place); coach printed `$(md5sum ...)` literally once; judge's unquoted heredoc lost backtick paths (14:41); runner closed its own idle tmux window by name once (14:49, disclosed); the R34 B5 dump peak was not captured (7 s run between samples); runner's ssh heredoc partly ran on the laptop (18:45, stopped at the deploy check, nothing written); PF2E's out_b5 copy lost the test / ext summaries (fixed 19:46, MANIFEST 6ea19679); a relative-path FileNotFoundError in runner's first PF2E local scoring (before any output).

## 11. Running and armed now (1 Nov ~20:30) and next steps
- **gaint:**
  - THIN-B3 opening (E1 opening #2), started 19:40:18 (trigger PID 2926375, `thin_post.sh` ca436052, GS 9,900, FROZEN 584cabea). Progress: m0_audit_b3 default 20:12, tau 0 20:18; min free since 19:40 21,400 MiB. ETA end ~21:45-22:00 (runner).
  - nq queue armed 19:43:42 (queue PID 1843760, gpumem 1843423; jobs 5cb4bad9: A8 s0, A8c s0, HC s5, A8 s1, A8c s1, HC s6-9; MAXC 3; gates HC 9,000, A8 / A8c 11,400); starts on THIN's "thin scoring done: post rc=0".
  - A8 scoring armed (PID 1908697, MODE=wait; FROZEN a8_score 75a57c9c, a8_calib_dump_4k 12e4818e, a8_init_dump 87923f8e; CPU fp32, val + rf only).
  - HC opening trigger armed 20:22:33 (PID 2122911, FROZEN a23994c4, GS 9,900); E1 opening #3 at that opening.
  - Frozen scorers: B5 (calib) FROZEN 475d78fb / THIN 584cabea (el_metrics 6e73ff11, calib_dump c172717e); THIN E1 relF1@2 98bcb979.
  - gaint watcher `rwatch_v2.sh` (PID 1914687).
- **cv02:** nothing of ours running; read-only polls every 15 min (`results/b6/cv02_polls.log`); 5 GPUs qualified at 18:50 and 19:02.
- **Next, with ETAs (S unless stated):**
  1. THIN-B3 verify (runner local analysis `thin_post_local.sh`, coach on gaint CPU, judge on the laptop): tonight after ~22:00.
  2. A8 screen: the 4 runs go first after THIN's opening (4k steps each); scoring 15-30 min after the 4th trains (`build_a8_runner.md`): night of 1-2 Nov. GO → a full-arm protocol (5 seeds, E1 co-primaries possible); KILL → "foundation encoder" closed.
  3. HC: 5 runs ≈ 12.5 lane-h (protocol_HC) + opening ~1.5-2 h (`build_hc_runner.md`): 2 Nov, likely midday or later.
  4. B6: builder respawns after THIN's window (~22:15) for the 5 fold roots + held-out scorer (~2-3.5 h CPU), then runner's jobs and coach's APPROVED; ~6.5 h on cv02 if ≥ 3 GPUs qualify per wave: 2 Nov at the earliest.
  5. Handbook refresh of this session (scribe, tonight); THIN-B3 section filled after verify.

## 12. Open decisions for the user
1. **Deployable model:** coach and judge recommend E-PF (PF ensemble, argmax) over the house ensemble; FINAL (cv02, +0.75, clean crack 0.492) is not comparable by rule. Adopt E-PF as the deployable candidate?
2. **D2 width flag:** both ensembles tripped it, so the headline is argmax. Whether the D2 grid or width threshold should change is a separate pre-registered question (coach), not a re-pick.
3. **Half-cut routing (PARKED):** needs a labelled half-cut set with E1-like context (Hanifi H36 cleanup would likely not show it, judge; B2 masks or B3 + mining are the route). Labelling stays the user's call (no manual labelling unless really needed).
4. **B1 / B2 marks:** optional (team-lead's reading of the user's 31 Oct ~13:45 line '…refrain from manual labelling unless very much needed', which overrides Om B4's 'now'); not done; not re-asked (§3). The user may still mark them; the B2 Hanifi panel redaction stays in the handbook sources until the marks are done.
5. **A8 full arm** if the screen says GO (GPU + E1 opening).
6. Still open from 31 Oct: delete the 293.6 MB HF sample; who rebooted gaint on 30 Oct 16:28; the 40-segment crack audit and 4 label questions; idle cv02 tmux shells.

## 13. Files
- **Brief, log, ledger:** `team_2026-10-31_next/README.md`, `log.md`, `om_2026-10-31.md`, `e1_openings.md`.
- **Protocols:** `protocol_PF2.md`, `protocol_PF2E.md`, `protocol_thin_b3.md`, `protocol_HC.md`, `protocol_A8screen.md`, `protocol_B6.md`.
- **Builds and reviews:** `build_pf2.md`, `build_pf2e.md`, `build_thin_b3.md`, `build_thin_runner.md`, `build_hc.md`, `build_hc_runner.md`, `build_a8_runner.md`, `review_hc.md`, `review_f8_wrapper.md`; judge's reviews in `judge/` (`review_B6_v0.md`, recompute scripts, `out/`).
- **Verifications:** `verify_pf2.md`, `verify_pf2e.md`.
- **Ideas:** `ideas/idea01`-`idea11` reports with judge verdicts, `idea7_metrics_defs.md`, `idea08_download.md`, `idea08_runspec.md`, `idea10_runspec.md`, `routing_precheck.md`, `t9_prereg.md`, `s10_prereg.md`; outputs `ideas/calib_out/`, `domain_out/`, `found_scripts/`, `figs/`; scripts `ideas/scripts/`.
- **Results:** `results/pf2/` (`results_pf2_runner.md`, rung files, `pf2_e1_extra.txt`, `pf2_e1_width.txt`, `coach_v/`, `d_rn/`, `gpumem.log`), `results/pf2e/` (`pf2e_boot_runner.txt`, `coach_v/`, `b5/`), `results/b6/` (folds, inactive counts, cv02 polls). Per-cell raw pulls (`results/*/raw`, `coach_raw`), the protocol_100 per-cell copies in `results/pf2/pooled10_m0`, `rules_in` copies, PF2E B5 record JSONs and calib's per-cell records (`ideas/calib_out/rec*`) are gitignored (kept locally and on gaint with MANIFEST.md5).
- **Item 13:** `team_2026-10-29_features/pool_large/CLOSED.md`.
- **Servers:** gaint worktrees `el_f3` (e544133; PF2, PF2E), `el_thin` (c9bbb02), `el_hc` (c2e6973), `el_f8` (c280e8c2); `/home/noob/work/nq/` (queue, HC opening), `a8_root/`, `a8_score/`, `weights/` (SAM2, DINOv3, MD5SUMS), `venv_sam2/`, `runner_events/`; quarantine `builder_scratch/quarantine_test_reads_2026-10-31`. cv02: unused.
