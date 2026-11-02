# judge fact-check: scribe's 3 Nov drafts (2026-11-03 ~02:5x IST)
Checked:
- `SESSION_RECORD_2026-11-01_to_11-03.md` 9e5e3a97 (all of it);
- `handbook/21_a8_hc_b6_skr2_skr2e.md` eb057389 (all of it);
- `git diff` of handbook 00, 11, 12, 13, 14, 15, 16, 20.

Sources: verify_a8screen 748be1ce, verify_hc 85db8111, verify_b6 1060d0e5, verify_skr2_hc2 d13cd6fa, verify_skr2e 507e9e7a, protocol_SKR2C 91b76abd, ideas/arch_A1-A6, judge/b2_scores/*, judge/out/hc_smoke_width_pf2.txt, log.md.

**Numbers: correct almost everywhere.**
- Every A8, HC, B6, SKR2 / HC2, SKR2E, arch and B2 number I traced matches its source.
- Also matching: the PF2 3-image qualifier (+0.1886, CI [+0.0232, +0.3537], leave-top-3 +0.0225); the near-miss figures; and the rootcheck run 2 facts.

There are 11 fixes. F1-F4 are substantive; the rest are small.

## Fixes
- **F1. "E-PF is the best deployable model" upgrades a recommendation into an adoption.**
  - The user has not adopted E-PF. doc 15 §3d row 19 ("adopt E-PF over the house ensemble?") is still a decision waiting on the user (HEAD e390044 and this diff), and there is no user ruling in log.md. team-lead's 23:41 line is team-lead's wording.
  - Write instead: "E-PF at argmax stays the recommended deployable candidate (coach and judge, PF2E); the user's adoption is doc 15 row 19, still open; SKR2E did not displace it. FINAL 0.492 (cv02) is not comparable by rule."
  - Places:
    - record §0 SKR2E bullet and §7 verdict line;
    - doc 21 §5 verdict line;
    - doc 00 update line and its "Best deployable model:" bullet;
    - doc 11 row 48 verdict, the "Best deployable model after these" line, and claim 29 ("remains the best deployable model" → "remains the recommended deployable candidate");
    - doc 15 §1j bullet and row 19's 3 Nov note ("stays the best deployable model" → "still open; SKR2E did not displace E-PF as the recommended candidate");
    - doc 12 D90 title ("deployable model" → "deployable candidate").
- **F2. The two team-lead incidents are told two ways, and one conflicts with the log.**
  - record §11 items 6 and 7 say "[pending team-lead]". Item 7 also says the 11:18 relay cited verify_hc 046c2c81 (pre-fix).
  - doc 13 D50 / D51, doc 12 D81 and doc 21 §11 state team-lead's message details: the first HC relay at ~03:14, a corrected version at ~11:18, the centre-cell instruction at ~11:21, corrected at ~11:31.
  - log.md has **no** team-lead line at ~03:14. Its only HC relay line (11:18) says "HC verified n.d. (coach verify_hc.md **046c2c81** + judge recompute agrees), relayed to the user", i.e. it cites the pre-fix md5 at the time D51 calls the corrected relay.
  - Fix:
    - use one account in all four places, labelled "team-lead's account (message to scribe, 3 Nov)";
    - add the fact "the log has no ~03:14 relay line, and its 11:18 line cites 046c2c81";
    - ask team-lead to append a dated log line with the account (the log is the record of truth).
  - Same for item 2 (THIN tail carry-over). No placeholder may remain at commit.
- **F3. doc 21 §9 calls SKR2C "the first independent replication".** It is not independent: same test and E1 cells, a 3rd look (protocol_SKR2C §1). Write "the first fresh-seed replication (same 106 E1 cells; it replicates seeds, not cells)".
- **F4. The SKR2C status omits judge's stage-1 code review.**
  - judge reviewed runner's queue / guard drafts at 02:38 (`judge/review_s2c_stage1_code.md` b0d866a4, log 02:38): NOT READY, 7 must-fixes.
  - Two required features were not in the code yet: the outside-process HOLD and the live startup "Labelled ... val 54 test 54" check with a stop on mismatch. Also:
    - no exact recorded-cmdline check;
    - no owner re-check before SIGKILL;
    - a second stop possible ~23 s after the first;
    - no nvidia-smi timeout;
    - a dry run that never sends a real signal.
  - coach holds APPROVED until judge confirms the fixed code and the pass 1-3 logs.
  - Add this to: record §0 "Now" and §12 "Not yet launched"; doc 21 status table and §10; doc 15 §1j and §4e rank 1 condition; doc 16 Q60.
- **F5. record §12 gates:** state the locked gates, GATE_SKR01 **9,100** and GATE_SUPPF **9,000**: measured peaks 7,020 / 6,830 + 2,048, rounded up (protocol_SKR2C §2b). The draft has runner's prep arithmetic, 9,068 / 8,878. doc 14 §1.2e already gives 9,100 / 9,000 with the prep values in brackets, which is fine.
- **F6. doc 11 row 46 title "improves E1 crack detection"** contradicts its own verdict ("not 'E1 detection BETTER'"; any-hit n.d.). Title it "improves E1 crack relF1@2 on BEST without a test cost".
- **F7. B2: add the reported Hanifi crack line.**
  - On gate B's 32 Hanifi half-cells the raters found **1 of 14 cracks** (speck labels; reported, not gated; judge log 2 Nov 11:49).
  - The crack gate passed on house CSIR cells only. So option (b), "a crack-only agent prereg" for B2 (Hanifi panels), rests on a gate that did not test Hanifi cracks. Say so next to (b).
  - Places: record §10 and §13.2b; doc 15 row 25; doc 13 E33; doc 21 §8; doc 11 row 50; doc 16 Q59.
- **F8. HC2 B5 comp precision:** next to "0.728 vs 0.846 (all 50)", add "(clean 49: 0.889 vs 0.890)", as judge's fix 5 in verify_skr2_hc2 states. The precision gap is the noisy cell. Places: record §6.4 and anywhere else it is quoted.
- **F9. "The ignore label taught HC2 to call inactive areas crack"** (doc 21 §4.4, doc 16 Q56, doc 11 row 47 "inactive called crack") states a cause.
  - The split is a post hoc descriptive readout, and judge's wording on the cause is "no support, cannot exclude".
  - Write: "post hoc readout: on the 11 SHV1 views with inactive, HC2 predicts almost no inactive (IoU 0.002 vs HC 0.386) and ×5.1 off-GT crack px".
- **F10. record §1 timeline "SKR2E FAIL (pull 23:31 ...)":** the pull ended 23:30:29 (`results/skr2e/post_local.log`). Write 23:30.
- **F11. Disclosure to add (judge's own actions, 3 Nov 02:3x)** under record §11 "Other" / doc 13 D54:
  - judge ran read-only checks on gaint (ssh -a; md5sum / find / readlink of split files and of the two `labeled` dirs);
  - it created and removed one temp dir, /tmp/jdg_lab.XXXX;
  - no process was left; logged 02:3x.
  - Finding: el_thin's `data/labeled` is a separate copy (1,747 common files identical, plus 585 B3 `masks_escdd_s` files).

## Checked and OK (no change)
- A8 GO table and readings.
- HC co-primaries, mechanism, F51, corrections (a) incl. seed-aware [−0.054, +0.005].
- B6 Δ, the three CIs, power wording (b): SE 0.020 planned vs 0.038-0.039 realised, ~6% / 12% / 26%, 80% at ~+0.11, E1-size gain excluded.
- SKR2 fragility and not-a-bias-shift lines.
- SKR2E (c): 0.0015, "not a confirmation", bias share, guard CIs.
- HC2 design history (d) and "§7 (a2) formally triggered, not applied, HC route open".
- B2 gate numbers (e) and 68 / 72.
- arch A1-A6 numbers.
- near-miss D46.
- the 4 new rules in doc 12 §6.
- doc 14 §1.2e / §5d.
- The SKR2C design lines (g) as far as they go (see F4, F5).

Send the revised md5s; I OK before commit.
