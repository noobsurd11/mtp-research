# A4: structured crack head (centreline + local direction field + width) (Om, 1 Nov; "second round")

arch, 2 Nov 2026. Lighter treatment as asked (repo priors, literature, cost, rank). Tags: E measured (file), R literature (Research MCP id), S judgement. One CPU premise check on existing val / `_rf` records; no test or E1 file opened.

## 0. Verdict (proposed): PARK behind SKR2. Not a protocol now.
- Om's own gate: "run only if THIN-B3 leaves crack recall weak". THIN-B3 did not leave it untouched: SKR w 1.0 (centreline supervision) lifted E1 any-hit component recall 0.381 → 0.523 and relF1@2 +0.059 (BETTER), at a fattening cost (test pred / GT 0.95 → 1.54). SKR2 (w 0.1, approved) is the direct dose follow-up. A4 is the next rung of the same family and should wait for it.
- **Its specific mechanism (linking fragments across busbars) has small headroom on non-E1 data** (§1): fragments ("hit but < 50% covered") are 7% of val GT components (4.7% of GT px) and ≤ 5% of F51's (≤ 1.2% of px). On F51 the loss is whole components missed (9% of GT px). On E1 (already-opened, judge) 62% of components are missed entirely vs 15% partial. A direction field does not find a crack the network does not fire on at all.

## 1. Premise check (E, new, descriptive)
`scripts/arch/a4_partial.py` c7fb76d6 → `ideas/arch_out/a4_partial.txt` bbf8c3d8. From el_metrics `gt_cc = [size, v50, vany]` (GT components ≥ 20 px): found ≥ 50% at b iff v50 + b > 0; any-hit iff vany + b > 0; partial = any-hit and not found. Seed means at each run's val b_rel.
| arm | set | comps | found ≥ 50% | any-hit | partial (share of comps) | GT px in partial comps | GT px in missed comps |
|---|---|---|---|---|---|---|---|
| SUPPF s5-9 | val | 125 | 0.837 | 0.909 | 0.072 | 4.7% | 2.5% |
| HC s5-9 | val | 125 | 0.854 | 0.920 | 0.066 | 4.8% | 1.9% |
| SKR w 1.0 s5-9 | val | 125 | 0.858 | 0.912 | 0.054 | 5.1% | 2.3% |
| CLD s5-9 | val | 125 | 0.834 | 0.917 | 0.083 | 5.1% | 2.3% |
| SUPPF s5-9 | F51 | 43 | 0.684 | 0.716 | 0.033 | 0.5% | 9.1% |
| HC s5-9 | F51 | 43 | 0.674 | 0.721 | 0.047 | 0.8% | 8.9% |
- Already-opened E1 context (protocol_SKR2_HC2 §3a, judge-confirmed): SUPPF any-hit 0.381 vs ≥ 50% 0.228 over 296 components → partial 0.153, missed 0.619. SKR w 1.0 any-hit 0.523 / ≥ 50% 0.365.
- **E1's partial share (0.153 of components) is about 2× val's (0.072) and 3-5× F51's** (judge). So the fragment-linking headroom is ≤ 5% of components on non-E1 data but ~15% on E1; whole-component misses (0.619) still dominate on E1. The non-E1 headroom is what any pre-E1 screen of A4 could measure.
- Width head: E1 GT is ~1.5× wider than train (3.66 vs 2.41 px, judge); a width head learns train widths, so it cannot match E1's convention. builder's distance-map costing: inside distance 1 px for 75.5% of train crack px (a width target is near-constant).

## 2. Prior tries in the repo
- THIN-B3 (`verify_thin_b3.md`): Skeleton Recall FAIL (test crack IoU WORSE via fattening; E1 detection gain), clDice FAIL (B5 relR@2 WORSE, OP transfer).
- SKR2 (in protocol_SKR2_HC2 v0.9.1, approved by the user): w 0.1 + precision guard G2.
- Distance-map target (`build_thin_b3.md` §10): costed, not recommended.
- No direction / orientation / multi-task crack head has been run (grep: none).

## 3. Literature (R)
- Batra et al. 2019, doi:10.1109/cvpr.2019.01063: orientation learning jointly with segmentation for road connectivity (+7.5-9% topology metric on SpaceNet / DeepGlobe); roads are wide, long and continuous, the setting where direction helps linking.
- CS²-Net, doi:10.1016/j.media.2020.101874: curvilinear structure segmentation with channel / spatial attention (medical).
- Kirchhoff et al. 2024 (Skeleton Recall), doi:10.1007/978-3-031-72980-5_13: the centreline term already tested here.
- Pantoja-Rosero et al. 2022 (TOPO-loss for crack continuity), doi:10.1016/j.conbuildmat.2022.128264; Carneiro Esteves et al. 2024 (learned reconnecting regularisation), doi:10.1016/j.neucom.2024.128055.
- S: these target fragmentation of structures the network already sees. Our measured non-E1 headroom for that is ≤ 5% of GT px. Abstracts only; no full text fetched.

## 4. Cost
- Dev ~2-3 days (builder): targets per train cell (skeleton, tangent direction from the skeleton (doubled-angle encoding for sign ambiguity), EDT width), **orientation targets transformed with every dihedral augmentation** (flips / rot90 change the angle), extra head (3-4 channels at full resolution), loss weights, CPU tests.
- GPU: one 5-seed arm ≈ 12.5-15 lane-h (R34 + small head; peak ~6.5-7 GB like SKR's 7,020 MiB), 2-3 lanes beside finllm.

## 5. Expected effect (S)
- Test: crack relF1@2 / component recall 0 to +0.01 (fragments are ≤ 5% of val px); crack IoU risk like SKR if the centreline term widens masks.
- E1: any-hit 0 to +0.03 beyond what SKR2 gives; the dominant E1 miss (whole components in scuff + half-cut) is not a linking problem.

## 6. Kill criterion
- Om's: component recall at fixed precision (B5, val-chosen OP) not better. Add, non-E1 first: val partial-component share (this file's readout) must fall by ≥ 0.02 vs SUP100-PF, else the mechanism did not act.

## 7. When to revive (S)
- After SKR2's opening: if SKR2 passes G2 (precision held) and its E1 any-hit gain survives, the family works at a safe dose and A4 can be scoped as a 2-seed 4k non-E1 screen (partial share + B5 on val / F51). If SKR2 fails G2, the skeleton family is closed at this thesis' doses (protocol_SKR2_HC2 §7) and A4 goes with it.

## 8. Files
| file | md5 |
|---|---|
| `scripts/arch/a4_partial.py` | c7fb76d6 |
| `ideas/arch_out/a4_partial.txt` | bbf8c3d8 |

## judge verdict (2026-11-02 11:43 IST; report md5 90b14d69 as reviewed)
**Verdict: PARK behind SKR2. Agreed.** Revive only on SKR2 PASS with G2 held, as in §7.

### What I reproduced (E)
Own stdlib code from the el_metrics records' gt_cc (`judge/out/arch_a4_check_out.txt`), at each run's val b_rel:
- SUPPF val: 125 components, partial 0.072, GT px in partial 0.047, in missed 0.025;
- SUPPF F51: 43 components, partial 0.033, 0.005, 0.091;
- HC val: 0.066 / 0.048 / 0.019; HC F51: 0.047 / 0.008 / 0.089.
- **Match.**
- E1 context, already opened: any-hit 0.381, ≥ 50% 0.228, so partial 0.153 and missed 0.619. This matches my HC width check.

### Notes (S)
- **On E1 the partial share (0.153) is about twice val's (0.072).** Linking headroom on E1 is real, though whole-component misses still dominate.
  - The skeleton family already acts on fragments: SKR w 1.0 val partial 0.054 vs SUPPF 0.072.
  - So A4's marginal value over SKR2 is the fragment share SKR2 leaves.
  - Your added kill rule (val partial share must fall ≥ 0.02) is the right non-E1 mechanism check.
- **Width head:** agreed that a width target learns train widths. It would also make the E1 width mismatch (1.5x) a trained-in bias. Leave it out of any revival.
