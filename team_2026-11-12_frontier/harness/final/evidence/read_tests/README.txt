Read tool tests (fork A, 21 Nov 2026; round 3 after FINAL_RULE.md 82867156: FLAG D4 / FLAG C2, approved E1 candidates C1-C3), CPU only, gaint, nice 19.
final_read_test.out       bash ../../final_read_test.sh <new dir>                  20 of 20 PASS (fake relay root, STUB; real bench_wt_final / bench_wt_fin checks; RELAY_FIN case)
final_verdict_test.out    python -B ../../final_verdict_test.py <new dir>          67 of 67 PASS (synthetic read.json, every row of section 4 incl. FLAG D4 / FLAG C2 and the CS - PF information)
final_verdict_mutants.out five tampered copies of final_verdict.py (headline lo >= 0; false_alarm_pf counted as width; no false_alarm_pf;
                          C2 check read from CS - PF; any GAIN supports D4): caught by 1, 2, 5, 4, 6 failing cases
mechanics_relabelled_c3x/ final_verdict.py --mechanics on a relabelled copy of the registered c3x read.json (see SOURCE.txt); NOT A RESULT
