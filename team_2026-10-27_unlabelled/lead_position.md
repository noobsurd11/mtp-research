# Team-lead's position (for `judge` only: attack it; do not pass it on to the others before they have written their first drafts)

1. **What we ran was not the user's intuition.**
   - Every SSL arm here (MT, CPS, FixMatch-style BsM, ALHVR, SKCDF) is label propagation: consistency or pseudo-labels on top of the supervised model's own predictions.
   - The user's intuition, "learn features from unlabelled data, then tie them to labels", is self-supervised (pre)training on the pool: contrastive, dense contrastive, MIM. It was never run.
   - MIM was ranked 7th on 24 Oct and gated out by the 25 Oct frozen-encoder probe.
2. **The bottleneck looks like discrimination plus label convention, not features.**
   - A frozen ImageNet ResNet-50 already ranks BMRK crack better than our fine-tuned model, but only at low precision.
   - At 100% labels the tolerant crack metric is high: test relF1@2 0.897 against IoU 0.49. Strict IoU is dominated by width and edge conventions.
   - If so, more features from unlabelled data cannot move strict IoU much.
3. **The real gap is unseen modules.** E1 crack recall is 0.21, against about 0.70 on test. That is a domain shift, the textbook place for unlabelled data. But the external pool is CSIR/ARTS only, and Sx100 was n.d. on E1 too.
4. **The test set is too small to see small gains.**
   - 50 cells, one noisy cell, 7 twins, a few crack-heavy cells. Rule-1 thresholds reach 0.03-0.09.
   - A bigger, pre-registered evaluation (E-SCDD official test split, CV folds, unseen modules split by module) may be needed. It must be reported beside the old one, never instead of it.
5. **The unlabelled pool's best proven use so far is as a pool to choose what to label.**
   - Track D: targeted crack cells beat random cells and beat SSL.
   - Other candidates: human-verified pseudo-labels, synthetic cracks pasted onto unlabelled backgrounds, anomaly modelling of normal cells.
