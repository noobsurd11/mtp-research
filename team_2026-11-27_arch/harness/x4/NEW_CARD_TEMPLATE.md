# x4: adding a new arm (card) and screening it against COMBO

1. In /home/noob/work/bench_wt_x4 (branch bench_x4): copy the COMBO card
   `bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml` to `bench/methods/<m>.yaml`; set `name: <m>`; change only the
   opts the arm changes (append `- key=value` lines or edit values in place); keep `readouts` if the arm keeps SWAD (then the
   queue dumps `<run>.swad` and the read compares swad readout with COMBO's swad readout); update `papers`, `notes`, `diff_ref`.
   Same file under `bench/methods_cv02/<m>.yaml` with only the weights paths changed to /tmp/noob_el/cache/hf/... .
   A new architecture: a model-factory branch in src/models (e.g. bench_smp handles any smp decoder + timm `tu-` encoder
   with no code change); add a unit test; keep flag-off identity (the COMBO identity check below must stay IDENTICAL).
2. Check: `python -m bench.cards validate bench/methods/<m>.yaml`; `python bench/q/cv02/cvcard.py bench/methods/<m>.yaml
   bench/methods_cv02/<m>.yaml`; `python -m bench.cards diff bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
   bench/methods/<m>.yaml` (must list only the intended keys); pytest tests/test_bench_cards*.py.
3. Commit (message ends with the Co-Authored-By line); deploy: `bash T/harness/c3base/c3_deploy.sh <commit>`;
   export `X4=<full commit>` for every x4_queue.sh call.
4. Peak memory: if the arm changes the model or batch, a 300-step memory smoke first:
   `x4_make_jobs.py --out jobs/<m>_mem.tsv --seeds 5 --folds 0 --extra '--exit_after_step 300' bench/methods/<m>.yaml=<short>@<guess>`,
   place / arm, read the peak of `smoke_x4_<short>_f0_s5` in the queue's gpumem.log. Otherwise use COMBO's 9,386 MiB.
5. Jobs (5 folds x seeds 5, 6): `python x4_make_jobs.py --out jobs/<qn>.tsv bench/methods/<m>.yaml=<short>@<peak>`.
6. `bash x4_queue.sh place <qn> jobs/<qn>.tsv 3 15`; `bash x4_queue.sh arm <qn>`; `bash x4_queue.sh relay <qn> 10`.
7. When relayed: `bash x4_queue.sh score <qn>`; then in tmux
   `bash x4_read.sh <tag> <ARM>=<qn>:<short>:<m>:swad` (or `:<weights_key>` for an arm without a swad readout).
   Verdict: /home/noob/work/bench_reads/x4_<tag>/verdict.txt.
