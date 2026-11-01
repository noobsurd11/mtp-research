# Item 13 (large unlabelled pool, HF `sasan/scdd-unlabeled`): CLOSED, 31 Oct 2026

Author: `domain` (team_2026-10-31_next), per Om B9 ("the MIM gate failed, so do NOT download now. Close item 13 with uses A + B"). Tags: E measured (file), R literature (Research MCP id), S judgement. No download, no pixel read beyond the files cited. Sources: `pool_large_audit_2026-10-30.md` (poolscout; manifest md5 25a553f1, sample index md5 85f138a7), `review_suggestions_2026-10-30.md` §6b (vetter recount), `verify_100_o1.md`, handbook 11 claims 25 and 29, handbook 03 §6, 27 Oct `ideas.md` F6-F10.

## Status
- **Decision:** not downloaded. The gate (opening 1: MIM100-PF − SUP100-PF BETTER, or same-sign on the clean set) failed (E, `verify_100_o1.md`; handbook 11 claim 25): crack IoU +0.0048 (thr 0.0113) all 50 / −0.0017 (thr 0.0100) clean; relF1@2 +0.0035 / −0.0039; inactive −0.0118 / −0.0112; n.d. at tau 0 and tau 1. E1 crack recall −0.024 (descriptive).
- **Reopen only if** Om's optional route is taken: MIM on the CSIR-complete subset (~22.9k), with a written reason it would differ from MIM100. None is known (S).
- Nothing on disk to clean up beyond the 599-row sample (`~/mtp/datasets/scdd_unlabeled_sample/`, 293.6 MB). Keep it for now: it is the only pixel evidence behind Use A.

## Use A. Thesis negative result: what the 150k pool contains and why it cannot fix E1
Claim (for the thesis): no public unlabelled EL pool we can reach contains the cell populations where our deployed model fails. Unlabelled-data methods therefore cannot close the unseen-panel gap through this pool, whatever the method.

| Fact | Number | Tag / source |
|---|---|---|
| What it is | Pratt's Dropbox pool re-hosted: 159,332 rows, the same 9 leaf folders and naming; all 11,993 files of our 6 Oct download are in it | E, audit §0.1, §2 |
| Sources | CSIR 22,931 + ARTS 136,401. 0 BMRK, 0 CFVS, 0 SDLE | E, audit §3.1 |
| Where the growth is | 147,394 new rows; 124,467 (84%) are ARTS mono 5-busbar, mostly native 512 px, bright and low-contrast (median mean 205, sd 24 vs labelled ARTS 133, 41) | E, audit §0.3, §3.3 |
| CSIR growth | 9,204 → 22,931 (2.5x); ARTS 2,734 → 136,401 (50x) | E, vetter §13.1 |
| Half-cells | 1,152, all from 8 CSIR modules (297-301, 333-335), all already in our 11,938 | E, audit §3.1; ideas F8 |
| E1's module family | E1's 58 half-cuts come from CSIR modules 1621-2328 (+1 in CSIR_00300). The pool has 0 CSIR modules between 400 and 2,362 | E, vetter finding 4; audit §3.1 |
| E1 cells / modules in the pool | 0 cells; 1 module (CSIR_00300, already excluded by rule R1) | E, audit §4.1 |
| Look of the pool vs E1 | No random sample row resembles E1 (r_hp max 0.81 to any E1 cell, 566 rows). Intensity is not the difference: E1 CSIR median mean 190 / sd 55 is the whole crop including E1's white letterbox. On content px E1 is close to train (non-padding mean of cell means 137.3 vs 136.5; half-cuts 140 / sd 26, full 162 / sd 33 on content px). The differences are cell type (half-cut), scale, scuff and histogram shape | E, audit §3.3, §4.3; `judge/out/intensity_stats.tsv`; `team_2026-10-31_next/ideas/idea11_augmentation.md` §2 (corrected 31 Oct after judge review) |

Why it cannot fix E1 (reasoning):
1. **Coverage, not quantity (E + S).** 75% of E1 crack px sit in 29 scuff + half-cut cells (judge 31 Oct log, from SUP s0 m0 GT rows). The pool adds no half-cells and no module from E1's era. The failure population is absent, so no SSL, MIM or pseudo-label method can see it.
2. **The method evidence is already null at the pool we hold (E).** MIM100-PF − SUP100-PF n.d. (above); CP100 n.d. (handbook 19); P9-P12 and P16 Sx100 pool arms n.d. (handbook 03 §6); no external-pool arm moved E1 half-cut recall by more than +0.023 (ideas F13).
3. **Scaling the same sources is unlikely to help (R + S).** In-domain SimCLR on 22k EL images gave 0.517 mIoU vs 0.534 for ImageNet SimCLR at full labels (R, arxiv:2402.17611). The new rows are 84% one cell type that is in neither the weak sources (BMRK, CFVS) nor E1.
4. **What would help instead (S, for the thesis discussion):** labels or simulation for the missing contexts (half-cut, scuff); the 31 Oct team tests synthetic half-cuts (idea 5) and appearance handling (ideas 2, 3, 11).

Suggested thesis wording (S): "The 150k-cell public pool from the same benchmark consists only of CSIR and ARTS cells from the same installations as our labelled data, 84% of its new rows are a single mono cell type, and it contains no cell from the module families of our unseen-panel set. We therefore treat it as evidence that more unlabelled data of the same provenance cannot address unseen-panel failure, consistent with our null pool results (MIM, copy-paste, SSL)."

## Use B. Provenance note: overlaps, leaks, licence, citation
For the methods section and for anyone who later downloads the pool.

**Identity and versions (E, audit §1).**
- HF `sasan/scdd-unlabeled`, revision `7c4e73d8590a` (11 June 2025 re-upload adding `file_path`; first upload `b3eab47e`, 23 May 2025, same rows). 302 parquet shards, 76.3 GB, per-shard sha256 in `out/hf_api.json`.
- Uploader profile: Sasan Jafarnejad, a co-author of Hanifi et al. (arxiv:2511.09604). Card: no description, no licence, no citation.
- "151,700 unlabelled" in Hanifi et al. = Pratt's 150,000 + their ~1,700 synthetic images, not a separate pool (D, audit §1.3).

**Our 11,938-cell pool is a capped subset of it (E/D, audit §2).** The 6 Oct downloader capped each Dropbox leaf folder at 2,500 entries (seed 42). That cap explains the skew of our pool: 0 CSIR mono 5-busbar cells, though they are 6.2% of their folder.

**Overlap with our labelled and held-out sets (E, audit §4).**

| Our set | In the pool by ID | Notes |
|---|---|---|
| train 478 | 271 | 169 of 322 train modules present |
| val 54 | 23 | one val ID (`CSIR_00127_r11_c5`) is a different image under the same ID (r_hp 0.52) |
| test 50 | **21** | 13 ARTS + 8 CSIR, incl. the noisy cell `CSIR_00070_r8_c4` and the D7 twin position `ARTS_00020_r5_c1` |
| E1 106 | 0 | 1 module (CSIR_00300) |
| Hanifi `_rf` 117 | 117 | all (100 already in our 11,938, 17 not) |

- **IDs are not unique keys.** 192 stems (modules CSIR_00029, 00053, 00056) occur in two folders as different images.
- **Byte copies under other module IDs:** 27 pairs measured within row groups; about 2,400 estimated over the pool (95% bounds 1,400-9,500), mostly in `multi/ribbons_3`, the folder holding 186 of our labelled IDs, including ARTS test cells. A test cell can therefore sit in the pool under a different ID.
- **Consequence for any future use (E/S):** ID rules are not enough. Required before any SSL or pretraining use: poolscout's D0-D4 dedupe (all 582 labelled incl. D7 twins, E1, ext117 and all 117 `_rf` by ID; ID-wide module rule for val/test/E1 modules (Om B10); md5 copies and their transitive closure; r_hp ≥ 0.95 to held-out cells after reconciling poolscout's r_hp with `neardup.py` on the D7 twins).

**Past claims (E/S).** Our 11,938 pool held 0 test IDs after the 6 Oct ID filter. Byte copies under other IDs were not screened beyond agent 4's 21 Oct content screen (no confirmed copy, decision D4) and R3 for `mim_pool_v11`. No re-run is needed. Add one disclosure line to the P9-P16 "x" arms and to MIM100 / CP100: "the external pool was screened by ID and by a content screen; the source pool contains byte-identical cells under different module IDs, and a full-pool md5 dedupe was not applied."

**Licence and citation (D, audit §1.2).**
- No licence on the Dropbox, the HF mirror or the GitHub repo (GitHub licence API 404). Treat as research use only. Do not redistribute images or any derived pool.
- Cite Pratt, Mattheus, Klein 2023 (R, doi:10.1016/j.sasc.2023.200048), as the BenchmarkEL README asks "for any other dataset on this repo or dropbox link". Name the HF mirror (`sasan/scdd-unlabeled`, revision `7c4e73d8`) as the access channel. Cite Hanifi et al. 2025 (R, arxiv:2511.09604) only for the mirror's provenance.

## Open items left (none blocking)
- poolscout Q3 (one near-duplicate metric) matters only if the pool is ever downloaded.
- The sample directory (293.6 MB) can be deleted once Use A is written into the thesis.

---

## judge review (31 Oct 2026, 14:53 IST from date; md5 3cbe7ce8 as reviewed)

**Accepted as the item-13 close-out (Om B9: uses A + B), with one correction.**
- **Correction:** in Use A's table, row "Look of the pool vs E1", "E1 CSIR median mean 190, sd 55" includes E1's white letterbox.
  - On non-padding px, E1's mean of cell means is 137.3 vs train 136.5 (E, `team_2026-10-31_next/judge/out/intensity_stats.tsv`; domain's own idea 11 §2.3).
  - Either restate it on content px, or label it "whole crop, incl. letterbox".
  - The r_hp ≤ 0.81 dissimilarity is unaffected.
- **Checked against the vetter's recount and poolscout** (`review_suggestions_2026-10-30.md` §6b; audit):
  - 159,332 rows;
  - CSIR 9,204 → 22,931; ARTS 2,734 → 136,401; 0 BMRK / CFVS / SDLE;
  - 0 CSIR modules 400 to 2,362;
  - test 21 / val 23 / train 271 by ID;
  - all 117 `_rf`;
  - 192 colliding stems;
  - ~2,400 byte copies (1,400 to 9,500).
  - **Consistent.**
- "75% of E1 crack px in 29 scuff + half-cut cells" matches my m0 GT count.
- The disclosure line for the P9 to P16 "x" arms and MIM100 / CP100 is appropriate. Add it to handbook 11 rows 5, 25 and 26 at the next handbook pass.
