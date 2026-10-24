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
| cv02 | 6, 7 (2 lanes each) | M (MD) | mq4 | 24 Oct 12:37 | ~25 Oct 02:00 | R4 x5 (protocol_r4 APPROVED), beside =mq |
| cv02 | 6 | M (MD) | midchk5 | 24 Oct 19:04 | done | el_mt5 identity IDENTICAL; R5 smoke OK (upsample_input: 2) |
| cv02 | 3, 6 (2 lanes each) | M (MD) | mq5 | 24 Oct 19:18 | ~25 Oct 08:00 | R5 x5 upsample x2 (protocol_r5 APPROVED); GPU 3 offered by DX |
