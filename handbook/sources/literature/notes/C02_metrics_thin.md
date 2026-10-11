# Metrics for thin and rare structures
- **Metrics Reloaded** (Maier-Hein, Reinke et al., Nature Methods 21:195–212, 2024; arXiv 2206.01653). https://arxiv.org/abs/2206.01653
  - Problem-fingerprint-driven metric selection. Recommends clDice for connectivity of tubular structures and NSD (surface Dice with tolerance) for boundary quality. Read: abstract + search summary.
- **Common Limitations of Image Processing Metrics** (Reinke et al., arXiv 2104.05642). Pitfalls of overlap metrics for small structures. Read: abstract.
- **What's Cracking?** (König et al., arXiv 2202.03714): review of crack segmentation. https://arxiv.org/abs/2202.03714
  - Read: sections (§VI-B).
  - Tolerance metrics give TP pixels an "allowance of being within a two-pixel or five-pixel distance". **Caution:** "this can lead to oversaturating the number of TP pixels by simply creating wider predictions, which leads to better results in the metrics but objectively worse results" (§VI-B3).
  - ODS/OIS (threshold-optimised F) are used for threshold-free comparison (§VI-B2).
  - Relevance: our models already over-predict crack width. A relaxed metric must be paired with relaxed precision and a width-insensitive score (clDice, skeleton recall), or it rewards the failure we have.
- **Deep Learning for Crack Detection review** (Zhang et al., arXiv 2508.10256, 2025). Calls for cross-dataset rather than single-dataset evaluation. Read: abstract.
