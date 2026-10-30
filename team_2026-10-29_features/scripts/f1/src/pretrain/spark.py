"""F1 / MIM5 (opt-in, used only by scripts/pretrain_mim.py): SparK-style masked image modelling for the smp ResNet
encoder of ``smp_unetpp`` (Tian et al., SparK, arXiv:2301.03580).

Sparse convolution is emulated densely, as in SparK's reference code:
- the current patch mask (True = visible) lives in a module-level context (``active_mask``);
- every encoder ``Conv2d`` and ``MaxPool2d`` output is multiplied by the mask at its resolution;
- every encoder ``BatchNorm2d`` computes its batch statistics over visible positions only and re-masks its output.
So masked input pixels can not reach any encoder output (tested). The modules only change class (``sparsify_`` /
``densify_``), so parameters, buffers and state-dict keys stay those of the smp encoder and load into
``smp.UnetPlusPlus(...).encoder`` with ``strict=True``.

The mask grid may be finer than the encoder's stride-32 map (``patch`` < 32): coarser maps then take the max over
the cells they cover (a position is visible if any of its cells is); this still never reads masked content, because
masked cells are zero at the finer level.
"""
from __future__ import annotations

import contextlib
import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class _Ctx:
    mask: torch.Tensor | None = None  # (B, 1, gh, gw) float {0, 1}, 1 = visible
    cache: dict = {}


_CTX = _Ctx()


@contextlib.contextmanager
def active_mask(mask: torch.Tensor):
    """Make ``mask`` (B, 1, gh, gw) bool or {0,1}, True/1 = visible, the current mask for sparse modules."""
    prev = (_CTX.mask, _CTX.cache)
    _CTX.mask, _CTX.cache = mask.float(), {}
    try:
        yield
    finally:
        _CTX.mask, _CTX.cache = prev


def mask_at(h: int, w: int) -> torch.Tensor | None:
    """The current mask at resolution (h, w): nearest upsampling for finer maps, max-pooling for coarser ones."""
    m = _CTX.mask
    if m is None:
        return None
    key = (h, w)
    if key not in _CTX.cache:
        gh, gw = m.shape[-2:]
        if h >= gh:
            if h % gh or w % gw or h // gh != w // gw:
                raise ValueError(f"feature map {h}x{w} is not an integer multiple of the mask grid {gh}x{gw}")
            f = h // gh
            out = m.repeat_interleave(f, 2).repeat_interleave(f, 3) if f > 1 else m
        else:
            if gh % h or gw % w or gh // h != gw // w:
                raise ValueError(f"feature map {h}x{w} does not divide the mask grid {gh}x{gw}")
            out = F.max_pool2d(m, gh // h)
        _CTX.cache[key] = out
    return _CTX.cache[key]


class SparseConv2d(nn.Conv2d):
    def forward(self, x):  # noqa: D102
        y = super().forward(x)
        m = mask_at(*y.shape[-2:])
        return y if m is None else y * m.to(y.dtype)


class SparseMaxPool2d(nn.MaxPool2d):
    def forward(self, x):  # noqa: D102
        y = super().forward(x)
        m = mask_at(*y.shape[-2:])
        return y if m is None else y * m.to(y.dtype)


class SparseBatchNorm2d(nn.BatchNorm2d):
    """BatchNorm over visible positions only (SparK's SparseBatchNorm2d), output re-masked. Without a mask it is the
    plain ``BatchNorm2d``. Statistics in float32; the running variance uses the unbiased estimate as PyTorch does."""

    def forward(self, x):  # noqa: D102
        m = mask_at(*x.shape[-2:])
        if m is None:
            return super().forward(x)
        if not self.training:
            return super().forward(x) * m.to(x.dtype)
        xf, mf = x.float(), m.float()
        n = mf.sum() * 1.0  # visible positions per channel (B * visible h*w)
        if n < 2:
            raise ValueError("SparseBatchNorm2d needs at least 2 visible positions")
        mean = (xf * mf).sum((0, 2, 3)) / n
        var = (((xf - mean[None, :, None, None]) ** 2) * mf).sum((0, 2, 3)) / n
        if self.track_running_stats:
            with torch.no_grad():
                self.num_batches_tracked.add_(1)
                mom = self.momentum if self.momentum is not None else 1.0 / float(self.num_batches_tracked)
                self.running_mean.mul_(1 - mom).add_(mean.detach(), alpha=mom)
                self.running_var.mul_(1 - mom).add_(var.detach() * (n / (n - 1)), alpha=mom)
        y = (xf - mean[None, :, None, None]) * torch.rsqrt(var[None, :, None, None] + self.eps)
        if self.affine:
            y = y * self.weight[None, :, None, None].float() + self.bias[None, :, None, None].float()
        return (y * mf).to(x.dtype)


_TO_SPARSE = {nn.Conv2d: SparseConv2d, nn.BatchNorm2d: SparseBatchNorm2d, nn.MaxPool2d: SparseMaxPool2d}
_TO_DENSE = {v: k for k, v in _TO_SPARSE.items()}


def sparsify_(module: nn.Module) -> int:
    """In place: switch every Conv2d / BatchNorm2d / MaxPool2d (exact class) to its sparse class. Returns the count."""
    n = 0
    for mod in module.modules():
        if type(mod) in _TO_SPARSE:
            mod.__class__ = _TO_SPARSE[type(mod)]
            n += 1
    return n


def densify_(module: nn.Module) -> int:
    """In place: undo ``sparsify_``. Returns the count."""
    n = 0
    for mod in module.modules():
        if type(mod) in _TO_DENSE:
            mod.__class__ = _TO_DENSE[type(mod)]
            n += 1
    return n


class UNetBlock(nn.Module):
    """SparK decoder block: 2x transposed-conv upsampling, then conv-BN-ReLU6, conv-BN."""

    def __init__(self, cin: int, cout: int) -> None:
        super().__init__()
        self.up_sample = nn.ConvTranspose2d(cin, cin, kernel_size=4, stride=2, padding=1, bias=True)
        self.conv = nn.Sequential(
            nn.Conv2d(cin, cin, 3, 1, 1, bias=False), nn.BatchNorm2d(cin), nn.ReLU6(inplace=True),
            nn.Conv2d(cin, cout, 3, 1, 1, bias=False), nn.BatchNorm2d(cout),
        )

    def forward(self, x):  # noqa: D102
        return self.conv(self.up_sample(x))


class LightDecoder(nn.Module):
    """SparK LightDecoder: log2(32) = 5 upsampling blocks, widths width / 2^i, 1x1 projection to ``out_ch``."""

    def __init__(self, width: int = 512, up_sample_ratio: int = 32, out_ch: int = 1) -> None:
        super().__init__()
        n = round(math.log2(up_sample_ratio))
        ch = [width // 2 ** i for i in range(n + 1)]
        self.dec = nn.ModuleList([UNetBlock(a, b) for a, b in zip(ch[:-1], ch[1:])])
        self.proj = nn.Conv2d(ch[-1], out_ch, 1, 1, bias=True)
        for m in self.modules():  # SparK's decoder init
            if isinstance(m, nn.Conv2d):
                nn.init.trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.ConvTranspose2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight); nn.init.zeros_(m.bias)

    def forward(self, to_dec: list[torch.Tensor]):  # noqa: D102
        x = 0
        for i, d in enumerate(self.dec):
            if i < len(to_dec) and to_dec[i] is not None:
                x = x + to_dec[i]
            x = d(x)
        return self.proj(x)


class SparKResNet(nn.Module):
    """Masked image model around an smp ResNet encoder (sparsified in place).

    Encoder features at strides 4, 8, 16, 32 (smp ``features[2:]``) are densified deepest first: sparse BN, masked
    positions filled with a learnable mask token per scale, a projection to the decoder width at that scale (1x1 for
    the deepest, 3x3 otherwise), then the LightDecoder reconstructs the full-resolution image. Loss: MSE on masked
    patches only, against per-patch normalised targets (SparK default).
    """

    def __init__(self, encoder: nn.Module, enc_channels: list[int], width: int = 512, patch: int = 32,
                 mask_ratio: float = 0.6, in_ch: int = 1) -> None:
        super().__init__()
        self.encoder = encoder
        self.n_sparse = sparsify_(self.encoder)
        self.patch, self.mask_ratio, self.in_ch = int(patch), float(mask_ratio), in_ch
        chs = list(enc_channels)[::-1]  # deepest first, e.g. [512, 256, 128, 64]
        self.mask_tokens = nn.ParameterList()
        self.densify_norms = nn.ModuleList()
        self.densify_projs = nn.ModuleList()
        d = width
        for i, e in enumerate(chs):
            tok = nn.Parameter(torch.zeros(1, e, 1, 1))
            nn.init.trunc_normal_(tok, mean=0, std=0.02, a=-0.02, b=0.02)
            self.mask_tokens.append(tok)
            self.densify_norms.append(SparseBatchNorm2d(e))
            k = 1 if i == 0 else 3
            proj = nn.Identity() if (i == 0 and e == d) else nn.Conv2d(e, d, k, 1, k // 2, bias=True)
            if isinstance(proj, nn.Conv2d):
                nn.init.trunc_normal_(proj.weight, std=0.02); nn.init.zeros_(proj.bias)
            self.densify_projs.append(proj)
            d //= 2
        self.decoder = LightDecoder(width=width, up_sample_ratio=32, out_ch=in_ch)

    def random_mask(self, b: int, h: int, w: int, generator: torch.Generator | None = None,
                    device=None) -> torch.Tensor:
        """(b, 1, h/patch, w/patch) bool, True = visible; exactly round(L * (1 - ratio)) visible patches each."""
        gh, gw = h // self.patch, w // self.patch
        L = gh * gw
        keep = round(L * (1 - self.mask_ratio))
        idx = torch.rand(b, L, generator=generator).argsort(dim=1)[:, :keep]
        m = torch.zeros(b, L, dtype=torch.bool).scatter_(1, idx, True).view(b, 1, gh, gw)
        return m.to(device) if device is not None else m

    def forward(self, x: torch.Tensor, mask: torch.Tensor):
        """x (B, C, H, W) normalised image, mask (B, 1, H/p, W/p) bool visible. Returns (loss, reconstruction)."""
        with active_mask(mask):
            feats = self.encoder(x * mask_at(*x.shape[-2:]).to(x.dtype))
            feats = feats[2:][::-1]  # strides 32, 16, 8, 4
            to_dec = []
            for i, f in enumerate(feats):
                f = self.densify_norms[i](f)
                vis = mask_at(*f.shape[-2:]).bool()
                f = torch.where(vis.expand_as(f), f, self.mask_tokens[i].to(f.dtype).expand_as(f))
                to_dec.append(self.densify_projs[i](f))
        rec = self.decoder(to_dec)
        return self.loss(x, rec, mask), rec

    def loss(self, x: torch.Tensor, rec: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Mean over masked patches of the per-patch MSE against the per-patch normalised target."""
        p = self.patch
        inp, out = patchify(x.float(), p), patchify(rec.float(), p)  # (B, L, C*p*p)
        mean = inp.mean(dim=-1, keepdim=True)
        std = (inp.var(dim=-1, keepdim=True) + 1e-6) ** 0.5
        tgt = (inp - mean) / std
        l2 = ((out - tgt) ** 2).mean(dim=2)  # (B, L)
        masked = (~mask.bool()).flatten(1).float()  # (B, L)
        return (l2 * masked).sum() / (masked.sum() + 1e-8)

    def unpatch_target(self, x: torch.Tensor, rec: torch.Tensor) -> torch.Tensor:
        """Reconstruction mapped back to image scale with the target's per-patch mean / std (for pictures)."""
        p = self.patch
        inp, out = patchify(x.float(), p), patchify(rec.float(), p)
        mean = inp.mean(dim=-1, keepdim=True)
        std = (inp.var(dim=-1, keepdim=True) + 1e-6) ** 0.5
        return unpatchify(out * std + mean, p, x.shape[1], x.shape[-2], x.shape[-1])

    def encoder_state_dict(self) -> dict[str, torch.Tensor]:
        """Encoder weights under ``encoder.<key>``; keys equal smp's (class swaps do not touch them)."""
        return {f"encoder.{k}": v.detach().cpu().clone() for k, v in self.encoder.state_dict().items()}


def patchify(x: torch.Tensor, p: int) -> torch.Tensor:
    b, c, h, w = x.shape
    x = x.reshape(b, c, h // p, p, w // p, p).permute(0, 2, 4, 1, 3, 5)
    return x.reshape(b, (h // p) * (w // p), c * p * p)


def unpatchify(x: torch.Tensor, p: int, c: int, h: int, w: int) -> torch.Tensor:
    b = x.shape[0]
    x = x.reshape(b, h // p, w // p, c, p, p).permute(0, 3, 1, 4, 2, 5)
    return x.reshape(b, c, h, w)
