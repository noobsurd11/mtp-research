"""U-Net++ with optional Self-Attention decoder nodes (SA U-Net++).

``self_attention=False`` gives a plain U-Net++ (every SA gate is an identity).

Architecture summary
--------------------
* 4 encoder levels + bottleneck.  Filter progression: 32-64-128-256-512.
* Encoder block: Conv2d(3×3, BN, ReLU).  Dropout(0.2) applied after the
  pooled output at encoder levels 2 and 3 (0-indexed, i.e. the 3rd/4th).
* Bottleneck: same Conv block, no pooling.
* U-Net++ nested decoder with combinational blocks (concat + Conv3×3).
* Each decoder node: CombBlock → Dropout → SelfAttention (or identity).
* Upsampling between levels: bilinear 2×.
* Output: 1×1 Conv → num_classes logits at original resolution.
"""

from __future__ import annotations

import contextlib

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint

from .self_attention import SelfAttention


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

class ConvBnRelu(nn.Module):
    """Conv2d(3×3) + BatchNorm + ReLU."""

    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class CombinationalBlock(nn.Module):
    """Combinational block: concatenated inputs → Conv3×3 → BN → ReLU.

    This is the U-Net++ "H" function applied inside each decoder node.
    """

    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.conv = ConvBnRelu(in_ch, out_ch)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class DecoderNode(nn.Module):
    """Single U-Net++ decoder node with self-attention.

    Pipeline: CombinationalBlock → Dropout → SelfAttention.
    Inputs must be pre-concatenated by the caller (SAUNetPlusPlus.forward).

    Args:
        in_ch:        Total channels of concatenated inputs.
        out_ch:       Output channels (= filter size at this encoder level).
        dropout_rate: Spatial dropout probability.
    """

    def __init__(
        self, in_ch: int, out_ch: int, dropout_rate: float = 0.2, self_attention: bool = True
    ) -> None:
        super().__init__()
        self.comb = CombinationalBlock(in_ch, out_ch)
        self.drop = nn.Dropout2d(dropout_rate)
        self.attn = SelfAttention(out_ch) if self_attention else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.comb(x)
        x = self.drop(x)
        x = self.attn(x)
        return x


@contextlib.contextmanager
def _frozen_bn_stats(module: nn.Module):
    """Run BatchNorm with batch statistics but leave running stats untouched.

    Used for the recomputation pass of gradient checkpointing, so running
    statistics are updated exactly once per real forward pass.
    """
    bns = [m for m in module.modules() if isinstance(m, nn.modules.batchnorm._BatchNorm)]
    saved = [(m.momentum, m.num_batches_tracked.clone()) for m in bns]
    for m in bns:
        m.momentum = 0.0
    try:
        yield
    finally:
        for m, (mom, nbt) in zip(bns, saved):
            m.momentum = mom
            m.num_batches_tracked.copy_(nbt)


# ---------------------------------------------------------------------------
# SA U-Net++
# ---------------------------------------------------------------------------

class SAUNetPlusPlus(nn.Module):
    """Self-Attention U-Net++ for semantic segmentation.

    Levels 0–3 are encoder levels; level 4 is the bottleneck.
    U-Net++ decoder nodes X[i][j] (i=level, j=depth≥1) are constructed
    for all valid (i,j) pairs such that i + j ≤ 4.

    Args:
        in_channels:   Number of input image channels (1 for grayscale EL).
        num_classes:   Number of segmentation classes.
        start_filters: Filter count at the first encoder level (default 32).
        dropout_rate:  Dropout probability used in encoder levels 2-3 and
                       all decoder nodes.
        input_size:    Expected spatial dimension (used only for documentation
                       and optional assertions; not enforced at runtime).
        self_attention: If False, decoder nodes have no SA gate (plain U-Net++).
        grad_checkpoint: Gradient-checkpoint every decoder node while training.
    """

    NUM_LEVELS: int = 5  # levels 0-3 (encoder) + 4 (bottleneck)

    def __init__(
        self,
        in_channels: int = 1,
        num_classes: int = 24,
        start_filters: int = 32,
        dropout_rate: float = 0.2,
        input_size: int = 512,
        self_attention: bool = True,
        grad_checkpoint: bool = False,
    ) -> None:
        super().__init__()

        self.num_classes = num_classes
        self.self_attention = self_attention
        # Recompute decoder nodes in backward instead of storing their
        # activations (same values and gradients, less memory, more compute).
        self.grad_checkpoint = grad_checkpoint
        self.input_size = input_size

        # Filter counts: [32, 64, 128, 256, 512]
        F = [start_filters * (2 ** i) for i in range(self.NUM_LEVELS)]
        self._filters = F

        # ---- Encoder ----
        self.enc0 = ConvBnRelu(in_channels, F[0])   # 512→512
        self.enc1 = ConvBnRelu(F[0], F[1])           # 256→256
        self.enc2 = ConvBnRelu(F[1], F[2])           # 128→128, dropout after pool
        self.enc3 = ConvBnRelu(F[2], F[3])           # 64→64,   dropout after pool
        self.bottleneck = ConvBnRelu(F[3], F[4])     # 32→32

        self.pool = nn.MaxPool2d(2, 2)
        # Dropout applied to the *pooled* feature (i.e., the downsampled map
        # that feeds the next encoder level) at levels 2 and 3.
        self.drop2 = nn.Dropout2d(dropout_rate)
        self.drop3 = nn.Dropout2d(dropout_rate)

        # ---- U-Net++ decoder nodes ----
        # X[i][j] exists for j in 1..4 and i in 0..(4-j)
        # Input channels = F[i] * j  (prev nodes at level i)
        #                + F[i+1]    (upsampled from level i+1)
        self.decoder: nn.ModuleDict = nn.ModuleDict()
        for j in range(1, self.NUM_LEVELS):
            for i in range(self.NUM_LEVELS - j):
                in_ch = F[i] * j + F[i + 1]
                self.decoder[f"{i}_{j}"] = DecoderNode(in_ch, F[i], dropout_rate, self_attention)

        # ---- Output head ----
        self.output_conv = nn.Conv2d(F[0], num_classes, kernel_size=1)

        self._init_weights()

    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    @staticmethod
    def _upsample(x: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Bilinear upsample x to match target's spatial size."""
        return F.interpolate(
            x, size=target.shape[2:], mode="bilinear", align_corners=False
        )

    # Decoder nodes returned as "features" by forward_dual.
    FEATURE_NODES = {
        "deep": (3, 1),         # first decoder node, 1/8 resolution (closest to the ALHVR reference feature)
        "penultimate": (0, 4),  # last decoder node before the 1x1 head (the ALHVR paper's description)
    }

    def encode(self, x: torch.Tensor) -> list[torch.Tensor]:
        """Encoder features [e0, e1, e2, e3, bottleneck]."""
        e0 = self.enc0(x)                             # (B, 32, H,    W   )
        e1 = self.enc1(self.pool(e0))                 # (B, 64, H/2,  W/2 )
        e2 = self.enc2(self.drop2(self.pool(e1)))     # (B,128, H/4,  W/4 )
        e3 = self.enc3(self.drop3(self.pool(e2)))     # (B,256, H/8,  W/8 )
        b = self.bottleneck(self.pool(e3))            # (B,512, H/16, W/16)
        return [e0, e1, e2, e3, b]

    def decode(self, feats: list[torch.Tensor]) -> tuple[torch.Tensor, dict]:
        """U-Net++ decoder.  Returns (logits, nodes) with nodes[(level, depth)]."""
        nodes: dict[tuple[int, int], torch.Tensor] = {(i, 0): f for i, f in enumerate(feats)}
        # Iterate depth-first: j=1 fills all width nodes before j=2, etc.
        for j in range(1, self.NUM_LEVELS):
            for i in range(self.NUM_LEVELS - j):
                # Same-level previous nodes X[i][0..j-1] + upsampled X[i+1][j-1]
                inputs = [nodes[(i, k)] for k in range(j)] + [nodes[(i + 1, j - 1)]]
                node = self.decoder[f"{i}_{j}"]
                if self.grad_checkpoint and self.training and torch.is_grad_enabled():
                    nodes[(i, j)] = checkpoint(
                        self._node_forward, node, *inputs, use_reentrant=False,
                        context_fn=lambda node=node: (contextlib.nullcontext(), _frozen_bn_stats(node)),
                    )
                else:
                    nodes[(i, j)] = self._node_forward(node, *inputs)
        return self.output_conv(nodes[(0, 4)]), nodes

    def _node_forward(self, node: nn.Module, *inputs: torch.Tensor) -> torch.Tensor:
        """Decoder node X[i][j]: concat(X[i][0..j-1], up(X[i+1][j-1])) -> node."""
        *same_level, lower = inputs
        lower_up = self._upsample(lower, same_level[0])
        return node(torch.cat(same_level + [lower_up], dim=1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Input tensor (B, in_channels, H, W).

        Returns:
            Logit tensor (B, num_classes, H, W) at the same spatial resolution
            as the input.
        """
        return self.decode(self.encode(x))[0]

    def forward_dual(
        self, x: torch.Tensor, feature_layer: str = "deep"
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Main and perturbed pass sharing one encoder pass and the same decoder.

        The perturbed pass runs the same decoder on encoder features perturbed
        by feature dropout or feature noise (``perturbations.perturb_features``),
        as in the ALHVR reference ``UNet_fea_aux``.

        Returns:
            (main_logits, perturbed_logits, main_features, perturbed_features),
            features taken from decoder node ``FEATURE_NODES[feature_layer]``.
        """
        from .perturbations import perturb_features

        node = self.FEATURE_NODES[feature_layer]
        feats = self.encode(x)
        logits, nodes = self.decode(feats)
        logits_aux, nodes_aux = self.decode(perturb_features(feats)[0])
        return logits, logits_aux, nodes[node], nodes_aux[node]
