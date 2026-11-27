# SKR2C stage 2: team-lead rulings on the runner's six questions (13 Nov 2026 17:12 IST)

Asked in `build_s2c_stage2.md` section 6. Protocol: `protocol_SKR2C.md` (v1 LOCKED 91b76abd + section 9). No SKR2C test or E1 number exists when these are written; nothing below was chosen with a number in hand. The user approved the opening on 12 Nov 2026 ("Open it now").

1. **G2's E1 bar = 1.5 x the fresh SUPPF s10-14 seed mean** (E1 crack px on the 74 crack-free cells). Reason: section 6 fixes "both arms are scored fresh (no comparator reuse)", and D's G2b already uses the fresh ensemble. The fixed 5,896 px bar (1.5 x 3,931, seeds 5-9) is printed beside it as a reference line and decides nothing. The old refusal ("SUPPF mean must round to 3,931") moves to the self-test on the opened s5-9 files, where it must still hold.
2. **Scope of "HC2 parts removed": confirmed.** Drop the SHV1 pass, the F51 / H36 pass and G3. Keep the encoder cosines and the cell-gate line as reported-only items.
3. **Thin-term magnitudes: omitted, and the omission is disclosed** in the verify ("reported-only item of section 4 not produced: no frozen grep pattern existed; no verdict depends on it"). No training stdout is opened for it.
4. **No trigger watcher; one manual driver; directory `/home/noob/work/s2c/open/`: confirmed.** Added: the driver is started only by the team-lead, through the shared GPU gate, and only when 9,900 MiB are free (wave 1 of the benchmark, tmux `bench_q_w1g`, holds the GPU until about 00:30 on 14 Nov; its queue, gate, guard and worktrees are not to be touched).
5. **D's pre-opening check: allowed.** A val-only run of the D script on the opened s5-9 members, compared with opening #6's val cells and val decisions. It must read no test or E1 cell (assert the stems).
6. **b_mv tie rule: confirmed.** The b nearer 0; then the smaller b.

Also:
- Before the opening, add one line to `../team_2026-11-12_frontier/benchmark/test_openings.md` and to `e1_openings.md` (#7): registered, with the frozen md5 list, the date and "same 50 test and 106 E1 cells, 3rd look for this contrast".
- The build ends with FROZEN.md5 and the exact command list. An independent reviewer (coach role) checks it against the protocol and these rulings. **Nothing is opened by the builder or the reviewer.**
