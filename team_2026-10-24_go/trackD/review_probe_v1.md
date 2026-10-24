# Review of protocol_probe.md v1 (C, 24 Oct 2026)

## Verdict: APPROVED, with three non-blocking notes

Checked against `critic_defaults.md` §0 and §2: question, encoders, probe recipe (one change from P4: the 23-cell 5% set on revised masks), evaluation sets, decision rule written before any number, identity check against `results/sk1/la_sa_test.json`, twin exclusion, inference only, booking. All match.

## Notes (put them in the results file, no protocol change needed)
1. **DINOv2 resolution.** At 518 px the patch grid is 37 × 37 (stride ~14 on a 512 cell). A 1-3 px crack cannot be resolved at that stride, so a DINOv2 fail is partly a resolution artefact. State this next to its row; it does not change the rule.
2. **BMRK test sample size.** State how many BMRK test cells and crack components carry the primary (BMRK holds 27% of test crack px, from few cells). If ≤ 10 cells, say the primary rests on them and lean on the pool row for robustness, as §"Robustness" already does.
3. **AP vs AP.** The probe's crack AP is from linear features; A5c's is from a fine-tuned decoder. That asymmetry favours A5c, as the protocol's own limit says. Keep the limit sentence in the results verbatim.

## Before launch
- GPU 6 on cv02: confirm < 1,000 MiB used and no other user > 4 GB on it at start; book in `gpu_ledger.md`.
- Record the SHA256 of each downloaded weight file.

## After the run, I recompute
- BMRK test crack AP per encoder and probe seed from the `probe.json` histograms, with my own AP code, and the pass/fail per encoder.
- The A5c τ 0/τ 1 identity against `la_sa_test.json`.
