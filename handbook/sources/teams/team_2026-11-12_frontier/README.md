# team_2026-11-12_frontier

Started 12 Nov 2026, 17:40 IST, on the user's instruction: find every paper of the last five-plus years that can raise the EL segmentation scores, adapt each to this project, test them on the GPUs, and close a hypothesis only after it is shown void. One month left (about 12 Dec 2026).

`BRIEF.md` is the context every agent reads first.

**Deliverable (the user, 12 Nov 18:15):** a new, trustworthy benchmark for EL defect segmentation (clean splits, one protocol, fitting metrics, many recent methods under it) and the best model on it; severity / post-evaluation only if valuable. Side agents: `harness/DESIGN.md` (one harness and one scorer for every method), `benchmark/PROTOCOL_DRAFT.md` (splits, metrics, tracks).

## Plan
| Phase | What | Where | State |
|---|---|---|---|
| A. Discovery | 44 direction scouts (Opus 5.5), 3 completeness critics, two-lens judging (upside, realism) of every deduped paper; each paper gets a score (raises our numbers) and a bench score (belongs in the benchmark) | laptop session, Workflow `frontier-paper-discovery`, run `wf_55e9fb90-47c` | launched 12 Nov 18:05; stalled at the usage cap 18:09; relaunched 19:34 (script v2, `log/workflow_A_v2.js`) |
| B. Paper cards | one agent per shortlisted paper (about 100): read the full text, check the code, write a hypothesis card with the adaptation, the cheapest decisive experiment and a kill line | laptop session (needs the Research MCP; campus VPN for IEEE / Elsevier full text) | after A |
| C. Experiments | grouped by mechanism cluster; cheap screen first, then seeds; critic-gated protocols | gaint + cv02, in tmux | after B; blocked on GPU access (below) |
| D. Assembly | combine the survivors into one model; confirm once on the sealed test and E1 sets | gaint + cv02 | last week |

## Screening instrument (lead's design, consistent with the standing rules)
- Development: module-grouped 5-fold cross-validation over the 532 train + val cells (fold roots exist from B6), plus F51 / H36 as an unseen-module development read. No test or E1 read during screening.
- Confirmation: the 50 test cells (reported with and without the noisy cell) and E1 (106 cells), opened once per locked protocol, for the few candidates that survive screening.

## Folders
- `directions/`: one markdown per scout (`Dxx_slug.md`) and per critic (`Cx_critic.md`).
- `rank/`: judge score files per chunk and lens; `SHORTLIST.md` and `shortlist.json` after the merge.
- `cards/`: one hypothesis card per shortlisted paper (phase B).
- `log/`: run notes.

## Access state, 12 Nov 20:10 IST
- gaint: direct over the institute VPN (`noob@172.18.22.20`), Cloudflare tunnel as fallback (`ssh.noobsurd.info`, drops about 1 handshake in 2). `scripts/gssh.sh`, `gput.sh`, `gget.sh` try both.
- gaint GPU: the user stopped the llama-server; finllm (5.9 GB, must never die) is the only outside process; about 25 GB free.
- cv02: reachable from gaint (`ssh cv02@10.8.1.106`, key installed on gaint by the user). Shared lab account: no agent forwarding, no keys copied there. Up 65 days, `/tmp/noob_el` intact. GPUs 6 and 7 free at 20:07, 0 to 5 busy with other users.
- Claude Code on gaint (2.1.292): logged in by the user; no MCP servers there.
- Research MCP: on the campus network; publisher full text works, capped at 40 downloads per day.
- SKR2C: all 10 runs trained (3 Nov 11:24); opening approved by the user 12 Nov; stage-2 build in progress (`runner`).
