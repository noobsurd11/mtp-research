# F04: paywalled EL / PV-defect papers to fetch through institutional access

Compiled 10 Oct 2026, 09:36 IST. Each DOI was checked against Crossref, and its open-access status against Unpaywall (all CLOSED as of today).
The publisher URL is where `doi.org` redirects. ScienceDirect: `https://www.sciencedirect.com/science/article/pii/<PII>` (the PDF link is on the page).

## Download queue, in priority order

| # | Paper | DOI | Publisher URL | Why we need it |
|---|---|---|---|---|
| 1 | Pratt, Govender, Klein: Defect detection and quantification in EL images of solar PV modules using U-net semantic segmentation. *Renewable Energy* 178 (2021) | 10.1016/j.renene.2021.06.086 | https://www.sciencedirect.com/science/article/pii/S0960148121009526 | The original BenchmarkEL annotation protocol: crack width, crack across busbars, dotted labels, class definitions, weighting/DOE. Our crack-label findings hinge on it |
| 2 | Su et al.: PVEL-AD, a large-scale open-world dataset for PV cell anomaly detection. *IEEE TII* 19(1) (2023) | 10.1109/TII.2022.3162846 | https://ieeexplore.ieee.org/document/9744494/ | Largest public EL set (about 36.5k NIR images, 12 anomaly classes, boxes). Needed for its label protocol, class counts, and whether its defect-free pool can serve as an unlabelled or weak-label pool for us |
| 3 | Liu et al.: A novel few-shot detector for rare defect localization in PV cells using EL images. *Solar Energy* (2025) | 10.1016/j.solener.2025.113546 | https://www.sciencedirect.com/science/article/pii/S0038092X25003093 | The only EL paper found that targets **rare** defects explicitly (few-shot). Direct competitor/related work for the rare-class framing |
| 4 | Gil et al.: Semi-supervised learning for PV cell defect detection using module- and cell-level labels. *ICEIC 2025* | 10.1109/ICEIC64972.2025.10879677 | https://ieeexplore.ieee.org/document/10879677/ | One of only three EL papers with SSL in the title. Mixed-granularity labels (module and cell), a weak-supervision route we have not considered |
| 5 | Jha, Rawat, Vyas: PV-S3, final journal version. *Eng. Appl. AI* (2025) | 10.1016/j.engappai.2025.111790 | https://www.sciencedirect.com/science/article/pii/S0952197625017920 | We read arXiv v4. Check whether the journal version fixed the background-drop metric or the split leakage we measured, before we cite it critically |
| 6 | Duan et al.: An enhanced algorithm for cell-level anomaly segmentation in PV panels using EL imaging. *Energy* (2025) | 10.1016/j.energy.2025.136711 | https://www.sciencedirect.com/science/article/pii/S0360544225023539 | Pixel-level EL segmentation, 2025. Check its dataset, metric and label regime |
| 7 | Lv et al.: Diagnostics in multi-line PV module manufacturing using EL-based unsupervised anomaly detection. *Solar Energy* (2026) | 10.1016/j.solener.2026.114674 | https://www.sciencedirect.com/science/article/pii/S0038092X26003622 | Unsupervised (normal-only) EL anomaly detection at production-line scale. Gives the real-time/throughput constraints for thesis part 3, and an "unlabelled data" use without pseudo-labels |
| 8 | Korovin et al.: Anomaly detection in EL images of heterojunction solar cells. *Solar Energy* (2023) | 10.1016/j.solener.2023.04.059 | https://www.sciencedirect.com/science/article/pii/S0038092X23003043 | Anomaly segmentation trained on normal cells. Journal version of arXiv 2208.05994, which we only titled |
| 9 | Su et al.: Deep-learning-based solar-cell manufacturing defect detection with complementary attention network. *IEEE TII* 17(6) (2021) | 10.1109/TII.2020.3008021 | https://ieeexplore.ieee.org/document/9136904/ | Origin of the PVEL-AD images and label protocol; companion to #2 |
| 10 | Chen, Karin, Libby, Deceglie, Hacke, Silverman, Jain: Automatic crack segmentation in EL images of solar modules and maximum inactive area prediction. *IEEE PVSC 2022* | 10.1109/PVSC48317.2022.9938503 | https://ieeexplore.ieee.org/document/9938503/ | Crack severity via **maximum inactive area**, the industry-relevant severity link (part 3). The JPV 2023 extension is OA (osti.gov/servlets/purl/1973673), so lower priority |
| 11 | Pratt et al.: Correlating defects in EL images to PV module power loss using DeepLabV3 for semantic segmentation. *ICTAS 2025* | 10.1109/ICTAS64866.2025.11155421 | https://ieeexplore.ieee.org/document/11155421/ | Pratt group's link from BenchmarkEL classes to power loss (severity). The SSRN preprint 10.2139/ssrn.4946862 is OA. Fetch the IEEE version only if it differs |
| 12 | Jost et al.: Variational autoencoder for EL image analysis for cell crack power loss prediction. *IEEE PVSC 2025* | 10.1109/PVSC59419.2025.11132908 | https://ieeexplore.ieee.org/document/11132908/ | Generative / self-supervised representation of cracks tied to power loss. Severity plus label-free representation |
| 13 | Haase et al.: Fracture probability, crack patterns, and crack widths of multicrystalline Si solar cells in PV modules during mechanical loading. *IEEE JPV* 8(6) (2018) | 10.1109/JPHOTOV.2018.2871338 | https://ieeexplore.ieee.org/document/8478423/ | Physical crack widths and how they appear in EL. Grounds our "visible crack about 4 px vs 1.75 px label" finding in physics |
| 14 | Lüer et al.: PV module power prediction by deep learning on EL images: assessing the physics learned. *Sol. Energy Mater. Sol. Cells* (2024) | 10.1016/j.solmat.2023.112621 | https://www.sciencedirect.com/science/article/pii/S0927024823004427 | Image-level regression to power as weak supervision; what the network attends to |
| 15 | Gabor et al.: EL analysis and grading of hail-damaged solar panels. *IEEE JPV* (2022) | 10.1109/JPHOTOV.2022.3206906 | https://ieeexplore.ieee.org/document/9900064/ | Severity grading protocol from EL (thesis part 3) |

## Not needed through the institution (already open access; links verified via Unpaywall)

- **Otamendi et al., Solar Energy 2021, segmentation of cell-level anomalies:** arXiv 2106.10962.
- **Chen, Karin, Jain, Solar Energy 2022, PV-Vision:** OA at publisher, 10.1016/j.solener.2022.06.031.
- **Chen et al., JPV 2023, crack segmentation and feature extraction:** osti.gov/servlets/purl/1973673.
- **Fioresi et al., JPV 2022:** osti.gov/servlets/purl/2283912.
- **Deitsch et al., Solar Energy 2019 (ELPV):** arXiv 1807.02894.
- **Deitsch et al., MVA 2021, cell segmentation:** Springer OA.
- **Lin et al., unsupervised and few-shot segmentation in PV EL images:** *Energy Environ. Sci.* 2026, 10.1039/d5ee05042a, CC BY-NC, at https://pubs.rsc.org/en/content/articlepdf/2025/ee/d5ee05042a. **High priority to read.**
- **Hijjawi et al., Solar Energy 2026, instance-segmentation benchmark on EL:** 10.1016/j.solener.2025.114083, OA.
- **Saleh et al., Comput. Electr. Eng. 2026, semantic segmentation of EL:** 10.1016/j.compeleceng.2026.111338, OA.
- **Aljabri & Jaha, Results Eng. 2026, crack segmentation and power-loss projection:** 10.1016/j.rineng.2026.109782, OA.
- **Kang et al., IEEE Access 2024, weakly supervised PV defect detection with module-level annotations:** 10.1109/ACCESS.2024.3349975, OA.
- **MS-OSSLNet, Sci. Rep. 2026, self-supervised (DINO) ordinal severity grading on EL:** 10.1038/s41598-026-63443-w, CC BY.
- **Hoffmann et al., Prog. Photovolt. 2021, module power from EL:** 10.1002/pip.3416, OA.
- **Karimi et al., JPV 2019, automated EL pipeline:** 10.1109/JPHOTOV.2019.2920732, OA.
- **Sandia/OSTI 2024, crack image generation for power-loss prediction:** 10.2172/2999409, OA.
- **Mayr et al., ICIP 2019, weakly supervised cracks:** arXiv 2001.11248.

## Additions (10:00 IST): found during the census

| # | Paper | DOI | Publisher URL | Why |
|---|---|---|---|---|
| 16 | A PV defect segmentation framework integrating domain knowledge and fine-tuned SAM. *Solar Energy* (2025) | 10.1016/j.solener.2025.114145 | https://www.sciencedirect.com/science/article/pii/S0038092X25009089 | The only journal paper found that fine-tunes SAM for EL defect segmentation (foundation-model direction). The SSRN "PV-SAM" preprint 10.2139/ssrn.5380963 may be the same group (OA) |
| 17 | Effective transfer learning of defect detection for PV module cells in EL images. *Solar Energy* (2023) | 10.1016/j.solener.2022.10.055 | https://www.sciencedirect.com/science/article/pii/S0038092X22007940 | Cross-dataset transfer on EL, relevant to the UCF→BenchmarkEL transfer option |
| 18 | A lightweight edge-computing neural network for online PV defect inspection. *IEEE TIM* (2025) | 10.1109/TIM.2025.3546382 | https://ieeexplore.ieee.org/document/10906652/ | Real-time/edge constraints, thesis part 3 |
| 19 | Unsupervised semantic segmentation for solar cell defect detection using SAM and feature fusion. *ICSMD 2024* | 10.1109/ICSMD64214.2024.10920517 | https://ieeexplore.ieee.org/document/10920517/ | Zero-training SAM on ELPV; weak (abstract reports only "confidence score") |
| 20 | Tiny-YOLOv8: embedded deployment for EL image detection. *J. Real-Time Image Proc.* (2026) | 10.1007/s11554-026-01855-7 | https://link.springer.com/10.1007/s11554-026-01855-7 | Embedded hardware numbers, thesis part 3 |

**OA, but the publisher blocks scripted download (HTTP 403); fetch it in the browser:** Lin et al., *EES* 2026, 10.1039/d5ee05042a, https://pubs.rsc.org/en/content/articlepdf/2025/ee/d5ee05042a. This is the unsupervised and few-shot **pixel-level** EL segmentation paper. Read it first among the new ones.
