# SKCDF track: ideas and the baselines a reviewer would ask for (agent 4, 21 Oct 2026)

Every citation is a paper returned by the Research MCP in this session; its id is given. DCA (CVPR 2026) and CGS (TMI 2025) are described in handbook 05 §10. The MCP did not return them this session, so they are not cited here.

Ranked by (answers a real open question) × (cost).

## 1. Prior-shift control: post hoc logit adjustment (required in review_v1)
- **Source:** Menon et al., "Long-tail learning via logit adjustment" (`arxiv:2007.07314`).
- **Why:** ABSH mainly moves the evaluated head's class prior toward crack and inactive. A free bias `z_c − τ·log π_c` on an existing checkpoint may give the same IoU change. Handbook 05 §10 row 9 already notes that an old-era crack-logit bias gave +0.03, more than any SSL arm.
- **What to measure:**
  - τ = 1, fixed, on the BsD5 and A5c checkpoints;
  - optional τ grid on val only;
  - no training, so cost is minutes.
- **Reading:** if BsDB5 ≈ BsD5+LA, ABSH is a prior shift. AP and bin-0 share will separate a ranking gain from a bias gain.
- **Variant arm (v2 candidate):** logit-adjusted CE during supervised training (same paper, loss form) as the cheapest rebalancing baseline against AB5.

## 2. Rare-class copy-paste into unlabelled images (adapted for thin cracks)
- **Sources:** AEL (`arxiv:2110.05474`) and Bidirectional Copy-Paste, BCP (`doi:10.1109/cvpr52729.2023.01108`).
- **Why:** at t = 0.95, hard PLs feed the student almost no rare pixels from unlabelled cells. P17's PL counts and conf_frac show this. ABSH rebalances the head but adds no rare *examples*. Copy-paste adds them.
- **EL adaptation:**
  - paste labelled crack and inactive regions from the 23 labelled cells into unlabelled cells of the same cell type (mono / multi / half);
  - include a 2-px context band so that width stays defined;
  - inactive regions are whole cell parts, so paste on cell-aligned masks;
  - pasted pixels carry GT labels, all other pixels carry PLs.
- **Risk:** cracks pasted onto a different texture are easy to spot, which may teach a shortcut. Check FP on clean cells and E1 ext.

## 3. Class-imbalanced SSL baselines a reviewer will ask for
- **Papers:**
  - DHC (`doi:10.1007/978-3-031-43898-1_56`): distribution-aware and difficulty-aware loss weights from PL statistics; 3-D co-training;
  - GA loss (`doi:10.1007/978-3-031-73001-6_27`);
  - DuoMod-Net (`doi:10.1016/j.patter.2026.101570`);
  - DyCON (`doi:10.1109/cvpr52734.2025.02873`): uncertainty-aware consistency for imbalance;
  - SKCDF itself (`doi:10.1109/cvpr52734.2025.02416`) and its origin ABC (`arxiv:2110.10368`).
- **Minimum credible set for a thesis claim on 2-D EL:**
  - (a) DHC-style class-weighted unlabelled CE inside our MT recipe; the 2-D port is the weighting rule only, not the 3-D co-training;
  - (b) logit adjustment (idea 1);
  - (c) ABSH (SK1).
- **Note:** ABC is a classification method; its balanced classifier is what ABSH copies. ABC's own claim concerns the balanced head, which supports keeping SK1's `teacher_aux` path as a pre-registered secondary.

## 4. General SSL segmentation baselines
- **Papers:**
  - UniMatch (`doi:10.1109/cvpr52729.2023.00699`): FixMatch-style weak-to-strong with feature perturbation and dual strong views;
  - UniMatch V2 (`doi:10.1109/tpami.2025.3528453`).
- **Status:** our BsM recipe (EMA teacher, hard PL ≥ 0.95, CutMix, separate BN) is close to FixMatch-style SSL, but it is not a published method.
- **What a reviewer will ask:** "how does it compare with UniMatch at 5%?" Porting UniMatch's feature-perturbation branch onto L3 is about a day of work.
- **Recommendation:** add this before any "SSL helps rare defects" claim goes into the thesis. It is a separate protocol, not part of SK1.

## 5. Statistical design: split seeds (strong recommendation for any final claim)
- Every P-series and SK1 contrast varies the *training* seed on *one* labelled subset (split seed 0; handbook 13 A9).
- At 5%, inactive appears in **2** labelled cells. The subset choice is likely a larger variance source than the training seed, and the current rule does not see it.
- **For the final thesis claim:** run the winning contrast on split seeds 0–2 (the files exist: `data/splits/seed1`, `seed2`), with a paired analysis over splits.
- **Cost:** 2× the runs of the chosen contrast.

## 6. Data hygiene follow-ups (from data/decision.md)
- **Twins (D7).** Remove the 7 train twins of test cells from the unlabelled pool (pending the user). Also report the existing SSL claims without them.
- **Test-vs-val twins.** Val has twins of test cells (`CFVS_00046_r8_c4`). Val is not used for selection, but any future val-based τ or threshold choice should drop them.
- **Pool dedup.** Content dedup of the external pool against our train set (exact twins found under other IDs) before any external-pool arm. The same applies to `sasan/scdd-unlabeled` if it is ever used.

## 7. Thin-structure supervision (low priority for this track)
- **Papers:**
  - Skeleton Recall loss (`doi:10.1007/978-3-031-72980-5_13`) claims connectivity gains on thin structures, cracks included;
  - "Does the Skeleton-Recall Loss Really Work?" (`arxiv:2508.11374`) reports the gains do not hold up.
- **Our own result:** P14's offset-tolerant loss recovered none of the label gap.
- **Recommendation:** not an SSL question. Leave it out unless the user wants a supervised-recipe study.

## 8. Not recommended now
- **DINO-Mix** (`arxiv:2602.07819`): its frozen DINOv3 teacher works at patch 16, which is too coarse for 1–2 px cracks.
- **STAC** (`doi:10.1109/bibm62325.2024.10822225`): it enlarges small structures, the opposite of what relP@2 rewards.
- **SKCM** (SKCDF's cross-attention): its gain is +1.77 with sd 0.9–2.0, and its premise is a fixed organ location, which cracks do not have.
