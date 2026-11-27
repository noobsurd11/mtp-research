#!/bin/bash
# Commit the x2 work in /home/noob/work/bench_wt_x2 (branch bench_x2) in three small commits. Touches no other worktree.
set -eu
W=/home/noob/work/bench_wt_x2
cd $W
[ "$(git rev-parse --abbrev-ref HEAD)" = bench_x2 ] || { echo "not on bench_x2"; exit 1; }
T="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Wi4ZqFN13pWYd2FWeXAPNX"
git add src/data/aux_targets.py src/losses/soft_ce_jml.py src/losses/cc_dicece.py src/losses/scnp.py \
  src/losses/loss_factory.py src/trainers/trainer.py scripts/train.py
git commit -q -m "x2: aux target hook (batch[\"aux\"]) and opt-in losses soft_ce_jml, cc_dicece, scnp

AuxTargetDataset adds targets built from the augmented mask (no RNG); the trainer passes the keys a loss
declares in aux_keys. loss.supervised=soft_ce_jml (soft CE + Jaccard metric loss, optional crack band),
loss.cc.weight > 0 (component-wise Dice + CE on crack), loss.scnp.enabled (SCNP, with fg_only_channels for
the critic's fallback). All keys absent = house path, flag-off CPU identity IDENTICAL vs 31c0c36.

$T"
git add tests/test_x2_losses.py
git commit -q -m "x2: unit tests for the aux hook, soft_ce_jml (incl. synthetic shifted labels), cc_dicece, scnp

$T"
git add bench/methods/soft_band_jml.yaml bench/methods/jml_hard.yaml tests/test_x2_cards.py scripts/x2_p1_band_precheck.py
git commit -q -m "x2: cards soft_band_jml and jml_hard, card tests, pre-check P1 script

Cards = house_r34_unetpp_pf_v11 plus loss.supervised=soft_ce_jml and the loss.soft_ce_jml keys only.
P1 with the critic's fix (cells with unchanged crack masks excluded and counted).

$T"
git log --oneline -4
git status --porcelain | wc -l
git rev-parse HEAD
