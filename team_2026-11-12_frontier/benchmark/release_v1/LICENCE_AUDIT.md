# Licence audit, release v1 (lists and code only) (bench_release, 22 Nov 2026)

Scope: the user's ruling of 22 Nov, "lists and code only, plus one email to Pratt, held privately until the user approves".
Answers PROTOCOL_v0.2 Open 8 ("a list of cleared data and weights; a release decision").
Tags: E = found in a file or on a fetched page (URL given, fetched 22 Nov 2026), S = judgement. Nothing was uploaded or sent.
Per-file rows: `MANIFEST.tsv`. Changes from the project's files: `SANITIZE.md`. Staged tree: `files/`.

## 1. Tally
| Group | clear | unclear | forbidden |
|---|---|---|---|
| Staged files (63) | 58 | 5 | 0 |
| Candidates considered, not staged (11) | 4 (out of scope) | 1 | 6 |
| Data and weight sources (section 2, 11 rows that bear on us), for this release | 5 | 6 | 0 |
| Same sources, for a commercial model (not this release) | 3 | 6 | 2 |

The 5 unclear staged files hold statistics derived from BenchmarkEL label pixels: `lists/cells.tsv` (per-cell pixel counts,
pool and `_rf` rows), `code/bench/sets/celltypes.tsv` (cell type from mask spacing classes), `lists/cv5v2_check.txt`,
`lists/cv5v3_check.txt` (per-fold crack / inactive counts), `lists/labels_v11/CHANGES_pool532.tsv` (pixel counts of the v1.1
edits). No staged file holds an image, a mask, a weight, or a label or per-cell result of test50 or E1.

## 2. Sources: what each states
"Release" = this release (we ship identifiers, hashes, counts and code, no data). "Research" = training and scoring for the
thesis and the benchmark tables. "Commercial" = a model WattCycle could deploy.

| Source | Terms found (E) | URL | Release | Research | Commercial |
|---|---|---|---|---|---|
| BenchmarkEL (`dataset_20211104`, `20220723`, `20221008`); private sources CSIR, CFVS, ARTS inside it | no LICENSE file; GitHub API `license: null`; README: "Please, cite the following publications when publishing work based on these datasets." | https://github.com/TheMakiran/BenchmarkELimages | unclear | unclear (citation asked, use invited, no grant) | unclear |
| BenchmarkEL unlabelled pool (Dropbox) | `dataset_unlabelled/README.md`: no terms, citation request only | same repo, `dataset_unlabelled/` | unclear (we ship a stem list only) | unclear | unclear |
| E-SCDD (revised crack / inactive masks, `_rf` cells) | HF card `license: mit`; card text: "extends ... BenchmarkELimages dataset, originally released under the MIT License" | https://huggingface.co/datasets/snt-ubix/escdd | clear (MIT, attribution) | clear | clear for E-SCDD's own additions; S: its MIT claim for BenchmarkEL is not backed by any licence at BenchmarkEL's source, so it cannot clear the BenchmarkEL part |
| E-SCDD code repo (pv-ddpm) | no LICENSE file; GitHub API `license: null` | https://github.com/sntubix/pv-ddpm | not used | not used | not used |
| E-SCDD paper (arXiv 2511.09604) | CC BY 4.0 (paper text only) | https://arxiv.org/abs/2511.09604 | n/a | n/a | n/a |
| ELPV (source of the 50 + 5 BMRK cells) | README: images "licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License"; code Apache-2.0; "For commercial use, please contact us"; LICENSE file = CC BY-NC-SA 4.0 legal code. GitHub API field says "Other / NOASSERTION" | https://github.com/zae-bayern/elpv-dataset | clear (no image or adaptation shipped) | clear (non-commercial, attribution) | **forbidden** without the holder's permission (images and adaptations, S: and likely models trained on them, untested in law) |
| CWRU SDLE set (source of the 17 + 1 SDLE cells) | OSF licence field: "CC-By Attribution 4.0 International" (via api.osf.io; the page itself is a JS shell) | https://osf.io/4qrtv/ | clear | clear | clear (attribution) |
| UCF-EL (extra-data track only) | no LICENSE file; README has no licence text; GitHub API `license: null` | https://github.com/ucf-photovoltaics/UCF-EL-Defect | unclear (nothing shipped) | unclear | unclear |
| Pratt et al. 2023 article (Systems and Soft Computing 200048) | not read: DOI redirect not followed, ScienceDirect 403 | https://doi.org/10.1016/j.sasc.2023.200048 | unverified | unverified | unverified |
| ResNet-34 / ResNet-50 / VGG-16 ImageNet weights (smp-hub; PF, HOUSE, Hanifi, UCF, Pratt rows) | HF tag `license: other`, no licence text; card: "Original weights URL: https://download.pytorch.org/models/resnet34-333f7ec4.pth"; torchvision README: "The pre-trained models provided in this library may have their own licenses or terms and conditions derived from the dataset used for training." | https://huggingface.co/smp-hub/resnet34.imagenet ; https://github.com/pytorch/vision | unclear (not shipped) | unclear (research use common practice, S) | unclear |
| HRNet-W18 ImageNet weights (timm; the final model C2) | HF tag `license: mit`; card: "Trained on ImageNet-1k by paper authors", original repo HRNet-Image-Classification, sidebar "MIT license" | https://huggingface.co/timm/hrnet_w18.ms_aug_in1k ; https://github.com/HRNet/HRNet-Image-Classification | clear | clear | clear by the MIT text; ImageNet data question open (next row) |
| SegFormer MiT-B2 weights (smp-hub; segformer row) | NVIDIA Source Code License for SegFormer s3.3: "The Work and any derivative works thereof only may be used or intended for use non-commercially." ... "'non-commercially' means for research or evaluation purposes only." | https://github.com/NVlabs/SegFormer/blob/master/LICENSE | clear (not shipped; numbers are evaluation) | clear (research / evaluation) | **forbidden** |
| ImageNet-1k data terms (behind every ImageNet weight) | page not read (connection refused). timm README licence section read only as a model-made summary, not verbatim: "one should assume that the original dataset license applies to the weights" (unverified wording) | https://www.image-net.org/download.php ; https://github.com/huggingface/pytorch-image-models | unclear | unclear | unclear |
| smp code / timm code (libraries, not shipped) | smp: MIT ("some files are subject to other licenses"); timm: Apache-2.0 | https://github.com/qubvel-org/segmentation_models.pytorch ; https://github.com/huggingface/pytorch-image-models | n/a | clear | clear |

Not re-checked in this pass (S, low relevance to a lists-and-code release): MultiSolSegment (extra-data track; PROTOCOL_v0.2
section 2.3 says it states no licence), DINOv2 ViT-S/14 weights (used only to compute the pool list), the HF mirror of the
unlabelled pool.

Source tally (section 1): the 14 rows less 3 that do not bear on us (pv-ddpm code not used, arXiv paper text, the
smp / timm libraries). Release column: clear 5 (E-SCDD, ELPV, SDLE, HRNet, SegFormer: nothing of theirs is shipped or
the terms allow it), unclear 6 (BenchmarkEL, unlabelled pool, UCF-EL, the Pratt 2023 article, ResNet / VGG weights,
ImageNet data), forbidden 0. Commercial column: clear 3 (E-SCDD additions, SDLE, HRNet by its MIT text), unclear 6,
forbidden 2 (ELPV images, SegFormer weights).

## 3. Clear (E, per MANIFEST)
- All 29 Python files under `code/`: the project's own code (28 copied, 1 written for the release). Every "copied from" note inside them names the project's earlier files
  (m0_audit.py, m0_analyze.py, threshold_free.py, miou24.py); no third-party code was found (grep for copyright, licence,
  "adapted from", github.com).
- Lists of identifiers, hashes and project assignments: split JSONs, group files, score-exclude lists, module identity, pool
  manifest (image md5s), unlabelled-pool stem list, set lists, v1.1 pixel-md5 manifest.
- `results/BASELINES.md`: the project's own measurements, aggregates only.

## 4. Unclear, and why
- The 5 staged files of section 1: per-cell or per-fold statistics computed from BenchmarkEL labels, whose source grants no
  licence. S: counts and class tallies are facts, not the masks; the risk is low, but the authors have not been asked.
- Everything trained on ImageNet weights with the tag "other" (no weights are shipped, so this binds future model releases,
  not this one).

## 5. Forbidden (not staged)
- Images, masks (v1.1 PNGs, 1,746 files), checkpoints: the release rule; also BMRK images are CC BY-NC-SA 4.0 and BenchmarkEL
  states no licence.
- Per-cell scores of E1 and test50 (`read.json` of the final opening), label columns of the 156 sealed rows of `cells.tsv`,
  test rows of the v1.1 manifests: the release rule (no E1 or test50 labels). Staged versions keep identity columns or pool
  rows only.
- For commercial use (not this release): ELPV-derived images and adaptations, SegFormer MiT-B2 weights.

## 6. Secrets grep of `files/` (E)
Patterns, case-insensitive, over all 63 staged files (before `git init`):

| Pattern | Lines | What they are |
|---|---|---|
| `key` | 143 | dict keys and field names (`keys`, `BOOT_KEYS`, `weights_key`, `MANIFEST_KEYS`); no key value |
| `token` | 1 | prose: "the module token in the stem" (`lists/score_exclude_v3.txt` l.3) |
| `secret`, `password`, `passwd`, `BEGIN` | 0 | |
| `@` | 54 | metric names (relF1@2), numpy matmul (`w @ x`), `@dataclass`, BibTeX `@article` / `@misc` |
| IPv4 address | 0 | |
| email address (`x@y.z`) | 0 | |
| `/home/`, `/tmp/`, `/mnt/`, `~/` | 0 | |
| host names (gaint, cv02) | 0 | replaced by machA, machB (`SANITIZE.md`) |
| user names (noob, yugma, the GitHub user) | 0 | |
| ssh, `.env`, credential, api key, bearer, HF / GitHub / AWS token shapes | 0 | |
| strings of 41+ token characters other than md5s | 30 | comment rulers (`----`) and path fragments |

Result: no secret, credential, address, host name or user name in the staged tree. `SANITIZE.md` and `staging/` contain the
original strings by design (they record the substitutions); they are not part of `files/`.

## 7. Decisions for the user (one recommendation each)
| # | Decision | Recommendation (S) |
|---|---|---|
| D1 | Publish the 5 unclear files (label-derived counts and cell types)? | Send the email first. Publish them with the rest once the authors reply without objection; if there is no reply in 3 weeks, publish them (they are counts, not masks, and the README cites the authors as they ask). |
| D2 | Licence of this release (none chosen; without one, nobody may reuse it) | MIT for `code/`, CC BY 4.0 for `lists/` and `results/`; add the LICENSE file and fill the citation block in `files/README.md` section 8. |
| D3 | Who must approve publication besides you (thesis code under IIT Mandi; WattCycle partnership terms)? | Ask the mentor and WattCycle in writing before publishing; name both in the README. |
| D4 | Commercial use: may a WattCycle model be trained on BMRK cells (ELPV, CC BY-NC-SA 4.0) or use SegFormer weights? | No. For any commercial model, drop the 50 BMRK pool cells (or get ZAE Bayern's permission), never use MiT-B2, and ask the BenchmarkEL authors about commercial use (optional line in the email). The final model C2 uses HRNet-W18 (MIT) and trains on BMRK cells, so it is research-only as it stands. |
| D5 | Ship training and inference code too? | Not in v1. The dump format (`bench/dumpfmt.py`, numpy only) lets any codebase be scored; the training code carries the project's infrastructure. Revisit after the thesis. |
| D6 | E1 has no label-view builder in the release (the rule is stated in the README) | Before publishing, have someone cleared to open E1 masks add and test a short builder (release `20221008` masks, class 24 to 2, classes 25 to 28 to ignore). This agent was not allowed to read them. |

Also kept by default, change if you disagree (S): the E1 and test50 stem lists and the `cell_type` of sealed rows (identity,
needed for the E1 strata; the code's own rule treats them as safe); the E1 aggregate tables T8, T10, T11a in `results/`.
