# applies the F2 CP switch to src/trainers/trainer.py and scripts/train.py (run once in el_f2)
from pathlib import Path


def rep(s, old, new, count=1):
    assert s.count(old) == count, (old[:80], s.count(old))
    return s.replace(old, new)


p = Path("src/trainers/trainer.py"); s = p.read_text()
assert "cp_lambda" not in s
s = rep(s, "        self.exit_after_step: int | None = None  # test hook: hard-exit right after this step (simulated crash)\n",
        "        self.exit_after_step: int | None = None  # test hook: hard-exit right after this step (simulated crash)\n"
        "        # F2 CP (opt-in, set by train.py after construction): copy-paste stream and its weight; lambda 0 or no\n"
        "        # stream = the plain step (no forward, no draw, no log keys).\n"
        "        self.cp_loader: Any | None = None\n"
        "        self.cp_lambda: float = 0.0\n"
        "        self._cp_it: Iterator | None = None\n"
        "        self._cp_out: dict | None = None\n")
s = rep(s, "                    loss_sup = self.sup_criterion(self.model(images), masks)\n                loss_con = torch.zeros((), device=self.device)\n",
        "                    loss_sup = self.sup_criterion(self.model(images), masks)\n                loss_con = torch.zeros((), device=self.device)\n"
        "                if self._cp_it is not None:\n"
        "                    self._cp_out = self._cp_loss(next(self._cp_it), masks)\n")
s = rep(s, "            loss = loss_sup + lam * loss_con\n",
        "            loss = loss_sup + lam * loss_con\n"
        "            if self._cp_out is not None:\n"
        "                loss = loss + self.cp_lambda * self._cp_out[\"loss_cp\"]\n")
s = rep(s, "        out = {\"loss\": loss.item(), \"loss_sup\": loss_sup.item(), \"loss_con\": loss_con.item(), \"lambda\": lam}\n",
        "        out = {\"loss\": loss.item(), \"loss_sup\": loss_sup.item(), \"loss_con\": loss_con.item(), \"lambda\": lam}\n"
        "        if self._cp_out is not None:\n"
        "            out.update({k: float(v) for k, v in self._cp_out.items()})\n"
        "            self._cp_out = None\n")
s = rep(s, "        unl_it = self.unlabeled_loader.iterate(start) if self.unlabeled_loader is not None else None\n",
        "        unl_it = self.unlabeled_loader.iterate(start) if self.unlabeled_loader is not None else None\n"
        "        if self.cp_loader is not None and self.cp_lambda > 0:\n"
        "            if self.ssl:\n"
        "                raise ValueError(\"cp is implemented for supervised runs only\")\n"
        "            self._cp_it = self.cp_loader.iterate(start)\n")
s = rep(s, "    # ---- SK1: auxiliary balanced head ----\n",
        '''    # ---- F2 CP: copy-paste stream loss ----
    def _cp_loss(self, cb: dict, masks: torch.Tensor) -> dict:
        """Separate forward of the pasted images with BN running statistics frozen (P13 mechanics); crack px:
        -log p14; ring px: -log(1 - p14) (log-sum-exp of the other classes); summed and divided by the number of
        valid labelled px, so a stream px weighs as one labelled px in the CE mean. fp32 losses."""
        img = cb["image"].to(self.device, non_blocking=True)
        tgt = cb["cp_target"].to(self.device, non_blocking=True)
        with frozen_bn_stats(self.model):
            logits = self.model(img)
        from src.data.copy_paste import cp_loss
        crack, ring = tgt == 1, tgt == 2
        n_lab = (masks != 255).sum().clamp(min=1).float()
        loss, p = cp_loss(logits, tgt, n_lab)
        with torch.no_grad():
            st = {"loss_cp": loss,
                  "cp_crack_px": crack.sum().float() / img.shape[0], "cp_ring_px": ring.sum().float() / img.shape[0],
                  "cp_p14_crack": p[crack].mean() if crack.any() else torch.zeros((), device=self.device),
                  "cp_p14_ring": p[ring].mean() if ring.any() else torch.zeros((), device=self.device),
                  "cp_fails": cb["cp_fails"].float().mean(), "cp_s": cb["cp_s"].float().mean(),
                  "cp_ring_med": cb["cp_ring_med"].float().mean()}
        return st

    # ---- SK1: auxiliary balanced head ----
''')
p.write_text(s)

p = Path("scripts/train.py"); s = p.read_text()
assert "cp_lambda" not in s
s = rep(s, "    trainer.metric_kw = data[\"metric_kw\"]\n",
        "    trainer.metric_kw = data[\"metric_kw\"]\n"
        "    # ``cp`` (opt-in, F2 / CP5; not in base.yaml): copy-paste stream (stream id 3) with weight cp.lambda. Built\n"
        "    # whenever the section exists (library and lists are checked), iterated only when cp.lambda > 0.\n"
        "    if cfg.get(\"cp\"):\n"
        "        if dataset != \"benchmark_el\" or method != \"supervised\":\n"
        "            raise ValueError(\"cp is implemented for supervised BenchmarkEL runs only\")\n"
        "        from src.data.copy_paste import build_cp_stream\n"
        "        trainer.cp_loader, cp_records, cp_sum = build_cp_stream(cfg, data[\"info\"], seed, nw,\n"
        "                                                                device.type == \"cuda\")\n"
        "        trainer.cp_lambda = float(cfg[\"cp\"].get(\"lambda\", 1.0))\n"
        "        logger.info(\"CP: lambda %s  %s\", trainer.cp_lambda, cp_sum)\n"
        "        with open(run_dir / \"cp_library.json\", \"w\") as f:\n"
        "            json.dump({\"summary\": cp_sum, \"components\": cp_records}, f, indent=1)\n")
if "\nimport json\n" not in s:
    s = rep(s, "import argparse\n", "import argparse\nimport json\n")
p.write_text(s)
print("patched")
