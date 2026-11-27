# What still needs the GPU (tranche 1 end, 12 Nov 2026)

Nothing below has run. Each needs the lead's word and free GPU memory (on 12 Nov 19:50 gaint had 2,787 MiB free: the
user's llama-server holds 22,382 MiB, root's finllm 5,876). Every GPU pass waits on the shared gate
(`/home/noob/work/gpu_gate`, free >= gate and >= 120 s since any start). Scripts are on gaint under
`/home/noob/work/bench_check/gpu/` (local copies `harness/bench_check/gpu/`).

## 1. GPU identity checks (one script, about 2 minutes of GPU, peak about 3.3 GB; gate 9,900 = GS)
```
tmux has-session -t "=bench_gpuchk" 2>/dev/null || tmux new-session -d -s bench_gpuchk "bash /home/noob/work/bench_check/gpu/run_gpu_checks.sh"
cat /home/noob/work/bench_check/gpu/out/run.log        # IDENTICAL / DIFF lines with counts only
```
- **I1b:** cuda bf16 dump of `f3_SUPPF_100pct_s0`, val54 → records == `b6_build/check/out_gpu/f3_SUPPF_100pct_s0.check.json`
  (that file equals the opening-1 m0 val block 54/54, build_b6 §9). Expect IDENTICAL.
- **I2:** cuda bf16 dump of `b6_SUP_f0_s5` (relayed cv02 run), `cv5v1_f0` (107 cells) → records == `b6_score/out/b6_SUP_f0_s5.b6.json`.
  The run's `data.root` is the cv02 path `/tmp/noob_el/el_b6/b6_roots/b6_root_0`; on gaint that resolves through the
  symlink `b6_roots -> /home/noob/work/b6` created for B6 scoring (still present, checked 12 Nov). Expect IDENTICAL.
- **I1c:** cuda fp32 (TF32 off) dump of the same run on val54 vs the bf16 one: DIFF counts only, to size the precision effect
  of the canonical benchmark setting.

## 2. Milestone 1 smoke (sets the gate of the first new architecture)
```
bash /home/noob/work/bench_check/gpu/ms1_setup.sh     # creates bq/ms1 + tmux bench_q_ms1 (gm, guard, q); refuses if either exists
tail -5 /home/noob/work/bq/ms1/launch.log
```
- Job `smoke_upernet_cnxt_f0` = card `upernet_convnext_t_in1k` (bench_timm, UPerNet, ConvNeXt-T torchvision IN-1k file),
  seed 5, `b6_root_0`, `--exit_after_step 1000` (exits rc 3 by design), start gate 16,000 MiB (peak unknown; A8's
  hrstem ConvNeXt-T peaked at 9,254).
- After it: peak = the smoke python's max MiB in `bq/ms1/gpumem.log`; write `memory.peak_mib` / `gate_mib = peak + 2048`
  into the card (version 2, commit), then the 20k-step job `ms1_upernet_cnxt_f0_s5` through a new queue dir.
- Then dump fold 0 (`bench_infer --set cv5v1_f0 --device cuda --precision fp32`) and score it beside the house fold-0
  runs dumped the same way. The house B6 runs were trained on cv02, the milestone on gaint: that comparison is
  descriptive only (machine rule).

## 3. Not GPU, but blocked on the same decision
- Smokes and gates for any other card (DPT DINOv3 ViT-S/16, SegFormer MiT-B2 once weights exist locally).
