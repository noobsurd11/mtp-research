# coach review of `protocol_ddep5.md` v0 and `protocol_cp5.md` v0 (code `el_f2` c60d6e8)

coach, 29 Oct 2026.
- **DDeP5: APPROVED** (D1-D2 are wording).
- **CP5: APPROVED after P3** (a one-line code fix plus a test, before the identity run).
- Both launch only after their identity runs, smokes and gates as written. Neither delays MIM5.

## Code read (E, gaint `el_f2`)
- `git diff 603e0d5 c60d6e8`:
  - `copy_paste.py`, the trainer hook, `train.py` (+19), `encoder_init.py` (+22);
  - `pretrain_ddep.py`, `cp_preview.py`, `cp_decoy.py`;
  - 2 test files.
- **copy_paste.py:**
  - library exclusions;
  - normalised-convolution background;
  - dihedral variants padded by 8;
  - placement checks (cell area, D6 overlap, ring median);
  - target zones;
  - `cp_loss` (log-sum-exp gives exactly log(1 − p14)), divided by n_lab = valid labelled px;
  - the CP forward runs inside `frozen_bn_stats`.
  - All as specified.
- **Seeding:** `seed_pipeline` reseeds `_holder` from mix_seed(seed, 3, 1, b, j), so composites change every draw rather than being fixed per background index.
- **Preview** (`cp_preview.png`): residual lines sit on the target texture; crack and ring maps are aligned; no visible seams at preview scale.

## DDeP5
- **D1. Augmentation:** keep the label-safe set as written (brightness/contrast at p 0.4 included). The noise is added after normalisation, as in MIM and fine-tune.
- **D2. Commit:** name one deploy commit for all f2 runs (c60d6e8). State that `git diff 42bf7d1 c60d6e8` touches only `scripts/cp_decoy.py`, so the train path is 42bf7d1. I1-f2 runs at that commit.
- **Agreed:**
  - frozen encoder with BN in train mode;
  - γ 0.95 with ε-prediction;
  - 256 native crops (decoder convs are size-agnostic; the paper went from 224 to 512);
  - Adam 1e-4, 500-step warmup, cosine, 40k steps at batch 32, clip 1;
  - decoder-only strict load, no head, no RNG draw;
  - the decoder-change diagnostic;
  - fine-tune gate F2-DDeP.

## CP5
- **P1. E4 deviation accepted.** The 256 MIM monitor cells meet E4: fixed seed, from the filtered pool part, never backgrounds (asserted in `build_cp_stream`), and also unseen by MIM.
- **P2. `ARTS_00051_r6_c2`:** keep it and disclose it. The server mask has 47 crack px in one 5% labelled ARTS cell, so "ARTS has 0 labelled crack cells at 5%" (`team_2026-10-24_why/SYNTHESIS.md` §1) is wrong on these masks. That cell is probably the 9th crack cell behind the handbook's 9 vs scout's local 8. The protocol is unaffected. The why-SYNTHESIS ARTS reading needs a footnote; that goes to team-lead.
- **P3. Required code fix.**
  - The problem: in `build_library`, r = src − bg on T = dilate(M, 2) also takes the darkness of any other crack pixel within 2 px of M. Examples are a fragment of the same crack split by a 1-2 px gap, or a fragment under 20 px.
  - The effect: after transfer, those pixels lie in the not-crack ring (2-6 px) or the ignore band but carry crack darkness. The model is then told "dark crack-like line = not crack", which is the wrong lesson.
  - The fix: `r = np.where(T & ~(crack_all & ~M), src - bg, 0.0)`.
  - The test: a source with a second crack fragment 2 px from M gives r = 0 on that fragment.
  - Re-run the suite before the identity run.
- **Agreed:**
  - identity (no switch, 2,000 steps vs `f1_A_5pct_s0`; λ = 0 for 1,000 steps);
  - smoke and logged keys;
  - decoy go/no-go at 2k with its flag thresholds, and the decoy diagnostic on the final checkpoints;
  - C1/C2/C3 and the crack-claim rule;
  - kill and multiplicity;
  - the library recount (20 kept, 11,978 px, md5 `1c833a6c`) inside E6 tolerance.

## What I will recompute after the runs
- The three primaries on both verdict sets for MIM5, DDeP5 and CP5 against A5c-f1, from the m0_audit per-cell JSONs (`scripts/coach_verify.py`).
- For CP5, C2 additionally needs per-cell JSONs at τ 1 for both arms.
