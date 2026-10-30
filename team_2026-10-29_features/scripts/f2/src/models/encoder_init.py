"""F1 switch ``model.encoder_init=<path>`` (opt-in; absent = no change): copy encoder weights into an smp model after
it is built. Loading consumes no random numbers, so the decoder init for a given seed is the same as without it.

Same contract as P15's ``load_encoder_init`` (``el_p14`` @ be67787): the source is a training ``latest.pth``
(``models.model``) or a bare state dict; any key prefix up to ``encoder.`` is dropped; a 3-channel first conv is summed
to 1 channel for a 1-channel model, as smp adapts ImageNet weights; every encoder tensor must match (strict).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import torch
import torch.nn as nn


def _encoder_of(model: nn.Module) -> nn.Module:
    net = getattr(model, "net", model)  # Track M R5 UpsampledInput wraps the core as .net
    if not hasattr(net, "encoder"):
        raise ValueError("model.encoder_init needs an smp model with an .encoder")
    return net.encoder


def load_encoder_init(model: nn.Module, path: str | Path) -> str:
    """Load ``path`` into ``model``'s encoder (strict). Returns a log string with tensor count and file md5."""
    path = Path(path)
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    st = torch.load(path, map_location="cpu", weights_only=False)
    sd = st["models"]["model"] if isinstance(st, dict) and "models" in st else st
    enc = {k.split("encoder.", 1)[1]: v for k, v in sd.items() if "encoder." in k}
    if not enc:
        raise ValueError(f"no encoder.* tensors in {path}")
    encoder = _encoder_of(model)
    target = encoder.state_dict()
    for k, v in enc.items():
        if k in target and v.ndim == 4 and v.shape[1] == 3 and target[k].shape[1] == 1:
            enc[k] = v.sum(dim=1, keepdim=True)
    encoder.load_state_dict(enc, strict=True)
    return f"{path} ({len(enc)} tensors, md5 {md5})"


def _core_of(model: nn.Module) -> nn.Module:
    net = getattr(model, "net", model)
    if not hasattr(net, "decoder"):
        raise ValueError("model.decoder_init needs an smp model with a .decoder")
    return net


def load_decoder_init(model: nn.Module, path: str | Path) -> str:
    """F2 switch ``model.decoder_init=<path>`` (opt-in, DDeP5): copy ``decoder.*`` weights into the model's decoder
    (strict on the decoder). ``segmentation_head`` is never loaded, so the 24-class head keeps its seeded init.
    Loading draws no random numbers. Source: ``{"models": {"model": sd}}`` or a bare state dict."""
    path = Path(path)
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    st = torch.load(path, map_location="cpu", weights_only=False)
    sd = st["models"]["model"] if isinstance(st, dict) and "models" in st else st
    dec = {k[len("decoder."):]: v for k, v in sd.items() if k.startswith("decoder.")}
    if not dec:
        raise ValueError(f"no decoder.* tensors in {path}")
    _core_of(model).decoder.load_state_dict(dec, strict=True)
    return f"{path} ({len(dec)} tensors, md5 {md5})"
