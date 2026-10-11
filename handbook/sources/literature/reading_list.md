# Reading list: training methodology for rare thin defects (prioritised)

Read in this order. Each item says *what to look for*, tied to our measured situation.

1. **ALHVR** (Lei et al., ICCV 2025): paper + supplement + code. https://mlanthology.org/iccv/2025/lei2025iccv-adaptive · https://github.com/ziziyao/ALHVR
   - Read Table 1, the masked-region experiment, critically. Its premise holds on our data (Ω3 holds 71% of crack pixels). The question for us: is the *teaching signal* in Ω3 good enough for a rare class? Ours is about 62% correct.
2. **Torpey, Pratt, Klein 2024**, pretraining paradigms on EL. https://arxiv.org/abs/2402.17611
   - The only multi-paradigm study on BenchmarkEL-family data. U2PL is *worse than random init*; CCT ≈ COCO pretraining; in-domain SimCLR is weak. Note the full-label-only design.
3. **Pratt et al. 2023**, BenchmarkEL (§3.2 test-set construction, §3.4 metric) and, if obtainable, **Pratt 2021** (Renewable Energy) and the **Pratt 2024 thesis** for the annotation protocol (crack width, crack crossing busbars). https://doaj.org/article/ddf0c876a3754064870a98960b3147cf · https://wiredspace.wits.ac.za/items/188c94a9-0c1e-45f6-92b0-ca0cf6913e71
4. **DHC** (Wang & Li, MICCAI 2023). https://arxiv.org/abs/2307.11960
   - The clearest case where class-aware weighting from pseudo-label statistics rescues classes that SSL drops to 0. Our 24-class setup has the same failure mode.
5. **AEL** (Hu et al., NeurIPS 2021). https://arxiv.org/abs/2110.05474
   - Rare-class sampling and mixing with a per-class confidence bank. The best-ablated rare-class mechanism. Check which component matters at which label split.
6. **DARS** (He et al., ICCV 2021). https://arxiv.org/abs/2107.11279
   - Pseudo-label distribution mismatch and over-confidence ties. Explains our UCF corrosion runaway and the case for class-wise thresholds.
7. **BUR** (Zhou et al., 2025). https://arxiv.org/abs/2502.07457
   - The opposite of ALHVR: labelled loss on uncertain regions, unlabelled loss only on certain ones. A serious alternative hypothesis to test against an ALHVR-style design.
8. **Oliver et al. 2018**, realistic SSL evaluation (https://arxiv.org/abs/1804.09170), with **UniMatch V2** §experiments (https://arxiv.org/abs/2410.10777) and **Yuan et al. 2021** (BN statistics under strong augmentation, https://arxiv.org/abs/2104.07256).
   - Together they define the fair-comparison protocol and explain our "loss-off" BN effect.
9. **Skeleton Recall loss** (Kirchhoff et al., ECCV 2024, https://arxiv.org/abs/2404.03010) with **clDice** (https://arxiv.org/abs/2003.07311).
   - Crack is fit-limited even on training images. Thin-structure supervision is a first-order lever before any SSL. Skeleton Recall is multi-class.
10. **Metrics Reloaded** (https://arxiv.org/abs/2206.01653) with **What's Cracking?** §VI-B (https://arxiv.org/abs/2202.03714).
    - How to measure 2–3 px cracks. Tolerance metrics can reward wider predictions, which is our exact failure mode. Pair relaxed recall with relaxed precision, a skeleton score and AP.

Next tier:
- MultiSolSegment (multi-label crack/busbar overlap)
- U2PL (to understand why it failed on EL)
- MCF (DTCT's ancestor)
- GA loss (absent classes)
- DAFormer RCS
- AOI-SSL (MAE in a small industrial domain)
- Menon et al. logit adjustment
