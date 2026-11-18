# Lead's instructions to the harness agent (consolidated 13 Nov 2026, 08:40 IST)

This file replaces the lead's chat messages, which do not survive an agent restart. Read it with `DESIGN.md` (accepted), `BUILD_LOG.md` (what is done, with md5s) and `notes.md`.

## Decisions in force
- **Base:** worktree `/home/noob/work/el_bench`, branch `bench`, from e544133 with thin and f8 cherry-picked; each flag-off arm must stay IDENTICAL on the 5-step CPU identity check.
- **Dumps and scorer:** as DESIGN.md 3.1 to 3.3. Canonical dumps fp32 on GPU with TF32 off; bf16 only for legacy identity checks. Scorer adds relaxed P / R / F1 at 1 and 3 px beside 2 px, cell-type and flag subsets from `benchmark/cells.tsv`, and the ground-truth-only reference rows (GT shifted 1 px, dilated 1 px).
- **Method cards:** one YAML per method in `bench/methods/`; the registry, the queue's config check and the dump manifest read from it.
- **User decisions (12 Nov):**
  - Label set **v1.1** for all new runs: scuff and star px to ignore (255), `BMRK_00031_cell0091` back to its `20220723` mask. The legacy test is scored on both label sets.
  - **Installs approved** as isolated venvs that share torch read-only (the `venv_sam2` pattern) plus public weights. Gated weights (larger DINOv3) are listed for the user first. The house venv is never changed.
  - E1 few-shot track T3b: last week only. Nothing to do now.
- **Splits:** `benchmark/splits/cv5v2.json` (md5 441d118f; B6 folds with 4 straddling cells moved to fold 1) and `legacy.json` (9bacb290); bootstrap groups `splits/cv5v2_groups.tsv` (330 groups); forbidden list = `b6_forbidden.txt`. Format: `benchmark/splits/README.md`. Label script and notes: `benchmark/scripts/make_masks_v11.py`, `benchmark/LABELS_V11.md` (section 4: the house trainer accepts ignore 255 in train masks only; held-out masks must be strict).

## Task list, in priority order (the GPUs are idle; wave 1 comes first)
1. Finish the launcher checks the cap interrupted (dry test t2) only as far as needed to trust the queue; log it.
2. GPU identity checks I1b and I2 on gaint through the shared gate.
3. v1.1 masks on gaint: run `make_masks_v11.py --base-masks <real labeled/masks_escdd>` (asserts the local rebuild is pixel-identical for all 582 cells; stop and report if any cell differs), then write v1.1 into a NEW folder outside every existing data dir (for example `/home/noob/work/bench_data/masks_v11/{masks,masks_strict,ignore}` with CHANGES.tsv and MANIFEST.md5). Touch no existing mask folder.
4. Roots from `cv5v2.json` with the generalised root builder (same asserts as B6: no group cut, 0 forbidden stems, held-outs partition the pool, re-read after write, refuse to overwrite). Two sets: `cv5v2_v11_f{0..4}` (train stems linked to v1.1 masks with ignore, held-out stems to the strict variant; or the two-line trainer change if cleaner, with flag-off identity kept) and `cv5v2_v1_f{0..4}` (current `masks_escdd`, for the label-fix ablation). As in B6, test.txt = val.txt = the held-out fold, so no sealed cell is ever read. Write ROOTS.md5.
5. Scorer on v1.1: ground-truth root and ignore masks come from the run manifest; ignore px are not scored.
6. **Wave 1 job list** (cards + jobs.tsv, md5-pinned; nothing launched before the lead's go):
   - W1a: `house_r34_unetpp` and `house_r34_unetpp_pf` on cv5v2_v11, folds 0 to 4, seeds 5 and 6 = 20 runs.
   - W1b: `house_r34_unetpp_pf` on cv5v2_v1 (old labels), folds 0 to 4, seeds 5 and 6 = 10 runs.
   - W1c (pathfinders, only after registry tests and a 1,000-step smoke each): under the PF recipe on cv5v2_v11, seed 5, folds 0 to 4: UPerNet + ConvNeXt-T (ImageNet), U-Net++ via the HR stem + ConvNeXt-T, DeepLabV3+ R34.
   Each run: house recipe otherwise, 20k steps, final weights, dump the held-out fold in canonical fp32 after training, score on CPU. Give per-run peak memory from smokes and the gate.
7. Placement. gaint: up to 3 lanes if memory allows (R34 peak about 6.8 GB; gate = peak + 2,048 MiB; starts 120 s apart; guard armed; MAXC file). cv02: read-only survey first through gaint (`ssh cv02@10.8.1.106`, key on gaint): venv versions, `/tmp/noob_el` state, disk, GPU state; then prepare a deploy by `git archive` + CODE.md5, roots with a fresh `labeled/` holding only the 532 pool stems, the B6-pattern queue with the python PID recorded, and a pull of results from gaint (rsync or tar over ssh, md5 on both ends, after every run). One comparison stays on one machine: propose which of W1a + W1b and W1c goes where.
8. **Stop before launching** and send the lead a launch request under 25 lines: commit id, identity results (I1a, I1b, I2, I3), roots and mask md5s, job list md5 and counts, gates, expected wall time per machine, exact launch commands.

## Hard rules
1. gaint GPU: root's `finllm` (PID 6206, 5,876 MiB) must never die; keep at least 2 GB free at all times; every GPU job goes through the shared gate (`gpu_gate.sh`, flock, start gate = peak + 2,048 MiB, 120 s between starts); log free memory at 1 s while a job of ours runs. One GPU job at a time until wave 1 is approved.
2. cv02 is a shared lab account: never forward an agent, never copy a key there, never touch other users' processes or files, never start on a GPU where another user holds more than 4 GB. Nothing is written or started on cv02 before the lead's go.
3. Nothing changes in `el-fault-detection` (working tree), `el_f3`, `el_thin`, `el_f8`, any other existing worktree, existing data or mask folders, or the house venv.
4. Sealed sets: no inference on test50 or e1_106; never open a training `.stdout`, metrics, rescore, m0 or b6 JSON to read numbers. Identity comparisons run by script and print only IDENTICAL / DIFF with counts. Val 54 and the fold roots are open.
5. Processes: long jobs in tmux on gaint, session names `bench_*`, always exact match (`-t "=name"`), `tmux has-session -t "=name"` before creating. Record the python PID of anything started; stop only by that PID after printing its full command line. Never `pkill`, `killall` or any pattern kill. No watcher as a bare trailing `&`.
6. Capture `rc=$?` before any `$(date)`. Log times from the clock.
7. Transfers: `team_2026-11-12_frontier/scripts/gssh.sh '<cmd>'` (direct VPN address first, tunnel fallback, no stdin), `gput.sh <local> <remote>` (md5-checked; only into /home/noob/work/el_bench, /home/noob/work/bq, /home/noob/work/bench_*), `gget.sh <remote file> <local>`. Develop under `harness/el_bench_src/` mirroring the worktree, push with gput, test on gaint.
8. Commits on gaint in el_bench, small, each message ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. No pushes anywhere.
9. Budget: the usage cap is tight and an agent can be cut off at any moment. Prefer scripts that run unattended in tmux over step-by-step supervision, and append to `BUILD_LOG.md` after every step so a restart loses nothing.
10. Style: terse, plain English, no em-dashes. E = measured, S = judgement.

## Update 13 Nov 2026, 09:30 IST: wave 1 as it will run (replaces tasks 6 to 8 above)

GPU identity check I1b passed on gaint at 09:21 (IDENTICAL, 54 cells, 0 differences); I2 and I1c were still running (log: `/home/noob/work/bench_check/gpu/out/run.log`).

### Machines
- **cv02 is the benchmark machine** (8 RTX A6000): every baseline and every arm that enters a table runs there, so all table comparisons share one machine.
- **gaint is the development machine** (one 32 GB GPU, 3 lanes of ResNet-34 runs): identity checks, smokes, pathfinders, CPU analyses, all scoring, plus a small same-machine reference so that arms developed on gaint have a fair comparator.

### Wave 1 runs
| Set | Machine | Card | Labels | Folds | Seeds | Runs |
|---|---|---|---|---|---|---|
| W1-G | gaint | `house_r34_unetpp_pf_v11` | v1.1 | 0 to 4 | 5, 6 | 10 |
| W1-C1 | cv02 | `house_r34_unetpp_pf_v11` | v1.1 | 0 to 4 | 5, 6, 7, 8, 9 | 25 |
| W1-C2 | cv02 | `house_r34_unetpp_v11` | v1.1 | 0 to 4 | 5, 6 | 10 |
| W1-C3 | cv02 | `house_r34_unetpp_pf` | v1 (current `masks_escdd`) | 0 to 4 | 5, 6 | 10 |

- W1-C1 with 5 seeds gives the reference for every later arm and the seed and fold noise that sets the pass margin (an A/A comparison of seeds {5,6} against {7,8} is part of the read).
- W1-C2 is the house fine-tune (benchmark row). W1-C3 is the label-fix ablation against W1-C1 seeds 5, 6.
- The `_v11` cards equal the house cards plus `data.mask_subdir=<per-root link folder>` and `data.mask_ignore_value=255`; nothing else changes.
- Every run: split `cv5v2`, 20k steps, final weights; root has test.txt = val.txt = the held-out fold, so no sealed cell is read. After training: dump the held-out fold in canonical fp32 on the training machine (keys `pred`, `oth`, `m_crack`, `p_crack`, `p_inact`, and `logp` for the PF v1.1 runs, which later arms use as teachers), keep `latest.pth`, relay to gaint, score on gaint CPU.
- cv02 placement: only GPUs where no other user holds more than 4 GB, at most 2 of our runs per GPU, starts 120 s apart, python PID recorded. Outputs are pulled from gaint after every finished run (md5 on both ends), because cv02 `/tmp` is wiped on reboot. Test and E1 images are never copied to cv02: its `labeled/` holds only the 532 pool stems.

### Launch authority (lead, 13 Nov 09:30)
The lead pre-authorises the launch of each wave 1 set on one condition: an independent reviewer (a different agent from the builder) runs the written checklist below against the real files and every item passes. The reviewer then launches and confirms the first job's live check. If any item fails, nothing is launched and the reviewer writes the reasons to `harness/REVIEW_W1_<machine>.md`.

Checklist (each item checked by command, result recorded):
1. el_bench HEAD equals the commit named in the launch request; no tracked change; flag-off identity results (I1a, I1b, I3; I2 if finished) are IDENTICAL in the logs.
2. v1.1 masks on the machine match `benchmark/out/masks_v11/` by manifest md5; the base-mask assertion (local rebuild of `masks_escdd` equals the real folder, pixel for pixel, 582 cells) passed.
3. Every root: train and held-out lists equal `benchmark/splits/cv5v2.json` for that fold (md5 of the sorted lists); the held-outs partition the 532 pool; 0 forbidden stems (`forbidden_v1.txt`); no physical module group split across train and held-out (`cv5v2_groups.tsv`); test.txt = val.txt.
4. v1.1 roots: every train stem's mask link points to the v1.1 mask with ignore, every held-out stem's to the strict variant; v1 roots point to the current `masks_escdd`; no link is dangling.
5. Cards: `_v11` cards differ from the house cards only in the two keys; weights md5s match.
6. Jobs file: names, cards, seeds, roots and gates as in the table; md5 pinned; no existing `experiments/<name>` would be overwritten.
7. Safety: gate, guard and 1 s memory logger alive on gaint (finllm PID 6206 protected, 2 GB floor); on cv02 the lane rule (other users' processes over 4 GB), PID files hold python PIDs, the relay is armed; no pattern kill anywhere in the scripts.
8. A 50-step smoke of one job of the set passes its config check and startup-line check, then is removed.
