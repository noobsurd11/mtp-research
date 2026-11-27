"""Self-attention module used in SA U-Net++ decoder nodes.

Architecture (per the SA U-Net++ specification):
  1. Input  → Q via Conv1x1
  2. Input  → K via Conv1x1
  3. attn   = sigmoid(Q + K)          (element-wise ADD, NOT matmul)
  4. Input  → V via Conv1x1
  5. gated  = attn * V
  6. output = Conv1x1(gated)
"""

import torch
import torch.nn as nn


class SelfAttention(nn.Module):
    """Spatial self-attention gate for feature re-calibration.

    Unlike standard dot-product attention, this module combines Q and K
    via element-wise addition followed by a sigmoid gate. This keeps the
    receptive field local (1×1 convolutions) while still allowing the
    network to learn which spatial features to amplify.

    Args:
        in_channels: Number of input (and output) feature channels.
    """

    def __init__(self, in_channels: int) -> None:
        super().__init__()
        self.q_conv = nn.Conv2d(in_channels, in_channels, kernel_size=1, bias=False)
        self.k_conv = nn.Conv2d(in_channels, in_channels, kernel_size=1, bias=False)
        self.v_conv = nn.Conv2d(in_channels, in_channels, kernel_size=1, bias=False)
        self.out_conv = nn.Conv2d(in_channels, in_channels, kernel_size=1, bias=False)

        self._init_weights()

    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply self-attention gate.

        Args:
            x: Feature map of shape (B, C, H, W).

        Returns:
            Attended feature map of the same shape (B, C, H, W).
        """
        q = self.q_conv(x)                   # (B, C, H, W)
        k = self.k_conv(x)                   # (B, C, H, W)
        attn = torch.sigmoid(q + k)          # element-wise add → sigmoid gate

        v = self.v_conv(x)                   # (B, C, H, W)
        gated = attn * v                     # channel-spatial gating

        return self.out_conv(gated)          # (B, C, H, W)
