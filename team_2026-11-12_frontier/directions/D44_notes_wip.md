# D44 notes (work in progress, session 2, 13 Nov)

Queries run so far:
1. electroluminescence power loss prediction deep learning (2020+)
2. crack mode classification inactive area solar cell electroluminescence power loss (2020+)
3. EL image I-V curve prediction photovoltaic module (2020+)
4. fraction of inactive cell area power loss photovoltaic module cracks (2020+)
5. Pratt electroluminescence segmentation module power degradation inactive area quantification (2020+)
6. defect detection and quantification electroluminescence U-net semantic segmentation power (2020+)
7. benchmark dataset defect detection classification EL semantic segmentation (2021+)
8. EL defect power loss module correlation inactive area cracks I-V measurement dataset (2025+)
9. IEC TS 60904-13 electroluminescence defect classification criteria (2018+)
10. power loss simulation cracked solar cell EL busbar isolated area (2019+)
11. solar cell output power prediction from EL image cell-level dataset (2022+)
12. Metrics Reloaded (2022+)
snippets: crack mode A B C (rate-limited)
snowball: citations of Hoffmann 2021 (pip.3416), Chen 2023 (jphotov.2023.3249970)

Candidates (verified via get_paper):
- arxiv:2608.01714 STC-Net 2026 (MERCon): crack seg PVEL-S + inactive-area proxy = dark pixels in dilated crack zone; dP linear in inactive fraction
- doi:10.1002/pip.3416 Hoffmann 2021: 719 module EL + Pmpp, MAE 7.3 Wp (3.2%), data+code public (ELPVPOWER per Chen 2025 review)
- doi:10.1016/j.enconman.2024.118866 Ozturk 2024: cell-level features -> module power nMAE 0.035, Rs
- doi:10.1016/j.solcom.2026.100196 Dhimish & Lee 2026: two-stage seg (Dice 0.86) -> power loss R2 0.93 on 500 half-cut modules
- doi:10.3390/en19040876 Dhimish et al 2026 EL-to-IV: 438 modules, IV curve from EL, MPP/FF error <2%
- doi:10.1109/jphotov.2025.3562931 Byford 2025: Swin -> IV curve from EL, MPP error <1%
- doi:10.1109/jphotov.2023.3249970 Chen 2023 PV-Vision: crack seg + crack-isolated area via busbar geometry, open code + data
- doi:10.1051/epjpv/2026017 Hashem 2026: 230 mini-modules; crack length / number NOT universal predictors of power loss (line cracks without isolation)
- doi:10.1051/epjpv/2024039 Jaeckel 2024: PV-Riss nomenclature, 4 categories, classification proposal linking power-loss risk and safety
- doi:10.1109/pvsc59419.2025.11132985 Del Prado 2025: benchmark bELMO (analytic) vs DTU ML power-loss models, lab vs daylight vs resolution
- doi:10.4229/wcpec-82022-3bo.11.6 Del Prado 2022: cell inactive area + histogram moments -> cell power, R2 0.87
- doi:10.1016/j.solener.2026.114394 Saborido-Barba 2026: Type-C crack severity on 100 modules, mean loss 12.77% (GEV)
- doi:10.1016/j.apenergy.2025.126132 Chen 2025 open data review: ELPVPOWER 718 modules + Pmpp; EPRI 36 modules EL + flash IV; Sandia VAE power from crack masks
- doi:10.1002/pip.3348 Kikelj 2020: quasi-SPICE from EL damage, 0.12% power error on one complex cell
- doi:10.1016/j.solmat.2023.112621 Lüer 2023: what physics the power-CNN learned (no abstract)
- doi:10.2139/ssrn.7649555 Jost 2026: crack morphology from EL for electrical response (no abstract)
- doi:10.1038/s41592-023-02151-z Metrics Reloaded 2024
