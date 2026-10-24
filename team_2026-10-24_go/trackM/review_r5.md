# MC review of `protocol_r5.md` (internal resolution x2)

MC, 24 Oct 2026. **Verdict: APPROVED.** Launch after the el_mt5 identity check (switch off, 1,000 steps) is IDENTICAL and recorded, and the smoke shows `upsample_input: 2` resolved, finite loss, steps/s and peak memory.

## Code (E: `git diff 0642889..1be64e1`, read on gaint)
- `build_model` wraps the core in `UpsampledInput` only when `upsample_input > 1`; otherwise it returns `_build_core(cfg)`, unchanged. The state-dict keys of the default path are unchanged; the x2 path adds a `net.` prefix, so any scorer must build through `build_model` from `config_used.yaml`, as stated.
- Determinism: the bilinear interpolate acts on the input, which needs no gradient, so its non-deterministic CUDA backward is never called. The `avg_pool2d` backward is deterministic. A re-run of seed 0 should reproduce exactly; check one log line at step 1,000 if a re-run happens anyway.

## Required in the results
1. **Compute is not matched**, so every claim carries it: about 4x FLOPs and the measured GPU-h against SUP100. Steps are matched; FLOPs are not. If R5 passes, the honest wording is "x2 internal resolution at about 4x compute". Whether more compute alone (R6, a longer schedule) gives the same is open; say so.
2. **Named secondaries as listed**, plus the share of GT crack px with p < 0.001, against SUP100's 0.189. This is the "confident miss" the rung is meant to reach. Also report crack precision beside every recall.
3. **E1 ext crack recall:** report it (secondary). Resolution should not help unseen modules much; a gain there would be informative.

## Not claimed (agreed)
- That x2 is the best factor.
- That the gain comes from resolution rather than the interpolation.
