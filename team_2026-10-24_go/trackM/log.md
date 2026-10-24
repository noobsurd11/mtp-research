# Track M log (IST)
- 24 Oct 11:21 MD started; peers MC ae52dc69513c0f95b, DX adb0336fb9b375643, C a6b7033e7a26beaab. Reading.
- 24 Oct 11:25 M0 audit: smoke L3 100% s0 reproduces P6 rescore exactly (crack/inactive IoU, relF1@2, test+val). Full run launched cv02 GPU 7 tmux m0audit: L3 s0-2, A100 s3-4, Sx100 s0-4.
- 24 Oct 11:34 v1 audit killed mid-run after MC review; v2 (asserts, step, REVISION, p-bands) done, 10 JSONs in trackM/m0, MD5 OK. m0_tables.md written. Val tuning m0_tune running GPU 7 (~9 min/item, 12 items).
- 24 Oct 11:42 val tuning done (m0_tune.json MD5 OK), GPU 7 freed. baseline.md draft written; sent to MC for recompute.
- 24 Oct 11:47 baseline APPROVED by MC. design CHANGES (C1-C7). el_m worktree (gaint, branch m @86197f3) deployed cv02 /tmp/noob_el/el_m (REVISION, data->el_p7/data; first attempt had repo data/ dir, fixed). Identity: m_idchk_A100s3 500 steps + val@500 IDENTICAL to p16_A_100pct_s3 (losses, lr, val line). Killed at 550.
- 24 Oct 11:51 identity rerun to 1,000 steps + val@500/1000 + Labelled line: IDENTICAL (identity_check.txt). DX probe: frozen rn50/ConvNeXt-T rank BMRK crack better than R34 -> R3 candidates.
- 24 Oct 11:56 protocol_r1 APPROVED with F1 (pass rule both sets / same-sign n.d.; worse on either fails); edit applied. protocol_r2, protocol_r3 written. R2 test commit 34feea9 (tests only) on branch m; suite 225 passed.
- 24 Oct 11:56 R1 launched cv02 GPU 7 tmux =r1 (m1_r1.py md5 checked).
- 24 Oct 11:59 R2, R3 APPROVED by MC with fixes; applied: pass-rule wording; R2 F2 log_grad_norm switch (commit 3c1b72b, tests 227 passed) + m_sup_gn_s0 descriptive run; R3 seeds 1-5, val-only pilot scoring (--sets), per-source AP histograms. Smoke checks: step-0 CE identical (3.66866), dice list resolved; convnext stem (96,1,4,4) = RGB sum.
- 24 Oct 12:06 el_mt (3c1b72b) identity with log_grad_norm on: IDENTICAL 1,000 steps; SUP100 clip rate 0.52-1.0 early. R1 done (results_r1.md to MC). Wave 1 launched: tmux =mq, GPUs 6-7, 4 lanes each, queue el_mt/queues/mq.q (9 runs).
- 24 Oct 12:13 R1 VERIFIED by MC (verify_r1.md); notes added; r1/md5_cv02.txt. m0b (SUP100 re-score with h1000 hist) relayed, MD5 OK. MC R4 ruling: 25-28 -> ignore (255) via opt-in switch, 29->1, 24->2.
- 24 Oct 12:27 R4: switch data.mask_ignore_value (0642889, tests 232 passed); data_r4 built on cv02 (585 train, val/test md5 identical, 180,016 ignore px in 32 cells); el_mt4 deployed; protocol_r4 APPROVED (E1 cell CSIR_00300_r25_c1 shares module, report with/without). MC data note: CSIR_00062_r5_c4 train image offset vs its mask (all P-series arms; negligible).
- 24 Oct 12:37 el_mt4 identity IDENTICAL 1,000 steps (switch off); R4 smoke OK (Labelled 585). R4 launched =mq4 (2 lanes x GPUs 6,7).
- 24 Oct 12:39 relayed cv02 trackM/ (39 files, no .npy logits) to gaint cv02_noob_el/trackM, MD5 OK both hops.
- 24 Oct 12:40 R5 switch model.upsample_input committed (el_m, tests 235 passed); not deployed; protocol later if R2/R3 justify.
- 24 Oct 16:11 pilot P-cnxt done; trainer's built-in test eval + lanes rescore JSON exist (sealed, not read: el_mt/reports/sealed_pilot_test/). Val-only score: crack 0.4087 relF1 0.8665 mIoU_rob 0.6202 -> score 0.6318 < 0.6414: does not qualify.
0b11849b4ef731ccd892d1664c94e1cd  sealed_pilot_test_cnxt.tgz
  sealed (MC request): 2d465f73bcea1b9083937991526212c8  sealed_pilot_test/m_r3p_cnxt_s0.json
- 24 Oct 19:02 R2 done (5/5 rc 0), scored (r2/, MD5 OK). Verdict WORSE (crack -0.0106, relF1 -0.0130 without noisy); val EXCLUDE. Gridline +0.10 IoU. Grad norm 6.7 vs 2.1, clip 97% vs 36%. results_r2.md to MC.
- 24 Oct 19:04 R2 VERIFIED WORSE by MC; results_r2 updated. R2c withdrawn on MC advice. protocol_r5 sent; el_mt5 (1be64e1) deployed, identity + R5 smoke running GPU 6.
- 24 Oct 19:18 el_mt5 identity IDENTICAL (switch off); R5 smoke 300 steps OK, 0.76 steps/s shared. R5 launched =mq5 on GPUs 3 (from DX) and 6, 2 lanes each.
- 24 Oct 19:18 R2c re-instated: APPROVED low priority by MC (F1 val motivation, F2 crack-recall guard applied); waits for spare lanes.
- 24 Oct 20:13 DX freed GPUs 0-2. R2c launched =mq2c on GPUs 0-1 (3 lanes each). effb4 pilot done (test JSON auto-sealed), scoring val-only on GPU 2.
- 24 Oct 20:13 effb4 pilot val score 0.6467 > 0.6414: qualifies (rn50 pending). R5 s4 started on GPU 2 (extra mq5 lane).
- 24 Oct 20:32 all 3 pilot test rescore JSONs sealed unread; tarball el_mt/reports/sealed_pilot_test_all.tgz:
    de16e362cfa55b2df632f0aa27862f6e  sealed_pilot_test_all.tgz
    2d465f73bcea1b9083937991526212c8  sealed_pilot_test/m_r3p_cnxt_s0.json
    35be805b9393e8a55584038c48593f4c  sealed_pilot_test/m_r3p_effb4_s0.json
    3396d45dbd899ccbb6845737a5d283a3  sealed_pilot_test/m_r3p_rn50_s0.json
- 24 Oct 20:33 pilots final (val only): cnxt 0.6318, effb4 0.6467, rn50 0.6474 (crack 0.4324 relF1 0.8893 mIoU_rob 0.6204). Locked rule (highest qualifying) -> rn50 (margin over effb4 0.0007). Part B launched =mq3b: m_r3_rn50_s1..5 on GPU 7 x3 + GPUs 0,1 x1.
- 24 Oct 20:33 m_sup_gn_s0 (el_mt, logging on) reproduces p6_L3_100pct_s0 exactly at 20k (test/val crack+inactive IoU, relF1). SUP100 grad norm 1.80, clip 0.253 over 20k; results_r2 updated.
- 24 Oct 21:26 R4 done (5/5), scored (r4/, MD5 OK). Verdict n.d. both sets; val EXCLUDE. ARTS crack +0.027 (descriptive), dead_cell FP mean ~1.3k px. results_r4.md to MC. GPU 6: 2 R5 lanes remain.
- 24 Oct 21:37 R4 VERIFIED n.d. by MC; per-source passes (ARTS crack, BMRK inactive) labelled post hoc leads.
- 24 Oct 21:45 protocol_final APPROVED by MC; F1-F4 + compute headline applied; LOCKED before any Part B/R5/R2c number opened. Relay: el_mt (R2, pilots, sup_gn; 37 files) and el_mt4 (R4; 21 files) to gaint cv02_noob_el, MD5 OK both hops (first el_mt attempt had a script quoting bug, fixed).
- 25 Oct 01:06 R2c done, scored (r2c/, MD5 OK): n.d. both sets, val EXCLUDE; gridline +0.074 (P down); grad norm x1.16. results_r2c.md to MC. GPUs 0-1 R2c lanes free (Part B s4 still on GPU 0? check).
- 25 Oct 01:15 R2c VERIFIED n.d. by MC.
- 25 Oct 02:36 R3 Part B done (5/5), scored (r3b/, MD5 OK): WORSE on inactive (-0.025 both sets), val EXCLUDE; BMRK crack AP +0.018, relR2 +0.025; E1 crack recall 0.178->0.214. results_r3.md to MC.
- 25 Oct 02:46 R3 Part B VERIFIED WORSE (inactive) by MC; CFVS crack AP -0.017 and CFVS inactive -0.044 added.
- 25 Oct 03:47 R5 done (5/5), scored (r5/, MD5 OK): n.d. both sets, val EXCLUDE; p<0.001 share 0.189->0.208; E1 recall 0.178->0.204; 4.0x FLOPs. results_r5.md to MC. No rung included -> FINAL recipe = SUP100 (F2). Launching m9_final.
- 25 Oct 03:52 FINAL scored (m9_final, val decisions = R1's; FINAL identical to R1 model, max diff 0). Contrast 1 passes crack IoU and relF1 (clean +0.018/+0.016 at b0.75). results_final.md to MC.
- 25 Oct 04:03 FINAL VERIFIED by MC (verify_final.md). README: both operating points + noisy fragility up front.
- 25 Oct 04:25 relay: el_mt (R2c, R3 Part B; 41 files), el_mt5 (R5; 21 files), trackM outputs (83 files, no .npy) to gaint cv02_noob_el, MD5 OK both hops. Laptop relay scratch deleted. All Track M GPUs released in ledger. Track M done.
