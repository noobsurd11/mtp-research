# Team 29 Oct: learn features from the unlabelled cells, then use the labels

## The user's ask (29 Oct, paraphrased)
"Learn features from the ~12k unlabelled cells without labels (pretraining, clustering, anything), then tie them to the 582 labelled cells. Find all such directions, run them, and have a critic who helps on training settings instead of writing essays. Lead just orchestrates."

**User's standing goal:** the highest scores. A model that catches almost all cracks, inactive and other important defects, with balanced mIoU on the other classes. Directions are judged by expected test gain, not by method novelty.

## What this is not
Pseudo-label SSL is done. Mean Teacher, CPS, BsM (FixMatch-style), ALHVR and SKCDF all propagate the supervised model's own predictions to the pool. At 20-100% labels they are null; at 5% only BsM helps.
- Do not re-run these.
- Why they failed: `team_2026-10-27_unlabelled/SYNTHESIS.md` and `team_2026-10-24_why/SYNTHESIS.md`.

The user's own intuition, feature learning on the pool, **was never run**. Only two runs came near it:
- **Frozen-encoder probe:** ImageNet weights, not pool-learned (`team_2026-10-24_go/trackD/verify_probe.md`).
- **P15:** UCF-EL labelled pretraining. n.d. at 5%, worse at 10% (`handbook/11_results_synthesis_and_claims.md` claim 7).

## Read first (under `/home/yugma/mtp/research/`)
- **Overview:**
  - `SESSION_RECORD_2026-10-21_to_27.md`: everything from 21 to 27 Oct, with numbers.
  - `handbook/00_START_HERE.md`.
  - `handbook/14_code_and_infrastructure.md`: code, configs, data paths, determinism.
  - `handbook/07_methodology_rules_and_statistics.md`: rule 1.
- **Plan item 3, already designed:** continued SparK-style MIM of ResNet-34 from ImageNet on about 12.4k cells, then fine-tune at 5% against A5c, 5 v 5. See `team_2026-10-27_unlabelled/SYNTHESIS.md` row 3 and `ideas.md`.
- **Best model:** `team_2026-10-24_go/trackM/results_final.md`. The protocol pattern is `trackM/protocol_*.md` and `review_*.md`.

## References to beat (test, revised masks, final-step weights, cv02)
| Setting | Model | Crack IoU | Note |
|---|---|---|---|
| 5% labels (23 cells) | A5c supervised | 0.304 | |
| 5% | A5c + logit adjustment (tau 1) | 0.319 | free-bias yardstick for crack claims |
| 5% | BsM5 (D7 pool) | 0.331 | only SSL that beat supervised |
| 100% | SUP100 single model | 0.474 | |
| 100% | FINAL (5-seed ensemble, crack bias +0.75) | 0.492 | relF1@2 0.897, inactive 0.456, mIoU_rob 0.583, E1 crack recall 0.215 |

E1 (106 unseen-module cells) is where the gap is: 75% of E1 crack sits in half-cut + scuff cells.

## Team (SendMessage by name; lead is `team-lead`)
- **`scout` (researcher).**
  - Surveys every way to learn from unlabelled cells without their labels, then tie it to the labelled set.
  - Candidate families (not exhaustive):
    - masked image modelling for CNNs (SparK, FCMAE);
    - dense contrastive (DenseCL, PixPro, VICRegL);
    - self-distillation (DINO / iBOT style);
    - clustering then mapping clusters to labels (DeepCluster, SwAV, unsupervised segmentation such as STEGO / PiCIE);
    - kNN or prototype label transfer;
    - anomaly models of normal cells (PatchCore-type) as a crack-recall aid;
    - synthetic defects on unlabelled backgrounds;
    - domain adaptation / test-time adaptation for E1;
    - anything else with evidence.
  - Writes `directions.md`: ranked, each row with
    - mechanism;
    - why it could work on EL, and why not (2 px cracks under 1% of pixels; ImageNet init already strong);
    - evidence (E/R/S, paper ids);
    - cost in GPU-h;
    - expected gain at 5% and at 100%;
    - a kill criterion.
  - Draft within the first hour, refine after. Uses the Research MCP.
- **`runner` (executor).**
  - Implements and runs the directions, starting with plan item 3 (MIM5) **now**, in parallel with scout's survey; then the next ranked items.
  - Writes `protocol_<id>.md` before every launch, then results.
  - Owns servers, code, queues, scoring and backups.
- **`coach` (critic and advisor).** Practical, not essays.
  - Advises on training settings: mask ratio, lr, schedule, augmentation that keeps 2 px cracks, batch, how long to pretrain, decoder init, freeze/unfreeze, BN.
  - Reviews protocols and code diffs. Catches bugs and leaks before they cost GPU hours. Sanity-checks smoke logs.
  - Gives `APPROVED` / `CHANGES` with a short list.
  - Recomputes every primary contrast from per-cell outputs with its own script before a result goes to team-lead.
  - Only writes when it changes a decision.

## Gates
1. **Launch gate:** no GPU run beyond a smoke of a few hundred steps without coach's `APPROVED` on the protocol version.
2. **Freezing protocols:** every protocol is frozen before its numbers are opened. It states:
   - the arms;
   - one change per arm;
   - matched optimizer steps;
   - seeds (5 v 5 for small effects);
   - the decision rule;
   - a pre-stated expectation.
3. **Statistics:** standing rules (`handbook/07`, memory).
   - Rule 1 (house R1, `scripts/ssl_rules.py` `cmp`): Δ > max(0.01, 2·sqrt((sdA²+sdB²)/3)). The divisor is 3 even at 5 v 5 (handbook/07 §5), so verdicts stay comparable with BsM5/CsM5/P16. Better on one primary, worse on none. A /5 variant may be shown as descriptive only. (Corrected 29 Oct 07:25 IST; the first version wrongly said /n.)
   - Final-step weights.
   - Selection on val only. E1 is never used for selection.
   - Report all four cell sets: all 50 / without `CSIR_00070_r8_c4` / without the 7 twins / without both.
   - Count test openings.
4. **Primaries:** test crack IoU, crack relF1@2, inactive IoU. Secondaries: mIoU_rob, crack recall, E1 crack recall, per source.
5. **Pool hygiene:**
   - Pretraining may use the 11,938 external cells plus train images.
   - Never val, test or E1 images.
   - The 7 train twins of test cells (`team_2026-10-21/data/decision.md` D7) stay out.
   - State the exact image list and its md5.
6. **Kill quickly.** A direction that is n.d. on all three primaries at its cheapest test is closed. Write one line saying so and move on.

## Servers and rules
- **gaint** `noob@172.18.22.20`: one RTX PRO 4500 Blackwell, 32 GB.
  - The user's own jobs run there too (`q3_*.py`, plus root's `finllm_chat.py`). Never kill or slow them badly. Fit around their memory, and tell team-lead if you need the whole GPU.
  - Code: `/home/noob/work/el-fault-detection` plus worktrees. Track M is `el_m` (`1be64e1`) and D1 is `el_d1` (`86197f3`).
  - New code goes in a new worktree (`git worktree add ../el_f1 -b f1`), never the main tree.
- **cv02** `cv02@10.8.1.106`: 8 A6000s, shared lab account.
  - Never use `ssh -A`. Never put a key there.
  - Never start on a GPU where another user holds more than 4 GB. At 07:00 IST on 29 Oct all 8 were taken.
  - Deploy one commit to `/tmp/noob_el/<dir>` with a `REVISION` file. Use the `.venv` at `/tmp/noob_el/el-fault-detection/.venv`.
  - Data is in `el_p7/data`, pool in `el_p7/data/unlabeled/images_512` (11,938).
  - `/tmp` is wiped on reboot: relay finished runs to gaint `/home/noob/work/cv02_noob_el/` through the laptop, MD5 on both hops.
- **Arms:** all arms of one experiment run on one hardware type and one commit, with data md5-identical.
- **tmux:**
  - One window per run, maximal safe parallelism.
  - `tmux has-session -t "=name"` (exact match).
  - Chain queues, never race them.
- **Downloads:** ask team-lead first for any new dataset (ELPV is pending the user's OK) and for any download over 0.5 GB. Torchvision/timm ImageNet weights already cached are fine.
- **Local PDFs** in `papers/` and `literature/` are never uploaded.
- **Research MCP:** cite only papers the tools return, with their ids. Fetch full text only for a shortlist.

## Style
- Terse. No em-dashes.
- Tag claims E (measured, with path) / R (literature, with id) / S (speculation).
- Write only in this folder (scripts in `scripts/`), plus run dirs on the servers.
- `log.md`: one line per event, with IST time.
- Report to team-lead only at milestones:
  - survey draft;
  - protocol approved;
  - smoke OK;
  - runs done;
  - verified result;
  - blocker needing the user.
