# x4_enskd: ensemble-to-single distillation (builder kd, 28 Nov 2026). STATUS: STOPPED BY GATE, not handed over for runs

E = measured, S = judgement. Progress log: harness/x4/arms/BUILD_kd.md.

## Why stopped
The lead's rule (27 Nov): build x4_enskd only if the 5-seed COMBO ensemble beats a single COMBO model by at least 0.010 relF1@2, or clearly on inactive. E (x4_ens_inference.md, read kd_ens1): ENS - COMBO = +0.0075 [+0.0035, +0.0124] relF1@2 (M 0.0100), inactive +0.0110 [-0.0246, +0.0456], and with D4 on both sides +0.0020 [-0.0013, +0.0060]. Distillation can at best recover the teacher's gain, so the gate fails. No card is committed, no jobs line exists, and no GPU smoke was run.

## What exists and is ready to resume (E)
- Code: branch x4_kd (worktree /home/noob/work/bench_wt_x4_kd), commits 51dfc5b and 779e88b on bench_x4 23717a7.
  - src/losses/kd.py: KDLoss = house ce_dice + weight * T^2 * mean over all pixels of KL(teacher^T || softmax(logits / T)); teacher^T = normalise(p ** (1 / T)). Opt-in `loss.kd.weight` > 0 (keys weight, T, teacher_root, teacher_index_md5). The val-loss path (no teacher) gives the base loss.
  - src/data/kd_targets.py: KDTeacherDataset. The uint8 teacher map goes through the same labelsafe flips and rotations as image and mask (albumentations masks=). check_store fails closed on: the pinned index md5, the fold manifest md5, the train.txt md5, a teacher stem that is a val or test stem of the root (fold safety), a missing teacher file, a file md5 mismatch.
  - scripts/kd_teacher.py: teacher of fold k = mean softmax of the 5 COMBO fold-k runs (swad, D4, fp32) on fold k's training cells only; refuses forbidden (test50 / E1) stems and any val or test overlap.
  - tests/test_x4_kd.py: 8 tests (hand-computed KL at T 1 and T 2 with weight, autograd gradient = w T (softmax(z/T) - p_t^T) / N, KL 0 when student = teacher, loss-factory switch, store checks, teacher-mask alignment and unchanged random draws, Model Stock hand values): 8 passed.
- Identity (keys off): identity_cpu 962379a6 / compare_id 3b83b364, COMBO card on cv5v3_v11_f0, seed 5, 5 CPU steps, ref 23717a7 vs 51dfc5b: **IDENTICAL**. Card opts equal at ref and new. pytest cards: 1 known failure (test_variants_exist, pre-existing on 03375d4).
- KD-on CPU smoke (fake one-hot-of-label teacher, 5 steps): runs; kd_base and kd_kl appear on the trainer's 'thin' log line.
- Teacher store (cv02 only, 248 MB): /tmp/noob_el/kd_teacher/c3x_swad_d4/, folds f0 to f3 done (425, 422, 429, 431 cells, about 62 MiB each, 6.5 to 7 min each, peak 5,546 MiB). Manifests: f0 b2d04c0d2805815f651dcc19d9ec4bd8, f1 c1c02bbeaee6642218e4b58e0866b052, f2 57856965cd6b18c9f9f1b34b9379ccbd, f3 1ebff28273d377a6cb152678b687c540. On its own training cells the teacher argmax agrees with the v1.1 labels on 96.7% of pixels, with strict crack recall 0.81 (f0). f4 not made (queue q_teach on HOLD).

## To resume (if the lead reverses the gate)
1. Remove /tmp/noob_el/kd/q_teach/HOLD (or rerun line kd_teacher_f4 with kd_run.sh) to make f4; TEACHER.md5 then has 5 lines; take its md5.
2. `python3 builder_scratch/kd/make_card.py /home/noob/work/bench_wt_x4_kd <TEACHER.md5 md5> <peak>` writes bench/methods{,_cv02}/x4_enskd.yaml = COMBO + 4 loss.kd opts (draft checked: cards validate OK, cvcard OK, cards diff = exactly the 4 loss.kd keys).
3. GPU smoke on cv02 (200 steps) of x4_enskd and of COMBO for the memory delta. S: expected below +1 GB over COMBO's 9,386 MiB (uint8 teacher 50 MB per batch plus float copies). Then commit, deploy and run `x4_make_jobs.py --out jobs/<qn>.tsv bench/methods/x4_enskd.yaml=enskd@<peak>`.
4. lambda 1.0, T 1.0 are the lead's start values; no other value was chosen. The P014 and CWD settings could not be checked (search rate-limited); CWD's channel-wise variant was not built because the lead specified pixel KL.
