# release_v1: staging package (bench_release, 22 Nov 2026)

Held privately. Nothing here was uploaded, pushed, published or sent. The user approves any publication separately.
Scope ruled by the user on 22 Nov: "lists and code only, plus one email to Pratt".

| Path | What |
|---|---|
| `files/` | the tree that would be published: 63 files (README, `lists/`, `code/`, `results/`). The release README is `files/README.md`. `files/.git` is a fresh repository with no remote and no commit (files added to the index only; the user commits under their own name when approving) |
| `MANIFEST.tsv` | one row per staged file (path, md5, bytes, what, source, source md5, terms status, reason, licence text or URL) plus 11 candidates considered and not staged |
| `LICENCE_AUDIT.md` | what is clear, unclear, forbidden; sources checked on the web; the secrets grep; decisions D1 to D6 for the user |
| `SANITIZE.md` | every substitution (rule, file, line), the two pin edits, content reductions, original and staged md5 of each changed file |
| `EMAIL_PRATT_DRAFT.md` | draft to the BenchmarkEL authors; address and sender left blank |
| `staging/` | the scripts that built `files/` (`stage.py`, `stage_results.py`, `make_manifest.py`, `make_sanitize.py`), their records (`sources.json`, `substitutions.tsv`), and the end-to-end check (`e2e/E2E_RESULT.md`, `e2e/make_oracle_dumps.py`) |

Only `files/` is meant for publication. `SANITIZE.md` and `staging/` contain the original paths and host names by design.

Rebuild from scratch: empty `files/` (keep `.git` or not), then run, in `staging/`, `python3 -I stage.py`,
`python3 -I stage_results.py`, apply the two pin edits listed in `SANITIZE.md` section 3, copy `staging/authored/*` (the
two files written for the release) into `files/`, then `python3 -I make_sanitize.py` and `python3 -I make_manifest.py`.
Git tree id of the staged index (`git write-tree` in `files/`): ff6274186b847e67757c15e95b2ae3252be44f00.

Checks run (E): the staged code imports and loads the staged lists; `tools/prepare.py` reproduces the legacy list md5s, the
cv5v3 held-out md5s pinned in `bench/sets.py`, and all 1,064 pool v1.1 mask pixel md5s; `bench_score.py records / summary`
and `bench_read_w1.py` (the README commands) run on oracle dumps of the 532 open pool cells (results in
`staging/e2e/E2E_RESULT.md`). No sealed label, prediction or image was read; no GPU was used.
