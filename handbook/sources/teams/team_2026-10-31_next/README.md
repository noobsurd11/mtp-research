# Team 31 Oct: PF2, thin-crack and scuff arms, and the unseen-panel (E1) ideas

Lead: `team-lead` (orchestrates only). SendMessage by name. Log every step in `team_2026-10-31_next/log.md`, one line each: `YYYY-MM-DD HH:MM IST <name>: ...`.

## The ask (31 Oct, user)
- The user pasted Om's answers and new ideas (`om_2026-10-31.md`, read it in full) and said: "read and launch agents to review validate and work on this direction further, no budget boundaries, we have 2 more months to work on this project. but id refrain from manual labelling unless very much needed".
- Standing goal: the highest-scoring deployable model. It should catch almost all cracks, inactive and other important defects, with balanced mIoU. Judge ideas by expected gain, not novelty.
- Om's diagnosis (S): the remaining failure is domain generalisation to unseen panels (E1), not data quantity.

## Where things stand (read first, under `/home/yugma/mtp/research/`)
- **Records:**
  - `SESSION_RECORD_2026-10-30_to_31.md` (commit f87711f): protocol_100, D checks, B2 v2, the suggestions review.
  - Earlier: `SESSION_RECORD_2026-10-28_to_30.md`, `SESSION_RECORD_2026-10-21_to_27.md`.
- **Handbook** (`handbook/`): start at 00_START_HERE.md. Then:
  - 07 for rule 1;
  - 11 for claims;
  - 13 for pitfalls;
  - 14 for code, infra, data paths and determinism;
  - 17 for the dataset audit;
  - 18 for Track D/M;
  - 19 for protocol_100.
- **protocol_100** (`team_2026-10-29_features/`):
  - `protocol_100.md`, `verify_100_o1.md`, `verify_100_o2.md`, `verify_d.md`, `d_prereg.md`;
  - `review_suggestions_2026-10-30.md` (vetter);
  - `spec_b3_scuff.md`;
  - `coach_100.md` (encoder erasure);
  - `pool_large/` (the HF pool audit);
  - `b2_mining/v2/`;
  - `log.md`.
- **Results, all n.d. on test at 100% labels:** MIM100-PF vs SUP100-PF, SUP100-PF vs SUP100-g, CP100 vs SUP100-g.
  - **PF:** keeps encoder layer3/4 (cos 0.93-0.96; the house recipe ~0).
  - **E1, descriptive:** PF lifts crack recall 0.169 → 0.213 and inactive IoU 0.041 → 0.245. The gain is only on the 29 scuff/half-cut cells; on the other 77, crack IoU drops 0.261 → 0.238.
  - **D:** RN50-5 helps E1 scuff/half-cut recall (+0.060). R34-10 shows this is not an ensemble-size effect.
- **Best deployable model:** FINAL, a 5-seed R34 ensemble with crack bias +0.75. Clean-test crack IoU 0.492.

## Team
| Name | Role | Scope |
|---|---|---|
| `runner` | executor, gaint GPU owner | PF2 build + launch, then thin-crack / B3 runs. The only agent that starts GPU jobs on gaint; others ask runner for a slot |
| `coach` | critic + protocol author | protocol_PF2; protocol for Skeleton Recall / clDice / B3 on SUP100-PF; distance-map costing with builder. APPROVED gate before every GPU launch; independent recompute of every verdict |
| `builder` | code | Skeleton Recall loss, clDice loss, B3 scuff class (per spec_b3_scuff.md), distance-map target cost estimate. gaint worktree, CPU unit tests, GPU smoke only through runner |
| `calib` | hands-on diagnostics (CPU) | Om ideas 1 (E1 threshold / calibration), 2 (intensity stats, normalisation premise), 7 (cell-level and operating-point metrics scorer) |
| `domain` | validation + prototypes (CPU) | Om ideas 3 (neighbour reference), 4 (periodic removal), 5 (synthetic half-cuts), 11 (appearance augmentation); item-13 close-out note |
| `found` | validation (literature + feasibility) | Om ideas 6 (high resolution), 8 (foundation encoder), 9 (test-time adaptation), 10 (AI-assisted labelling) |
| `judge` | adversarial reviewer | Reviews every calib / domain / found output; recomputes E claims; PASS-to-protocol or DROP, with reasons |

## Pipeline
1. A validation report per idea, in `team_2026-10-31_next/ideas/<idea>.md`. It covers:
   - premise checked in data (E);
   - prior tries in the repo (cite the file);
   - literature (R, with Research MCP ids);
   - cost (GPU-h, wall);
   - expected E1 and test effect (S);
   - a kill criterion;
   - a protocol sketch, or DROP.
2. `judge` reviews and recomputes. Its verdict is appended to the same file.
3. `coach` turns PASS items into protocols.
4. GPU approval:
   - Om already approved PF2, the two thin-crack arms (Skeleton Recall, clDice) and B3: these launch on coach's APPROVED.
   - Everything else needs the user's OK. team-lead batches these requests.

## Rules (all agents; break none)
- **Security:**
  - cv02 is a shared lab account: never `ssh -A` into cv02, and never put a private key there.
  - Never expose credentials.
  - PDFs in `literature/papers` stay local; never upload or redistribute them.
- **Processes:**
  - Stop processes only by a recorded PID, or one printed with its full command line first. Never `pkill -f`, `killall` or any pattern kill: on gaint, cv02 or the laptop.
  - Never kill root's finllm or any process you didn't start.
  - Watchers go in tmux or with a recorded PID. Never a bare trailing `&`.
- **gaint** (noob@172.18.22.20; 1 GPU, 32.6 GB):
  - Root's `finllm_chat.py` (~5.9 GB, PID 6206) must never OOM or die. Keep >= 2 GB GPU memory free at all times.
  - Gate each training start at its measured peak + 2 GB, behind the lock, >= 120 s apart.
  - Gate any scoring pass beside other GPU jobs at 7,154 MiB free.
  - Log free memory every 10 s whenever our jobs share the GPU.
  - The user's own jobs have priority.
  - CPU jobs on gaint: `nice -n 19`, <= 8 threads, never during a runner-declared critical window.
- **cv02** (cv02@10.8.1.106): never start on a GPU where another user holds > 4 GB. Use it only through runner.
- **No package installs** (pip, venv, conda) and no downloads > 0.5 GB without asking team-lead first. Downloads of model weights (DINOv3, SAM) need the user's OK: cost them, don't fetch them. ELPV: no.
- **Laptop disk is 96% full (13 GB free).** Keep laptop outputs small. Put bulk intermediates on gaint under `/home/noob/work/` (578 GB free).
- **Data use:**
  - **E1 (106 unseen-module cells) is sealed:** no training, tuning, threshold choice or method selection on it. Diagnostic and descriptive reads are allowed and must be labelled descriptive. Pre-registered co-primary use in PF2 is allowed.
  - **Test (50 cells):** only at a protocol's pre-registered opening. Never ad hoc.
  - **Selection:** use val (54) and the Hanifi `_rf` validation set. Hygiene: drop the 7 CSIR_00300 cells and the 4 val/test-module cells.
  - Do not name the 3 Hanifi B2 panel cells: the user hasn't marked B2.
- **Experiment rules:**
  - rule 1: Δ > max(0.01, 2·sqrt((sdA²+sdB²)/3)), better on one primary and worse on none, in both sets (all 50 and clean without `CSIR_00070_r8_c4`);
  - 5 seeds per arm; one change per arm; same commit, data and hardware across arms; matched steps; final-step weights;
  - LA tau 1 is the crack-bias yardstick;
  - lock the protocol before launch.
- **Primaries** stay crack IoU / relF1@2 / inactive IoU.
  - From now on every protocol also pre-registers component recall at component precision >= 0.90 and relR@2 at relP@2 >= 0.90, with the threshold chosen on val, never on test or E1. These two are co-primaries for the Skeleton Recall and clDice arms.
  - Cell-level metrics (idea 7) are reported.
- **No manual labelling.** Do not ask the user to label. Prefer label-free or AI-assisted routes. If a step truly needs human labels, state the minimal hours and why, and send that to team-lead.
- **Literature:** Research MCP. Cite only papers it returns, with their ids. Fetch full text only for a shortlist (daily cap).
- **Style:** tags E (measured, with the file path), R (literature id), S (judgement). Terse. No em-dashes.
- **Status lines:** capture `rc=$?` before any `$(date)`.
