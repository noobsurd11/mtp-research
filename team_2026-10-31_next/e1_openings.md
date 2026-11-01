# E1 openings ledger (for the paper)

coach, started 2026-10-31 17:37 IST at team-lead's request. E1 = the 106 unseen-module cells (ext117 eval list). **User policy 31 Oct ~15:00:** E1 is a second test set; any protocol may pre-register E1 co-primaries, read once at that protocol's single opening, never for tuning, selection or threshold choice; the paper reports every E1 opening. From that date, no E1 read outside a registered opening (diagnostic reads included).

## Before the policy (descriptive / diagnostic reads; E1 was "sealed, descriptive reads allowed")
E1 was read many times before 31 Oct ~15:00. The PF2 replication exists because of this. The main reads, for the record:
- P13 onward: E1 per-cell metrics as labelled secondaries in every P-series README (handbook 07 §4).
- Track M rungs (R3, R4, FINAL, ...): E1 ext descriptive rows (team_2026-10-24_go/trackM/).
- 27 Oct unlabelled team: E1 diagnostics F1-F11 (ideas.md), scuff_check.
- D (30 Oct, d_prereg.md): E1 target / must-not-hurt reads, val + E1 only; R34-10 control (31 Oct 01:41).
- protocol_100 opening 1 (31 Oct 00:59-01:33) and opening 2 (06:53-07:07): E1 split, crack-free px.
- 31 Oct (before / around the policy): calib's idea-1 and idea-7 backfill (FINAL, SUP5, SUPPF5, MIMPF5, CP5 on E1), judge's checks and idea-1 oracle split, builder's quarantined CPU batch (14:46-14:54; E1-scuff on f3_SUPPF s0 / p6_L3 s0; unread, chmod a-r).
- Consequence: FINAL and protocol_100 seeds 0-4 are **not blind** on E1; any later E1 number for them is labelled "not blind" and enters no conclusion.

## Registered E1 openings (under the policy)
| # | protocol | models | E1 co-primaries / readouts (pre-registered) | registered | opened | result file |
|---|---|---|---|---|---|---|
| 1 | protocol_PF2 | pf2_{SUP,SUPPF,RN50PF}_100pct_s5..9 | co-primary (PF2 contrast): E1 crack recall, E1 inactive IoU; reported: relR@2 / relP@2 / component R-P, strata, oracle relF1@2, B5 at val b; §13 routing readout VOID (non-E1 pre-check FAILED 18:03: no-op), so not read | 31 Oct 13:58 (v1), Om; policy note §12 | **opened 1 Nov 06:33-08:26** | `verify_pf2.md`: E1 inactive IoU +0.189 BETTER (replicated); E1 crack recall +0.027 n.d. Addendum (1 Nov 08:47, same models, pre-registered §3c RN secondary, descriptive): SUPPF_5 vs RN50PF_5 ensembles at +0.75, E1 + val, `results/pf2/d_rn/` |
| 2 | protocol_thin_b3 | SKR / CLD / B3 s5-9 (+ PF2's SUPPF s5-9 reused) | co-primary: E1 crack relF1@2 (all 106, argmax) | v0.2 31 Oct 17:34 (locks before PF2's opening) | pending | |
| 3 | protocol_HC | HC s5-9 (+ SUPPF s5-9 reused) | co-primaries: E1 crack relF1@2, E1 inactive IoU | v0 draft 31 Oct | pending (user GPU OK) | |

- Re-use note: PF2's SUPPF s5-9 E1 per-cell files are opened at opening #1 and reused unchanged as the comparator in #2 and #3. That is a re-use of already-opened comparator numbers, not a new E1 read of those models.
| 4 | protocol_PF2E | E-PF (pf2_SUPPF s5-9 ensemble) vs E-g (pf2_SUP s5-9 ensemble) | co-primaries: E1 crack relF1@2, E1 inactive IoU (module-cluster bootstrap, 71 clusters) | v1 1 Nov (user's go ~13:15) | **opening started 1 Nov 19:02:04 (runner; coach APPROVED 1 Nov ~18:58; python PID 1604806, tmux pf2e; gaint CPU fp32, `el_f3/reports/pf2e/out/`)** | `verify_pf2e.md` (coach CONFIRMED 1 Nov): verdict b clarified 19:04:56 before the val decisions file (19:05:49); headline b 0 both; **E1 inactive IoU +0.214, cluster CI [+0.030, +0.382] PASS**; E1 crack relF1@2 +0.036 n.d.; test n.d. (relF1@2 +0.012). Not independent of #1 (same member models) |
