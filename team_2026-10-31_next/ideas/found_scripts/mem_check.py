import torch, segmentation_models_pytorch as smp
torch.set_num_threads(8)
m = smp.UnetPlusPlus(encoder_name="resnet34", encoder_weights=None, in_channels=1, classes=24)
m.train()
# decoder block output shapes
shapes = {}
for n, mod in m.decoder.blocks.items():
    mod.register_forward_hook(lambda mod, i, o, n=n: shapes.__setitem__(n, (tuple(o.shape), [tuple(t.shape) for t in i if torch.is_tensor(t)])))
def saved_bytes(sz):
    tot = [0]
    def pack(t):
        tot[0] += t.numel() * t.element_size(); return t
    with torch.autograd.graph.saved_tensors_hooks(pack, lambda t: t):
        y = m(torch.randn(1, 1, sz, sz))
    return tot[0], y
b512, y = saved_bytes(512)
print("decoder blocks (out shape at 512):")
for k in sorted(shapes): print("  ", k, shapes[k][0])
shapes.clear()
b1024, _ = saved_bytes(1024)
print(f"saved-for-backward bytes, batch 1, fp32: 512px {b512/2**20:.0f} MiB, 1024px {b1024/2**20:.0f} MiB, ratio {b1024/b512:.2f}")
p = sum(t.numel() for t in m.parameters())
print(f"params {p/1e6:.2f}M -> weights+grads+Adam(2) fp32 = {p*16/2**20:.0f} MiB")
