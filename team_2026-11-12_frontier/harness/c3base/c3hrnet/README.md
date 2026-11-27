# c3hrnet: 5-seed confirmation of hrnet_w18_unetpp_pf on cv5v3 (lead, 16 Nov 2026, 14:08 IST)

Why: the row passed the screen on crack relF1@2 at OP-A and OP-W, on 532 cells and on the 416 clean cells (`results/ROWS2_PRELIM.md` section 2). Protocol v0.2: a screen pass is promoted to a 5-seed confirmation; the final 5-seed table is trained and scored on cv5v3.

What: 25 runs `c3h_hrnet_w18_unetpp_pf_f{0..4}_s{5..9}` on cv02, same deploy as c3base (`/tmp/noob_el/bench_89b9ea5`, 89b9ea5a, CODE.md5 OK, cq 02d5ba5f). Read against the c3base rows `c3_pf_v11` and `c3_house_v11` (same machine, same split, same seeds).

Job list `jobs.txt` (md5 8cf0c22bf70261641d08593be0f9ffb5, 25 lines), built by the lead from reviewed lines only, checked field by field by script:
- card, training gate, dump gate, logp, extra = the reviewed rows 2 line of the same fold (`bench/methods/hrnet_w18_unetpp_pf_v11.yaml`, 10478, 6200, 1, empty);
- root, fold, seed = the reviewed c3base PF line of the same fold and seed (`/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f<f>`);
- the card in the deploy is byte-identical to the reviewed rows 2 card (md5 c89314d8); its cv02 variant differs only in the weights path; weights md5 e6bb005d OK on cv02.
No independent review was run for this list (no new code, no new card, no new data; the queue's own arm checks passed: jobs md5, deploy, data, roots, cards, weights, gates).

**Superseded 16 Nov 14:56 IST: this queue is frozen (MAXC 0) after its first three runs; the other 22 lines run in the merged queue `../c3all/`.** Armed: cv02 tmux `bench_q_c3hrnet`, queue `/tmp/noob_el/bench_q/c3hrnet`, 08:38:29 UTC (14:08 IST), LPG 1, MAXC 8, gpumem 1141814, queue pid 1142062. Relay: gaint tmux `bench_relay_c3hrnet` (pid 2199340) to `/home/noob/work/bench_relay/c3hrnet` (N 25, names ^c3h_).
First-job check owed: `c3h_hrnet_w18_unetpp_pf_f0_s5 config OK (= card)` and `startup line OK: Labelled: 425 (/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107`.
Stop: `touch /tmp/noob_el/bench_q/c3hrnet/HOLD` on cv02; relay `touch /home/noob/work/bench_relay/c3hrnet/STOP`. Relayed dump folders off cv02: `c3_f81_list.sh` with `RD=/home/noob/work/bench_relay/c3hrnet B=/tmp/noob_el/bench_89b9ea5 NAMES_RX=^c3h_`.

Disk guard on cv02 (`diskguard.sh`, md5 9aeef4a5, tmux `bench_diskguard`, pid 1141451, log `/tmp/noob_el/bench_q/diskguard.log`): every 5 minutes, below 20 GB free on /tmp it touches HOLD in the c3base, c3hrnet and rows2 queue dirs. It starts, stops and deletes nothing. Stop: `touch /tmp/noob_el/bench_q/DISKGUARD_STOP`.
