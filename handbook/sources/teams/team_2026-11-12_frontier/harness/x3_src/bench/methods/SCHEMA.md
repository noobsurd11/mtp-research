# Method card schema (bench/methods/<name>.yaml)

One file per method the benchmark runs. Validated by `python -m bench.cards validate bench/methods/*.yaml`.
The queue renders the run's opts from the card (`python -m bench.cards opts <card> --seed K --run-name N --data-root R`)
and checks the run's `config_used.yaml` against the card (`python -m bench.cards cfgcheck ...`: exact equality, ignoring
`logging.experiments_dir`). `scripts/bench_infer.py --card` records the card path and md5 in the dump manifest and takes
`weights_key` and `decision_rule` from it.

| key | type | meaning |
|---|---|---|
| name | str | = the file stem |
| version | int | bump on any change; a changed card is a new method for the tables |
| family | str | free tag (cnn-unetpp, vit-dpt, external-nnunet, ...) |
| papers | list | paper ids (doi:..., arXiv:...) the method adapts; [] for house methods |
| kind | harness / external | harness = scripts/train.py in el_bench; external = its own codebase, writes dumps via bench/dumpfmt.py |
| config | path | harness: base YAML for --config (repo-relative) |
| opts | list of k=v | harness: --opts tokens; never seed, run_name or data.root (the queue adds them) |
| weights | list of {path, md5} | pretrained files the build reads; the queue md5-checks them before a start |
| weights_key | model / ema / teacher | which state dict of latest.pth the dump uses |
| decision_rule | argmax24 | how scores become the class map (more rules come with multi-label heads) |
| memory | {peak_mib, gate_mib, source} | measured peak (nvidia-smi per process) and start gate = peak + 2,048; null = smoke first |
| external | null or {venv, train_cmd, infer_cmd, export} | external adapters only |
| diff_ref | card name (optional) | cfgcheck / `diff` prints the config difference against this card |
| notes | str (optional) | |
