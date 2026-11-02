# judge review: protocol_SKR2C v0.9 (md5 6958d22f), 3 Nov 2026

**Verdict: NOT READY TO LOCK. There are 5 must-fixes, all small.**
- Two are safety and hygiene: the unattended auto-stop (M1) and the resume rule (M2).
- One is inference: the "REPLICATED" label ignores seed noise (M3).
- Two are definitions to fix before lock (M4, M5).
- The design itself is sound: symmetric b 0, the data root, and the disclosures are in.
- **Worth the night: yes**, with the expectation stated honestly (end of file).

Inputs: the draft; team-lead's approved auto-stop conditions (a)-(d), 3 Nov ~02:25; `judge/out/skr2c_power_out.txt` 2e15d408. Read-only gaint checks are in the next section.

## Read-only gaint checks (E, 02:3x; md5sum / find / readlink only, no process left)
- **Splits.** `el_f3/data` and `el_thin/data` both have train 842f27c4, val 9dcccf00 and test a31fad14. `b6_build/idroot` has train 842f27c4 and val = test = 9dcccf00. `labeled` → `el-fault-detection/data/labeled`. The draft's root premise holds.
- **el_thin's `labeled` is a separate directory, not a symlink:** 2,332 files against 1,747.
  - All 1,747 common files are byte-identical (per-file md5).
  - The 585 extra files are `masks_escdd_s/` (582 files) plus its diff / MANIFEST / summary: B3's scuff masks.
  - So the root has no `masks_escdd_s`. The SKR2 arm's identity check A (el_thin, `data.root=data`) vs B (root) is what shows that SKR01's opts never read that directory. Keep A = el_thin's own `data`.
  - The 1,000-step GPU smoke vs `skr2_smk_SKR01_s0.stdout` covers it again.
- The trainer writes `experiments/<run>/metrics.json` next to `train.log` (seen in skr2_SKR01_100pct_s5). Under the fallback branch that file holds test numbers too (M4).

## Must fix
**M1. The unattended auto-stop (§2b). The draft contradicts team-lead's approved conditions.**
- §2b says "There are no automatic kills: stops only by recorded PID, by runner". Overnight no agent will be alive, and rwatch4 only writes ALERTs. So nothing would protect finllm if an outside job grew. Replace it with team-lead's conditions, verbatim in substance:
  - (a) The auto-stop may stop **only our newest running SKR2C run, by the PID recorded at its launch**. Never a pattern match, never finllm (6206), never another user's process.
    - **PID-reuse guard:** before signalling, compare `/proc/<pid>/cmdline` with the cmdline recorded at launch, which contains the run_name. If they differ, do not signal; log and HOLD.
  - (b) Trigger: free < 2,048 MiB on **3 consecutive 1 s samples**.
    - If free stays < 2,048 after a stop, the rule may apply again to the then-newest SKR2C run, one at a time, at least 10 s apart (state this).
  - (c) After a stop the queue **HOLDs**: no new start and no restart overnight.
  - (d) Every event is logged with the PID, its full cmdline, and the free-memory trace (the 3 samples plus 60 s around the event).
- The watcher runs in its own process: tmux, recorded PID, own 1 s sampling. It must not depend on the queue being alive.
- **SIGTERM, not SIGKILL**, then wait for the PID to exit. Say what happens if it does not exit within N s (log and HOLD; no escalation to other PIDs).

**M2. Pre-register the resume vs rerun rule now (team-lead's (c) defers the decision to "the protocol's pre-registered rule", and the draft has none).**
- **Default:** a stopped run is **rerun from scratch** with the same seed and opts. Its partial dir is moved aside, not deleted, and logged.
- **Resume from latest.pth only if** the trainer restores optimizer, scheduler, AMP scaler, RNG and data order, and a resume identity is shown first: an N-step continuation equal to an uninterrupted run's step lines.
- Otherwise a resumed run is not matched training (rule 1: matched steps, one change per arm). A rerun run keeps its arm and seed; the rerun is disclosed in the opening.

**M3. The named "REPLICATED" claim rests on a fixed-model CI. A replication claim is about seed noise, which that CI leaves out (§3d, §5).**
- **E, from #5 / #6:**
  - Cluster SE of the E1 relF1@2 ensemble Δ: ≈ 0.013 (SKR2E half-width 0.0256).
  - Ensemble seed-composition noise of the same Δ: ≈ √(0.0272² + 0.0135²) / √5 ≈ 0.014 (#5 singles' E1 relF1 sds; the house approximation used for G1t).
- **So (S, rough):**
  - At a true recipe effect 0, the observed fresh-seed Δ has sd ~0.019. It still needs only > ~0.026 to pass.
  - **The named claim's recipe false-pass is ~8-9%, not ~4-6%.**
  - Its power is ~68% / 46% / 28% at a true +0.035 / +0.024 / +0.015.
- **Fix: two-tier wording.**
  - **"REPLICATED on fresh seeds (seed-aware; same 106 E1 cells, 3rd look)"** needs all of:
    - the seed-aware two-stage bootstrap (seeds within arm × 71 module clusters, on the 10 fresh singles at b 0; coach_s2_boot.py 7ea26cfb pattern, seed 0) with CI > 0 for E1 relF1@2;
    - co-primary 4 passes;
    - the verdict is not FAIL.
  - **If only the ensemble CI passes:** "the fresh-seed ensemble pair differs on E1 relF1@2 (fixed-model CI; seed noise not included); replication at recipe level not shown".
  - State the seed-aware power: ~45% at +0.035, ~25% at +0.024, ~12% at +0.015 (SE ≈ 0.019). The likeliest single honest outcome is "not shown", not "refuted".
- Fix §3d's multiplicity line and §5 to these figures.

**M4. Fallback branch (`data.root=data`): define it fully before lock (§2a, §6 gate (a)).**
- Under the fallback, test numbers exist on disk before the opening, in two places: the stdout end-of-run block and `experiments/<run>/metrics.json`. Neither may be read.
- §6 gate (a) reads "its own end-of-run block". Under the fallback that block contains TEST.
- Before lock, state how gate (a) reads only val. Options:
  - an exact grep anchored to the VAL lines that cannot match TEST lines, shown on the S2 stdout format;
  - or a script that loads only metrics.json's val key and never prints the others;
  - or drop gate (a) for a CPU vs GPU recompute of member s10 on val.
- Disclose "test numbers on disk since training (unread)" in the opening if the fallback is taken.

**M5. The B5 co-primaries in m_common form (§3b 6-7): fix the definition now, and apply D1's logic to a B5-carried PASS.**
- The component definition is a co-primary definition, so it cannot be "stated in the build note". Write it in §3b now:
  - connectivity;
  - size floor for GT and for prediction components;
  - "≥ 50% covered" for component recall;
  - the component-precision definition;
  - pooled over cells.
- **m_common form instead of el_metrics: acceptable** (#5's B5 were n.d.; README asks for the pair, not a code path). Say plainly that it is not the #5 / PF2E B5 form, so no B5 number is comparable across openings.
- Per-arm val OPs at matched val precision 0.90 are a **symmetric rule**: fine. But the §7 recommendation at a B5 OP should carry SKR2E D1's condition. If a PASS is carried only by B5 co-primaries, E-SKR2 is recommended at that OP only if the G2a-form (< −0.03) and G2b-form (> ×1.5) values at the B5 OP pair do not trip. They stay reported, but they gate the recommendation.
- Grid −2 … +4: fine for ensembles (PF2E's B5 ensemble OPs were 1.1-1.5). The singles' #5 OPs (3.9-4.8) are on a different object; say so, so nobody reads "OP unreachable" as a regression.

## Should fix
1. **User priority (README "the user's own jobs have priority"):** HOLD new starts while any GPU process that is neither ours nor finllm holds > 1 GB. The auto-stop protects finllm; this keeps us from adding load under a user job. team-lead's call. If not applied, say why.
2. **Two worktrees (el_f3 e544133 / el_thin c9bbb02):** cite the S0 training-code identity at d93d9a1 as in S2, and the `labeled` finding above.
3. **§7 "FAIL by G1t: the Skeleton Recall route closes"** should add "(G1t null false-FAIL ~8%)". A route closes on a guard with an 8% null trip; the user should see that.
4. **§1 / §5:** add that a test PASS at b 0 is likely and likely mostly volume (as #6). The volume wording in §3d covers the claim; the expectation line should say it too.
5. **§3d test-only wording:** the volume wording is good. Also keep SKR2E's line for a PASS carried only by test primaries: "SKR2's E1 gain is not replicated at ensemble level".

## What is right as drafted
- **Symmetric b 0 for the verdict, with no per-arm headline:** this removes SKR2E's asymmetry. The post-SKR2E choice is disclosed in §0 (the OP was chosen knowing s5-9's b 0 result on the same cells); fresh seeds make it a new draw of models, not of cells. Good.
- **Matched-val-volume OP b_mv:** val-chosen, reported only. It is the right not-a-bias-shift check that can be made without an oracle. Good.
- **Data root:** the copy of idroot is correct (E above). The identity design (CPU 5 steps A/B per arm, GPU 1,000-step step-line match vs the reference stdouts, startup "test: 54" and the CE-weight line) is **enough**.
  - The GPU match is exact on step lines, as at H0. If it is not exact, the fallback (M4) applies.
  - The opening asserts it never reads `<root>/splits/test.txt` and uses el_f3's real test (a31fad14). Good.
- **Disclosures:** the 3rd look at the same test and E1 cells, and "reproducible on these cells, not unseen panels", are on every line. Good.
- **Guards:** SKR2E's guards at the symmetric pair; G1t ~8%; G1e collapse-only. Good.
- **Stage 2 frozen before any number; opening only on the user's OK; e1_openings #7 registered as not opened.** Good.

## Worth the night? (S)
- **Yes.** The GPU is otherwise idle, no labels are needed, and the answer feeds the one open deploy-recipe decision.
- **Expectations, to state in §5 as team-lead asked:**
  - P(PASS) **~35-65%**, from the judge's rule-1 Monte Carlo at 0.5-0.75 × #5's deltas. With the ensemble verdict it is similar or a little higher.
  - Seed-aware E1 replication ~25-45%.
  - A test PASS at b 0 is likely but mostly volume.
- What a positive result can and cannot mean is already said in §1. Keep it next to every result.

## Lock condition
Apply M1-M5; should-fix 1 is team-lead's call; 2-5 are wording. Then I sign. Re-review time is ~10 min, so the ~04:30 launch is feasible.

## Re-review: v0.9.1 (md5 91f875c9), 2026-11-03 02:34 IST
**Verdict: SIGNED for lock, conditional on L1 (team-lead's decision) and L2-L4 (wording).** v0.9.1 resolves M1-M5:
- **M1 auto-stop:** (a)-(d) are in §2b. It acts on the verified python PID (alive, owned by noob, cmdline has the run_name), never a pattern. The queue HOLDs if the watcher or logger is gone, and on any outside GPU process.
- **M2:** rerun from scratch, partial dir kept and renamed, resume not used.
- **M3:** the named E1 claim now rests on rule 1 on the singles (seed noise in the threshold); power is stated at ~18-35%. Verdict D does not use "replicated".
- **M4:** no fallback, so no launch unless IDENTICAL. No test number can exist on disk. D's gate (a) uses the R-opening m0, not the end-of-run block. The opening asserts the real test md5 a31fad14 and never reads the root's test.txt via config_used.
- **M5:** B5 is now S2's frozen el_metrics_w form in R (comparable with #5). It is not a D primary.
- Should-fix 1 (outside-process HOLD, stricter than team-lead's > 1 GB: any compute process) and 2 (S0 identity d93d9a1) are applied.

**Remaining:**
- **L1 (team-lead):** §2b(b) escalates SIGTERM → **SIGKILL after 30 s** to the same PID. team-lead approved "SIGTERM-only".
  - My view (S): allow it. A trainer that ignores SIGTERM keeps its GPU memory, and finllm is the thing being protected.
  - Condition: re-verify the PID's owner and cmdline immediately before the SIGKILL, and never signal any other PID.
  - The second-stop clause (fresh trigger, ≥ 30 s, the newest remaining S2C run) is fine.
- **L2 (wording, §5 / §7):**
  - Put the null false-FAIL next to every route-closing consequence: R's G1 ~9-15% (S2 W1), D's G1t ~8%.
  - Across both, the chance that a true null closes the route or keeps SUP100-PF by an inactive guard alone is ~15% (S; correlated, same test cells).
  - §7 "R FAIL … route closes" must say which guard and carry that rate.
- **L3 (wording, §3c):** if R PASS + D PASS rests only on volume-sensitive carriers, the recommendation sentence must carry the volume wording **and** the b_mv matched-val-volume result in the same sentence. Those carriers are test crack primaries at argmax, and E1 any-hit.
- **L4 (E, §2a):** add judge's read-only finding.
  - el_thin's `data/labeled` is a separate dir: its 1,747 common files are byte-identical to el-fault-detection's, plus 585 B3 `masks_escdd_s` files the root lacks.
  - So the SKR2 CPU identity's A must be el_thin's own `data.root=data`. That run is what shows SKR01 never reads `masks_escdd_s`.
- **Stage 1:** judge checks the watcher code (signal path, PID verification, HOLD file, logging) before APPROVED, as §6 says.

## SIGNED: v1 candidate (v0.9.2, md5 5995fcd5), 2026-11-03 02:36 IST
**Signed for lock, with 6 small wording / fact fixes (no design change). I check the post-sign diff after lock.**
- Every M1-M5 item and should-fix is applied as asked. team-lead's rulings are in: SIGKILL after 30 s only after re-checking; second stop; cap of 2 stops; outside-process HOLD > 1 GB; logger / watcher HOLD; dry run before APPROVED.

The six fixes:
1. **§2a root path is wrong.** It says `/home/noob/work/s2c/root/`. Runner built and checked `/home/noob/work/s2c_root` (log 02:33, SPLITS.md5 24568cdb). State the real path, and its SPLITS.md5.
2. **§2b(b) SIGKILL re-check:** add "and owner = noob" next to the cmdline re-check. team-lead's ruling names both.
3. **§2b dry-run required results:** add the items judge sent runner (02:3x):
   - the recorded PID is the python trainer, not the subshell (shown with `ps -o pid,ppid,args`; runner's s2q finding);
   - 2 low samples do not trigger, 3 do;
   - a SIGTERM-ignoring dummy reaches SIGKILL only after the re-check;
   - new starts HOLD on an outside process > 1 GB and when the logger / watcher is gone;
   - autostop.log carries the listed fields.
4. **§2a identity:** add "per-step wall time ('sec') is not compared", as B6's idchk and runner's run-2 compare do. The IDENTICAL list itself is unchanged.
5. **§7 contradicts §3a.**
   - §7 "R n.d.: recorded as 'not replicated on fresh seeds'" can clash with the named claim. The seed-aware CI (> 1.96 SE) is looser than rule 1 (~2.58 SE), so "REPLICATED (seed-aware)" can hold while R is n.d. Replace it with: "R n.d.: R's rule-1 verdict is n.d.; the E1 claim is stated by §3a's two-tier rule only."
   - Likewise, §7's handbook line "SKR2 replicated on fresh seeds" must become: "R PASS on <carriers> (same cells); E1 relF1@2 per §3a's named-claim tier". An R PASS carried by test primaries is not an E1 replication.
6. **§7 / §5:** add the combined null false-FAIL of the two inactive guards (~15%, S; correlated, same test cells) next to the existing 9-15% / ~8% line.

Stage 1: judge checks the watcher code and the dry-run log, and the rootcheck run-2 field list and SKR01 result, before APPROVED.

## Post-sign check: v1 LOCKED (md5 91b76abd, 02:37), checked 02:39 IST
- **No saved copy of 5995fcd5 exists, so this is not a byte diff.** I compared the locked text section by section with the 5995fcd5 text I read at sign (§0-§2b, §3a-§3c, §6-§9). A copy of the lock is kept at `judge/out/protocol_SKR2C_v1_lock_91b76abd.md` for future diffs.
- **Every change is one of the listed edits:**
  - §2a: root path `/home/noob/work/s2c_root` + SPLITS.md5 24568cdb; the 'sec' line.
  - §2b(b): owner + cmdline re-verify before SIGKILL.
  - §2b: the dry-run list, extended.
  - §3c: L3 volume / b_mv sentence; L2 cause-naming + ~15% line.
  - §5: ~15% combined; "~18-35% for an R rule-1 BETTER on E1"; the named claim ~25-45%.
  - §7: handbook line; R FAIL lines; R n.d. line.
  - Header / history.
- **§3a, §3b, §6:** the verdict rules, the named-claim definition (two-tier, seed-aware), the guards and the stage-2 build are unchanged.
- **Named claim:** I confirm coach's v0.9.2 definition, which is my M3. REPLICATED (seed-aware) = seed-aware CI > 0 + D's E1 relF1@2 pass + neither R nor D FAIL. Do not revert to v0.9.1's rule-1 definition.
- **Locked v1 accepted.** APPROVED still waits on stage 1: `judge/review_s2c_stage1_code.md` b0d866a4, G1-G8, + dry passes 1-3 + rootcheck run 2.
