# Frozen PF2 B5 scorer (calib), local copy
Byte-identical to gaint `/home/noob/work/calib/frozen_candidate/` and runner's `el_f3/reports/pf2/post_extra/calib/`:
- calib_dump.py c172717e
- el_metrics.py 6e73ff11
- pf2_b5_hook.sh e06dfc5f
- pf2_b5_pooled.sh 873591ff

**FROZEN by coach (31 Oct, after runner's exact GPU smoke): FROZEN.md5 475d78fb; B5_DEVICE = cuda, tolerance profile exact. Used by the PF2 and THIN-B3 openings. No changes.**

The `../el_metrics.py` (f40a0efe) and `../calib_dump.py` (9694ad7d) in the parent folder are a superset: they add the synval (SHV1) set and the `routing` subcommand for PF2 §13.
- §13 is VOID: the routing pre-check failed (ideas/routing_precheck.md).
- So the superset is NOT frozen. Its B5 outputs are byte-identical to 6e73ff11 (8 regression summaries + records).
