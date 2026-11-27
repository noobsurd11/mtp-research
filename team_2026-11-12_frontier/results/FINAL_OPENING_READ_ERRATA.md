# Errata to FINAL_OPENING_READ.md (lead, 21 Nov 2026 15:12 IST)

Found by the thesis_tables trace pass (T/thesis/GAPS.md a081ce87: G-W1, G-W2, G-D1, G-W4, G-W11).

- FINAL_OPENING_READ.md stays unchanged, so its pinned md5 16e3f1e7 holds.
- These corrections supersede the lines cited.
- No number changes. Every value below is in results/final_opening_read/verdict.txt (bbb5f3b4) or read_e1/read.txt.

1. **Reading 5 (l76), "about 3 x its CV5 size".**
   Read instead:
   - On E1 the point effect is about 2 to 3 x its CV5 size: +0.043 vs +0.015 to +0.022.
   - Against CS_D4 - PF (+0.0222, selection-biased) it is about 2 x.
   - The E1 interval [+0.0013, +0.1043] contains the CV5 values, so E1 does not show a larger effect than CV5.
2. **Reading 2 (l69 to l70), "The gain is the model, not the TTA".**
   Read instead:
   - Most of the gain is the model. C2 - C1-D4 (both 8 views) is +0.0451 [+0.0173, +0.0699].
   - The D4 part is not resolved on E1. C1-D4 - C1 is -0.0021 [-0.0423, +0.0575]. That interval does not exclude a CV5-sized D4 effect (PF_D4 - PF +0.0134 on CV5).
3. **test50 leakage (l61), "8 test cells are pool cells".**
   Read instead: 8 test cells are the same physical cell as a pool cell (SPLIT_INTEGRITY 5b).
   - 7 of them are confirmed by pixels.
   - 1 (CFVS_00063_r3_c1) rests on the cells.tsv link only, "not confirmed and not refuted".
4. **Strata (l47), not stated.**
   On the 5 BMRK cells: C2 relF1@2 0.0000 [0.0000, 0.0000], C1 0.1843 [0.0000, 0.9216].
   - C1-D4, C3 and E-PF also score 0.0000.
   - The C2 - C1 stratum delta of -0.1843 [-0.5529, 0.0000] rests on 5 cells.
5. **Prior looks.**
   - The ledger row #8 phrase "4th look at these 106 cells" (team_2026-10-31_next/e1_openings.md) is ambiguous.
   - The reference wording is verdict.txt l138: "E1 7 registered openings (3 looks at one contrast) plus reads before 31 Oct and one use of published E1 contrasts (R0, 15 Nov); the final models were never scored on either set."
   - Reading 1 (l66 to l67), "No candidate, readout or threshold was selected on these cells", holds for E1. But C2's readout (swad) and D4 were chosen on pool cells (verdict.txt l139).
