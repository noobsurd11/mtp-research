"""elbench model registry (opt-in; nothing here is reachable from an existing model.name).

model.name = bench_smp   any smp 0.5.0 architecture with any smp or timm-universal (tu-*) encoder.
  decoder               unet | unetplusplus | fpn | deeplabv3 | deeplabv3plus | pspnet | linknet | manet | pan | upernet |
                        segformer | dpt   (smp class names, case-insensitive)
  encoder_name          smp encoder (resnet34, mit_b2, ...) or tu-<timm name>; DPT needs tu-<ViT>
  encoder_weights       smp weights tag (e.g. imagenet; read from the offline HF cache), or null for random init
  encoder_weights_file  optional local timm-format file for a tu- encoder (passed to timm as pretrained_cfg_overlay);
                        timm adapts the first conv / patch embedding to in_channels=1 by summing the RGB filters
  decoder_kwargs        dict passed to the smp class (e.g. decoder_channels, encoder_depth, img_size for ViTs)
  in_channels / num_classes   1 / 24

model.name = bench_timm  a timm backbone built from a local file (f8's build_backbone: timm or torchvision-ConvNeXt
  format, RGB-sum stem, intermediate layers pruned) with smp decoder modules:
  backbone, backbone_weights (path or null), backbone_weights_format (timm | torchvision_convnext), backbone_drop_path
  decoder  upernet | fpn | segformer : stride-4 decoders, the missing stride-2 skip is an empty (0-channel) map, as smp
                                        does for transformer-style tu- encoders
           unet | unetplusplus       : f8's HR stem (stride-2 conv stem on the input) supplies the stride-2 skip
           dpt                        : delegated to smp.DPT with encoder tu-<backbone> and the local file (timm format)
  decoder_kwargs, hr_stem_channels (64), in_channels, num_classes

Parameter naming: the backbone / encoder is always `encoder.*`, so training.encoder_pf applies PF to it only.
Inference (scripts/bench_infer.py) nulls encoder_weights / backbone_weights and drops encoder_weights_file: weights come
from the checkpoint.
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

SMP_ARCHS = {"unet": "Unet", "unetplusplus": "UnetPlusPlus", "fpn": "FPN", "deeplabv3": "DeepLabV3",
             "deeplabv3plus": "DeepLabV3Plus", "pspnet": "PSPNet", "linknet": "Linknet", "manet": "MAnet", "pan": "PAN",
             "upernet": "UPerNet", "segformer": "Segformer", "dpt": "DPT"}


def build_bench_smp(cfg: dict[str, Any]) -> nn.Module:
    import segmentation_models_pytorch as smp

    dec = str(cfg["decoder"]).lower()
    if dec not in SMP_ARCHS:
        raise ValueError(f"bench_smp: unknown decoder {cfg['decoder']!r} ({sorted(SMP_ARCHS)})")
    enc = cfg.get("encoder_name", "resnet34")
    w = cfg.get("encoder_weights")
    kw = dict(cfg.get("decoder_kwargs") or {})
    wf = cfg.get("encoder_weights_file")
    if wf:
        if not enc.startswith("tu-"):
            raise ValueError("bench_smp: encoder_weights_file is for tu-* (timm) encoders")
        kw["pretrained_cfg_overlay"] = dict(file=str(wf))
        w = w or "imagenet"   # any non-null tag: smp then asks timm for pretrained weights, read from the overlay file
    return getattr(smp, SMP_ARCHS[dec])(encoder_name=enc, encoder_weights=w, in_channels=cfg.get("in_channels", 1),
                                        classes=cfg.get("num_classes", 24), **kw)


class _Stride4Seg(nn.Module):
    """timm backbone (stride 4..32 features) + an smp stride-4 decoder (UPerNet / FPN / SegFormer) + smp head (x4)."""

    def __init__(self, backbone: nn.Module, chs: list[int], dec: str, in_channels: int, num_classes: int, kw: dict):
        super().__init__()
        from segmentation_models_pytorch.base import SegmentationHead
        from segmentation_models_pytorch.base import initialization as init

        self.encoder = backbone
        enc_ch = [in_channels, 0, *chs]
        if dec == "upernet":
            from segmentation_models_pytorch.decoders.upernet.decoder import UPerNetDecoder
            dch = int(kw.get("decoder_channels", 256))
            self.decoder = UPerNetDecoder(encoder_channels=enc_ch, encoder_depth=5, decoder_channels=dch,
                                          use_norm=kw.get("decoder_use_norm", "batchnorm"))
            out_ch = dch
        elif dec == "fpn":
            from segmentation_models_pytorch.decoders.fpn.decoder import FPNDecoder
            self.decoder = FPNDecoder(encoder_channels=enc_ch, encoder_depth=5,
                                      pyramid_channels=int(kw.get("decoder_pyramid_channels", 256)),
                                      segmentation_channels=int(kw.get("decoder_segmentation_channels", 128)),
                                      dropout=float(kw.get("decoder_dropout", 0.2)),
                                      merge_policy=kw.get("decoder_merge_policy", "add"))
            out_ch = self.decoder.out_channels
        elif dec == "segformer":
            from segmentation_models_pytorch.decoders.segformer.decoder import SegformerDecoder
            out_ch = int(kw.get("decoder_segmentation_channels", 256))
            self.decoder = SegformerDecoder(encoder_channels=enc_ch, encoder_depth=5, segmentation_channels=out_ch)
        else:
            raise ValueError(dec)
        self.segmentation_head = SegmentationHead(out_ch, num_classes, kernel_size=1, upsampling=4)
        init.initialize_decoder(self.decoder)
        init.initialize_head(self.segmentation_head)

    def _feats(self, x):
        return list(self.encoder.forward_intermediates(x, indices=(0, 1, 2, 3), intermediates_only=True))

    def forward(self, x):
        b, _, h, w = x.shape
        f = [x, x.new_empty(b, 0, h // 2, w // 2), *self._feats(x)]
        return self.segmentation_head(self.decoder(f))


class _HRStemUnet(nn.Module):
    """f8's HRStemUnetPlusPlus generalised to the smp Unet decoder as well (same stem, channels and init)."""

    def __init__(self, backbone: nn.Module, chs: list[int], dec: str, in_channels: int, num_classes: int,
                 hr_ch: int, kw: dict):
        super().__init__()
        from segmentation_models_pytorch.base import SegmentationHead
        from segmentation_models_pytorch.base import initialization as init

        from .hrstem_unetpp import DECODER_CHANNELS, HRStem

        dch = tuple(kw.get("decoder_channels", DECODER_CHANNELS))
        self.encoder = backbone
        self.hr_stem = HRStem(in_channels, hr_ch)
        enc_ch = [in_channels, hr_ch, *chs]
        if dec == "unetplusplus":
            from segmentation_models_pytorch.decoders.unetplusplus.decoder import UnetPlusPlusDecoder
            self.decoder = UnetPlusPlusDecoder(encoder_channels=enc_ch, decoder_channels=dch, n_blocks=5,
                                               use_norm="batchnorm", attention_type=None, interpolation_mode="nearest",
                                               center=False)
        else:
            from segmentation_models_pytorch.decoders.unet.decoder import UnetDecoder
            self.decoder = UnetDecoder(encoder_channels=enc_ch, decoder_channels=dch, n_blocks=5, use_norm="batchnorm",
                                       attention_type=None, add_center_block=False, interpolation_mode="nearest")
        self.segmentation_head = SegmentationHead(dch[-1], num_classes, kernel_size=3)
        init.initialize_decoder(self.decoder)
        init.initialize_head(self.segmentation_head)
        init.initialize_decoder(self.hr_stem)

    def _feats(self, x):
        return list(self.encoder.forward_intermediates(x, indices=(0, 1, 2, 3), intermediates_only=True))

    def forward(self, x):
        return self.segmentation_head(self.decoder([x, self.hr_stem(x), *self._feats(x)]))


def build_bench_timm(cfg: dict[str, Any]) -> nn.Module:
    dec = str(cfg["decoder"]).lower()
    in_ch, ncls = cfg.get("in_channels", 1), cfg.get("num_classes", 24)
    kw = dict(cfg.get("decoder_kwargs") or {})
    wts = cfg.get("backbone_weights")
    wts = None if wts in (None, "none", "") else wts
    if dec == "dpt":
        if cfg.get("backbone_weights_format", "timm") != "timm":
            raise ValueError("bench_timm dpt: timm-format weights only")
        sub = {"decoder": "dpt", "encoder_name": "tu-" + cfg["backbone"], "encoder_weights": None,
               "encoder_weights_file": wts, "in_channels": in_ch, "num_classes": ncls,
               "decoder_kwargs": {**kw, "drop_path_rate": float(cfg.get("backbone_drop_path", 0.0))}}
        return build_bench_smp(sub)
    from .hrstem_unetpp import build_backbone

    bb = build_backbone(cfg["backbone"], wts, cfg.get("backbone_weights_format", "timm"), in_ch,
                        float(cfg.get("backbone_drop_path", 0.0)))
    with torch.no_grad():
        chs = [t.shape[1] for t in bb.forward_intermediates(torch.zeros(1, in_ch, 64, 64), indices=(0, 1, 2, 3),
                                                            intermediates_only=True)]
    if dec in ("upernet", "fpn", "segformer"):
        return _Stride4Seg(bb, chs, dec, in_ch, ncls, kw)
    if dec in ("unet", "unetplusplus"):
        return _HRStemUnet(bb, chs, dec, in_ch, ncls, int(cfg.get("hr_stem_channels", 64)), kw)
    raise ValueError(f"bench_timm: unknown decoder {cfg['decoder']!r}")
