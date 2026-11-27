# FINAL_RULE addendum 1: disclosure of the fin incident (final_builder2, 21 Nov 2026, about 07:55 IST)

Written after the incident and before any sealed-set opening. It changes nothing in FINAL_RULE.md, whose md5 82867156 stays
pinned. E = measured, with the record cited; S = judgement.

1. **Incident** (E, log.md 21 Nov 07:07):
   - By about 07:55, 8 of the 10 full-pool trainings of queue fin had stopped at step 20000 under F (821dfad):
     fin_pf_v11_pool_s5..s7 and fin_hrnet_swad_v11_pool_s5..s9. Their final validation on the in-sample monitor (val = test =
     107 training cells) refused v1.1 train masks holding the ignore value 255, because the val/test datasets had no ignore
     value. The smoke found a second stop behind it: the BN re-estimate guard of the final averaging step refuses the
     train/val overlap.
   - Each stopped run's latest.pth is at step 18000. PF s8 and s9 had started at 07:53 / 07:54 IST and were still running
     (correction by the lead, 21 Nov 09:18: the first version said "had not started"); under F they stopped the same way at
     08:53 IST, with latest.pth at step 18000. The 75 D4 dumps of fin (cv5v3 runs) are not affected.
2. **Plan for the 10 runs** (REVIEW_FIN2.md 9d11087e PASS; LAUNCH_REQUEST_fin2.md c8f1df79; one queue fin2, after fin's ALL DONE):
   - Steps 1 to 18,000 run under F, in /tmp/noob_el/bench_821dfad.
   - Steps 18,001 to 20,000 **will be resumed** under F2 (9967d59) from each run's step-18000 latest.pth. F2 will then run the
     final validation, the averagers' finalize, the save and the post-fit test eval.
   - New checkpoint location: **F2B /tmp/noob_el/bench_9967d59/experiments/fin_{hrnet_swad_v11,pf_v11}_pool_s{5..9}/checkpoints/**
     (latest.pth with all readouts, slim.pth). It replaces the paths in LAUNCH_REQUEST_final.md section 11.
   - The step-18000 copies in bench_821dfad stay as a fallback until the lead removes them.
   - Dump manifests of these runs will carry train_code_revision 9967d59 (the REVISION of the deploy that holds the run).
3. **Exactness:**
   - CPU (E, harness/final2/final2_smoke.sh): a crash under F resumed under F2 is bit-equal to an uninterrupted F2 run in every
     tensor of all six readouts (12,360), and in the optimizer, scheduler, scaler, RNG and averager states. The F and F2
     training states are bit-equal, and a held-out root gives identical results under F and F2.
   - GPU (E, src/utils/seed.py): deterministic: True is cuDNN-deterministic only, and some kernels accumulate with atomics. Any
     cv02 run, fresh or resumed, is therefore reproducible only up to that noise. The resumed 2,000 steps will differ from
     a hypothetical uninterrupted run by that noise alone, because the restored state is exact (S).
4. **What F2 changes** (E, final2_codeproof.sh 0 FAIL; 6 paths):
   - The val/test datasets accept 255 only when every val/test cell is a training cell.
   - weight_avg.train_fold_loader's overlap guard allows that same case.
   - A cv02 queue --resume job kind.
   - Nothing on the training trajectory changes.
5. **Readouts and the changed guard:**
   - C2 and C3 read `swad`: the uniform average that the averager's update() accumulates over steps 10,000 to 20,000.
     finalize only reads it and writes nothing into it, and train_fold_loader is not on its path.
   - C1 reads PF's `model`: PF has no averagers and no BN re-estimate.
   - The only readouts that pass through the changed guard are the BN re-estimates over the 532 train cells: **raw_bn,
     ema_9998_bn, swad_bn** (candidate runs only). None is an approved candidate's readout; swad_bn stays information only.
   - The eval change touches only the in-sample monitor outputs (val history, best.pth, metrics.json), which are never read.
6. **No change** to the rule (FINAL_RULE sections 0 to 7, D4, M, guards, cell sets, the CV5 TTA read and its verdict), to the
   approved E1 candidates C1 to C3, or to their readouts (C1 model; C2 and C3 swad).

## Completion (to be filled after fin2)
<!-- by the lead, from the cv02 and gaint logs; times in IST -->
Filled by the lead 21 Nov 09:18 IST (E; cv02 /tmp/noob_el/bench_q/fin2/launch.log, gaint relay log; log.md 08:55 to 09:17).
- fin2 armed 08:55:48 (request c8f1df79, F2 9967d59, F2B /tmp/noob_el/bench_9967d59); resumecopy 08:54:33 copied the 10
  step-18000 run dirs (md5s in /home/noob/work/bench_fin2_io/resumecopy.tsv). Every run's stdout says
  'RESUMED from .../latest.pth at step 18000/20000'.
- 10 x 'trained <run> rc=0' (fin2 launch.log): PF s5 09:05:16, s6 09:06:00, s7 09:06:30; HRNet+SWAD s5 09:08:10,
  s6 09:08:48, s7 09:09:29, s8 09:10:02, s9 09:10:37; PF s8 09:12:01, s9 09:12:43.
- 'final-step lines 1, Traceback lines 0' for each of the 10 runs; RUN.md5 rc 0 for each (HRNet 4 files, PF 3 files).
- fin2 'BENCH CV02 Q ALL DONE (10 trained rc 0, 0 dumped rc 0, 10 RUN.md5 of 10 jobs)': 09:12:47.
- relay 'RELAY ALL DONE: 10 of 10 runs relayed': 09:16:57, to /mnt/nas/noob_el_archive/bench_relay/fin2 (each unit md5sum -c
  OK on both ends).
- No SHARED lane / dump line, no HOLD, SHARE_DUMP absent throughout fin2.
