# Protocol SKR2C: fresh-seed replication of SKR2 vs SUP100-PF (seeds 10-14), singles rule 1 + ensembles at a shared b 0 (gaint)

coach, 3 Nov 2026. **v1 LOCKED 2026-11-03 02:37 IST.** judge SIGNED the v1 candidate 5995fcd5 (`judge/review_SKR2C_v09.md` 47f8e6f0). The post-sign edits are judge's 6 wording / fact fixes plus L1-L4 only; there is no design change. No SKR2C number exists at lock, and no S2C run has started. Tags: E (file), R, S.
- History:
  - v0.9 6958d22f; v0.9.1 91f875c9 (team-lead's additions; judge's advance checklist).
  - v0.9.2 applies judge's review `judge/review_SKR2C_v09.md` e146f83b (M1-M5 + should-fix 1-5, approved by team-lead).
  - It also applies team-lead's rulings (~02:3x): second stop yes; SIGKILL only after re-checking owner noob and the identical cmdline; HOLD on an outside GPU process > 1 GB; a dry run with a faked free value before APPROVED.
  - judge SIGNED v0.9.1 (91f875c9) conditional on L1-L4 (`judge/review_SKR2C_v09.md` 7f3b94d1). L1-L4 are applied here (§2a, §2b, §3c, §7).
- Asked by team-lead (3 Nov 02:2x): the user is offline until tomorrow and said "if theres anything else to do run this night".
- **Tonight: training only.** No SKR2C test or E1 number may exist before the opening.
- **The opening (E1 #7) runs only after the user's explicit OK**, relayed by team-lead.

## 0. What I had seen when writing this (E), and what that means
- **#5 SKR2 singles, s5-9** (`verify_skr2_hc2.md`, judge CONFIRMED):
  - E1 crack relF1@2 +0.0364 BETTER (thr 0.0351). It passed by 0.0013, and the label is fragile (5 / 10 seed drops; leave-one-image-out keeps it in 65 / 71).
  - Test n.d.; E1 any-hit +0.044 n.d.; G1 / G2 ok.
- **#6 SKR2E ensembles, s5-9** (`verify_skr2e.md` 507e9e7a, judge CONFIRMED): FAIL, by G2a / G2b at the asymmetric headline pair (E-PF b 0 vs E-SKR2 b 1.0). The width flag alone decided FAIL vs PASS.
  - At a shared b 0, no primary failed and no guard tripped: test crack IoU +0.0102 / relF1@2 +0.0104 (≥ 56-62% volume); E1 relF1@2 +0.0353 (a curve shift, +0.024 at matched volume); any-hit +0.0676 (60% volume, n_eff 3.6 images); E1 inactive −0.042 (3 images).
- **Disclosure (S): this design was chosen after SKR2E.** The shared b 0 OP was picked knowing that b 0 passed on s5-9 while the asymmetric headline failed. Fresh seeds make every contrast a new draw of models. The guards and pass rules are S2's and SKR2E's; the only change is that the per-arm headline b is removed.

## 1. Question; what SKR2C can and cannot answer
- **Question:** with fresh seeds (10-14, both arms), does the SKR2 recipe (Skeleton Recall w 0.1) beat SUP100-PF:
  - as single models (house rule 1, the recipe verdict), and
  - as 5-member ensembles at a shared argmax (the deployable reading)?
- **Test and E1 reuse (judge item 3):**
  - Test and E1 were opened for this exact contrast at #5 (singles) and #6 (ensembles). This is the **3rd look**, at the same 50 test and 106 E1 cells.
  - **Fresh seeds remove seed luck, not cell luck.** The E1 effect sits in a few images: leave-one-image-out keeps the #5 label in 65 / 71; any-hit gain n_eff 3.6.
  - So a PASS is a **seed-level replication on reused cells, not new-panel evidence**. Every result line says "same cells as #5 / #6".
- **Why it is worth the night (S):**
  - It answers the open seed-robustness question: #5's label was fragile, and #6's fixed-model CIs left seed noise out.
  - The GPU is otherwise idle, and no labelling is needed.
  - The result decides whether SKR2 is carried into the next deployable (e.g. a cv02 R34 ensemble) or dropped.

## 2. Arms, code and training (20,000 steps, batch 8, final weights; one change per arm)
| Arm | Code | Opts | Run names |
|---|---|---|---|
| SUPPF | el_f3 **e544133** | `pf2_jobs.txt` 210d0d6f pf2_SUPPF s5 line, seed K, run_name, + `data.root=<S2C root>` | `s2c_SUPPF_100pct_s10..14` (el_f3/experiments) |
| SKR2 | el_thin **c9bbb02** | the same + `loss.skel_recall.weight=0.1` (= s2q_jobs d6efb9af recipe) | `s2c_SKR01_100pct_s10..14` (el_thin/experiments) |

- **Rule-1 hygiene (judge item 7):**
  - Two worktrees, as S2. Shared-baseline condition: SKR2's tree with the switch off is e544133 on SUPPF opts, shown by the S0 2,000-step identity at d93d9a1 (1 Nov 00:19), and c9bbb02's training code = d93d9a1 (THIN build).
  - Seeds 10-14 are new: no `*_s1[0-4]` dir exists in either tree (runner, E).
  - 20,000 steps, final-step weights, same hardware (gaint), matched steps.
  - **Config diff of every run vs pf2_SUPPF_100pct_s5** = seed + run_name + data.root (+ `loss.skel_recall.weight=0.1` for SKR2) only. Anything else → HOLD.
### 2a. No test or E1 number before the opening: the data root (team-lead 1; judge item 2)
- **Root:** `/home/noob/work/s2c_root` (built by runner's `s2c_make_root.sh` 133ad184, log 02:33; `SPLITS.md5` **24568cdb**), one root for all 10 runs:
  - `splits/train.txt` = el_f3 train **842f27c4**;
  - `splits/val.txt` = `splits/test.txt` = the real val **9dcccf00**, byte copies;
  - `labeled` → the same target as B6's `b6_build/idroot/labeled` (`/home/noob/work/el-fault-detection/data/labeled`).
  - All three md5s and the symlink target are recorded and re-checked at arming.
- **Why:** the trainer evaluates the test split at the end of every run and writes those numbers to stdout and to the results payload. Unread stdouts are not enough. Under this root that pass sees val only.
- **E1 (judge item 2, E):** the trainer never builds E1. `scripts/train.py` and `src/` of el_f3 e544133 and el_thin c9bbb02 contain no ext117 reader. The only E1 reference is el_thin's `src/evaluation/b3_scuff.py`, which train.py and the trainer do not import (grep on gaint, coach 02:4x).
- **Identity, before APPROVED (B6 pattern; this replaces a GPU smoke):**
  1. **CPU identity:** `b6_build/scripts/identity_cpu.py` 962379a6, 5 steps, seed 0, per arm (`--code` = the arm's tree, the arm's opts). A = `data.root=data`, **the tree's own data dir**; B = the S2C root. **IDENTICAL** is required in: init state, class counts, the fixed batch, and at every step the loss repr, lr, parameter sha and fixed-batch logits sha.
     - Per-step wall time ('sec') is not compared (as B6's idchk). The IDENTICAL list above is unchanged (judge fix 4).
     - e544133 + SUPPF opts has passed this before (build_b6 §4).
     - el_thin + SKR01 is new.
     - **el_thin's `data/labeled` is its own directory** (judge, E): its 1,747 files shared with the root's target are byte-identical, and it adds 585 B3 `masks_escdd_s` files that the root lacks. So A must be el_thin's own `data`. That run is what shows SKR01's opts never read those files.
  2. **CPU data-build line** per arm (runner's `s2c_databuild_check.py`; B6's b6_databuild_check pattern):
     - "Labelled: 478 … val: 54 test: 54" (the train count is as PF2's train.log);
     - CE class weights equal to the PF2 / S2 stdout lines;
     - config = pf2 s5 config with data.root changed only.
  3. **Live, per run** (queue, before the next start): the startup "Labelled … val: 54 test: 54" line and `config OK`. A mismatch → that run is stopped by its recorded PID and the queue HOLDs.
- **No GPU smoke** (runner Q4, accepted): same commits and opts as opened runs apart from seed and root; the CPU identity covers the root; the peaks are measured (below).
- **Stdouts:** grep only (step lines, counts, Tracebacks); never tail.
- **Fallback:** if a CPU identity or data-build line is not as required, there is **no launch**, and it goes back to team-lead. The `data.root=data` / unread-stdout branch is not allowed (team-lead 1). So judge's M4 (gate (a) under the fallback) cannot arise.
- **Note:** under the root, each run's stdout end-of-run block and `experiments/<run>/metrics.json` "test" entries hold **val** numbers (val = test there). They are labelled so in every record, and no opening pass reads them as test (§3).
### 2b. Queue and the overnight auto-stop (team-lead 2; judge item 5)
- **Queue** (`build_s2c.md`, s2q pattern):
  - **Order and concurrency:**
    - 10 jobs; for each K, SKR01 sK and then SUPPF sK, so each seed's pair trains side by side;
    - MAXC **2**; shared gpu_gate, ≥ 120 s between starts, HOLD honoured.
  - **Gates** (peak + 2,048, rounded up), from measured peaks (runner, E, gpumem logs):
    - GATE_SKR01 **9,100** (peak 7,020);
    - GATE_SUPPF **9,000** (peak 6,830).
    - Worst case: 19,916 MiB used, ~12.7 GB free.
  - **Start conditions:**
    - **New starts HOLD while any GPU process that is neither ours nor finllm (PID 6206) holds > 1 GB** (team-lead; README: the user's jobs have priority). Running runs continue, under the auto-stop.
    - **New starts HOLD if the 1 s gpumem logger or the auto-stop watcher is gone** (runner Q3: HOLD).
- **Auto-stop watcher** (required, team-lead; judge M1). Runner builds it; coach and judge check the code; a dry run with a faked free value happens before APPROVED.
  - **Why:** rwatch_v4 only writes ALERTs, and nobody reads them overnight, so this watcher is what protects finllm.
  - **Process:** its own process (tmux window, recorded PID, its own 1 s nvidia-smi sampling), independent of the queue.
  - **(a) Which process:**
    - It stops **only our newest running S2C run**: the most recently started alive run, by the trainer python PID recorded at its launch. Per the B6 lesson, this is the python process, not the launching subshell.
    - The full cmdline is recorded at launch (`/proc/<pid>/cmdline`, containing `run_name=<name>`).
    - **PID-reuse guard:** before any signal, `/proc/<pid>/cmdline` must equal the recorded cmdline exactly, and the owner must be noob. If not: log, HOLD, no signal.
    - **Never** a pattern match, never finllm 6206, never another user's process, never a PID not in `s2c/pids/`.
  - **(b) Trigger and action:**
    - Trigger: GPU free < 2,048 MiB on **3 consecutive 1 s samples**.
    - Action: SIGTERM to the verified PID. If it has not exited after 30 s, **re-verify, immediately before the SIGKILL, that the same PID's owner is noob and its `/proc/<pid>/cmdline` = the recorded cmdline**, then SIGKILL that same PID and never any other (judge L1) (team-lead ruling: a stuck process must not keep the memory). If the re-check fails: log, HOLD, no signal.
    - **A second stop** needs a fresh trigger (3 new consecutive samples, ≥ 30 s after the first stop) and goes to the newest remaining S2C run.
    - **At most 2 stops**, which covers both of our runs at MAXC 2 (team-lead ruling: finllm's floor outranks finishing our runs).
  - **(c) After any stop:** the queue HOLDs (no new start, no restart overnight). Runs still alive continue.
  - **(d) Logging:** every event goes to `s2c/autostop.log`, with:
    - the PID and its full cmdline (`ps -o pid,user,lstart,args` + the recorded cmdline);
    - the free-memory trace (the 3 trigger samples plus 60 s around the event);
    - the nvidia-smi compute-apps list;
    - each action and its result (exit seen, or SIGKILL sent).
  - **Dry run before APPROVED:** a faked free series fed to the watcher logic, with a dummy process that runner starts and records. Required results:
    - the recorded PID is the python trainer, not the launching subshell (`ps -o pid,ppid,args`);
    - 2 low samples do not trigger; 3 do;
    - it stops only that recorded PID;
    - a SIGTERM-ignoring dummy gets SIGKILL only after the owner + cmdline re-check passes, and gets no signal if the re-check fails;
    - it refuses a PID whose cmdline differs from the recorded one;
    - the HOLD file appears;
    - the second-stop and 2-stop-cap logic behave as written;
    - new starts HOLD on an outside GPU process > 1 GB and when the logger or the watcher is gone;
    - `autostop.log` carries every field listed in (d) (judge fix 3).
- **Resume vs rerun (pre-registered now; judge M2):**
  - **Default: a stopped run is rerun from scratch** with the same seed and opts, after team-lead's OK tomorrow. Its arm and seed stay the same.
  - The partial dir is moved aside to `<name>_STOPPED_<time>`, kept, logged, and never read beyond the step count. The rerun's config diff and completion checks are as for any run.
  - **Resume from latest.pth only if** both of these hold, shown before the resume:
    - the trainer restores optimizer, scheduler, AMP scaler, RNG and data order;
    - a resume identity check passes: an N-step continuation whose step lines equal an uninterrupted run's.
  - Otherwise a resumed run is not matched training (rule 1).
  - Any stop and rerun is disclosed in the verify.
- **Completion:** `S2C ALL TRAINED (10 rc 0 of 10)`. Each run must show 1 header line, "step 20000/20000" and 0 Tracebacks (grep -c). Nothing is scored.
- **Expected:** ~2h28 per run at 2 alive, so 5 waves take **~12.3-12.5 h**: done ~17:00 from a ~04:30 start. ~25 GPU-h, ~5 GB disk.

## 3. Opening analysis (fixed now; E1 opening #7; read once, after the user's OK)
**The opening must read the real splits** (el_f3 `data/splits/test.txt` **a31fad14**, val 9dcccf00, the ext117 list). It must **never** read `<data.root>/splits/test.txt` from a run's config_used.yaml. Each pass asserts its test stems md5 = a31fad14's list, and its per-cell output stems = the real test stems.
### 3a. Verdict R, the recipe replication (house rule 1, singles, both arms at b 0 / argmax, as S2's tau 0)
- **Co-primaries:** exactly S2's SKR2 set (protocol_SKR2_HC2 §3a), 5 v 5, rule 1 /3.
  1. **Test at argmax:** crack IoU, crack relF1@2, inactive IoU. Two-set rule: all 50 and clean 49 (without CSIR_00070_r8_c4).
  2. **B5 on the wider grid:**
     - comp recall at comp P ≥ 0.90, and relR@2 at relP@2 ≥ 0.90;
     - arm-pooled OP chosen on val over b ∈ −8.0 … +12.0, step 0.1 (calib's rule; S2's frozen el_metrics_w 45b1df03);
     - two-set rule.
  3. **E1 (all 106 cells, argmax):** crack relF1@2, and any-hit component recall (S2's definition).
- **Guards** (S2 §3c, seed means):
  - **G1:** test inactive IoU Δ ≤ −0.015 in both sets.
  - **G2:**
    - test crack relP@2 Δ < −0.03 (all 50); or
    - E1 crack px on the 74 crack-free cells > 1.5 × SUPPF's.
- **Verdict R:**
  - **PASS:** ≥ 1 co-primary BETTER, none WORSE, no guard tripped.
  - **FAIL:** any WORSE, or any guard tripped.
  - **Else n.d.**
- **Named claim, two tiers (judge M3; a replication claim is about seed noise):**
  - **"SKR2's E1 crack relF1@2 gain REPLICATED on fresh seeds (seed-aware; same 106 E1 cells, 3rd look)"** holds iff all three hold:
    - the **seed-aware two-stage bootstrap** of E1 relF1@2 on the 10 fresh singles at b 0 has its 95% CI wholly above 0. The bootstrap resamples seeds within arm × 71 module clusters, 2,000 draws, seed 0, following the `coach_s2_boot.py` 7ea26cfb pattern (`results/s2/coach_v/diag/`);
    - D's E1 relF1@2 primary passes;
    - neither R nor D is FAIL.
  - **If only D's ensemble CI passes:** "the fresh-seed ensemble pair differs on E1 relF1@2 (fixed-model CI; seed noise not included); replication at recipe level not shown".
  - R's rule-1 label for E1 relF1@2 (BETTER / n.d.) is part of verdict R and is reported next to both.
- **Multiplicity:**
  - R (S2 §3d): rule 1 sits at ~2.58 SE, so ~0.5-1.6% false BETTER per co-primary and ≤ ~10% family-wise over 7.
  - The named claim's recipe-level false pass is ~2.5% one-sided. It uses the seed-aware CI, with judge's SE ≈ 0.019 (cluster ~0.013 + seed composition ~0.014).
  - A D-only E1 pass, read as a recipe claim, would be ~8-9% (judge M3). That is why it gets the lower-tier wording.
### 3b. Verdict D, the deployable reading (5-member ensembles E-SKR2' / E-SUPPF' at a shared b 0; judge item 1)
- **Objects:** s10-14 per arm, mean softmax, final weights, TTA off. One process, one model code (el_f3 e544133, strict load), gaint CPU fp32. This is the SKR2E pattern.
- **One verdict pair: b 0 for both.** No per-arm headline b. The D2 b and width flag are reported (val only).
- **Primaries (SKR2E §3a at that pair):**
  - test crack IoU, relF1@2, inactive IoU: all 50 / clean 49, paired image bootstrap, 2,000, seed 0;
  - E1 crack relF1@2 and any-hit: 71-module-cluster bootstrap, 2,000, seed 0.
  - **Pass:** the CI is wholly above 0. For test this must hold in both sets, or in one with a same-sign estimate in the other.
  - **Fail:** the CI is wholly below 0 in either set.
- **Guards at the b 0 pair (point estimates):**
  - **G2a:** test relP@2 Δ < −0.03.
  - **G2b:** E1 crack-free px > 1.5 × E-SUPPF'.
  - **G1t:** test inactive Δ ≤ −0.015 in both sets.
  - **G1e:** E1 inactive cluster CI wholly below 0.
- **Verdict D:**
  - **PASS:** ≥ 1 primary passes, none fails, no guard trips.
  - **FAIL:** any primary fails, or any guard trips.
  - **Else n.d.**
- **Fixed wording:**
  - Every PASS names its carrying primaries.
  - A PASS carried only by test crack IoU / relF1@2 and / or E1 any-hit adds: "carried by argmax readouts that were mostly volume on seeds 5-9 (SKR2E §3a); see the matched-volume lines (§4)."
  - A PASS carried only by test primaries also adds SKR2E's line: "SKR2's E1 gain is not replicated at ensemble level." (judge should-fix 5)
  - Every any-hit line carries the per-image concentration line.
- **B5 is not part of D** (it is R's co-primary in S2's el_metrics_w form, comparable with #5). So judge's M5 (the m_common component definition, and the D1 condition at a B5 OP) does not arise in D. R's B5 OPs are on single models (S2's grid); no B5 number is read at the ensembles.
- **Multiplicity (SKR2E §3c):** ~12% family-wise false PASS for the objects; ~15-20% as a recipe claim; G1t null false-FAIL ~8%.
### 3c. How R and D combine (fixed now)
- **R PASS and D PASS** → E-SKR2' at b 0 is recommended as the deployable candidate over E-SUPPF' (§7).
  - **If both PASSes rest only on volume-sensitive carriers** (test crack IoU / relF1@2 at argmax, any-hit), the recommendation sentence carries the volume wording (§3b) **and** the b_mv matched-val-volume result (§4) (judge L3).
- **R FAIL or D FAIL** → the SUP100-PF ensemble stays (#6's E-PF at b 0).
  - The FAIL line names the guard or primary that caused it.
  - If an inactive guard alone caused it, the line carries its null false-FAIL: R's G1 ~9-15% (S2 W1), D's G1t ~8%; combined, **~15% that a true null keeps SUP100-PF through an inactive guard alone** (judge L2).
- **Otherwise** → reported as is (each verdict with its carriers); the SUP100-PF ensemble stays. Coach does not recommend a switch; the user decides.

## 4. Reported (never change a verdict)
- **R (as S2 §4):** B5 per run; LA tau 1; scuff-ignored test; cell-level; E1 strata; width (pred / GT, relP / relR on test and E1); crack-free px; per-source rows; seed-aware two-stage bootstrap of each test co-primary; thin-term magnitudes.
- **D (as SKR2E §4):**
  - matched val volume: E-SKR2' at b_mv, the b on −1.50 … +0.50 (step 0.05, val only) where its val crack pred / GT is nearest E-SUPPF''s at b 0, vs E-SUPPF' at b 0, test and E1 with CIs;
  - the E1 aggregate sweep (−1.5 … 3, step 0.25) and E1 matched volume;
  - E1 concentration and leave-one-cluster-out;
  - four test sets, test_noscuff, per source;
  - singles vs ensemble.
- **References (descriptive, already opened):**
  - #5 / #6 rows;
  - a 10-seed view (s5-14 single means; labelled "5 of 10 seeds opened before");
  - FINAL 0.492.

## 5. Expectations and power (S)
- **R** (judge, `judge/out/skr2c_power_out.txt` 2e15d408): Monte Carlo of rule 1, 5 v 5, from #5's seed sds. The primaries are treated as independent, so these numbers are optimistic.
  - P(PASS) 0.90 / 0.64 / 0.34 / 0.05 at 1 / 0.75 / 0.5 / 0 × #5's deltas.
  - P(E1 relF1@2 BETTER) 0.57 / 0.35 / 0.18 / 0.02.
  - Winner's curse: #5 passed by 0.0013, so the true effect is more likely 0.5-0.75 ×.
  - **Realistic: ~35-65% chance of an R PASS; ~18-35% for an R rule-1 BETTER on E1 relF1@2.**
  - Inactive-guard null false-FAIL: R's G1 ~9-15%, D's G1t ~8%, so **~15% combined** (S, correlated) that a true null fails through an inactive guard alone (judge fix 6).
- **D (judge M3, E1 relF1@2 ensemble Δ, SE ≈ 0.019 with seed composition):** P(pass) ~68% / 46% / 28% at a true +0.035 / +0.024 / +0.015.
  - **A test crack pass at b 0 is likely, and likely mostly volume** (as #6; should-fix 4).
  - G2a / G2b are unlikely to bind at b 0 (#6: −0.011, ×1.06).
- **Named seed-aware claim:** ~45% / 25% / 12% at a true +0.035 / +0.024 / +0.015, so **~25-45% realistic**. The likeliest honest outcome is "replication not shown", not "refuted".
- **Likeliest overall:** R a PASS carried by one co-primary, or n.d.; D a test-crack PASS with the volume wording.

## 6. Build, gates and order
- **Stage 1, tonight (runner; coach reviews; judge checks the auto-stop):**
  - **Root and checks:** the root; the CPU identity for both arms and the data-build lines (§2a).
  - **Jobs and queue:** jobs (10 lines, md5; coach parses the diff vs pf2_SUPPF s5: seed + run_name + data.root (+ skel_recall)); the queue with the outside-process HOLD and the logger / watcher HOLD; the gpumem 1 s logger.
  - **Watcher:** the auto-stop watcher (§2b) and its faked-free dry run (shown to coach and judge before APPROVED); rwatch_v4 stays armed.
  - **Registry:** `e1_openings.md` #7 "registered; NOT opened; opens only on the user's OK".
  - Then APPROVED, then launch.
- **Stage 2, after training and before the opening (runner builds; coach reviews; frozen md5s before any S2C number):**
  - R = S2's frozen opening set (FROZEN fb5becd2) with the HC2 parts removed and the run lists changed. Both arms are scored fresh (no comparator reuse). The real-splits assert is in every pass.
  - D = skr2e_infer 5ba3c597 / skr2e_boot 7520afc0, with one pair, b_mv, no E-PF identity check, and the sweep extended to −1.5.
  - **D gate (a):** each member alone, CPU fp32, val vs its R-opening m0 JSON (GPU bf16): |Δ| ≤ 0.005, any-hit ≤ 0.01. Also val GT comps 125 and E1 296 (asserted).
  - **Named claim's seed-aware two-stage bootstrap:** E1 relF1@2 on the 10 fresh singles' m0 per-cell files from R's pass (`coach_s2_boot.py` 7ea26cfb pattern, seed 0); frozen with stage 2.
  - **Order:** R's passes, then D. Coach's own recompute of both before any verdict goes to team-lead; then judge.

## 7. After the opening
- **R PASS + D PASS:** E-SKR2' at b 0 is the recommended deployable candidate, named by its carriers.
  - Handbook: "R PASS on <carriers> (same cells); E1 relF1@2 per §3a's named-claim tier". An R PASS carried by test primaries is not an E1 replication (judge fix 5).
  - A cv02 R34 SKR2 ensemble would need its own protocol.
- **R FAIL** (a WORSE co-primary, or G1 / G2): the Skeleton Recall route closes for the deployable at w 0.1.
  - **The line names the guard or co-primary that caused it** (judge L2).
  - **If G1 alone caused it:** the line carries "G1 null false-FAIL ~9-15% (S2 W1); with D's G1t ~8%, ~15% combined that a true null closes the route through an inactive guard alone".
- **R n.d.:** R's rule-1 verdict is n.d.; the E1 claim is stated by §3a's two-tier rule only. The seed-aware CI (~1.96 SE) is looser than rule 1 (~2.58 SE), so REPLICATED (seed-aware) can hold while R is n.d. (judge fix 5).
- **D FAIL with R PASS:** the recipe effect is real at single-model level, but the ensemble pays the guarded cost. The SUP100-PF ensemble stays.

## 8. Before lock
1. **judge:** v0.9 reviewed (e146f83b, NOT READY, M1-M5). v0.9.2 applies M1-M5, should-fix 1-5 and team-lead's rulings.
   - v0.9.1's R + D structure follows judge's advance checklist item 1.
   - M4 cannot arise, because there is no fallback branch.
   - M5 does not apply to D, because B5 sits in R in the el_metrics_w form.
   - To judge for sign.
2. **Lock v1** → runner stage 1 (root, identity, data-build lines, jobs, queue, watcher + faked-free dry run) → coach reviews; judge checks the watcher code and dry run → **APPROVED** → launch.

## 9. Launch record
(empty)
