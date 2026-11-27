"""Factory function to build a model from a config dict."""

from __future__ import annotations

from typing import Any

import torch.nn as nn

from .sa_unetpp import SAUNetPlusPlus
from .deeplabv3plus import DeepLabV3PlusWrapper


class UpsampledInput(nn.Module):
    """Track M R5 (opt-in ``model.upsample_input: f``): run the network at f x the input resolution (bilinear input
    upsampling) and average-pool the logits back by f, so labels, losses and scoring stay at the native 512 px.
    Thin (1-2 px) structures then occupy f x more pixels inside the network. Off (f = 1) returns the plain model."""

    def __init__(self, net: nn.Module, factor: int) -> None:
        super().__init__()
        self.net, self.factor = net, int(factor)

    def forward(self, x):
        import torch.nn.functional as F
        y = self.net(F.interpolate(x, scale_factor=self.factor, mode="bilinear", align_corners=False))
        return F.avg_pool2d(y, self.factor)


def build_model(cfg: dict[str, Any]) -> nn.Module:
    """Build ``_build_core(cfg)``; wrap it in ``UpsampledInput`` when ``model.upsample_input`` > 1 (Track M R5)."""
    net = _build_core(cfg)
    f = int(cfg.get("upsample_input", 1))
    return UpsampledInput(net, f) if f > 1 else net


def _build_core(cfg: dict[str, Any]) -> nn.Module:
    """Instantiate a segmentation model from a model config dict.

    Args:
        cfg: Model configuration section (typically ``config['model']``).
             Required key: ``name``: ``'unetpp'`` (U-Net++; ``sa_gating: true``
             adds the SA gate of tag v0-sa-failed to every decoder node),
             ``'sa_unetpp'`` (legacy alias of ``unetpp`` + ``sa_gating: true``)
             or ``'deeplabv3plus'``.

    Returns:
        Instantiated PyTorch model (weights on CPU; move with ``.to(device)``).

    Raises:
        ValueError: If ``cfg['name']`` is not a recognised model name.
    """
    name = cfg["name"].lower()

    if name in ("unetpp", "sa_unetpp"):
        sa_gating = bool(cfg.get("sa_gating", name == "sa_unetpp"))
        if name == "sa_unetpp" and not sa_gating:
            raise ValueError("model.name=sa_unetpp with sa_gating=false is contradictory")
        return SAUNetPlusPlus(
            in_channels=cfg.get("in_channels", 1),
            num_classes=cfg.get("num_classes", 24),
            start_filters=cfg.get("start_filters", 32),
            dropout_rate=cfg.get("dropout_rate", 0.2),
            input_size=cfg.get("input_size", 512),
            self_attention=sa_gating,
            grad_checkpoint=cfg.get("grad_checkpoint", False),
        )

    if name == "smp_unet":
        import segmentation_models_pytorch as smp

        return smp.Unet(
            encoder_name=cfg.get("encoder_name", "vgg16"),
            encoder_weights=cfg.get("encoder_weights", "imagenet"),
            in_channels=cfg.get("in_channels", 1),
            classes=cfg.get("num_classes", 24),
        )

    if name == "smp_unetpp":
        # U-Net++ with a pretrained encoder (P6, arm L2): same decoder topology as ``unetpp``, ImageNet resnet34 by
        # default. smp adapts the first conv to ``in_channels=1`` by summing the RGB filters.
        import segmentation_models_pytorch as smp

        return smp.UnetPlusPlus(
            encoder_name=cfg.get("encoder_name", "resnet34"),
            encoder_weights=cfg.get("encoder_weights", "imagenet"),
            in_channels=cfg.get("in_channels", 1),
            classes=cfg.get("num_classes", 24),
        )

    if name == "hrstem_unetpp":
        # F8 (idea 8, opt-in): U-Net++ on a timm hierarchical backbone (ConvNeXt / SAM2 Hiera) plus a stride-2 stem.
        from .hrstem_unetpp import build_hrstem_unetpp

        return build_hrstem_unetpp(cfg)

    if name == "deeplabv3plus":
        return DeepLabV3PlusWrapper(
            in_channels=cfg.get("in_channels", 1),
            num_classes=cfg.get("num_classes", 24),
            encoder_name=cfg.get("encoder_name", "resnet50"),
            encoder_weights=cfg.get("encoder_weights", "imagenet"),
        )

    raise ValueError(
        f"Unknown model name '{cfg['name']}'. "
        "Choose from: 'unetpp', 'sa_unetpp', 'smp_unet', 'smp_unetpp', 'hrstem_unetpp', 'deeplabv3plus'."
    )
