# GPU ledger, 24 Oct team
| machine | GPU | track | tmux | start IST | expected end | status |
|---|---|---|---|---|---|---|
| cv02 | 7 | M (MD) | m0audit | 24 Oct 11:23 | 24 Oct 11:41 | M0 audit + val tuning done; GPU 7 free |
| cv02 | 6 | D (DX) probe, inference | dxprobe, dxedge, dxprobe2 | 24 Oct 11:25 | 24 Oct 11:46 | done, GPU 6 freed |
| cv02 | 0, 1 | D (DX) identity (500 steps) + 2 smokes (300 steps) | d1chk | 24 Oct 11:34 | 24 Oct 11:37 | done, freed |
| cv02 | 0, 1, 2, 3 (2 lanes each) | D (DX) labelset, 27 supervised runs | d1 | 24 Oct 11:38 | ~24 Oct 21:15 | done 20:02; post 20:02-20:06 on GPU 0; GPUs 0-2 freed 20:06 (3 freed 18:55) |
| cv02 | 7 | M (MD) | midchk | 24 Oct 11:45 | 12:15 | identity 1,000 steps IDENTICAL (trackM/identity_check.txt); GPU 7 free |
| cv02 | 7 | M (MD) | r1 | 24 Oct 11:56 | done 12:02 | R1 inference done; GPU 7 free |
| cv02 | 6 | M (MD) | msmoke | 24 Oct 11:57 | done 12:02 | smokes done; GPU 6 free |
| cv02 | 7 | M (MD) | midchk2 | 24 Oct 12:02 | done | identity el_mt with grad logging IDENTICAL |
| cv02 | 6, 7 (4 lanes each) | M (MD) | mq | 24 Oct 12:06 | ~25 Oct 00:00 | wave 1: R2 x5, R3 pilots x3, m_sup_gn_s0 (protocol_r2/r3 APPROVED) |
| cv02 | 7 | M (MD) | m0audit | 24 Oct 12:07 | +10 min | SUP100 re-score with per-cell 1,000-bin crack histograms (R3 per-source AP), inference |
| cv02 | 7 | M (MD) | midchk4 | 24 Oct 12:16 | done | el_mt4 identity IDENTICAL, R4 smoke OK |
| cv02 | 6, 7 (2 lanes each) | M (MD) | mq4 | 24 Oct 12:37 | ~25 Oct 02:00 | R4 x5 done 21:26 |
| cv02 | 6 | M (MD) | midchk5 | 24 Oct 19:04 | done | el_mt5 identity IDENTICAL; R5 smoke OK (upsample_input: 2) |
| cv02 | 3, 6 (2 lanes each) | M (MD) | mq5 | 24 Oct 19:18 | ~25 Oct 08:00 | R5 done 03:47; GPU 3 back to DX |
| cv02 | 0, 1 (3 lanes each) | M (MD) | mq2c | 24 Oct 20:13 | ~25 Oct 02:00 | R2c x5 done 01:06 |
| cv02 | 2 (1 lane) | M (MD) | mq5 | 24 Oct 20:13 | ~25 Oct 04:00 | R5 s4 done |
| cv02 | 7 (3 lanes), 0, 1 (1 lane each) | M (MD) | mq3b | 24 Oct 20:33 | ~25 Oct 08:00 | R3 Part B done 02:36 |
| cv02 | 7 | M (MD) | final | 25 Oct 03:47 | +30 min | FINAL done 03:52 |
| cv02 | 0, 1, 2, 3, 6, 7 | M (MD) | (all Track M sessions idle) | – | 25 Oct 04:25 | Track M finished; no Track M job running; all M GPUs free. Idle tmux shells left: m0audit, midchk*, mq*, r1, final |
