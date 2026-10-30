# diag: does a 5% null carry to 100%? (MIM, DDeP, CP, PL-SSL)

`diag`, 30 Oct 2026. Tags: E measured (path), R literature (Research MCP id; [F] full text read, [A] abstract), S judgement.
Counts marked "recount" are mine: local `~/mtp/datasets/escdd_full` masks over `splits_benchmark/seed0` lists (script was in my scratchpad, not kept). Local masks miss 1 server crack cell at 5% and 5 train cells at 100%.

## 1. What the labels give each method (E)
| | 5% (23 cells) | 100% (478) | ratio |
|---|---|---|---|
| crack cells (recount / server) | 8 / 9 | 203 / 209 | ×23 |
| crack components ≥ 20 px (recount) | 37 | 850 | ×23 |
| CP paste library after spec filters (`scripts/scout/cp_library_stats_out.txt`; server 20 at 5%) | 17 | 556 (non-twin) | ×28 to ×33 |
| crack cells ARTS / BMRK / CFVS / CSIR / SDLE (recount) | 0 (server 1, 47 px) / 2 / 3 / 2 / 1 | 42 / 24 / 88 / 47 / 2 | |
| library ARTS / BMRK / CFVS / CSIR (pre-contrast) | 0 / 2 / 18 / 2 | 70 / 22 / 346 / 183 | |
| inactive cells (recount; BMRK 1, CFVS 1 at 5%) | 2 | 41 / 42 server | ×21 |

## 2. Power: 100% is better powered, not worse (E)
- Rule-1 thresholds seen at 5% vs A5c-f1: crack 0.010 (DDeP, floor) to 0.019 (MIM, seed sd 3×), relF1@2 0.017 to 0.030, inactive 0.059 to 0.116 (`verify_mim5.md`, `verify_ddep5.md`). 80%-power MDE, clean: 5% crack 0.019 / inactive 0.084; 100% crack 0.012 / relF1 0.013 / recall 0.018 / inactive 0.032 (`team_2026-10-27_unlabelled/eval.md` §1.2).
- So the 5% screen does not buy power; it buys effect size, and only for methods whose effect shrinks with labels.
- **The 5% nulls are informative on crack, not on inactive.** MIM5 crack −0.0116, house SE 0.0093: a 5% gain above about +0.007 is unlikely; cell bootstrap [−0.018, −0.004]. DDeP5 +0.0070, SE 0.0038: upper bound about +0.015, and +0.0045 once the bias is matched (C2). Inactive at 5% rests on 2 training cells: no verdict either way (E/S).

## 3. Cross-fraction evidence
- **PL-SSL, gains shrink (E):** BsM crack +0.029 / +0.012 / −0.006 (clean +0.013) at 5 / 10 / 20%; Cs inactive +0.105 / +0.029 / +0.006 / +0.003 at 5 / 20 / 50 / 100% (`handbook/11` rows 3, 10; P18 exploratory). Not monotone everywhere: BsM inactive +0.107 / +0.132 / +0.060 at 5 / 10 / 20%.
- **PL-SSL, a 5% null that did not carry (E):** joint-BN MT n.d. at 5% (Cm5 − A5c +0.006 / +0.003 / +0.015, `results/p12/README.md`), passes at 10% (Cm − A inactive +0.071, relF1 +0.013, `results/p11/README.md`). Cause: the joint-BN handicap grows as labels shrink (Dm5 − A5c −0.017 vs Dm − A −0.007, `handbook/11` claim 4). This is the user's mechanism, in our own data.
- **Encoder init (E):** P15 in-domain labelled encoder +0.010 at 5% (cell CI above 0), −0.012 at 10%, worse on all three (`results/p15/README.md`).
- **Gains that grow with labels (E):** only L0 → L3 (CE + Dice): crack IoU +0.077 at 10%, +0.134 at 100% (`results/p6/README.md`). A label-consuming loss change, the same kind as CP. Band-ignore shrinks: +0.018 to +0.027 at 5 to 10%, +0.007 at 100% (`SESSION_RECORD_2026-10-21_to_27.md` l.145).
- **R, pretraining:** pretraining helps at 1/5 COCO and hurts at full COCO; self-training helps at all sizes (R [A] arxiv:2006.06882). DDeP: Pascal Ctx +11.3 → +1.3, Cityscapes +9.8 → +0.3 from few to full labels (R [F] arxiv:2205.11423, via `directions.md`).
- **R, MIM is label-hungry:** MAE needs about 100× more labels than MSN in low-shot classification (R [F] doi:10.1007/978-3-031-19821-2_26 §1, Fig. 1). Caveat: ViT from scratch, classification, not a continued CNN with full fine-tuning (S).
- **R, copy-paste:** positive at every COCO fraction. Largest at 10%: +6.9 box AP over SSJ, +4.8 over LSJ. At full COCO: +1.0 to +1.5 box AP, +0.5 to +1.1 mask AP. Pasting on more varied backgrounds adds more (+0.8 vs +0.4 box AP), and the gain is largest on the hardest classes (R [F] doi:10.1109/cvpr46437.2021.00294 §4.2-4.4, App. B). COCO 10% still holds thousands of instances per class; no fraction there is as starved as our 17 to 20 components (S).

## 4. Verdict per method (strongest case on each side, then decision)
| Method | For "the 5% null fails" | For "the 5% null holds" | Verdict |
|---|---|---|---|
| MIM encoder init | MIM features are label-hungry (MSN). With 9 crack cells the fine-tune may fail to re-map them. Seed sd ×3 looks like a scarcity instability | Every MIM5 estimate is negative, and the 5% crack gain is bounded at about +0.007. Init effects shrink or flip with labels: P15 +0.010 → −0.012 from 5% to 10%; Zoph; DDeP. At 100% the ImageNet arm sees the same 209 crack cells, so nothing is left to unlock unless MIM features are better, and AM found no crack localisation in them | **holds** (moderate). Expected MIM100 − SUP100 crack −0.010 to +0.005 (S) |
| DDeP decoder init | lr 1e-3 erased the init at 5% (cosine 0.090 vs 0.072 for a random init), so 5% tested a near-random decoder | The paper's own gain falls to +0.3 to +1.3 at full labels. At 100% more label gradient erases the init further. The 5% gain behaved as a crack prior shift (recall +0.019, precision −0.022, C2 +0.0045), which FINAL's bias already supplies | **holds** (strong). Expected 0 to +0.003 (S) |
| Crack copy-paste | No 5% score exists. Its dose is labels: library ×28 to ×33, ARTS 0 → 70, BMRK 2 → 22. A 5% CP can only re-show 17 to 20 mostly-CFVS shapes. Our one growing-with-labels case (L0 → L3) is also a label-consuming change | COCO gain over LSJ shrinks about 4× from 10% to 100% (+4.8 → about +1.3 box AP). At 100% the labelled stream already shows all 850 components, so CP adds only background variety and a prior shift that the bias gives for free | **unknown; the 5% screen is the wrong test for CP.** Expected CP100 − SUP100 crack IoU +0.005 to +0.015, relR@2 +0.005 to +0.02 (S) |
| PL-SSL (calibration) | Joint-BN MT: a 5% null turned into a 10% pass | Every passing PL recipe shrank with labels; Cs reached 0 by 50 to 100% | **holds for gains, fails for scarcity artefacts** |

**Rule this supports (S):** "null at 5% ⇒ null at 100%" is safe only if two things hold. First, the method's mechanism does not consume labels. Second, the 5% estimate is tight on crack. MIM and DDeP meet both; CP meets neither; inactive never meets the second at 5%. So the user's principle is right; applied per method, it still closes the two init methods and reopens CP.

## Implications for the 100% plan
1. **CP100: run it; it is the only one with an open question.**
   - Design: SUP100 at the same commit and hardware, 5 v 5. Verdict sets: all 50 and clean.
   - Expected crack IoU +0.005 to +0.015 against a clean rule1_80 of 0.012: roughly a coin flip on IoU (S). A pass is likelier on capture: relR@2 and component recall (recall MDE 0.018).
   - Keep a matched-bias contrast (both arms at FINAL's +0.75, or LA τ 1), as at 5%.
   - Library: the 100% non-twin set, spec filters unchanged (556 components, 70 ARTS). Sample uniformly. A source-balanced variant only after a pass.
   - Backgrounds: the 5% spec's in-domain half (unlabelled train cells) does not exist at 100%. Use 50% pool and 50% labelled train cells, with ignore outside the paste and ring. Pasting into both gave the largest COCO gain (R §4.4).
   - Paste rate: keep λ 1, 4 backgrounds per step, K 1 to 3. With a mean kept component of 272 px, that adds about 2.2k crack px per step to about 4.0k labelled (+55%, vs about +100% at 5%) (E/S, from §1 stats). There is no reason to raise it, since the extra prior is what the bias already gives. Keep 20k steps (matched).
2. **MIM100: not worth it for score** (expected below the 0.012 MDE, likely ≤ 0).
   - Run it only if the user wants the direct 100% answer for the thesis: 5 fine-tunes (pretrain exists), plus the same SUP100 arm as CP100.
   - Do not lower the encoder lr. That keeps more of a start that was worse at 5%; the label-hungry reading predicts gains from more labels, not a gentler lr.
   - Free first: measure encoder drift (cosine of the MIM5 fine-tuned encoder to the MIM init vs to ImageNet) to see whether MIM5's harm is instability or features (S).
3. **DDeP100: no.** Lit gain at full labels is below our MDE, and the init is overwritten. A lower decoder lr is a 5% question that needs a matched pair (A5c and DDeP at 3e-4), not a 100% arm.
4. **Screening policy:** 100% has the tighter MDE (crack 0.012 vs 0.019; inactive 0.032 vs 0.084). Screen at 5% only methods whose effect shrinks with labels. Test label-dosed methods (copy-paste, loss changes) and anything aimed at inactive directly at 100% (S).

## Addendum (30 Oct, after `coach_100.md` §0)
- **New fact (E, `coach_100.md` §0):** under the house optimizer, layer3-4 end at cosine 0.00-0.02 to their init, norms 2-9%, for every start: ImageNet at 5% and 100%, and MIM5. MIM changed mostly layer2-4 (cosine to ImageNet 0.53-0.76), and fine-tuning reset exactly those.
- **MIM verdict, revised:** "holds" stands only for plain MIM100 on the house recipe, which erases at 100% too (SUP100 layer3 0.018). MIM5 tested conv1/layer1 transfer, not MIM features. My MIM arguments built on P15 and AM therefore lose most of their weight (P15 ran under the same erasure). **MIM under an encoder-preserving fine-tune is unknown at both 5% and 100%.**
- **Retract "don't lower the encoder lr":** it assumed the MIM5 start had been tested; it had not. Coach's PF package (1k-step freeze, encoder lr ×0.1, encoder wd 0) is the right test. Lower lr alone would keep the coupled-L2 norm collapse, so wd 0 is the operative part (S).
- **Attribution needs the SUP100-PF arm** (S): the optimizer change is large on its own, so MIM100-PF − SUP100 confounds init with recipe. I would run SUP100-PF unconditionally rather than only after a pass, since SUP100-PF − SUP100 is the likeliest of the three contrasts to move FINAL.
- **Unchanged:** DDeP (the lit gain at full labels is below our MDE whatever the optimizer) and CP100 (house optimizer, one change). Scope: every "init does not matter" result in §3-4 is conditional on the house recipe.
