# F06. Post-Torpey literature scan: EL defect segmentation and label-efficient EL work (Feb 2024 to Oct 2026)

Done 13 Oct 2026 in chat (guide session). Sources: Research MCP (OpenAlex, Scopus, ScienceDirect, arXiv; Semantic Scholar was rate-limited), forward citations of Pratt 2023 BenchmarkEL (62 citers, 52 listed), 4 keyword searches, plus web search. Read scope: abstract only unless marked FULL. Rare-class SSL methods are covered separately in F01 (10 Oct).

## A. Work on our dataset family (BenchmarkEL / SCDD)

| Paper | Data | Reported | Catch | Read |
|---|---|---|---|---|
| SEiPV-Net, Eesaar et al., Energies 2023 | same 50 test cells, 54 val; train 1,912 (likely 478 x 4 augmented) | mIoU 0.8604, F1 0.9426, Dice 0.8531 (24 classes) | averaging undefined; no per-class numbers; single run; our L3 100% gives 0.840 (per image, absent = 1) and F1w 0.933 under similar rules (results/seipv_compare) | FULL |
| Attention-Based SegNet, Mazen et al., IEEE Access 2024 (doi 10.1109/access.2024.3431098) | 29-class SCDD | mIoU 0.9101, Dice 0.9408; claims +4.97% mIoU over SEiPV-Net | same averaging family as SEiPV | abstract |
| Hanifi et al., IEA/AIE 2025, LNCS (SnT Luxembourg, the E-SCDD group); code github.com/sntubix/pv-defect-segmentation | 29-class SCDD, 765 images | VGG16-UNet: mean IoU 0.663 feature classes, 0.326 defect classes | the only recent defect-level number; code public; best candidate baseline. **Read in full and reproduced 14 Oct (P19, `results/p19/README.md`; note A10)** | FULL |
| Pratt, May, Mkasi, ICTAS 2025 (doi 10.1109/ictas64866.2025.11155421) | DeepLabV3, 29 classes, 48,960 cells from 680 fielded modules | brightening defect vs fill factor r2 = 0.42 | severity / power link (thesis part 3); same work as the CSIR 680-module entry in the index | abstract |
| EFSegNet, Lodhi and Lin, Energy Convers. Manag. X 2026 (doi 10.1016/j.ecmx.2026.101847) | two benchmark EL datasets (names not in abstract) | mIoU 0.699 / 0.794, macro F1 0.832 / 0.898 | EfficientNet-B7 + FPN + focal-dice; datasets unconfirmed (Elsevier full text not accessible via API) | abstract |

## B. EL segmentation on other or private data
- DSDINet, Applied Energy 2026 (doi 10.1016/j.apenergy.2026.128093): public polycrystalline dataset PSCDE; code github.com/Taraseu/PV-Defect-Segmentation-DSDINet.
- PDeT, Sensors 2024: own dataset, mIoU 88.4%.
- STC-Net, arXiv 2608.01714 (2026): crack segmentation for power loss, PVEL-S (already in index).
- MSC-FPL, Aljabri and Jaha, Results Eng. 2026: crack segmentation + power-loss projection.
- Lightweight autoencoder, Elbahri et al., Solar Energy 2026: IoU 92% (binary defect), 0.076 s per frame.
- Saleh et al., Comput. Electr. Eng. 2026 / Alzu bi and Saleh 2025: Attention U-Net, mIoU 97% (background included).
- Duan et al., Energy 2025: cell-level anomaly segmentation.
- Hijjawi et al., Solar Energy 2025: instance segmentation on UCF-EL (already in F04).
- MultiSolSegment, Solar Energy 2026: multi-label masks (already in index).

## C. Label-efficient EL work
- Lin et al., Energy and Environmental Science 2025 (doi 10.1039/d5ee05042a): unsupervised and few-shot pixel-level defect segmentation with an iterative autoencoder (PVEL images).
- Kang et al., IEEE Access 2024: weakly supervised defect detection from module-level labels (classification level).
- Gil et al., ICEIC 2025: SSL with module + cell labels (classification; already in F05).
- Dai et al., ICSMD 2024: SAM-based unsupervised segmentation of solar cell surface defects.
- No new semi-supervised segmentation on BenchmarkEL/SCDD after PV-S3 (2024/2025) and Torpey (2024).

## D. Resources
- Chen et al., Applied Energy 2025, Open data sets for assessing PV system reliability (doi 10.1016/j.apenergy.2025.126132): dataset census.
- PSCDE (via DSDINet).

## Takeaways
1. The label-efficient gap holds: no label-budget curves with loss-off controls on EL segmentation since PV-S3 and Torpey.
2. The highest EL numbers (mIoU 0.86 to 0.97) average over all classes with background or score absent classes as perfect. The only recent defect-level number on SCDD is Hanifi 2025 (0.326 over defect classes, 29 classes), with public code: the natural modern baseline.
3. Pratt 2025 links segmented defects to fill factor on 680 fielded modules: useful for part 3.
4. Read in full next: Hanifi 2025 (and run its code), Attention-Based SegNet 2024, EFSegNet 2026, Lin 2025 (EES), DSDINet 2026.

Limits: Semantic Scholar snippet search was rate-limited; most entries are abstract-level; conference-only and non-English work is under-covered.
