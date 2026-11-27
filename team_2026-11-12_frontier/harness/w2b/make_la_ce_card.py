"""Write the la_ce method card (w2b builder, 17 Nov 2026) from the classbias_xfit variant 1 fits on gaint.

Source (E): /home/noob/work/bench_reads/stageB/B1/fit_gaint_pf/classbias_b.tsv (md5 d6a2bf00..., gaint PF v1.1 W1-G +
W1-G2 seeds 5 to 8, 20 fits; row (seed, fold k) = b_k, fitted on the out-of-fold cells of the folds != k of that seed,
bench_wt_b scripts/bench_classbias.py line 213 `fit_folds = sorted(f for f in CACHE[r.seed] if f != r.fold)`).
T10 spec (arm 2, gated follow-up): o_c = -b_c for c in FREE = {1, 2, 4, 5, 7, 11, 13, 15, 16, 20, 21}, 0 otherwise.

--mode perfold (proposed, S, waiting for the lead's ruling): fold k gets o^(k) = -mean over seeds 5..8 of b_{s,k}. b_k is
    fitted on folds != k only = the training cells of the fold-k run, so no held-out label enters the run. The card holds
    one row per fold keyed by the md5 of the root's splits/train.txt (`loss.logit_offset_by_train_md5.<md5>=[...]`);
    scripts/train.py picks the row and fails closed if none matches.
--mode pooled (the spec's literal text): one vector, o = -mean over the 20 fits (`loss.logit_offset=[...]`).
Per-fold means of 4 grid values (step 0.25) are multiples of 0.0625 (exact in binary); pooled means of 20 are multiples
of 0.0125. Values are written with repr() and parsed back by yaml to the same float.

Usage: python make_la_ce_card.py --mode perfold --out <repo>/bench/methods/la_ce_pf_v11.yaml
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

TSV = Path("/home/noob/work/bench_reads/stageB/B1/fit_gaint_pf/classbias_b.tsv")
TSV_MD5 = "d6a2bf002ca33bc0e845b5e76b8f4824"
ROOTS = Path("/home/noob/work/bench_data/roots")
FREE = (1, 2, 4, 5, 7, 11, 13, 15, 16, 20, 21)
SEEDS = (5, 6, 7, 8)
NC = 24
W = "/home/noob/.cache/huggingface/hub/models--smp-hub--resnet34.imagenet/snapshots/7a57b34f723329ff020b3f8bc41771163c519d0c/model.safetensors"
BASE_OPTS = ["data.labeled_fraction=1.0", "training.total_steps=20000", "data.split_seed=0",
             "training.labeled_batch_size=8", "data.mask_subdir=masks_v11", "data.mask_ignore_value=255",
             "model.name=smp_unetpp", "data.augmentation=labelsafe", "loss.supervised=ce_dice",
             "training.val_every=20000", "training.encoder_pf.freeze=1000", "training.encoder_pf.ramp=1000",
             "training.encoder_pf.lr_mult=0.1", "training.encoder_pf.wd=0"]


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def load_b() -> dict[tuple[int, int], list[float]]:
    assert md5(TSV) == TSV_MD5, f"{TSV} md5 is not {TSV_MD5}"
    rows = [l.rstrip("\n").split("\t") for l in TSV.read_text().splitlines() if l.strip()]
    assert rows[0][:2] == ["seed", "fold"] and rows[0][2:] == [f"b{c}" for c in range(NC)], rows[0]
    out = {}
    for r in rows[1:]:
        s, k, b = int(r[0]), int(r[1]), [float(x) for x in r[2:]]
        assert len(b) == NC and b[0] == 0.0 and b[14] == 0.0, r
        assert all(b[c] == 0.0 for c in range(NC) if c not in FREE), r
        out[(s, k)] = b
    assert sorted(out) == [(s, k) for s in SEEDS for k in range(5)], sorted(out)
    return out


def offset(bs: list[list[float]]) -> list[float]:
    """o_c = -mean_c(b) on FREE, 0.0 elsewhere (no -0.0)."""
    o = [0.0] * NC
    for c in FREE:
        m = sum(b[c] for b in bs) / len(bs)
        o[c] = -m if m != 0 else 0.0
    return o


def fmt(o: list[float]) -> str:
    return "[" + ",".join(repr(float(x)) for x in o) + "]"   # no spaces: bench_q word-splits the opts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["perfold", "pooled"], required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    B = load_b()
    if a.mode == "perfold":
        opt_lines, table = [], []
        for k in range(5):
            tl = ROOTS / f"cv5v2_v11_f{k}" / "splits" / "train.txt"
            h = md5(tl)
            o = offset([B[(s, k)] for s in SEEDS])
            opt_lines.append(f"loss.logit_offset_by_train_md5.{h}={fmt(o)}")
            table.append(f"#   fold {k} (train.txt md5 {h}): " + ", ".join(f"{c}:{o[c]:g}" for c in FREE))
        key_note = ("loss.logit_offset_by_train_md5 (5 rows, one per cv5v2_v11 fold, keyed by the md5 of the root's "
                    "splits/train.txt; row k = -mean over seeds 5-8 of the fold-k bias b_k, fitted on folds != k)")
    else:
        o = offset(list(B.values()))
        opt_lines = [f"loss.logit_offset={fmt(o)}"]
        table = ["#   all folds: " + ", ".join(f"{c}:{o[c]:g}" for c in FREE)]
        key_note = "loss.logit_offset (one vector = -mean over the 20 gaint fits, the spec's literal text)"
    head = [
        "# T10 gated follow-up la_ce (cards/T10_rare_classes_spec.md arm 2, last bullet; WAVE3_REVIEW: 'as specified, read",
        "# against OP-C'): house_r34_unetpp_pf_v11 with a logit-adjusted CE (P045): CE(z + o, y), the offset on the CE term",
        "# only (the crack / inactive Dice and every prediction use z); plain argmax at test, no post-hoc bias on top (P045",
        "# 5.3). o_c = -b_c from classbias_xfit variant 1 (the registered OP-C) for the 11 FREE classes, 0 for the others",
        "# (background 0 and crack 14 stay 0). Fits: gaint PF seeds 5-8, classbias_b.tsv d6a2bf00 (results/stageB/",
        f"# B1_classbias_xfit.md). Generated by harness/w2b/make_la_ce_card.py --mode {a.mode}. Offsets by class (nats):",
        *table,
    ]
    lines = head + [
        "name: la_ce_pf_v11", "version: 1", "family: cnn-unetpp",
        'papers: ["arXiv:2007.07314", "doi:10.1016/j.patcog.2026.114961"]', "kind: harness",
        "config: configs/supervised.yaml", "opts:", *[f"  - {x}" for x in BASE_OPTS + opt_lines],
        "weights:", f"  - path: {W}", "    md5: f57b430554b18e1238c4f92eac566544",
        "weights_key: model", "decision_rule: argmax24", "memory:", "  peak_mib: null", "  gate_mib: 11000",
        '  source: "peak not measured (built on CPU); wave 2a default gate 11,000 MiB until the memory smoke measures it"',
        "external: null", "diff_ref: house_r34_unetpp_pf_v11",
        f'notes: "w2b la_ce ({a.mode}). Config = house_r34_unetpp_pf_v11 plus {key_note}."',
    ]
    Path(a.out).write_text("\n".join(lines) + "\n")
    print(f"wrote {a.out} md5 {md5(Path(a.out))}")


if __name__ == "__main__":
    main()
