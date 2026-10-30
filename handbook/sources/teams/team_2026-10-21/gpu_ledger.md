# GPU ledger (book before launch, free after)
| machine | GPU | track | tmux | start IST | expected end | status |
|---|---|---|---|---|---|---|
| gaint | 0 | alhvr D0 probe (inference only) | alhvr_d0 | 21 Oct 13:45 | 21 Oct 14:05 | done 13:47, freed |
| gaint | 0 | alhvr D0b probe, noise-only (inference only) | alhvr_d0 | 21 Oct 13:49 | 21 Oct 14:05 | done 13:51, freed |
| gaint | 0 | skcdf code check (2 runs x 20 steps, batch 2+2, <4 GB) | sk1chk | 21 Oct 13:47 | 21 Oct 14:02 | done 13:48, freed |
| gaint | 0 | alhvr functional smoke (150 steps, AL + CPS, sequential) | alhvr_smk | 21 Oct 13:53 | 21 Oct 14:05 | done 13:56, freed |
| cv02 | 4,5 | skcdf identity checks (2,500 steps each, ~10 GB) | sk1chk | 21 Oct 13:55 | 21 Oct 14:45 | died at start (argparse), freed 13:57 |
| cv02 | 6 | skcdf smoke (300+300+60 steps, ~25 GB) | sk1smoke | 21 Oct 13:55 | 21 Oct 14:35 | stopped 13:57 per leader (no launches), freed |
| gaint | 0 | alhvr D0c grad probe (inference only) | alhvr_d0 | 21 Oct 13:58 | 21 Oct 14:15 | done 14:06, freed |
| gaint | 0 | alhvr C1-gaint λ=0 identity (2 runs x 300 steps, sequential) | alhvr_c1 | 21 Oct 14:11 | 21 Oct 14:35 | done 14:14, freed |
| cv02 | 4 | alhvr C1/C3 | al1chk | 21 Oct 14:50 | – | not used: same-minute clash with sk1chk, moved to GPU 0 |
| cv02 | 5 | alhvr C2 | al1chk2 | 21 Oct 14:50 | – | not used: clash, moved to GPU 1 |
| cv02 | 4,5 | skcdf identity checks (GPU 4: chk_BsD ~10 GB; GPU 5: 2 x chk_A ~12 GB) | sk1chk | 21 Oct 14:48 | 21 Oct 15:48 | done 15:04, freed |
| cv02 | 6 | skcdf smoke (300+300+60+20 steps, ~30 GB) | sk1smoke | 21 Oct 14:48 | 21 Oct 15:33 | done 15:10, freed |
| cv02 | 0 | alhvr C1 then C3 | al1chk | 21 Oct 14:55 | 21 Oct 15:45 | done 15:18, freed |
| cv02 | 1 | alhvr C2 | al1chk | 21 Oct 14:55 | 21 Oct 15:35 | done 15:00, freed |
| cv02 | 4,5,6 | skcdf SK1 final, D7-yes queue, 20 runs, 4 fixed lanes per GPU (≤ ~44 GB per GPU) | sk1 | 21 Oct 15:11 | 22 Oct ~05:00 | done (all 20 rc 0); GPUs 4,5,6 freed 22 Oct |
| cv02 | 0 | alhvr AL1 v2 main queue: lane big0 (two-network, ~30 GB) + lane small0 (A5/BsM5, ≤ 10 GB), shared queue files | al1 | 21 Oct 15:20 | ~23 Oct 20:00-24:00 | done 23 Oct 00:43 (CPSm5_s4 rc 0, big0 queue empty, small0 done), freed |
| cv02 | 1 | alhvr AL1 v2 main queue: lane big1 (two-network, ~30 GB) + lane small1 (A5/BsM5, ≤ 10 GB), shared queue files | al1 | 21 Oct 15:20 | ~23 Oct 20:00-24:00 | done 23 Oct 06:37 (ALdh5_s4 rc 0, last run), freed |
| cv02 | 2 | alhvr AL1 v2 main queue: lane big2 (two-network, ~30 GB) + lane small2 (A5/BsM5, ≤ 10 GB), shared queue files | al1 | 21 Oct 15:20 | ~23 Oct 20:00-24:00 | done 22 Oct 23:40 (big2 queue empty, small2 done), freed |
| cv02 | 3 | alhvr AL1 v2 main queue: lane big3 (two-network, ~30 GB) + lane small3 (A5/BsM5, ≤ 10 GB), shared queue files | al1 | 21 Oct 15:20 | ~23 Oct 20:00-24:00 | done 23 Oct 03:17 (ALdh5_s2 rc 0, big3 queue empty, small3 done), freed |
| cv02 | 7 | alhvr AL1 v2: extra lane big7 (two-network only, ~30 GB), same queue file; GPU idle (1 MiB) at booking; agent 3 agreed 7 is ours if free | al1 | 21 Oct 19:28 | with queue | done 23 Oct 02:38 (ALdh5_s3 rc 0, lane done), freed |
| cv02 | 5 | skcdf critic per-cell rescore (inference only, <3 GB) | c4score | 22 Oct 18:45 | +30 min | done, freed |
| cv02 | 5 | skcdf post-run scoring (per-image, hist, LA, E1; inference only, < 6 GB) | sk1post | 22 Oct 18:45 | 22 Oct 19:45 | done, freed |
| cv02 | 5 | skcdf critic LA check (inference only, <3 GB) | c4la | 22 Oct 18:57 | +15 min | done, freed |
| cv02 | 5 | alhvr AL1 v2: extra lane big5 (two-network only, ~30 GB), same locked big queue; at booking 494 MiB (cv13 two.py 482 MiB < 4 GB), SK1 rows freed | al1 | 22 Oct 19:30 | with queue (~23 Oct 06:00) | done 23 Oct 00:56 (ALdh5_s1 rc 0, lane done), freed |
| cv02 | 5 | skcdf critic null-diagnosis probe (inference only, <4 GB) | c4probe | 22 Oct 19:30 | +30 min | done, freed |
| cv02 | 3 | alhvr critic probe (b): pool confident-miss probe (inference only, <4 GB; shares GPU with AL1 lanes) | a2probe | 22 Oct 19:34 | +40 min | done, freed |
| cv02 | 5 | skcdf S-a logit-adjustment rescore, 64 existing checkpoints (inference only, < 4 GB; co-located with AL1 lane) | sksa | 22 Oct 19:35 | 22 Oct 21:05 | done 20:02, freed |
| cv02 | 5 | skcdf critic S-a recompute 5% arms (inference only, <3 GB) | c4sa | 22 Oct 20:05 | +30 min | done, freed |
| cv02 | 0 | alhvr AL1 post-scoring (per-image, hist, E1 of 35 runs; inference only, < 6 GB) | al1post | 23 Oct 06:44 | +30 min | done 23 Oct 06:51, freed |
