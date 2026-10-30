# Team, 24 Oct 2026: critic's directions + the best-scoring model

**User, 24 Oct:** "take the critics decisions, and go. btw my goal in very clear terms is highest scores, a model which captures almost all of the cracks, inactive and other important defects balancing the miou for other classes as well."

The leader is team-lead, the user's main session. Rules are inherited from `team_2026-10-21/README.md`: gate, compute, communication and writing style. Read it first, along with memory (`/home/yugma/.noobsurd/projects/-home-yugma-mtp/memory/`, all files) and `team_2026-10-24_why/SYNTHESIS.md` plus `critique.md`.

## Track D: the critic's ranked directions (already approved by the user)
Executor: agent DX. Gate and verifier: critic C, who wrote SYNTHESIS.md.
1. SSL method work for crack is stopped. BsM5 (+LA) is the SSL result.
2. The 40-component audit and the label conventions belong to the user and are pending. Do not block on them; the critic sets the defaults.
3. **Labelled-set experiment:** random / crack-only / weak-source crack cells, 27 runs, 3 seeds per draw. The user accepted the 3-seed design by adopting the critic's decisions. The critic settles the main contrast (R1 vs R2, open in SYNTHESIS).
4. **Frozen-encoder probe per source:** about 1 GPU-h of inference. Approved.
5. Re-score the inactive-edge convention, CPU or inference.
6. SSL on the better-covered labelled set: only if 3 says coverage matters.

Folder: `trackD/`.

## Track M: the best-scoring model (the user's goal)
Designer: agent MD. Critic: agent MC.

**Targets** (test opened only per locked protocol; val for every choice):
- crack recall and IoU (the user wants "almost all cracks"), plus crack relF1@2;
- inactive IoU and recall;
- the other important defect classes;
- mIoU over all classes (24, BenchmarkEL `dataset_20211104`, masks_escdd);
- unseen modules (E1), as a secondary.

**Current best, the baseline to beat:** L3 at 100% labels (U-Net++, ImageNet ResNet34, CE+Dice, label-safe augmentation, 512 px): crack IoU 0.471, inactive 0.429, relF1@2 0.876. On unseen modules, crack falls to 0.152. Sources: handbook 00, 11 row 13 and the 100% table, `results/p6`, `results/p16`, `results/e1`. All-class mIoU and per-class IoU of the existing 100% checkpoints must be measured first. Rescore, don't retrain.

**In scope** (the designer proposes a ladder; each step is one change against the current best, with val selection, seeds and the rule-1 or bootstrap stats from handbook 07):
- backbones and decoders (ConvNeXt, SegFormer/Mask2Former, UperNet, HRNet);
- input resolution and no downscaling;
- thin-structure losses (clDice, skeleton recall, Lovasz, focal/Tversky);
- class weighting and LA;
- val-tuned per-class thresholds;
- TTA and ensembles;
- longer schedules and deep supervision;
- more labelled data with no test leakage: E-SCDD's extra real cells, decided by the critic against `data/decision.md`;
- pretraining on the unlabelled pool;
- BsM-style SSL on top.

**Discipline:**
- Never tune on test.
- Report all 50 / without the noisy cell / without the 7 twins.
- Report per-source numbers (CFVS/BMRK/ARTS/CSIR).
- Final claims need the critic's independent recompute.

Folder: `trackM/`.

## Compute (both tracks)
cv02 has 8 A6000s; gaint has 1 GPU. Book in `team_2026-10-24_go/gpu_ledger.md`. Follow the 4 GB rule for other users, one worktree per experiment, `REVISION`, tmux `-t "=name"`, and fixed lanes popping from flock-locked queues. No re-launch after an ssh timeout without first checking for duplicates. Relay cv02 outputs to gaint `cv02_noob_el` with MD5 checks. Fill idle GPUs.

## Reporting
Message team-lead at these points: protocol approved and launched, verified results, user decisions needed. Results go to the user only after critic verification. Team-lead commits the research repo.
