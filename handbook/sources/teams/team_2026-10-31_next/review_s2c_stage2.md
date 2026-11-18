# SKR2C stage 2: independent review (coach role), 14 Nov 2026 00:15-00:30 IST

Reviewed against `protocol_SKR2C.md` (v1 LOCKED + §9), `rulings_s2c_stage2.md` (final) and the files themselves, not the runner's summary. Build record: `build_s2c_stage2.md`. Set: gaint `/home/noob/work/s2c/open/FROZEN.md5` 836be7e50c509339266097f4ba712f67 (27 files). Tags: E = measured / read by me, S = judgement.

## VERDICT: APPROVED

Team-lead may run the opening with the command in `build_s2c_stage2.md` §7, as written. No blocking defect. The notes N1-N6 below do not block. N1 has a step to do before the local readout.

Nothing was opened by this review. On gaint I only read files, plus my own outputs in `s2c/open_check/review/`. Every check I ran used opened s5-9 files (PF2 / #5 / #6) and printed md5s, counts, booleans or self-test PASS/FAIL. I ran nothing on the fresh s10-14 runs. No GPU was used. My one process: tmux `s2c_review`, bash PID 1696182 (CPU, nice 19, 8 threads), 00:18:35-00:18:39; it ended by itself, so nothing of mine is running.

## Evidence per item

### 1. Adapted scripts vs frozen sources (E, every .diff read in full, plus the full adapted files)
- **s2c_settings.sh** (vs af791321):
  - HC2 block out; SUPPF becomes a fresh arm (el_f3 e544133, exp dc9c344a, LA ec315d2e, rescore 1e41202b).
  - Runs `s2c_<arm>_100pct_s10..14` for both arms, checked by `settings_check` (k starts at 10).
  - Paths changed s2q -> s2c. #5 / #6 MANIFESTs added as reference / self-test inputs. Real-split, root SPLITS and launch.log md5s added.
  - REQ = the 27-file set.
  - Nothing else changed.
- **s2c_post.sh** (vs 039c1dc6):
  - Arms SKR01 + SUPPF, both scored from their own worktrees (SUPPF: m0_audit d36f7438 + m0_audit_tau d77241bb, as PF2's opening).
  - Removed per ruling 2: pass 1b, SHV1 (11), F51 / H36 (12) and G3. Encoder cosines (9) and the cell gate (10b) are kept as reported passes.
  - Comparator-reuse checks (PF2 B5 dumps, HC syn_work) are gone.
  - Added: launch.log conditions, `rs` real-splits calls, pass 14 (named boot), `exit $rc`. The FAST touch is gone.
  - No other logic changed.
- **s2c_e1_coprim.py** (vs 6e08c084):
  - Arm runs are s10..14 and refs s5..9; labels changed.
  - Added a reported 10-seed view (protocol §4).
  - relf1 / anyhit / inact / rule1 are verbatim; rule 1 = `delta > max(0.01, 2*sqrt((sdA^2+sdB^2)/3))`.
  - The self-test is unchanged.
  - Extra change: a GT-only assert (74 crack-free cells, 296 comps; see N6).
- **s2c_guards.py** (vs 0a8ea7dc), ruling 1 implemented:
  - The 3,931 refusal is removed from the main path. The self-test still asserts per-seed [3092, 2718, 5178, 4179, 4486] and mean 3,931.
  - The G2 E1 bar is `x = mean(arm) / mean(fresh base) > 1.5`.
  - The fixed bar `FIXED_BAR = 1.5 x 3931` is printed as a reference line with `'decides': False`.
  - G3 is not requested by the driver.
- **post_extra/s2c_b5w.sh** (vs c4472057):
  - Both arms go through the frozen hook and the wide steps.
  - The block that remade SUPPF from PF2 dumps is removed, together with its `ops` check.
  - The table is called with `--old` for both arms. `--old SUPPF` is valid: it reads `sum/<run>.test.pooled.json`, written by pf2_b5_pooled.sh.
- **post_extra/s2c_scuffign.sh** (vs 662bf5dc): settings path and arms only.
- **d/s2c_d_infer.py** (vs 5ba3c597), read in full:
  - Arms s10-14, or s5-9 in `--val-only`.
  - Gate (a) on each of the 10 members, tolerance 0.005 / 0.01; val GT comps 125; E1 GT comps 296 from the masks alone.
  - D2 is written as reported only.
  - b_mv grid `[-1.5 + 0.05 i, i = 0..40]` = -1.50..+0.50, chosen on val before any test or E1 read. Tie key `(|d|, |b|, b)` = ruling 6.
  - E1 sweep grid `[-1.5 + 0.25 i, i = 0..18]` = -1.5..3 (protocol §4).
  - Per-cell files: E-SUPPF b 0, E-SKR2 b 0 and b_mv.
  - Removed: E-PF identity and gate (c).
  - Added: refusal to rerun into a used out dir.
- **d/s2c_d_run.sh** (vs b2816cb3): two modes (idcheck / full); logs and PIDs outside `open/`; refuses an existing out dir; CUDA hidden.
- **local/s2c_d_boot.py** (vs 7520afc0):
  - Labels changed.
  - The U x U grid and the headline pair are removed; one verdict pair at b 0.
  - The b_mv pair is reported with CIs.
  - New `dverdict()` with the §3b wording, and self-tests (5) / (6).
  - verdict / passing / cluster_boot / cluster_boot5 / pair are unchanged apart from labels (diff grep).
- **local/s2c_post_local.sh**: rewrite of a short file, as stated in §4a (see N1).
- **Thin-term magnitudes (ruling 3):** no stdout is read beyond `grep -q "step 20000/20000"` (pass 1).
- **Verdict pairs:** exactly one at b 0, in both D (`pairs` / headline removed) and R (argmax m0).

### 2. Real-splits rule (E)
- **Every scorer takes its splits from the worktree (gaint grep):**
  - m0_audit d36f7438, m0_audit_tau d77241bb and m0_audit_b3 7aa7d6d8: `DATA = CODE / "data"`, with `--code` = the arm's worktree.
  - rescore_label_versions 1e41202b (both trees) and rescore_logit_adjust (ec315d2e / 419486b1): `DATA = ROOT / "data"`, ROOT = the script's own worktree. The train.txt they use for class priors is 842f27c4 in both trees, equal to the root's.
  - calib_dump c172717e: `D = Path(a.code) / "data"`. pf2_scuffign: `DATA = CODE / "data"`. s2c_d_infer: `D = el_f3/data`.
  - `config_used.yaml` is used only for the `model` / `mean` / `std` / `input_size` fields.
  - So no pass can read `s2c_root/splits/test.txt`.
- **Asserts in R:**
  - Pass 0 asserts both worktrees' test a31fad14 / val 9dcccf00 and ext 5266806b (`rs pre` plus scorer_md5).
  - Every later `rs` call re-asserts the list md5s (`lists()`) and the output stems after passes 3 / 4 / 6 (aborting), 10a (decision) and 10c (reported).
- **Asserts in D:** md5 asserts come before any read. The read log is checked against the real lists, and the driver runs `realsplits d` on d_out.
- **SUPPF call forms (gap closed by me):** gate C2 tested these modes only on SKR01 outputs. I ran them on the opened PF2 SUPPF s5-9 outputs (same scorers as fresh SUPPF), in `open_check/review/`:
  - `rs m0` PASS (15 files, incl. .tau0 / .tau1);
  - `rs b5` PASS;
  - `rs rescore` PASS;
  - `rs la` PASS on a SUPPF-only subset of PF2's la.json (40 entries, n 50 / 54, per_cell stems = the real lists);
  - pass 5's tau0 check heredoc with dep e544133: OK (step 20000, code_revision e544133, tau0 = default).

### 3. Verdict logic (E, re-derived from code)
- **R guards (s2c_guards.py):**
  - Constants `G1_BAR, G2_RELP, G2_X = -0.015, -0.03, 1.5`.
  - G1 trips iff the delta of seed means is <= -0.015 in all 50 AND clean 49.
  - G2 trips iff test relP@2 delta (all 50) < -0.03, OR mean E1 crack-free px (arm) / mean (fresh SUPPF s10-14) > 1.5.
  - This matches §3a and ruling 1.
- **R co-primaries:**
  - E1: rule 1 /3 on relF1@2 and any-hit (`--contrast SKR01 relF1 anyhit`).
  - B5: s2_b5w_check table on the wide grid -8..+12, verbatim S2 copy (s2c_copies.md5).
  - Test: Track M m2_rung 0ae9d505 on the fresh m0 (local).
  - S: no script assembles PASS / FAIL / n.d. for R, nor the named-claim tier. As in S2, that happens in coach's recompute (protocol §6 order). See N4.
- **Named claim condition 1 (s2c_named_boot.py):**
  - feats / metr / boot are verbatim from coach_s2_boot.py 7ea26cfb (compared with the laptop copy, md5 7ea26cfb).
  - The bootstrap unit is two stages. Stage 1 draws module clusters with replacement, with the same draw for both arms. Stage 2 draws 5 runs with replacement per arm, independently.
  - The metric is pooled per drawn run; arm = mean of the drawn runs.
  - E1 asserts 71 clusters; 2,000 draws; seed 0 in the main path.
  - Condition 1 = the 2.5th percentile > 0.
- **D (s2c_d_boot.py):**
  - Test primaries use `verdict()`. Pass = CI above 0 in both sets, or in one set with a same-sign point estimate in the other. Fail = hi < 0 in either set.
  - E1: relF1@2 and any-hit, 71-cluster bootstrap (asserted), 2,000 draws, seed 0.
  - G2a: relP@2 delta < -0.03. G2b: crack-free px > 1.5 x E-SUPPF (74 cells asserted). G1t: point delta <= -0.015 in both sets. G1e: E1 inactive cluster hi < 0.
  - `dverdict`: FAIL if any primary fails or any guard trips; else PASS if there are carriers; else n.d.
  - Fixed wordings: carriers named; the volume line iff carriers are within {test crack IoU, test relF1@2, E1 any-hit}; "not replicated at ensemble level" iff no E1 pass; the ~15% line iff only G1t / G1e tripped; `e1_relF1_primary_passes` goes to the JSON.
  - All of this matches §3b / §3c.

### 4. Self-tests and the D identity (E)
- **Re-run by me on gaint CPU** (`open_check/review/`, tmux s2c_review):
  - s2c_named_boot --selftest: **PASS** (3 lines equal to boot.txt 7ce0faa0, RNG 20261102).
  - s2c_guards --selftest: **PASS**.
- **Gates run 3:** `gates_rc.txt` shows A / B / C / C2 / D / E rc=0 and GATES PASS.
- **D identity:** `d_val_identity/s2c_d_identity.txt` reads IDENTITY PASS, with "108 reads, sets ['val'], 54 stems == the 54 val stems". d_val_identity holds no E-* file (only gate, identity and val_decisions).

### 5. FROZEN (E)
- On gaint, `md5sum FROZEN.md5` = 836be7e5 and `md5sum -c` passes.
- The file set in open/ equals the FROZEN list (27 + FROZEN.md5).
- No file is writable and there is no `__pycache__`.
- The laptop FROZEN.md5 equals gaint's byte for byte, and `md5sum -c` passes locally.
- **At run time:** the driver, post, b5w, scuffign and d_run write only under `s2c/` (post, post_work, d_out and top-level logs / pids). `cp` copies out of open/, never into it. No set file can change.

### 6. Command-list safety (E)
- **GPU gate:** gpu_gate.sh 00fabfdd (md5-asserted in pass 0) flocks the shared `/home/noob/work/gpu_gate`. A start needs free >= GS and >= 120 s since any start, and HOLD is honoured. The benchmark uses the same gate (gate.log, `pass bench ...` lines).
- **9,900 MiB floor:** post `pre()` refuses GS < 9,900, and the driver sets GS=9900.
- **Peaks:** about 4-6.5 GB, so >= 3.4 GB stays free at a start.
- **No signals:** a grep of the set finds no `kill`, `pkill`, `killall`, `signal` or `6206`.
- **CPU only for D:** d_run.sh exports `CUDA_VISIBLE_DEVICES=""`, nice 19, 8 threads, and d_infer has no device option. CPU passes use the CPU array.
- **PIDs recorded:** opening.pid, post_pids.txt, d_run_full.pid, d_py_full.pid.
- **Outputs:** only under `/home/noob/work/s2c/` (post, post_work, d_out, plus logs / pids at that level), and nothing into a worktree (N3 aside).

### 7. Nothing opened yet (E, 00:16 IST)
- On gaint, `s2c/{post, post_work, d_out, opening.log, post.log, opening.pid, d_realsplits.txt, opening_refused.log, HOLD}` do not exist, and tmux `s2c_open` does not exist.
- On the laptop, `results/s2c/` does not exist.
- `e1_openings.md` #7 and `test_openings.md` row 18 both read "registered, NOT opened" with 836be7e5.

## Notes (not blocking)
- **N1. `local/s2c_post_local.sh` has only had `bash -n`.**
  - It must run on crampbook. The orchestrator moved to gaint on 14 Nov; run there, the script stops at its first check and does nothing.
  - Its m2_rung calls use `2>/dev/null` under `set -e`, so a failure exits silently. After a partial failure, `results/s2c/raw_*` blocks a rerun until moved aside.
  - It does not run `s2c_d_boot.py --selftest`, and it does not pin the md5 of Track M `m1_analyze.py` (laptop now 8e566254; m0_analyze d5adbe6b; m2_rung 0ae9d505).
  - **Before the local readout:** run `s2c_d_boot.py --selftest` (argument list as in its docstring) and check m1_analyze.py md5 = 8e566254.
- **N2. Split-list md5s are not re-checked before each pass.** They are asserted at pass 0 and re-asserted after every scoring pass (`lists()`), not separately before each one. Nothing writes those files, so the rule holds in effect (S).
- **N3. The B5 hook's pythons run without PYTHONDONTWRITEBYTECODE** (calib_dump and el_metrics, unchanged from S2). They import `src.*` from the worktree, which already has cpython-312 `__pycache__` from training (counted on gaint). Worst case is an untracked pyc; `git status --untracked-files=no` and every md5 are unaffected.
- **N4. The R verdict is not computed by any script.** The R PASS / FAIL / n.d. combination, the test two-set rule, the named-claim tier and the R FAIL wording (§3a, §3c, §7, incl. the G1 null false-FAIL line) are assembled in coach's recompute from the frozen outputs, as at S2. Coach must apply §3a / §3c verbatim.
- **N5. The GPU is currently too full to start.** At 00:16 gaint had 4,735 MiB free, and the benchmark queue is now `bench_q_w1g2` (need 9,000 per job). The driver will wait at the gate and may be outpaced by benchmark starts. This only means waiting, not a safety issue.
- **N6. One change not listed in the protocol.** s2c_e1_coprim asserts 74 crack-free cells and 296 GT comps per fresh run. Both are GT-only quantities and cannot change a verdict; a mismatch would only stop pass 7 (decision rc 1, so D is not run). Accepted (S).
