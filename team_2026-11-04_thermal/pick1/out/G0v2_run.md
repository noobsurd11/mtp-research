# G0 v2 run record (post hoc instrument fix)
- cellreg: scripts/frozen/cellreg_7d9a9fe0.py, md5 7d9a9fe0 (v0.4.1; check GO, factcheck §30)
- manifests: pick1/out/G0v2_A1_manifest.tsv (fdd16047), pick1/out/G0v2_A2_manifest.tsv (a68b773d); same EL / IR files as G0 v1, UVF column emptied (G0 does not use UVF; avoids the portrait-UVF leak)
- grids: A1 3x12, A2 6x12; orientations id, fliph, flipv, rot180 (primary rot180, plan Amendment 3)
- outputs: pick1/out/G0v2_A1/<orient>/, pick1/out/G0v2_A2/<orient>/ (new dirs; nothing from v1 is overwritten)
- QA before any number: criteria pick1/out/qa_v04/visual_qa_v04_criteria.md (fae36d53 + addendum), edge check scripts/edge_check.py, overlays scripts/qa_overlay.py; table to check for co-sign
- started: 2026-11-04 13:35 IST
