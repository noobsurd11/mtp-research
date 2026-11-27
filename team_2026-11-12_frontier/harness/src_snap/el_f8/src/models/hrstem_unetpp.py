"""F8 (idea 8, opt-in; protocol_A8screen.md): U-Net++ on a timm hierarchical backbone (ConvNeXt, SAM2 Hiera) plus a light
stride-2 stem.

``model.name: hrstem_unetpp`` selects it; nothing else changes and no config default is added. Keys (model section):
  backbone                 timm model name, e.g. ``convnext_tiny`` or ``sam2_hiera_tiny`` (a pretrained tag is allowed)
  backbone_weights         path to a weights file, or absent / none for random init
  backbone_weights_format  ``timm`` (default: a timm-format state dict, loaded by timm itself, which also adapts the first
                           conv to 1 channel by summing the RGB filters) or ``torchvision_convnext`` (torchvision ConvNeXt
                           state dict, remapped to timm names, RGB-summed here)
  hr_stem_channels         channels of the stride-2 stem (64)
  backbone_drop_path       stochastic-depth rate passed to timm as drop_path_rate (code default 0.0 = timm's default for
                           both backbones; protocol_A8screen sets it explicitly in the run opts)
  in_channels / num_classes  as smp_unetpp (1 / 24)

Why the stem: these backbones start at stride 4, but smp's U-Net++ decoder expects a stride-2 skip (smp builds U-Net++ with
a 0-channel stage there and the forward fails). The stem supplies it: conv3x3(s2)-BN-ReLU-conv3x3-BN-ReLU on the input.

Parameter names: ``encoder.*`` is the backbone only, so ``training.encoder_pf`` (F3) applies PF to the backbone and leaves
``hr_stem.*``, ``decoder.*`` and ``segmentation_head.*`` in the house group. The decoder and head are smp's own
UnetPlusPlusDecoder / SegmentationHead with the house settings (decoder channels 256-128-64-32-16, batchnorm, nearest
upsampling, no attention, no centre) and smp's initialisation.

Design choices: no drop-path (stochastic depth) in the backbone: ``backbone_drop_path`` 0.0 (timm's default) is written
explicitly into the screen's opts, so the only change between A8 and A8c is the backbone weights (the house ResNet-34 has none).
"""
from __future__ import annotations

import re
from typing import Any

import torch
import torch.nn as nn

DECODER_CHANNELS = (256, 128, 64, 32, 16)


class HRStem(nn.Module):
    def __init__(self, in_channels: int, channels: int) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, channels, 3, stride=2, padding=1, bias=False), nn.BatchNorm2d(channels), nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 3, padding=1, bias=False), nn.BatchNorm2d(channels), nn.ReLU(inplace=True))

    def forward(self, x):
        return self.block(x)


def torchvision_convnext_to_timm(sd: dict) -> dict:
    """torchvision ConvNeXt (features.*, classifier.*) -> timm ConvNeXt names. Classifier keys are dropped."""
    out = {}
    for k, v in sd.items():
        if k.startswith("classifier."):
            continue
        m = re.match(r"features\.(\d+)\.(.*)", k)
        assert m, k
        i, rest = int(m.group(1)), m.group(2)
        if i == 0:  # stem: Conv2d, LayerNorm2d
            out["stem." + rest] = v
        elif i % 2 == 0:  # downsample before stage i//2: LayerNorm2d, Conv2d
            out[f"stages.{i // 2}.downsample.{rest}"] = v
        else:  # stage blocks: CNBlock j: block.0 dwconv, block.2 LayerNorm, block.3 fc1, block.5 fc2, layer_scale (C,1,1)
            s = (i - 1) // 2
            mb = re.match(r"(\d+)\.(.*)", rest); j, r = int(mb.group(1)), mb.group(2)
            pre = f"stages.{s}.blocks.{j}."
            if r == "layer_scale":
                out[pre + "gamma"] = v.reshape(-1)
            else:
                name = {"block.0": "conv_dw", "block.2": "norm", "block.3": "mlp.fc1", "block.5": "mlp.fc2"}[r.rsplit(".", 1)[0]]
                out[pre + name + "." + r.rsplit(".", 1)[1]] = v
    return out


def build_backbone(name: str, weights: str | None, fmt: str, in_channels: int, drop_path: float = 0.0) -> nn.Module:
    import timm

    dp = dict(drop_path_rate=float(drop_path))
    if weights and fmt == "timm":
        m = timm.create_model(name, pretrained=True, pretrained_cfg_overlay=dict(file=weights), num_classes=0, in_chans=in_channels, **dp)
    elif weights and fmt == "torchvision_convnext":
        sd = torch.load(weights, map_location="cpu", weights_only=True)
        sd = torchvision_convnext_to_timm(sd)
        if in_channels != 3:
            sd["stem.0.weight"] = sd["stem.0.weight"].sum(1, keepdim=True)
        m = timm.create_model(name, pretrained=False, num_classes=0, in_chans=in_channels, **dp)
        missing, unexpected = m.load_state_dict(sd, strict=False)
        assert not unexpected and all(k.startswith("head.") for k in missing), (missing, unexpected)
    elif not weights:
        m = timm.create_model(name, pretrained=False, num_classes=0, in_chans=in_channels, **dp)
    else:
        raise ValueError(f"model.backbone_weights_format: unknown '{fmt}'")
    m.prune_intermediate_layers(indices=(0, 1, 2, 3), prune_norm=True, prune_head=True)
    if hasattr(m, "head"):
        m.head = nn.Identity()  # unused by forward_intermediates; keeps PF / Adam free of never-updated tensors
    return m


class HRStemUnetPlusPlus(nn.Module):
    def __init__(self, backbone: str, backbone_weights: str | None = None, backbone_weights_format: str = "timm",
                 in_channels: int = 1, num_classes: int = 24, hr_stem_channels: int = 64, backbone_drop_path: float = 0.0) -> None:
        super().__init__()
        from segmentation_models_pytorch.base import SegmentationHead
        from segmentation_models_pytorch.base import initialization as init
        from segmentation_models_pytorch.decoders.unetplusplus.decoder import UnetPlusPlusDecoder

        self.encoder = build_backbone(backbone, backbone_weights, backbone_weights_format, in_channels, backbone_drop_path)
        with torch.no_grad():
            chs = [t.shape[1] for t in self._feats(torch.zeros(1, in_channels, 64, 64))]
        self.hr_stem = HRStem(in_channels, hr_stem_channels)
        self.decoder = UnetPlusPlusDecoder(encoder_channels=[in_channels, hr_stem_channels, *chs], decoder_channels=DECODER_CHANNELS,
                                           n_blocks=5, use_norm="batchnorm", attention_type=None, interpolation_mode="nearest",
                                           center=False)
        self.segmentation_head = SegmentationHead(DECODER_CHANNELS[-1], num_classes, kernel_size=3)
        init.initialize_decoder(self.decoder)
        init.initialize_head(self.segmentation_head)
        init.initialize_decoder(self.hr_stem)

    def _feats(self, x):
        return list(self.encoder.forward_intermediates(x, indices=(0, 1, 2, 3), intermediates_only=True))

    def forward(self, x):
        return self.segmentation_head(self.decoder([x, self.hr_stem(x), *self._feats(x)]))


def build_hrstem_unetpp(cfg: dict[str, Any]) -> nn.Module:
    w = cfg.get("backbone_weights")
    return HRStemUnetPlusPlus(backbone=cfg["backbone"], backbone_weights=None if w in (None, "none", "") else w,
                              backbone_weights_format=cfg.get("backbone_weights_format", "timm"),
                              in_channels=cfg.get("in_channels", 1), num_classes=cfg.get("num_classes", 24),
                              hr_stem_channels=cfg.get("hr_stem_channels", 64),
                              backbone_drop_path=cfg.get("backbone_drop_path", 0.0))
