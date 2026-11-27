"""DeepLabV3+ wrapper using segmentation_models_pytorch.

Provides the same interface as SAUNetPlusPlus so the training loop
is agnostic to the backbone choice.

Two changes that leave the function unchanged:

* the ASPP image-pooling branch's ``AdaptiveAvgPool2d(1)`` is replaced by a
  spatial mean (same value; its CUDA backward is deterministic, the adaptive
  pool's is not);
* inputs whose height or width is not a multiple of the output stride (16) are
  replicate-padded on the bottom/right and the logits cropped back (UCF-EL
  evaluates whole images of varying size; smp rejects such shapes).

No auxiliary head (the UCF-EL reference uses torchvision's with an aux loss).
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import segmentation_models_pytorch as smp
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "segmentation_models_pytorch is required for DeepLabV3+. "
        "Install it with: pip install segmentation-models-pytorch"
    ) from exc


class GlobalAvgPool(nn.Module):
    """``AdaptiveAvgPool2d(1)`` as a spatial mean."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x.mean(dim=(2, 3), keepdim=True)


class DeepLabV3PlusWrapper(nn.Module):
    """Thin wrapper around smp.DeepLabV3Plus.

    Args:
        in_channels:      Number of input channels.
        num_classes:      Number of segmentation output classes.
        encoder_name:     Encoder backbone name (e.g. 'resnet50').
        encoder_weights:  Pre-trained weights ('imagenet' or None).
    """

    STRIDE = 16

    def __init__(
        self,
        in_channels: int = 1,
        num_classes: int = 24,
        encoder_name: str = "resnet50",
        encoder_weights: str | None = "imagenet",
    ) -> None:
        super().__init__()
        self.model = smp.DeepLabV3Plus(
            encoder_name=encoder_name,
            encoder_weights=encoder_weights,
            in_channels=in_channels,
            classes=num_classes,
            activation=None,  # raw logits
        )
        for name, mod in list(self.model.named_modules()):
            if isinstance(mod, nn.AdaptiveAvgPool2d) and mod.output_size in (1, (1, 1)):
                parent = self.model.get_submodule(name.rsplit(".", 1)[0])
                setattr(parent, name.rsplit(".", 1)[1], GlobalAvgPool())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning logits (B, num_classes, H, W)."""
        h, w = x.shape[-2:]
        ph, pw = (-h) % self.STRIDE, (-w) % self.STRIDE
        if ph or pw:
            x = F.pad(x, (0, pw, 0, ph), mode="replicate")
        out = self.model(x)
        return out[..., :h, :w] if (ph or pw) else out
