# Review of protocol AL1 v1 (agent 2, ALHVR critic), 21 Oct 2026, about 14:15 IST

## Verdict: APPROVED, with launch conditions

**What the approval covers:**
- the checks C1, C2 and C3 on cv02 at commit `3a94457`;
- C2 running past smoke length, to step 2,050, which is about 15 min on one GPU;
- the design, arms, rules and compute plan as written.

**The final 25 to 30-run launch may start only when all three hold:**
1. **C1 and C3 pass.** Agent 2 has read their log diffs in `alhvr/log.md`. C1 means: network A's state dict is `torch.equal` to A5's at step 300, and `sup_a` equals `loss_sup` at every logged step. C3 means: every term is finite, and memory gives the per-GPU packing.
2. **D7 is answered by the user** (`data/decision.md`). The C2 outcome then settles BsM5: if D7 is yes or C2 fails, BsM5 is re-run.
3. **GPUs are booked** in `gpu_ledger.md`, coordinated with agent 3. The cv02 rule holds: no GPU where another user holds more than 4 GB.

Any code change after `3a94457` needs a new commit, a note here, and a re-run of C1.

## What I checked, independently
- **Commit content.** `git show 3a94457` on gaint covers 6 files, +468/−13: `train.py`, `losses/alhvr.py`, `trainers/alhvr_trainer.py`, new `models/dual_smp.py`, `configs/alhvr_el.yaml`, `tests/test_alhvr_el.py`. I read the full diff.
- **Tests.** I ran `pytest tests/test_alhvr_el.py tests/test_alhvr.py` myself on gaint, CPU: 32 passed.

**Code review against the paper, the reference and the intent:**

| Item | Finding |
|---|---|
| Default paths | Every new key is opt-in. The `joint` path is untouched, and a config validator refuses new keys under `joint`. OK |
| Network B build | Built inside `torch.random.fork_rng`, so the global RNG after network A matches a supervised run. OK |
| Streams | Seeded per stream (`stream.py` `SeededSampler` and its own `torch.Generator`). Calling `next(unl_it)` at λ = 0 cannot shift the labelled stream. GPU check C1 still required |
| Precision | `GradScaler` is disabled under bf16, so network B cannot change network A's loss scale. OK |
| BatchNorm | Labelled forward per network; unlabelled clean and perturbed passes inside `frozen_bn_stats`, and only when λ > 0. Matches the P13 fix. OK |
| λ schedule | `lambda_at` gives 0 for steps < 2,000, then linear to λ_max at step 3,999 (tested). OK |
| Perturbation | `smp_forward_dual`: one encoder pass, the decoder on clean and on noise-perturbed `feats[1:]`. `feats[0]` is the input, which U-Net++ drops. Faithful in form |
| CPS | CE from the perturbed logits to the partner's clean argmax (no gradient through the argmax), mean over all pixels. `cps_routed` multiplies by ¬Ω1 and divides by all pixels, so the mask is the only change. Tested by hand case. OK |
| CPCL `pull: target` | Unscaled cosine to the target prototype, masked mean. Tested by hand case. OK |
| Pool exclusion | `unlabeled_exclude` refuses stems not in the pool. OK |
| Grad-share logging | `autograd.grad(retain_graph=True)` does not touch `.grad`; logging only. OK |

**Smoke logs** (gaint, batch 8+4, λ ramp compressed to 50+50 steps; `reports/smoke/smoke_AL.stdout`):
- **The loss is active.** At step 100: λ 0.051, share_a 0.070, gshare_a 0.13. At step 150: λ 0.1, share_a 0.119, gshare_a 1.61.
- **Regions are non-empty.** At step 150: Ω1 0.41, Ω2a 0.39, Ω2b 0.05, Ω3 0.15.
- All terms are finite.
- Peak memory is 23.4–23.8 GB with batch 8+4, so batch 8+8 on a 48 GB A6000 is plausible. C3 settles it.

**D0c arithmetic** (`alhvr/d0/d0c_grad.json`), recomputed by me:
- AL: 22.35/204.07 = 0.110 and 34.50/261.17 = 0.132, mean 0.121, rounds to 0.1.
- CPS: 22.35/49.53 = 0.451 and 34.50/47.19 = 0.731, mean 0.591, rounds to 1.0. The log midpoint of 0.3 and 1 is 0.548, so this is not a tie.
- Both match the protocol.

**Standing rules:**
- one change per arm;
- 5 v 5 seeds;
- 20,000 steps, matched;
- final step only (`latest.pth`; best-val never read);
- one machine, and A5 re-run on the same commit;
- test never used for selection;
- noisy-cell and twin rows pre-declared;
- one primary contrast, with the secondary contrasts counted.

All present.

## Points recorded. None blocks; each must appear in the analysis
1. **ALd5 is weaker than its matched strength.** In D0c, CPCL carries most of AL's loss at trained weights: `ce_a` 2.20 against `mse_a` 0.40. ALd5 inherits λ 0.1, which puts its unlabelled gradient share at about 0.38× BsM's (its matched λ is 0.3).
   - S2 (AL5 − ALd5) is still a valid one-change contrast for "CPCL as configured".
   - If ALd5 − A5 is n.d., the README must not conclude "DTCT does nothing". It can only say "DTCT at λ 0.1 does nothing".
   - Logged `gshare_a` for ALd5 must be reported next to it.
   - Optional, and only by a pre-launch amendment: an ALd5 arm at λ 0.3.
2. **Early dominance.** At step 150 of the smoke run, gshare_a was 1.6 against a smoke λ of 0.1 and an early-training supervised gradient. In the real run λ starts at step 2,000. The §7 activity rule (stop and amend if the 4k–6k share is below 0.03 or above 3) is the guard. I will read the step-6,000 shares for every SSL arm before letting the queue continue.
3. **Routing premise.** D0 found Ω1 holds 65–69% of GT crack on this base. A "better" S1 (CPSm5 − CPS5) or P would contradict D0's prior. That is fine, but the README must report the logged per-region GT-crack shares from `regions.csv` alongside it.
4. **CPCL feature.** The prototype feature is the 16-channel decoder output at full resolution, against the paper's "second-to-last layer". Agreed and grounded in D0-1. The README must state that the reference-code layer is unusable here (cross-network prototype cosine about 0).
5. **Twins (D7).** If D7 is no, every SSL-vs-A5 contrast inherits the twin advantage (`data/decision.md` D6). The "without 7 twins" row is then the most important robustness line, and the README must say so plainly.
6. **Log timestamps.** Both agents' log entries drifted ahead of the real IST clock. Mine are corrected and marked "~". From now on, use `TZ=Asia/Kolkata date`.

## Post-run verification I will do (before anything is reported)
- Recompute every rule from the raw per-run rescore JSONs with my own script.
- Check that each scored checkpoint is the step-20,000 `latest.pth`.
- Check rc = 0 for every run and that the logged shares are active.
- Check per-cell FP on `CSIR_00070_r8_c4` for every run.
- Produce the with/without tables for both cell lists.
