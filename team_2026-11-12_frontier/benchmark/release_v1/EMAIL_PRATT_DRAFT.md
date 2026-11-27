# Draft email to the BenchmarkEL authors (not sent; the user sends it)

To: [address: fill in]
From: [sender: fill in]
Subject: A benchmark protocol built on BenchmarkEL: planned release of split lists and code, and a question on terms

---

Dear BenchmarkEL authors,

I am writing from a master's thesis project at IIT Mandi, run with an industry partner (WattCycle), on defect segmentation in
EL images of solar cells. Your BenchmarkEL dataset is the basis of our work, and I would like to ask about its terms before we
release anything.

What we built on your data:
- A module-grouped 5-fold split of the 532 train and val cells of dataset_20211104, after a check of which cells come from the
  same physical module.
- A label variant ("v1.1"): your 2021 masks with the E-SCDD crack and inactive corrections, scuff and star pixels set to
  "ignore", and one BMRK cell whose mask in the 20221008 release belongs to another image (BMRK_00031_cell0091 carries the
  mask of BMRK_00075_cell0255) given back its earlier mask.
- A scoring protocol (crack F1 with a 2-pixel tolerance, intervals over module groups, fixed operating points), and baselines
  under it, including our re-implementations of models from your 2023 paper.

In passing we found that 8 cells of the 2021 test set are the same physical cells as train or val cells (7 of them confirmed
from the pixels). We are glad to send the list if it is useful to you.

What we would like to release: lists and code only. That is the split and group lists, a cell table (file names, sources,
module groups, and per-cell pixel counts for every cell except those we keep as test sets), the scoring code, and a script
that rebuilds the v1.1 masks from your public masks and E-SCDD. No images, no masks and no model weights would be
redistributed. Both of your papers would be cited as your README asks.

My questions:
1. The repository does not state a licence. Under what terms may others use the dataset and share material derived from it?
2. May we publish per-cell statistics computed from your masks (pixel counts per class, file hashes), as described above?
3. Would you allow redistribution of the derived v1.1 masks, or do you prefer that we keep shipping only the script that
   rebuilds them from your files?
4. Is there a citation you prefer beyond the two papers listed in your README?
[Optional, delete if not wanted: 5. Are models trained on BenchmarkEL usable in a commercial inspection product, and if so
under what conditions?]

We would value your view before we publish anything, and I am happy to share the lists and code with you first.

Thank you for making the dataset available.

Kind regards,
[sender name, affiliation]
