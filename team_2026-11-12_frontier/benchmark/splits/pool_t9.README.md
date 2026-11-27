# pool_t9.txt: the one pool list for every pool arm (lead's ruling, 15 Nov 2026)

6424 unlabelled pool cells (of 11,938 on disk), md5 6e6344ba6c97f563095b37452e789779. By source: {'ARTS': 1743, 'CSIR': 4681}.

Rule (stage A item A6, `results/stageA/A6_duplicates.md`; the T12 threshold 0.830 was unusable: 6.6% false matches between different sources). A pool cell is excluded if any of these holds against a labelled or sealed image (cv5v2 cells, legacy test, E1, F51, H36; image pixels only):
1. same module as an evaluation cell (module rule): 5,091 cells out;
2. same md5;
3. DINOv2 ViT-S/14 embedding cosine >= 0.98 (8 dihedral views): tool run `/home/noob/work/bench_reads/stageA/dup/run_tau098` (bench_a 81b4505, `--tau 0.98`), 6,696 cells left after rules 1 to 3;
4. band-pass NCC >= 0.80: 272 more cells out (applied here from `pool_best.tsv` of that run).
The 74 near-exact copies (cosine and NCC >= 0.999, among them the 5 that the module rule missed) are all out. Highest scores kept: NCC < 0.80, cosine < 0.98.
Rules 3 and 4 over-exclude same-layout cells of other modules on purpose: a lost pool cell costs nothing, a leaked one costs a result.
Not searched (not on disk): the 159k full pool, two `_rf` images of CSIR_00046.

## pool_t9_v2.txt (lead's ruling, 15 Nov 2026): use this list, not pool_t9.txt
The module rule of pool_t9.txt worked on image ids. The module-identity audit (`results/stageC/SPLIT_INTEGRITY.md`, `module_identity_v3.tsv`) shows that one physical module can carry several image ids: 1475 cells of pool_t9.txt sit in physical modules that also hold labelled cells (under the audit's rule B: 1003; under its looser pre-set rule: 1475; the union is removed). pool_t9_v2.txt = pool_t9.txt minus those cells: **4949 cells**, md5 39877edec7b3a1b1211aa9fcd6c5e95b, by source {'ARTS': 1497, 'CSIR': 3452}. Table of the removed cells: `results/stageC/split_integrity/pool_t9_in_labelled_modules.tsv`. No pool arm has run yet, so nothing is invalidated.

