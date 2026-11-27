Round 4 (21 Nov 2026, 08:45 IST): **PASS** (B3 closed; no blocking item remains), pinned to OPENING_REQUEST fdc08f95, OPENING_RULE 065a7ddd, G 8bd1c27, R3 0c72cf94 and the script md5s in the "Round 4" section at the end; register with rule md5 065a7ddd after fin2 and its relay end.

Round 3 (21 Nov 2026, 08:20 IST): **FIX, one blocking item B3** (relative paths pass the TEST_MODE guard of run_opening_read.sh; one-line fix); fin2 adaptation, rule 32ac11dc, amendment patches accepted; FINAL_RULE_ADDENDUM_1 substance verified, tense to fix. See "Round 3" at the end.

Round 2 (21 Nov 2026, 07:25 IST): **FIX, one blocking item B2** (TEST_MODE dry runs can fall back to production label, relay and output paths); round-1 B1 and notes N2 to N15 closed or taken. Pinned to OPENING_REQUEST 932d21f2, OPENING_RULE 69f0c0f3, G 8bd1c27, R3 0c72cf94: see the "Round 2" section at the end.

Verdict (21 Nov 2026, 06:42 IST): **FIX, one blocking item (B1), read side only.** Pinned to OPENING_REQUEST.md
**608b41cac205d80bcc8dc559b2680860**, OPENING_RULE.md **69f0c0f382083f049e676221e9d8daac**, G **8bd1c2761c85f4721e444a8bf7124d2e5804973a**
(tree 38a8cdfd), R **19764b255ac29f3834bd2c5b1b53f85bc374ff58** (tree 866cee48), jobs 2e421795 / dbd54984, evidence MD5_evidence.txt
e94d7b8a and the script md5s in the table below. B1 (strict crack IoU contrasts printed without the convention band in
opening_verdict.py) touches nothing that steps 3 to 11 run or pin: the rule, the job lists, opening_make_jobs.py, t50_nolink.txt,
G, R, opening_register.sh, opening_queue.sh and opening_relay.sh stay as they are. **I find no blocking item in steps 3 to 11
(registration, deploy, stage, render, place, arm, relay); B1 must be closed, and its diff re-checked by me, before step 12
(run_opening_read.sh).** Whether to register before or after that round 2 is the lead's call; the fix cannot change a number.

# Review of the final opening package (E1 opening #8, test50 opening #19), round 1

Reviewer: opening reviewer (independent; I did not build this package). Review 06:10 to 06:42 IST, 21 Nov 2026.
E = shown by my own command (output quoted, or in my scratch), S = judgement.
Limits kept: gaint CPU only, nice 19, at most 8 threads at a time (chain smoke 2 x 4; the two pytest suites 4 + 4; everything else 1);
no GPU; cv02 read only (one `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 '<df, test -e, ls, free>'`; nothing inside
/tmp/noob_el/bench_q/fin or ext117 read); no file of H, G, R, F or any worktree changed (bench_wt_openg and bench_wt_open:
`git status --porcelain --ignored` identical before and after, E); my clones, copies, sandboxes and logs are in
/home/noob/work/bench_int_io/review_opening/ (copies of H there are md5-equal; the two smoke drivers there differ from H only in
their scratch path, E sed); no commit, no push. **No sealed label, mask, ignore file or prediction was read, opened, hashed or
summarised**: opening_register.sh and run_opening_read.sh ran only on synthetic dirs named by the real stem lists (every label
variable forced into my scratch and checked by a guard before each call); I read the stem lists, split files, the
masks_v11 MANIFEST.md5 as a hash list (copied for its pin), sealed_image_ids.tsv (image ids and module links, no label columns),
the header line of ext117/manifest.csv and of cells.tsv, and of cells.tsv only the stem column (row presence and field count of the
156 sealed rows, no value printed). I read the PIL header (mode, size) of the sealed images (E1 'L' 512 x 512 x 106; test50
'RGBA' 512 x 512 x 50, as the open val54): images are not labels and the protocol lets tools read sealed images.

**Short form.** The package does what the user decided and the lead ruled, and its code holds under my reruns: G's diff is the 4
stated paths, R's the 9; with Q/SEALED absent G's cq.sh renders the real fin list (cc4d7006, 85 lines) **byte-equal** to F's;
with SEALED it refuses every training and open line of that list; the job lists regenerate byte-equal; the render smoke gives
0 FAIL twice with both negatives refused (rendered lines = the builder's evidence, cmp); the synthetic chain smoke at PAR=2
reruns to read rc 0 (30 of 30 dumps in 873 s, the three read.txt md5-equal to the builder's) with its 3 negatives refused and no
output folder; my own 15 registration cases and 20 read cases (18 refusals, 2 positive controls) refuse or pass exactly as the rule says, every read refusal before
the output folder exists; pytest at G 839 passed / 5 skipped / 0 failed and at R 782 passed / 4 skipped / 0 failed (= the builder's), verdict tests 21 passed; my 33 boundary cases of opening_verdict.decide pass; of 15 verdict mutants the builder's tests catch 14 and mine 15; of 12 public_metrics mutants (incl. rule B scoring 1) the builder's tests catch 10 (N15). The rule matches the
user's decisions of 21 Nov 00:22, PUBLIC_BENCH 6c and FINAL_RULE section 4; the power numbers recompute to the printed ones.
**B1:** opening_verdict.py prints 13 lines with strict crack IoU contrast deltas and no convention band (E1 S1 to S5, C1-D4 lines,
every E1 stratum), against the user's decision (3) "strict crack IoU printed only with its convention band"; the same defect was
B3 of REVIEW_FINAL. Notes N1 to N15 are not blocking; N2, N3, N9, N6a and the verdict test of N15 are cheap and best done in the same round as B1.

## Files reviewed (md5 on disk at 06:10 and again at the end; unchanged)

| File (H = T/harness/final/opening) | md5 | Request section 12 | |
|---|---|---|---|
| OPENING_REQUEST.md | 608b41cac205d80bcc8dc559b2680860 | (pin of this review) | = |
| OPENING_RULE.md | 69f0c0f382083f049e676221e9d8daac | 69f0c0f3 | = **pinned by this review**; opening_register.sh default RULE_MD5 = this |
| opening_make_jobs.py | 9ab874c79c4c6c537e8ffe2c07d467e9 | = | = ; pinned in opening_register.sh (MAKE_MD5) |
| jobs/jobs_open_c1d4_no.txt / _yes.txt | 2e421795c86022f790ce258202dc572f / dbd54984b5e34555169796ac5a5726c5 | = | = ; regenerated byte-equal (E) |
| t50_nolink.txt | 66f48dc371fbdf8bf95eb66287e74283 | = | = ; recomputed equal from sealed_image_ids.tsv 201b0ec3 (E) |
| opening_register.sh | 7c1db27803abe6ce525bc98a06e3392b | = | = |
| opening_queue.sh | 34de69082a7272618e7fed3ca1016b0b | = | = |
| opening_rendercmp.py | edb49a036be8f8c7b0539f37b2dad240 | = | = |
| opening_relay.sh | 9667cff856b2c0fc21363a5c84b55a98 | = | = (relay_w1c.sh at stage bench_89b9ea5 = 74a2ec3d, E) |
| run_opening_read.sh | 43a468a4d588eccc4dd86aadb316bd03 | = | = |
| opening_verdict.py | c1eef6a442809a21f53869a2024f37c5 | = | = (B1, N2, N3 change it) |
| opening_verdict_test.py | 21b0be1b8d1df517e551a0380fa9ba5c | = | = |
| opening_render_smoke.sh / opening_chain_smoke.sh | 553fce22be28734ebce3d9a04ecce598 / dc2a1d55299cc27521f3e08dd9683db8 | = | = (rerun from md5-equal copies with my scratch path) |
| evidence/MD5_evidence.txt | e94d7b8a518a61d827705bc4c8e11840 | = | = ; `md5sum -c`: 31 of 31 OK (E) |
| G (bench_wt_openg) | 8bd1c2761c85f4721e444a8bf7124d2e5804973a, tree 38a8cdfdfd739e631547792e63dc4c1e707d21bb, parent 821dfad | = | = ; cq.sh 6371dc56, bench_infer.py a3268638 (= PINS of opening_queue.sh) |
| R (bench_wt_open) | 19764b255ac29f3834bd2c5b1b53f85bc374ff58, tree 866cee48a71de9f81822cc12393ebac4bfc7f3a3 (82ea81c, 19764b2 on 89b9ea5) | = | = |
| Background | FINAL_RULE.md 82867156, PUBLIC_BENCH.md 136e27cb, PROTOCOL_v0.2.md b8b7f66a, c3_deploy.sh 2d9fdbb3, cards 98f152de / a4a46a52 | | read |

## Blocking finding

**B1. Strict crack IoU contrasts without the convention band in the verdict file (read side; before step 12).** (E)
- User decision (3), 21 Nov 00:22 (log.md l.224): "strict crack IoU printed only with its convention band ... no decision rests on
  it"; OPENING_RULE section 4 prints it "with the convention band"; REVIEW_FINAL B3 required the band on every strict-IoU contrast
  line of final_verdict.py, a header line was not enough.
- opening_verdict.py l.172-173 (E1 "printed beside": S1 C3 - C1, S2 C3 - E-PF, S3 C3 - C2, S4 C2S5 - C1, S5 E-PF - C1, C1-D4 - C1,
  C2 - C1-D4) print `strict crack IoU {delta} [lo, hi]` and l.183 (E1 strata) `strict IoU {delta} [lo, hi]`, with no band and no
  "decides nothing". E: my chain smoke's verdict (pinned c1eef6a4) has these 13 lines (verdict_synthetic.txt lines 38 to 44 and
  48 to 53); only the P block (l.153) and the test50 lines (l.225-226) carry the band. On the real E1 the strata are 6 lines (src:
  BMRK, src:CSIR, type:halfcut, type:full, crack_cells, crack_free_cells).
- **Smallest fix:** a helper `band(d)` = "inside" / "outside the convention band +-0.019; decides nothing" appended to each
  strict-IoU delta in e1_lines (BESIDE_E1 and strata) and t50_lines (they say "inside the band" without the value), and one test in
  opening_verdict_test.py: every line of the verdict that contains "strict" and a signed number also contains "convention band".
  No number, bound or decision changes. Round 2: I check the diff of these two files and rerun the 21 + my 33 cases.

## Notes (not blocking)

**N1. read.txt of bench_open_read (R) prints strict-IoU contrasts without the band (S).** These are working tables written by R;
changing R re-pins R in three scripts. Leave R; the verdict is the result file. If the read.txt files are quoted, quote them with
the band.

**N2. Items the rule says are printed exist only in read.json (E, code).** Rule section 4: inactive IoU "printed with both
intervals" - the verdict (l.150) and read.txt print the seed-aware interval only. Rule section 5: "per-class IoU of the 13 robust
classes; component recall and precision (crack >= 20 px, inactive >= 100 px)" - computed (model_metrics: per_class_iou,
cc_rec50_20, cc_prec_20, in_cc_rec50, in_cc_prec) but printed in neither verdict.txt nor read.txt. No new look is needed to print
them later (read.json is in MD5.txt), but they are cheap to add in the B1 round (opening_verdict.py only).

**N3. Rule section 10 says the fin CV5 TTA verdict "is quoted in the opening's verdict file as registered" (E, code).** The verdict
quotes only the registration lines `c1d4 ... (fin verdict <md5>)` and `flags ... | ruled: ...`; with no FLAG, the fin decisions (a),
(b), (c) are not in the file. Smallest fix (B1 round): the registration or the verdict copies the three "(a) / (b) / (c)" decision
lines of the fin verdict (the verdict already reads REGISTERED.txt, which holds the fin verdict's md5).

**N4. C2 is entry class (c) by protocol 6.1 ("several models or views"; D4 = 8 views) (S).** P = C2 - C1 compares 8 views of
HRNet + SWAD with 1 view of PF; the same-view comparator C1-D4 is in the opening only if the fin read (a) replicates (FINAL_RULE
section 4 row (a), pinned and reviewed, so the opening rule follows it correctly). This is the user's chosen contrast and is not
wrong, but if (a) does not replicate, no row on E1 separates the D4 part from the model part. Recommendation for the claim
wording (lead): "C2 (HRNet-W18 U-Net++ + SWAD, D4: 8 views) against C1 (PF, one view)"; adding C1-D4 regardless would need a
ruling against FINAL_RULE's "iff" and costs 10 dumps (about 20 GPU-min, 1.3 GB).

**N5. OP-A only is a deviation from protocol 5.4, which counts a crack gain only "at OP-A and at OP-W inside the width band" (E
text, S).** Ruling 5 is right: the full-pool models have no held-out cells, so OP-W cannot be fitted without sealed cells; G1 / G2
(width ratio 0.85 to 1.15, pooled and CSIR) take OP-W's role. The verdict's disclosures should say so in one line.

**N6. The NAS relay path is not consistently supported (E; all fail closed).** (a) `opening_queue.sh unstage` hard-codes
RD=/home/noob/work/bench_relay/open_final (l.156), so with the relay on the NAS it refuses and the sealed images stay on cv02;
one-line fix `RD=${RD:-/home/noob/work/bench_relay/open_final}`. (b) /mnt/nas/noob_el_archive/bench_relay does not exist (E `ls`);
opening_relay.sh l.27 runs `df` on `dirname $RD` and refuses with "free ? GB": `mkdir -p` the parent first. (c) opening_relay.sh's
header says "RELAY_OPEN=<that dir> for the read"; run_opening_read.sh reads `RD` (the request's step 12 is right).

**N7. Disk and cost (E sizes, S).** cv02: /tmp 82 GB free at 06:2x (E), arm needs 35 GB, the opening peaks at about 11.5 GB; fin
must still write and remove its 75 D4 dumps first. No disk guard covers queue `open` (diskguard5 covers `fin` only, E): start a
copy for `open` or keep the window short. After the relay, GB/dumps on cv02 still hold the 20 or 30 sealed dumps (about 11.5 GB of
sealed predictions); `unstage` removes only DS: remove GB/dumps after the read's manifest check (logp copies are on gaint / NAS).
gaint: / has 44 GB free (E 06:2x); fin's relay adds about 12.5 GB -> about 31 GB; the opening relay adds about 11.5 GB and checks
FLOOR 25 only at its start, with no relay guard, on the filesystem where root's finllm runs: put RD on the NAS (after N6) or call
with FLOOR=40. NAS 8.2 TB free (E). GPU about 0.75 to 1.1 GPU-h and the read about 4 CPU-min at 8 workers (E chain smoke: read
06:26 to 06:30 on synthetic data) are as the request says.

**N8. The builder's chain-smoke evidence predates the pinned verdict script (E).** evidence/chain_smoke/MD5_synthetic.txt lists
opening_verdict.py 534cabff; the pinned c1eef6a4 was written at 06:01:47, after that read ended (06:01:32). My rerun with c1eef6a4:
read_e1 / read_t50_v0 / read_t50_v11 .txt md5-equal to the builder's (ca6196ee / 4ef5ad79 / 56a70ffd); the verdict differs in one
line only ("SE 0.0014; M 0.010" against "SE +0.0014; M 0.01"). Closed by my rerun.

**N9. test50 v1.1 masks are pinned by the MANIFEST.md5 md5 only, not file by file at the read (E code).** cellmeta `v11` checks
md5(MANIFEST) prefix 9c0e0687; E1 masks + ignore and v0 test50 are md5sum -c checked before the output folder (E: my negatives).
Cheap fix in run_opening_read.sh before the output folder: `grep -E '  (masks|ignore)/(<50 stems>)\.png$' MANIFEST.md5 | md5sum -c`.
Descriptive set only.

**N10. Ledger format (E).** opening_register.sh prints row #19 "for test_openings.md section B" with 7 cells (# / protocol / models /
primaries / registered / opened / result); section B's table has 6 columns, section E ("Benchmark openings (from 12 Nov)") has
exactly these 7. The E1 row #8 matches e1_openings.md's 7 columns. Lead's call where #19 goes.

**N11. Test-only overrides are honoured silently (E code).** opening_register.sh (SKIP_GIT, EXT_DIR, LABELED_DIR, MASKS_V11_DIR,
REPO_G, G, R) and run_opening_read.sh (PINS_FILE, DEVICE_OK, CELLS_TSV, BENCH_*, RF) record none of them. Most wrong combinations
fail closed (the read re-hashes the default label dirs against the registration; E), but run steps 3 and 12 from a clean shell
(`env | grep -E 'SKIP_GIT|PINS_FILE|DEVICE_OK|BENCH_|EXT_DIR|LABELED_DIR|MASKS_V11_DIR|CELLS_TSV|^RF='` empty). The registration also
accepts a fin verdict file that carries "[MECHANICS TEST, NOT A VERDICT]" lines; only the default path protects it.

**N12. C1 plain near-tie contingency (ruling 8): agreed, pre-write the amendment (S, E code).** The plain path fails closed when two
non-crack classes merge in float32 log(p) while their logits differ; with trained logits of magnitude >~ 1 their ulp (>~ 1e-7) is
larger than the merge width, and the CV5 plain PF dumps of these cards passed the same check, so it is rare. But the remedy needs
three edits (opening_rendercmp.py semantics call a C1 line with `--tta id` a FAIL; run_opening_read.sh's C1 glob
`fin_pf_v11_pool_s[5-9].e1_106.json`, the E-PF regex and the tta expectation; a job line in a new queue, and a failed dump leaves
its dump dir, which bench_infer refuses). Writing and reviewing that amendment now avoids a review under time pressure mid-opening.

**N13. test50 clusters are image ids (48), which form 45 physical modules (E, sealed_image_ids.tsv).** Two modules hold more than
one test image id, so the test50 seed-aware interval is slightly narrow. test50 decides nothing; E1's 71 image ids are 71 modules
(E), as the rule says.

**N14. Wording only (E, my cases).** With Delta missing and lo > 0 the outcome text says "below M"; with lo missing it says "the
interval holds 0". Both are NOT CONFIRMED (fail closed); cannot occur with real reads.

**N15. Test gaps found by mutation (E).** opening_verdict_test.py does not test hi = 0 (the "WORSE" wording at `hi <= 0` passes it;
my case "hi == 0 exactly" catches it); tests/test_bench_public_metrics.py never asserts `CLASSES` (spacing [1, 2] passes) nor the
pooled P / R / F1 (F1 = PR / (P + R) passes). The code is right today (E, read against the spec), and R is pinned, so this does not
block; add the hi = 0 case in the B1 round; the two R asserts belong to the next commit on R, if there is one.

## Lead's rulings on the builder's choices (section 9 / 11): my view
1. Seed-aware primary, fixed-model beside: **agree** (S). It is the recipe-level claim of opening #7's named claim; the fixed-model
   interval is printed (E verdict l.154) and labelled as a statement about the trained models.
2. M = 0.010 not re-estimated on E1: **agree**. It is protocol 5.4's cv02 relF1@2 margin (E table); the dumps run on cv02; the E1
   A/A (C1 {5,6} v {7,8}) is printed descriptive (E run_opening_read.sh l.142, verdict l.174).
3. E-PF kept, descriptive; C1-D4 by the fin verdict: **agree**. Protocol 6.1 (c) asks for the ensemble comparator; the rule states
   honestly that E-PF is not equal in inference cost (C3 = 8 x E-PF views) and that it decides nothing. See N4 for C1-D4.
4. C3 not on test50: **agree** (the user's "final model" there is C2; test50 decides nothing).
5. OP-A only: **agree**, with the disclosure of N5.
6. Inactive never a guard on E1: **agree** (10 inactive cells; label-noise band 0.05 to 0.07); printed, "inactive lower" named.
   Add the fixed-model interval (N2).
7. logp dumps to the NAS, images unstaged: **agree**; fix `unstage` for an NAS relay (N6a) and remove GB/dumps too (N7).
8. C1 plain with the `--tta id` remedy: **agree**; pre-write the amendment (N12).
9. cv02 /tmp/noob_el/ext117 untouched and unused: **verified in code** (E): G's sealed mode exports BENCH_EXT=DATA_S/e1_106 and
   BENCH_LABELED=DATA_S/legacy only; no H script names ext117 on cv02; the only `/tmp/noob_el/ext117` in G is the default of the
   old scripts/b3/m0_audit_b3.py, which no job line runs. I did not list or read the dir.

## What I verified (E unless marked)

**Diffs (check 1).** `git diff 821dfad 8bd1c27 --stat`: bench/q/cv02/cq.sh, scripts/bench_infer.py, tests/test_bench_cq_sealed.py,
tests/test_bench_infer_sealed.py; nothing else. `git diff 89b9ea5 19764b2 --stat`: bench/cellmeta.py, bench/derived.py,
bench/public_metrics.py, bench/sets/masks_v0_pool532.md5, scripts/bench_ens_dump.py, scripts/bench_open_read.py,
scripts/bench_score.py, tests/test_bench_opening_read.py, tests/test_bench_public_metrics.py; nothing else. Trees 38a8cdfd /
866cee48 = the pins.
- cq.sh (read in full around the change): SEALED is parsed only if the file exists; without it the only changes on any path are a
  declared empty array, two empty variables and `read` into two more words (`-z "$w4"` is equivalent to F's `-z "$wx"`), so the
  open-line refusal message is F's. With SEALED: the header refuses a bad key, a bad opening name, no manifest line, a DATA_S
  MANIFEST md5 other than SEALED's, a failing `md5sum -c`, and any dir named masks / ignore / masks_* under DATA_S; a line passes
  only as `--dumpof <run> --key <k> --tta <m> --set <s>` with s in SEALED, the full-pool root (NOD), a name ending `.<s>`, plus
  F's dump-only checks (run dir pattern, config_used.yaml + latest.pth, name prefix, charset, mode, key, no 10th field, cfgcheck
  against card, seed, run name and root). Every other line (training, fixture, smoke, open dump-only) reaches `[ $SEALQ = 0 ] ||
  fail` or the eight-word check. The sealed dump command adds `--opening <set's opening>` and, with logp 1, always both
  `--logp --ens-member`. Nothing in it trains, and bench_infer reads only S["images"] and S["stems"] (no mask path is opened;
  sets.resolve only builds paths).
- bench_infer.py: `--ens-member` refused unless sealed + `--opening` + `--logp`; `--logp` on a sealed set refused without
  `--ens-member`; the manifest gets `ens_member: true` only with it. logp = float16 log(p + 1e-12) of the view-averaged p (the
  rule's C3 input).
- derived.py / bench_ens_dump.py: without `--opening` the open path is unchanged (argmax pbar; sealed or fold-less members
  refused); with it, every member must have set_kind sealed, that opening, ens_member true, fold None; `--logp` refused; pred =
  argmax float32 log(pbar + 1e-12) (decision_rule argmax24_of_log_mean_softmax); manifest set_kind sealed, members' tta and
  checkpoint md5s.
- cellmeta v0: refuses non-legacy stems before any md5 / open (E1 first); pool manifest a3fa609f lists exactly the 532 train + val
  stems, 0 test, 0 E1 (E comm); test cells need the registration manifest by path and md5 and must list exactly the 50.

**Render (checks 1, 3).** My sandbox (render_fin_FG.sh: git archives of F and G as deploys, real yget / cards opts on each
deploy's cards, cfgcheck / validate / cvcard stubbed, logger absent): the fin list cc4d7006 renders 85 lines (10 training, 75
dump, 0 `--opening`, 0 `--ens-member`) through F and through G, md5 caa21961 both, `cmp` equal; with a valid SEALED + DATA_S the
same list stops at its first line "fin_hrnet_swad_v11_pool_s5: a sealed-opening queue (Q/SEALED) takes only sealed dump-only
lines; not starting", and its 75 open dump-only lines alone stop at "c3x_hrnet_swad_v11_f0_s5.swad.tta_d4: a sealed-opening queue
takes only '--dumpof ... --set <set>'". The builder's render smoke (md5-equal copy): "render compare: 0 FAIL" for 20 and 30 lines,
cfgcheck 20 / 30 calls, both no-SEALED negatives refused, "render smoke rc 0"; rendered files cmp-equal to evidence/render_smoke.

**Chain smoke (check 2).** `PAR=2 opening_chain_smoke.sh G R` (copy, my scratch): register rc 0; "dumps: 30 of 30 in 873 s";
"negative wrong REG_MD5: rc 1 (REFUSED: REGISTERED.txt md5 != REG_MD5); out dir created: no"; "negative tampered manifest: rc 1
(fin_pf_v11_pool_s7.test50: weights_key = 'swad', expected 'model'); out dir created: no"; "read rc 0"; "manifest check: 30 dumps,
device ['cpu']: OK"; records 15 / 15 / 15; "arms: E1 C1 5 C2 5 C1-D4 5"; "FINAL OPENING VERDICT: E1 P ... NOT CONFIRMED (the
interval holds 0; Delta > 0); Delta +0.0016 [+0.0000, +0.0048]" (synthetic, meaningless); "negative existing output: rc 1".
Worktrees unchanged after (E). Wall 06:11:58 to 06:29:59.

**Registration refusals (my synthetic dirs; check 5).** pos (verdict REPLICATED) rc 0, jobs dbd54984, 30 lines; pos (NOT
REPLICATED) rc 0, jobs 2e421795, 20 lines, 165 of 165 IO files read-only, stage MANIFEST 157 lines, 0 mask dirs in stage;
refused, with no IO made: FLAG D4 without FLAGS_RULED ("fin verdict holds a FLAG ((b) FLAG D4: ...)"), both (a) lines present ("row
(a) decision not found exactly once"), empty verdict, RULE_MD5 wrong, G = F ("G is not ... with tree 38a8cdfd"), R wrong, one E1
ignore file missing, E1 list md5 wrong, masks_v11 MANIFEST changed ("is not 9c0e0687"), one v0 file missing; second call on the
same IO "exists". FLAG with FLAGS_RULED: rc 0 and REGISTERED.txt records "flags (b) FLAG D4: ... | ruled: keep: test ruling". The
FLAG / (a) parsing also matches the real final_verdict.py format (E: harness/final evidence verdict_mechanics.txt: REPL 0, NOT 1,
FLAG 2 lines).

**Read refusals (fake relayed manifests on the registration above).** Each refused before the output folder ("output folder:
none"): one `.ok` missing; one `relayed` log line missing; ens_member missing on a logp job; ens_member on a non-logp job;
checkpoint_md5 not the relayed LATEST.md5; a second GPU model; opening name; C2 dump with tta false; writer md5; train revision;
n_cells 105; step 10000; seed; one E1 mask file changed after registration; one v0 file changed; masks_v11 MANIFEST changed;
REG_MD5 wrong; OPENING_RULE.md changed after registration. Positive control: the manifest check passes and the read creates its
folder, then stops at records (fake dumps), as expected.

**Sealing grep (check 5).** H: masks / ignore / masks_coded occur only as file hashes in opening_register.sh (l.63-64 `-f` tests,
l.74-75 md5sum) and as "no mask dir" checks in opening_queue.sh; opening_verdict.py only in strings. run_opening_read.sh hashes the
label files (md5sum -c) and scores them only after every check (step 12). R: mask reads only in cellmeta / bench_score (scoring)
and tests (synthetic masks or open cv5v3 cells). The DS staging dir holds images and lists only, checked three times (register
count 157, `stage`, cq.sh arming).

**Rule (check 4).**
- Candidates and readouts: C1 PF model plain; C2 HRNet-W18 U-Net++ SWAD key swad + D4; C3 = mean softmax of the 5 C2 = the user's
  three (log.md 00:22) and FINAL_RULE section 1; C2 is "the final model" (lead 01:29 Q1); E-PF and C1-D4 are labelled comparators
  that decide nothing; C1-D4 iff (a) = FINAL_RULE section 4 row (a).
- Labels: E1 = its own masks + ignore, as openings #1 to #7 (the bench path = m0_audit's masks + `~(ignore > 0)`, E code); test50
  v0 = masks_coded and v1.1; relF1@2 decides, strict IoU with the band (B1 aside).
- Primary, statistics, guards: as the rule; implemented as written (E code: bench_open_read boot() draws clusters then A's then
  B's models, Random(0), 2,000; guards from arm means; G2 = sources with >= 40 cells = CSIR only on E1, 101 of 106, E).
- Public table = PUBLIC_BENCH 6c line for line (merge, iou_cell, rules A / B / C, recall median, the five classes, pooled with
  both background rules, the SEiPV family incl. micro IoU); published rows copied correctly (E: verdict PUBLISHED against PUBLIC_BENCH
  2a). Disclosures: test50 leakage 8 / 7 / 19 (+16 without a link) = SPLIT_INTEGRITY 5b; prior looks 18 / 7 = the ledgers; selection
  of swad after the c3x read; E1 composition (E1 image ids with a pool cell in their module: 0 of 71, E).
- Power (section 6): Phi(Delta / SE - 1.96) at SE 0.019 gives 18.2 / 35.2 / 51.6 / 69.6 / 79.7% at +0.020 / 0.030 / 0.038 / 0.047 /
  0.053; at SE 0.017: 21.7 to 87.6%; at 0.021: 15.7 to 71.4%; MDE80 = 2.80 SE = 0.048 / 0.053 / 0.059 (E python). SE 0.019 = sqrt(0.013^2
  + 0.014^2) (protocol_SKR2C.md l.148, E); seed sd 0.017 / 0.022 / 0.026 = R1 thresholds / (2.58 sqrt(2/5)) (E). At the CV5-sized
  +0.023 to +0.027, power is about 22 to 30%: "NOT CONFIRMED, interval holds 0" is indeed the likeliest outcome.

**Tests (check 2).** Scratch clones (`git clone --shared` of the repo, checked out at G and at R, data links as in the worktrees; the worktrees were not used for pytest), `-p no:cacheprovider`, PYTHONDONTWRITEBYTECODE=1, OMP 4: **G full suite 839 passed, 5 skipped, 0 failed (392 s); R full suite 782 passed, 4 skipped, 0 failed (192 s)**, both equal to the builder's counts; they include section 8.2's targeted files (G: test_bench_cq_sealed + cq_final + infer_sealed = 60 tests; R: public_metrics + opening_read = 34 = 11 + 23; the request's section 3 says "11 + 21", section 7 "23": text only). H: `pytest -q opening_verdict_test.py` in my md5-equal copy: 21 passed (41 s). Disclosure: pytest's default basetemp /tmp/pytest-of-noob/ (rotating, last 3 kept) held the tests' tmp_path dirs; nothing else outside my scratch was written.

**Verdict tool (check 3).** My 33 boundary cases (rv_verdict_cases.py; all pass): Delta = M with lo 1e-12 CONFIRMED; Delta
0.0099999 "below M"; lo = 0 not confirmed; hi = 0 not WORSE, hi -1e-9 WORSE; Delta NaN / lo None fail closed; fixed-model
interval never decides (passes alone: NOT CONFIRMED; fails alone: CONFIRMED); G1 0.85 / 1.15 pass, 0.849 / 1.151 / NaN fail; G2
CSIR 1.16 fails alone; a source with 39 cells is no guard, with 40 it is; G3 B = 1.5 A passes, 1.5 A + 0.01 fails, A = B = 0
passes, A 0 B 1 fails, A None fails; G4 -0.010 passes, -0.0100001 and NaN fail; four guards fail together and are all named; a
failed headline with a failed guard stays NOT CONFIRMED; inactive wholly below 0 sets "inactive lower" and stays CONFIRMED; band
labels at +-0.019 inside, 0.0191 and None outside. **Verdict mutants** (rv_mutants.py verdict; one textual change each in a copy, the builder's 21 tests and my 33 cases run on it): M strict (`d > M`), lo inclusive (`lo >= 0`), M 0.005, width band 1.20, width band exclusive, FA x 2, mIoU -0.02, source floor 102 cells, the fixed-model interval deciding, guards ignored, guards rescuing a failed headline, inactive deciding, band 0.025, G4 on the fixed interval: **all caught by both**; "WORSE at hi <= 0" is missed by the builder's tests and caught by mine (wording of NOT CONFIRMED only; N15).

**public_metrics mutants (check 3).** rv_mutants.py public, on my clone of R (restored after, `git status` clean), the builder's public-metrics and --public tests: caught: rule B scores 1 (3 failed), rule C always 1, rule A keeps absent cells as 0, PV-S3 drop of the prediction column instead of the GT row, micro IoU acc / (2 + acc), median recall over predictions, Dice in place of IoU, gt from columns, avg defects over 5 classes, mean in place of median. **Missed: spacing = [1, 2] (CLASSES is never asserted; the tests pass [1, 2, 3] themselves) and PV-S3 pooled F1 = PR / (P + R) (pooled P, R, F1 are not asserted).** The code itself matches the spec (E: CLASSES = crack 14, gridline 15, inactive 11, ribbons 4, spacing 1 / 2 / 3 = sp_multi / sp_mono / sp_dogbone of bench/cv5v3.py CLASS_NAMES; F1 = 2PR / (P + R)); see N15.

## Not verified
- Anything on cv02 or a GPU (deploy, check / stage / render / place / arm / status / unstage against cv02, GPU memory and time of
  sealed dumps, relay of a sealed unit): the steps follow final_queue.sh's reviewed pattern; G's cq.sh render path ran for real in
  two local sandboxes.
- The real registration and the real read (forbidden to me); both ran on synthetic dirs with the same scripts.
- That the ext117 masks hold only 0 to 23 and 255 (m0core asserts < 24 on kept px): not opened by me; the same files were scored by
  m0_audit, whose load is the bench's, in E1 openings #1 to #7 (S).

## For round 2
B1 (and, recommended in the same round, N2, N3, N9 and N6a): send the diffs of opening_verdict.py, opening_verdict_test.py
(and run_opening_read.sh / opening_queue.sh if N9 / N6a are taken) with their new md5s and the request's section 12 updated. I will
check only those diffs, rerun opening_verdict_test.py, my 33 cases and the verdict mutants, and re-pin.

---

# Round 2 (21 Nov 2026, 07:10 to 07:25 IST): **FIX, one blocking item (B2)**

Pinned to: OPENING_REQUEST.md **932d21f2e7c61010690844bc0f7835e1**, OPENING_RULE.md **69f0c0f382083f049e676221e9d8daac** (unchanged),
G **8bd1c2761c85f4721e444a8bf7124d2e5804973a** (unchanged; bench_wt_openg clean), R3 **0c72cf942a5cc89accfcd02e1d2b443a033549d9** (tree
57eaeef9669ebb89524a3b960967b455490760e5, parent 19764b2; bench_wt_open clean); opening_verdict.py 65cfcf52, opening_verdict_test.py
0cf71d7c, run_opening_read.sh eaf7661a, opening_register.sh 8bcf673d, opening_queue.sh edae9df6, opening_relay.sh 4f2a28a3,
opening_chain_smoke.sh e465f378, opening_unstage_smoke.sh bdd1b1df, diskguard6.sh 8eb052e1, v11_filecheck.sh dcc3bfe4,
AMENDMENT_C1_TTAID.md f0650748 (+ make_amend.py 2546103d and patches 75f01a93 / 66e2bf8a / efd5e80f / 0bcfae8e, not applied);
unchanged: opening_make_jobs.py 9ab874c7, jobs 2e421795 / dbd54984, t50_nolink.txt 66f48dc3, opening_rendercmp.py edb49a03,
opening_render_smoke.sh 553fce22; evidence MD5_evidence.txt 02f1a1b2 (`md5sum -c`: 50 of 50 OK). All E, at 07:10 and again at 07:24.
Same limits as round 1. Every run used md5-equal copies of H (scratch H2) and synthetic dirs. Every label, relay, output and
verdict variable was set into my scratch and checked by a guard before each call; nothing ran on production paths or on cv02.

## Round 1 items: closed (E unless marked)
- **B1 closed.** Diff of opening_verdict.py (round 1 c1eef6a4 -> 65cfcf52): `band()` / `siou()` now carry every strict-IoU delta
  (P, S1 to S5, C1-D4 lines, every E1 stratum, the test50 contrasts). The builder's round-2 chain-smoke verdict has 20 lines with
  "strict": 17 delta lines, all with "convention band +-0.019; decides nothing", and 3 header / level lines without a delta.
  Tests 27 passed in my copy (41 s). My 33 cases: 0 FAIL. My two B1 mutants (stratum line without band; beside line without
  band) are caught by the new test, and so is the band threshold `<` instead of `<=`.
- **N2, N3, N4, N5 closed.** The inactive fixed-model interval, per-class IoU of ROB13 and the component table are printed; ROB13 in
  the verdict = bench/score_ext.py ROB13 (0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21). The fin decisions (a) / (b) / (c) are quoted
  only if the fin verdict md5 = the registered one, MECHANICS lines are absent and each decision occurs once. The entry-class (c)
  and OP-A-only disclosures are added. No number, bound or decision changed: the builder's chain-smoke read.txt md5s are
  ca6196ee / 4ef5ad79 / 56a70ffd, the same as round 0 and as my round-1 run.
- **N6 closed.** RD = /mnt/nas/noob_el_archive/bench_relay/open is the default in opening_relay.sh, run_opening_read.sh and
  `unstage`. The relay does `mkdir -p` of the parent before `df`; /mnt/nas/noob_el_archive exists and is writable by noob.
- **N7 closed.**
  - diskguard6.sh = diskguard5.sh with only the names changed (E diff: header, log, stop file, `for q in open`). It touches HOLD
    in /tmp/noob_el/bench_q/open only, never in fin. It starts, stops and deletes nothing. Its stop file DISKGUARD6_STOP and its
    log are its own.
  - The `guard` step places a new file (`test ! -e`) and a new tmux session, bench_diskguard6. `arm` refuses unless that session
    runs with md5 8eb052e1 and open has no HOLD. Nothing in either step touches fin's queue, its guard 5 or its files.
  - `unstage` removes cv02 dump dirs only after a check on both ends. My rv_unstage.sh (stub ssh mapping /tmp/noob_el into
    scratch; gaint has no /tmp/noob_el) ran 8 cases:

    | Case | Result |
    |---|---|
    | relay not done | refused; 3 of 3 dump dirs and DS kept |
    | one cv02 file differs | SKIP md5sum -c; that dir and DS kept |
    | extra file in a cv02 dump dir | SKIP count; that dir and DS kept |
    | cv02 RUN.md5 edited | SKIP RUN.md5; that dir and DS kept |
    | relayed copy corrupted on gaint | refused before any cv02 command; nothing removed |
    | wrong `.ok` md5 | refused before any cv02 command; nothing removed |
    | a second dump dir of one job | SKIP nodir; that job's dirs and DS kept |
    | all equal | REMOVED_DUMPS 3, then DS removed; runs/*/RUN.md5 kept; removal log written |

    In every refused or skipped case the step ends refused and DS stays.
- **N9 closed.** v11_filecheck.sh runs before the output folder (E: a changed synthetic v1.1 ignore file is refused, "test50 v1.1
  files: md5sum -c failed", with no output folder).
- **N10 closed.** The ledger rows are checked against the header column counts of their tables (7 / 6 / 7; E: TEST_MODE run).
- **N11: the refusals work as claimed (E, synthetic).**
  - Register: overrides without TEST_MODE (also TEST_MODE=0) refused, no IO made. TEST_MODE=1 with a wrong RULE_MD5 refused.
    TEST_MODE=1 with synthetic overrides: rc 0, and REGISTERED.txt starts "TEST MODE (dry run, NOT a registration; ...)".
  - Read: overrides without TEST_MODE refused. TEST_MODE=1 against a registration without the TEST MODE line refused. A changed
    fin verdict refused ("is not the registered one"). A TEST MODE registration runs through all checks to "20 dumps not
    relayed". Every read refusal leaves no output folder.
  - The MECHANICS refusal outside TEST_MODE, and the read's refusal of a TEST MODE registration outside TEST_MODE, could not be
    reached without production paths; I checked them by reading the code.
  - **But TEST_MODE does not keep a dry run off the sealed data: B2.**
- **N12.** The amendment is pre-written. `patch --dry-run -p1` applies all four patches cleanly to the round-2 files (E, my copy),
  although AMENDMENT_C1_TTAID.md says they are "against the round-1 files". I only skimmed the logic (read patch: amended job list
  of the same length, tta id expectation, `.ttaid.` globs and E-PF regex). If it is ever applied, it needs its own review, as its
  procedure says.
- **N15 closed.**
  - Public metrics: R3 adds only tests/test_bench_public_metrics.py (+18 lines; E diff). R3 full suite in my clone: 783 passed,
    4 skipped, 0 failed (193 s). My 12 public_metrics mutants on R3 are now **12 of 12 caught**, including spacing [1, 2] and
    F1 = PR / (P + R).
  - Verdict: my 15 round-1 verdict mutants are all caught by the new tests, including "WORSE at hi <= 0". Of 8 new round-2
    mutants, 7 are caught by the builder's tests.
  - Missed by both the builder's tests and my cases: `bad += fbad` -> `pass` in main(). The verdict would then not itself refuse
    a fin verdict md5 mismatch; run_opening_read.sh refuses it before the output folder (E above), so this is a redundant layer
    without a test (note).

## Blocking

**B2. TEST_MODE lets a dry run use production label, relay and output paths (E code; S on the risk).**
- **The gap (E code).** In TEST_MODE, both scripts honour whatever is overridden and fall back to the production defaults for the
  rest; nothing requires the sealed-data or output paths to be overridden.
- **What it allows.** Two short commands, both accepted:
  1. `TEST_MODE=1 IO=<scratch> bash opening_register.sh` hashes the real E1 masks + ignore and the v0 test50 masks, and copies the
     156 sealed images into the scratch IO. It writes a TEST MODE record whose hashes equal the real ones.
  2. `TEST_MODE=1 IO=<scratch> REG_MD5=<its md5> bash run_opening_read.sh` uses the default RD (the real NAS relay), BENCH_EXT /
     BENCH_LABELED / BENCH_MASKS_V11 (the real labels) and READ_ROOT (/home/noob/work/bench_reads).
- **The result (E code, line by line: REG checks, TEST MODE line, fin md5, R, mask hashes, v11 files, relay, manifests, all pass).**
  Once the real dumps are relayed, the second command passes every check and scores the sealed E1 and test50 labels into the
  production output folder /home/noob/work/bench_reads/open_final. That is an unregistered opening of both sealed sets. It also
  blocks the registered read ("output folder exists").
- **Why it blocks (S).** The builder's near-miss of a production-default registration in round 2 shows that dry runs with partial
  overrides do happen. The same chain existed in round 1 with silent overrides; I missed it then (my N11 said "most combinations
  fail closed").
- **Smallest fix (a few lines per script, plus negatives).**
  - opening_register.sh: with TEST_MODE=1, refuse unless IO, EXT_DIR, LABELED_DIR, MASKS_V11_DIR and FIN_VERDICT are all set and
    each differs from its production default.
  - run_opening_read.sh: with TEST_MODE=1, refuse unless IO, RD, RF, READ_ROOT, BENCH_EXT, BENCH_LABELED, BENCH_MASKS_V11,
    FIN_VERDICT and CELLS_TSV are all set and each differs from its production default.
  - Prefer requiring every one of them to lie under a scratch root, e.g. /home/noob/work/bench_int_io/.
  - Add two negatives per script (TEST_MODE with one label dir left at its default -> refused before anything is read or written).
  - No number, pin or registered file changes. opening_register.sh is a step-3 script, so fix it before registration.

## Notes (round 2, not blocking)
- **N16.** `unstage` deletes the cv02 copies after RELAY ALL DONE without requiring the read to have run. This is safe, because
  each copy is md5-equal to a relayed copy verified on gaint, but the logp dumps then exist only on the NAS. Run `unstage` after the
  read, as the procedure says.
- **N17.** I did not rerun the chain smoke in round 2. My targeted runs plus the builder's TEST_MODE chain smoke cover it (read rc 0,
  read.txt md5-equal to round 0, 5 negatives refused).
- **Disclosure.** pytest basetemps were in my scratch (`--basetemp`). No process of mine is left running.

## For round 3
Send the diffs of opening_register.sh and run_opening_read.sh (B2) with their new md5s and the negatives' output. I will check
only those diffs and rerun my N11 and refusal harnesses (synthetic, guarded).

---

# Round 3 (21 Nov 2026, 08:13 to 08:20 IST): **FIX, one blocking item (B3, a one-line gap in the B2 guard)**

Pinned to:
- OPENING_REQUEST.md **e6a3e68be2b4450b738f9d973cebc947**, OPENING_RULE.md **32ac11dce44b4a1c67a6ec017910771b**.
- G 8bd1c27 (unchanged, clean); R3 0c72cf94 (unchanged, clean); F2 9967d59 (tree adcdf7ec; F is its ancestor, E git).
- opening_register.sh 0b9b0323, run_opening_read.sh 4652ec58, opening_queue.sh bf531dae, opening_make_jobs.py 6ad871e0,
  opening_rendercmp.py c42cc6db, diskguard7.sh 1771e3fc.
- jobs 07e34090 / 3a308b9c; opening_testmode_guard_test.sh 1afb9a99; opening_render_smoke.sh fec8cd23;
  opening_chain_smoke.sh e0c67c75.
- AMENDMENT_C1_TTAID.md fff97f24, with patches 2f317ce0 / bcfec40d / 49271426 / 66e2bf8a (make_amend.py 2546103d), not applied.
- Unchanged from round 2: opening_verdict.py 65cfcf52, opening_verdict_test.py 0cf71d7c, opening_relay.sh 4f2a28a3,
  v11_filecheck.sh dcc3bfe4, opening_unstage_smoke.sh bdd1b1df.
- evidence MD5_evidence.txt 863cf891 (`md5sum -c`: 80 of 80 OK). FINAL_RULE.md 82867156 (unchanged);
  FINAL_RULE_ADDENDUM_1.md d5243f3a.
- All E at 08:13 and again at 08:18. Limits as before.
- CPU: 1 thread at a time, because the fin TTA read holds 8 workers.
- I used md5-equal copies in my scratch (H3), synthetic dirs only, and two scratch git clones.
- Nothing ran on production paths or on cv02. /home/noob/work/bench_open_io and bench_reads/open_final are absent (E).

## 1. B2 fix: works for absolute paths; relative paths bypass it in the read (B3)
- **Diffs.** Both scripts add the same guard right after the override check, before any read, hash or mkdir. With TEST_MODE=1:
  - the listed variables must be set;
  - every listed path, and every symlink found inside the scratch dirs, must resolve (`readlink -m`) under
    /home/noob/work/bench_int_io;
  - register checks IO, FIN_VERDICT, EXT_DIR, LABELED_DIR, MASKS_V11_DIR and their subpaths;
  - the read checks IO, RD, RF, READ_ROOT, BENCH_EXT, BENCH_LABELED, BENCH_MASKS_V11, CELLS_TSV, FIN_VERDICT and
    V11_FILECHECK_MANIFEST.
- **Builder's test, rerun from my copy:** "guard test: 0 FAIL". R1 to R4 and D1 to D5 are refused by the guard. Controls R5, R6 and
  D6 pass the guard and are refused later; no IO and no output folder is made.
- **B3. Relative paths pass the read's guard but are used relative to RT (E, synthetic).**
  - The guard resolves each path against the caller's cwd. Then run_opening_read.sh does `cd $RT` (l.80) and only afterwards
    uses BENCH_EXT / BENCH_LABELED / BENCH_MASKS_V11 / IO / RD / READ_ROOT (l.87-92 and later).
  - In the real read worktree, RT/data/labeled is a symlink to the real labeled data.
  - My rv_relpath.sh, all scratch: a TEST_MODE registration on scratch dirs; RT = a scratch clone at R3 whose data/labeled points to
    a scratch dir B; cwd = a scratch dir A that holds data/labeled with no mask files.
    - Control, BENCH_LABELED=<absolute A>: "REFUSED: v0 test50 masks differ from the registration".
    - **BENCH_LABELED=data/labeled (relative):** the guard passed on A, the v0 hash check passed on B's files through RT, and the
      read went on to "20 dumps not relayed".
    - **READ_ROOT=reads (relative):** also accepted; the output would go under RT.
  - So with the real RT, `TEST_MODE=1 ... BENCH_LABELED=data/labeled` run from a scratch dir that mirrors that layout would
    `md5sum -c` the real test50 v0 masks in a dry run. Scoring would still be refused (the scratch registration's hashes differ),
    but the round-2 aim, "a dry run can never reach the real data", does not hold.
  - **Smallest fix:** in tm_in of both scripts, refuse a non-absolute path before resolving it:
    `case "$1" in /*) ;; *) tm_no "$1 is not an absolute path";; esac`. Add one negative per script (a relative path refused by the
    guard). No other change. Round 4 = that diff and the guard test output.

## 2. fin2 adaptation (REVIEW_FIN2 N2 / N3): correct (E unless marked)
- **diskguard7.sh** = round-2 diskguard6.sh with only the names changed (header, log diskguard7.log, stop file DISKGUARD7_STOP);
  `for q in open` is unchanged.
  - fin2's harness/final2/diskguard6.sh (8137e124) covers `fin2` with the DISKGUARD6 names, so there is no collision.
  - The `guard` and `arm` steps now use bench_diskguard7 and pin GUARD7_MD5 1771e3fc. Neither touches fin, fin2 or their guards.
  - Comment typo at opening_queue.sh l.24: "fin2's disk guard 7" should read 6.
- **EXP -> F2B** in opening_make_jobs.py and opening_rendercmp.py (one line each, plus comments).
  - My regeneration gives 07e34090 / 3a308b9c, and each list equals the round-2 list with bench_821dfad -> bench_9967d59 (E diff).
  - Render smoke rerun from my copy: "render compare: 0 FAIL" for 20 and 30 lines; cfgcheck 20 / 30; both no-SEALED negatives
    refused; rendered files cmp-equal to the builder's evidence (30 lines name bench_9967d59/experiments).
  - bench_infer at G takes train_code_revision from the run's deploy REVISION (scripts/bench_infer.py l.212-216), so F2B dumps carry F2.
- **opening_queue.sh fin_check** now requires all of the following before check and arm (FB stays G's code reference):
  - F2B latest.pth = LATEST.md5 of fin2's relay at RF=/mnt/nas/noob_el_archive/bench_relay/fin2;
  - 10 × 'trained <run> rc=0' in /tmp/noob_el/bench_q/fin2/launch.log;
  - exactly one 'BENCH CV02 Q ALL DONE';
  - 'RELAY ALL DONE: 10 of 10'.
- **run_opening_read.sh** expects train_code_revision = F2 for every dump; RF defaults to the same NAS fin2 relay; the registration
  must hold `runs F2 9967d59...`.
- **opening_register.sh** pins F2 + tree adcdf7ec (git check), MAKE_MD5 6ad871e0 and RULE_MD5 32ac11dc, and writes the `runs F2`
  line. The builder's chain smoke with these md5s gives read rc 0; its read.txt md5s are ca6196ee / 4ef5ad79 / 56a70ffd, as in
  rounds 0 to 2; its 5 negatives are refused (E, evidence/chain_smoke).
- **Procedure points (S):**
  - fin2's relay must run with exactly `RD=/mnt/nas/noob_el_archive/bench_relay/fin2`. final2_relay.sh defaults to gaint, and RF
    is now a test-only override, so any other dir makes the opening's check and read refuse until edited.
  - FB (/tmp/noob_el/bench_821dfad) must stay on cv02 until the opening's `arm`, because gb_check compares GB's code with it.

## 3. Rule edit 69f0c0f3 -> 32ac11dc: accepted
- `diff` (= evidence/rule_edit_fin2.diff) changes exactly four places:
  - a 4-line header note;
  - section 2 "All checkpoints" (F2B location, steps 1 to 18,000 under F and the rest under F2 by resume, fin2's relayed
    LATEST.md5, train_code_revision F2);
  - section 8 (train_code_revision F2, fin2's LATEST.md5);
  - section 9 step 1 (fin2 `trained rc=0` × 10, fin2 ALL DONE, fin2 relay 10 of 10 before the opening).
- **No candidate, readout, inference, decision rule, label, contrast, interval, margin, guard, table or disclosure line
  changed.** The table of section 2 and sections 4 to 7 and 10 are untouched.
- The header note is accurate. Two wording points, not blocking:
  - it cites REVIEW_FIN2 N3, while FINAL_RULE_ADDENDUM_1.md is named in section 2;
  - "before any number" is better as "before any number of the final models": the fin CV5 TTA read, on other models, is
    running now.
- Optional (S): opening_verdict.py quotes registration lines registered / rule / jobs / c1d4 / flags / TEST but not `runs`, so the
  verdict file does not mention the resume. Add "runs" to the quoted keys, or one disclosure line naming FINAL_RULE_ADDENDUM_1.md.

## 4. Amendment patches: still apply, same content
- `patch --dry-run -p1` applies all four cleanly to my copy of the round-3 files (E).
- Their +/- lines are identical to round 2's patches; only context and offsets moved (E diff of the +/- lines).
- AMENDMENT_C1_TTAID.md now says the patches are against the current files (right).
- One stale line (l.37): "disk guard 6 already covers open" should say 7.
- Not applied; the full review only if the amendment is ever used, as before.

## 5. FINAL_RULE_ADDENDUM_1.md (d5243f3a): substance verified; tense must be fixed before it is cited as a record
- **Verified (E code at F2 = 9967d59):**
  - F -> F2 touches 6 paths. The train.py eval change applies only when every val/test cell is a training cell; the weight_avg
    guard change is `and not held <= set(stems)`; plus cq --resume and tests.
  - `WeightAvgSet.finalize` runs train_fold_loader and bn_recalibrate only on a deepcopy `scratch`, into which each averager's
    state is copied by load_state_dict. It writes only `self.final[<name>_bn]`. **`swad` (uniform, card start 10000 / end
    20000) is never written by finalize, and train_fold_loader is not on its path.**
  - PF's card has no weight_avg / bn_recal, so C1's `model` has no averager and no BN re-estimate.
  - The only readouts through the changed guard are raw_bn, ema_9998_bn and swad_bn; none is a candidate's readout.
  - seed.py `deterministic: True` = cuDNN deterministic + benchmark off only (the GPU noise caveat is right).
  - The incident causes match log.md 07:09 / 07:35.
- **Not yet facts (E log times; S):**
  - The note is dated about 07:55 but says "the 10 full-pool trainings ... stopped at step 20000" and "each run's latest.pth stayed
    at step 18000". At 07:55 only 8 had stopped; PF s8 / s9 started 07:53 / 07:54 and are expected to stop about 08:52.
  - Section 2 states in the past tense that steps 18,001 to 20,000 "ran under F2" and were "resumed exactly", tagged E. fin2 has
    not run (it waits for fin's ALL DONE, about 09:00).
- **Fix (final_builder2, before registration):** either put section 2 in the future tense now, or add a dated completion line
  after fin2. That line must give the E: fin2's 10 'trained rc=0', ALL DONE and 'RELAY ALL DONE: 10 of 10'. The lead then logs the
  addendum's final md5. Not blocking for the opening package (the rule names the file, not its md5), but it should be true
  before step 3.

## Round 3 verdict
**FIX:** B3 only (absolute paths in the TEST_MODE guard, one line per script plus one negative each).
**Accepted:**
- the B2 guard, apart from B3;
- the fin2 adaptation, the rule edit 32ac11dc and the regenerated amendment patches;
- the addendum's substance (its tense to be fixed before registration).

Nothing in steps 4 to 11 changes with B3 (it touches opening_register.sh at step 3 and run_opening_read.sh at step 12). Once the
B3 diff is checked, I expect to give PASS.

---

# Round 4 (21 Nov 2026, 08:35 to 08:45 IST): **PASS**

Pinned to:
- OPENING_REQUEST.md **fdc08f95**; OPENING_RULE.md **065a7dddfff2efd4897503561955093f**.
- G 8bd1c2761c85f4721e444a8bf7124d2e5804973a and R3 0c72cf942a5cc89accfcd02e1d2b443a033549d9 (both unchanged and clean); F2 9967d59
  (tree adcdf7ec).
- opening_register.sh fdcd3b59, run_opening_read.sh 2525575e, opening_testmode_guard_test.sh d6c91976, opening_verdict.py
  433f61de, opening_verdict_test.py a8895db3, opening_queue.sh 451a053d, AMENDMENT_C1_TTAID.md 43d2da58.
- Unchanged since round 3: opening_make_jobs.py 6ad871e0, opening_rendercmp.py c42cc6db, opening_relay.sh 4f2a28a3, diskguard7.sh
  1771e3fc, v11_filecheck.sh dcc3bfe4, the smokes (e0c67c75 / fec8cd23 / bdd1b1df), jobs 07e34090 / 3a308b9c, the amendment
  patches (2f317ce0 / bcfec40d / 49271426 / 66e2bf8a, make_amend.py 2546103d).
- evidence MD5_evidence.txt 75923e46 (`md5sum -c`: 80 of 80 OK); FINAL_RULE.md 82867156; FINAL_RULE_ADDENDUM_1.md 3001ce66.
- All E. Limits as before: scratch copies (H4), synthetic and TEST_MODE only, 1 thread, nothing on production paths or cv02.

**Diffs (E), each exactly as announced:**
- **opening_register.sh and run_opening_read.sh:** `tm_in` first refuses a non-absolute path, then resolves it; plus the
  RULE_MD5 pin 065a7ddd in register. Nothing else changed.
- **opening_verdict.py:** quotes the registration's `runs F2` line. Outside `--mechanics` it refuses unless there is exactly one
  such line. The read already requires that line before its output folder, so this is a second layer.
- **opening_queue.sh:** comment only ("fin2's disk guard 6").
- **OPENING_RULE.md:** one phrase in the header note, "before any number of the final models". No other line changed.
- **AMENDMENT_C1_TTAID.md:** l.37 "disk guard 7".

**Reruns (E):**
- **Guard test** from my copy: "guard test: 0 FAIL". R1 to R7 and D1 to D8 are refused by the guard; controls R5, R6 and D6 are
  refused later; no IO and no output folder made.
- **B3 mutant:** with the absolute-path check removed from both scripts, the same test reports "3 FAIL" (R7, D7, D8). The test
  catches B3.
- **My round-3 B3 demo** (rv_relpath4.sh; scratch RT clone whose data/labeled points to scratch B): the relative
  `BENCH_LABELED=data/labeled` and relative `READ_ROOT=reads` are now "REFUSED (TEST_MODE guard): ... is not an absolute path".
  The absolute control is unchanged ("v0 test50 masks differ").
- **Verdict:** opening_verdict_test.py 28 passed (41 s); my 33 boundary cases 0 FAIL.

**B3 is closed.** No blocking item remains. All earlier blocking items (B1, B2, B3) are closed.

**Before registration (lead), conditions already named, none a package defect:**
- fin2 ends with 10 × 'trained rc=0' and ALL DONE, and its relay runs with exactly `RD=/mnt/nas/noob_el_archive/bench_relay/fin2`
  and ends 'RELAY ALL DONE: 10 of 10'. opening_queue.sh `check` / `arm` enforce this.
- Fill the Completion section of FINAL_RULE_ADDENDUM_1.md and log its final md5.
- Keep /tmp/noob_el/bench_821dfad on cv02 until `arm`.
- Run steps 3 and 12 from a clean shell, with no test-only variable set; both scripts refuse otherwise.
- **The rule md5 to register is 065a7ddd.**

FINAL_RULE_ADDENDUM_1.md 3001ce66 is now written as a plan, with an empty Completion section (my round-3 point is taken). One
remaining slip: section 1 says "PF s8 and s9 had not started" by about 07:55. log.md 08:01 records their starts at 07:53 / 07:54
IST: they had started and had not yet reached step 20000. Correct that wording when the Completion section is filled.
