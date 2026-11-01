**CONFIRMED by coach (verify_pf2.md), 1 Nov 2026: pull byte-identical (290 files, MANIFEST 3827f7c0); every number matches coach's recompute to 4 dp. Verdicts are coach's, in verify_pf2.md.**

# PF2 opening: runner's local analysis (1 Nov 2026), for coach's independent recompute

No verdict here: coach recomputes from the raw pull and rules. Rules as `protocol_PF2.md` §3 (rule 1 /3, 5 v 5, seeds 5-9; test two-set rule on crack IoU, relF1@2, inactive IoU; E1 co-primaries for PF2 only). Tags: E (file).

## Provenance (E)
- Opening on gaint 06:33:18-08:26:14 IST, `pf2_post.sh` 1c56be64, `post rc=0`; `tau0_check.txt`: tau0 == default cells for all 15, step 20000, code_revision e544133.
- Pull: `results/pf2/raw/` (MANIFEST.md5 290 files, `md5sum -c` OK). Local scripts: `pf2_post_local.sh` b9fe78a6, `pf2_e1_extra.py` d404dd25 (frozen), `pf2_e1_width.py` 241260db, Track M `m2_rung.py`, `scripts/ssl_rules.py`.
- Extras (FROZEN 475d78fb): `pf2_scuffign.sh` rc 0 (every run self-checked: 2 cells = the m0 JSON before writing); `pf2_b5.sh` rc 0 (B5_DEVICE cuda, 45/45 records self-checks PASS at tol profile exact; 45 per-run + 45 pooled summaries; b5_hook / b5_pooled logs 0 failing steps). B5 numbers are calib's / coach's to read (`raw/b5/sum/`).
- The `RUNG VERDICT` line inside the m2_rung files is Track M's 4-primary rule (includes mIoU_rob); a first-line note says so. Below, only the 3 protocol primaries.

## Contrast PF2: SUP100-PF − SUP100-g (E, `m2_rung_PF2.txt` md5 77764c27; cross-check `ssl_rules_pf2.txt` ac671e3d agrees)
| primary | set | SUP100-g | SUP100-PF | Δ | thr | rule 1 |
|---|---|---|---|---|---|---|
| crack IoU | all 50 | 0.4662 ± 0.0014 | 0.4651 ± 0.0048 | −0.0011 | 0.0100 | n.d. |
| crack IoU | clean 49 | 0.4693 ± 0.0015 | 0.4684 ± 0.0045 | −0.0009 | 0.0100 | n.d. |
| relF1@2 | all 50 | 0.8730 ± 0.0017 | 0.8847 ± 0.0057 | +0.0117 | 0.0100 | BETTER |
| relF1@2 | clean 49 | 0.8772 ± 0.0019 | 0.8891 ± 0.0054 | +0.0120 | 0.0100 | BETTER |
| inactive IoU | all 50 | 0.4385 ± 0.0136 | 0.4557 ± 0.0209 | +0.0173 | 0.0288 | n.d. |
| inactive IoU | clean 49 | 0.4524 ± 0.0139 | 0.4694 ± 0.0205 | +0.0171 | 0.0286 | n.d. |
- Width check: crack relP@2 +0.0009 (ok). relR@2 0.814 → 0.834 (all 50). Bootstrap relF1 Δ +0.0117 [−0.0034, +0.0292], P>0 0.93.
- **E1 co-primaries** (`pf2_e1_extra.txt` e135ce60, section 4; all 106 cells pooled per run, argmax):

| E1 | SUP100-g | SUP100-PF | Δ | thr | rule 1 |
|---|---|---|---|---|---|
| crack recall | 0.1715 ± 0.0238 | 0.1986 ± 0.0214 | +0.0271 | 0.0370 | n.d. |
| inactive IoU | 0.0481 ± 0.0260 | 0.2371 ± 0.0271 | +0.1890 | 0.0433 | BETTER |
| crack precision (flag only) | 0.4539 | 0.4284 | −0.0255 | | flag needs recall BETTER and drop > 0.05: no |
- Per seed (E1 recall / inactive IoU): SUP 0.1886 0.1473 0.1879 0.1436 0.1900 / 0.0399 0.0248 0.0578 0.0293 0.0886; SUPPF 0.1945 0.1992 0.2306 0.1983 0.1705 / 0.2465 0.2252 0.2074 0.2787 0.2276.
- LA tau 1 (reported, `m2_rung_PF2_tau1.txt`): crack IoU +0.0029 / +0.0030 n.d.; relF1@2 +0.0126 / +0.0127 BETTER; inactive +0.0171 n.d. (all / clean).
- Scuff-ignored test (descriptive, `m2_rung_PF2_scuffign.txt`): relF1@2 +0.0117 / +0.0119 BETTER; crack IoU and inactive n.d. (same signs as the verdict set).

## Contrast RN: RN50-PF − SUP100-PF (E, `m2_rung_RN.txt` md5 726d2706; ssl_rules agrees)
| primary | set | SUP100-PF | RN50-PF | Δ | thr | rule 1 |
|---|---|---|---|---|---|---|
| crack IoU | all 50 | 0.4651 ± 0.0048 | 0.4595 ± 0.0030 | −0.0056 | 0.0100 | n.d. |
| crack IoU | clean 49 | 0.4684 ± 0.0045 | 0.4628 ± 0.0028 | −0.0057 | 0.0100 | n.d. |
| relF1@2 | all 50 | 0.8847 ± 0.0057 | 0.8820 ± 0.0028 | −0.0028 | 0.0100 | n.d. |
| relF1@2 | clean 49 | 0.8891 ± 0.0054 | 0.8862 ± 0.0028 | −0.0029 | 0.0100 | n.d. |
| inactive IoU | all 50 | 0.4557 ± 0.0209 | 0.4269 ± 0.0060 | −0.0289 | 0.0251 | WORSE |
| inactive IoU | clean 49 | 0.4694 ± 0.0205 | 0.4405 ± 0.0065 | −0.0289 | 0.0249 | WORSE |
- Per source (test, inactive IoU): ARTS 0.534 → 0.000 (SUP100-g also 0.000), BMRK 0.360 → 0.313, CFVS 0.556 → 0.556.
- RN named secondary (E1, descriptive; `pf2_e1_extra.txt` section 3): E1 scuff + half-cut crack recall SUPPF 0.1378 ± 0.0237, RN50-PF 0.1153 ± 0.0090; all-106 crack recall 0.1986 vs 0.1918 (n.d.), inactive IoU 0.2371 vs 0.2372 (n.d.). The 5-member ensemble at bias +0.75 (as D) is not computed here.
- Scuff-ignored test (descriptive): inactive WORSE in both sets (same as the verdict set).

## Reported (E)
- **E1 width-robust** (`pf2_e1_width.txt` df3897ce, all 106): relF1@2 SUP 0.3837, SUPPF 0.4202, RN50-PF 0.4173; relR@2 0.3007 / 0.3515 / 0.3497; component recall 0.1730 / 0.2284 / 0.2027 (SUPPF − SUP +0.0554, thr 0.0552: BETTER, reported only); strata in the file.
- **E1 strata** (`pf2_e1_extra.txt` section 3): half-cut 58 inactive IoU SUP 0.162, SUPPF 0.537, RN50-PF 0.598; full 48: 0.025 / 0.097 / 0.071. Scuff + half-cut 29 crack recall 0.103 / 0.138 / 0.115.
- **Crack px on crack-free cells** (sum over cells, mean over seeds): test (2 cells) SUP 0.2 / SUPPF 0.0 / RN50-PF 14.2; val (31) 164.8 / 6.8 / 17.0; E1 (74) 3,626 / 3,931 / 4,327.
- **Encoder cosine at 20k** (`raw/enc_cosine_20k.txt`): SUP100-g layer3 / layer4 0.007-0.017 / −0.000-0.004 (erased, as protocol_100); SUP100-PF 0.928-0.929 / 0.931-0.941; RN50-PF 0.928-0.930 / 0.907-0.919, except s5 layer4 0.998 (as at its 4k gate).
- **10-seed pooled** (seeds 0-9, descriptive, `pooled10_e1_descriptive.txt`): E1 crack recall SUP 0.170, SUPPF 0.206; E1 inactive IoU 0.044 / 0.241.
- **Memory** (`gpumem.log`, 1 s during the opening): scoring peaks rescore 6,020 (RN50), m0 / m0_tau 5,254, LA **7,758** MiB; min free **2,635 MiB** at 07:45:13 (LA beside THIN SKR s5 7,020 + CLD s5 8,374 + finllm 5,876): floor held by 587 MiB; the GS 7,900 gate assumed the smoke's 5,824. Disclosed in log.md; THIN's opening GS raise to 9,900 proposed.
