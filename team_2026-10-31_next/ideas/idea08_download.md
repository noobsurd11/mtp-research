# Idea 8 / idea 10: weight downloads (found, 31 Oct 2026)

**User approval:** team-lead relayed it (log.md): the DINOv3 ConvNeXt-T, DINOv3 ViT-S/16 and SAM2 Hiera-T weights (~290 MB) for idea 8, and the SAM2.1 Hiera-T checkpoint (~156 MB) for idea 10.
- DINOv3 is under Meta's gated licence, which the user accepts themselves.
- No token is ever shared with the team.

**Facts:** checked with the Hugging Face API (`https://huggingface.co/api/models/<id>?blobs=true`, metadata only, nothing downloaded), 31 Oct.

## 1. Model ids, sizes, gating

| Use | HF repo @ revision | File | Bytes | sha256 (LFS oid) | Gated | Licence |
|---|---|---|---|---|---|---|
| idea 8 A8 (timm, what our code loads) | `timm/convnext_tiny.dinov3_lvd1689m` @ `39c7bb32f83c11bbb13cb23058f8852a4dac88ed` | `model.safetensors` | 111,298,008 | a7637753…f36847f | **no** (HF `gated: false`) | `other` (DINOv3 License) |
| idea 8 probe (timm) | `timm/vit_small_patch16_dinov3.lvd1689m` @ `3bf4720a82ec2066db88137180ff1f83a675cef0` | `model.safetensors` | 86,362,376 | 2a1ec16a…906b040 | **no** | `other` (DINOv3 License) |
| idea 8 probe (timm) | `timm/sam2_hiera_tiny.fb_r896` @ `92aa8e856f52f9224008a266757a30a91dc1894a` | `model.safetensors` | 107,418,216 | 3298636a…e2d69 | no | apache-2.0 |
| idea 10 S10 (full SAM2.1 with prompt decoder) | `facebook/sam2.1-hiera-tiny` @ `de431c4043854a71d8101e17995dfe596bf101a5` | `sam2.1_hiera_tiny.pt` | 156,008,466 | 7402e0d8…34be69 | no | apache-2.0 |
| (Meta originals, not needed) | `facebook/dinov3-convnext-tiny-pretrain-lvd1689m` @ `10d30274…` | `model.safetensors` | 111,299,216 | bd30a945…39cb2 | **yes, `manual`** (login + accepted licence) | `other` |
| (Meta originals, not needed) | `facebook/dinov3-vits16-pretrain-lvd1689m` @ `114c1379…` | `model.safetensors` | 86,406,384 | 4610ad75…c91d | **yes, `manual`** | `other` |

Full sha256 values are in the API output and are verified at download (§3).

**The DINOv3 point the user must decide (S):**
- timm's mirrors of the DINOv3 weights are not gated on HF: no login is needed. Their licence is the same DINOv3 License as Meta's gated originals.
- Fetching from the ungated mirror would skip the place where the licence is normally accepted.
- So I have **not** fetched them. Two equivalent routes, the user's choice:
  - **(A) Preferred: the user downloads Meta's gated originals with their own HF login** (§2A), on their laptop or on gaint under their own session. Then copies them to gaint `/home/noob/work/weights/`. Our code loads the file through timm's `pretrained_cfg_overlay=dict(file=...)`, with a key remap if needed (builder checks; the timm and Meta files differ by ~1 KB, key naming).
  - **(B) The user writes "I accept the DINOv3 License; fetch the timm mirrors".** Then I fetch the two timm DINOv3 files (197.7 MB total) with the §2B commands. No login, no token.

**SAM2 (Apache-2.0, ungated):** fetched by me within the approval and the 0.5 GB cap (§3).

## 2. Exact commands
**2A. DINOv3 originals (user, with their own HF token; the token stays with the user).**
```bash
# on the user's machine (or gaint, in the user's own session); requires: huggingface.co login + "Agree" on both model pages
mkdir -p ~/dinov3_dl && cd ~/dinov3_dl
huggingface-cli login            # user's own token, never shared
huggingface-cli download facebook/dinov3-convnext-tiny-pretrain-lvd1689m model.safetensors --revision 10d30274b4d445111e2d5bf75ac93bbd94db274b --local-dir cnx_t
huggingface-cli download facebook/dinov3-vits16-pretrain-lvd1689m model.safetensors --revision 114c1379950215c8b35dfcd4e90a5c251dde0d32 --local-dir vit_s16
sha256sum cnx_t/model.safetensors vit_s16/model.safetensors
# expect bd30a9459d6149564ef53af6e8a1999980953b009b94cde836ac1bac4d339cb2 and 4610ad75edef83e75afdebf162d148dc628045ea6cbb83d67d4708c709c4f91d
scp cnx_t/model.safetensors noob@172.18.22.20:/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_meta.safetensors
scp vit_s16/model.safetensors noob@172.18.22.20:/home/noob/work/weights/dinov3_vits16_lvd1689m_meta.safetensors
```

**2B. DINOv3 timm mirrors (only after the user's explicit licence line; run by found on gaint).**
```bash
cd /home/noob/work/weights
curl -L -f -o dinov3_convnext_tiny_lvd1689m_timm.safetensors https://huggingface.co/timm/convnext_tiny.dinov3_lvd1689m/resolve/39c7bb32f83c11bbb13cb23058f8852a4dac88ed/model.safetensors
curl -L -f -o dinov3_vits16_lvd1689m_timm.safetensors https://huggingface.co/timm/vit_small_patch16_dinov3.lvd1689m/resolve/3bf4720a82ec2066db88137180ff1f83a675cef0/model.safetensors
sha256sum dinov3_*_timm.safetensors   # expect a7637753a2e85d709d1a5474e13382d39e7bc581a35868b477585c970f36847f / 2a1ec16ae28ffa07bc0ead0241ee7df9fc26451fe6f9f839b7b3afa0a906b040
md5sum dinov3_*_timm.safetensors >> MD5SUMS
```

**2C. SAM2 (ungated, Apache-2.0; run by found on gaint, see §3).**
```bash
cd /home/noob/work/weights
curl -L -f -o sam2.1_hiera_tiny.pt https://huggingface.co/facebook/sam2.1-hiera-tiny/resolve/de431c4043854a71d8101e17995dfe596bf101a5/sam2.1_hiera_tiny.pt
curl -L -f -o timm_sam2_hiera_tiny_fb_r896.safetensors https://huggingface.co/timm/sam2_hiera_tiny.fb_r896/resolve/92aa8e856f52f9224008a266757a30a91dc1894a/model.safetensors
sha256sum sam2.1_hiera_tiny.pt timm_sam2_hiera_tiny_fb_r896.safetensors   # expect 7402e0d8...34be69 / 3298636a...e2d69 (full values in the API listing)
md5sum sam2.1_hiera_tiny.pt timm_sam2_hiera_tiny_fb_r896.safetensors >> MD5SUMS
```

## 3. Done so far (E; md5 in `/home/noob/work/weights/MD5SUMS`, 31 Oct 17:37 IST on gaint)
- `sam2.1_hiera_tiny.pt`: 156,008,466 B; sha256 7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69 (= LFS oid); **md5 6aa6761c9da74fbaa74b4c790a0a2007**.
- `timm_sam2_hiera_tiny_fb_r896.safetensors`: 107,418,216 B; sha256 3298636ac6f04e2a2bacb56e63f555d6cde080528961defd5f97cd1bc96e2d69 (= LFS oid); **md5 c453c0749746456916fdd110ae8aa724**.
- **DINOv3: route B, chosen by the user on 1 Nov 2026 (~13:15 IST, relayed by team-lead, log.md 14:27).** User's words, verbatim: **"B: I accept, fetch timm"**. **The user accepts the DINOv3 License.** No token or login was involved: the timm repos are not gated.
  - Fetched 1 Nov 14:28 IST to gaint `/home/noob/work/weights/` with the §2B commands (pinned revisions):
    - `dinov3_convnext_tiny_lvd1689m_timm.safetensors`: 111,298,008 B; sha256 a7637753a2e85d709d1a5474e13382d39e7bc581a35868b477585c970f36847f (= LFS oid, MATCH); **md5 abf904631bf1ba23642e60c46b20dc5e**;
    - `dinov3_vits16_lvd1689m_timm.safetensors`: 86,362,376 B; sha256 2a1ec16ae28ffa07bc0ead0241ee7df9fc26451fe6f9f839b7b3afa0a906b040 (= LFS oid, MATCH); **md5 d6f2118f2b32975eb1eb2514d2612f31**.
  - **Key-format / equivalence check** (`found_scripts/dinov3_equiv.py` 864f7576 → `dinov3_equiv.txt` 7a9d78d7; CPU):
    - both files load strictly into timm's own models (180 / 162 keys, no missing or unexpected keys);
    - timm's pretrained-file path gives the identical state and forward (max |d| 0);
    - el_f8's wrapper (c280e8c2) carries the deep weights unchanged and RGB-sums the stem to 1 channel exactly; forward finite at 512.
    - Builder's review item (b) is closed. No remap is needed (timm format).

## 4. Budget
- SAM2 files: 263.4 MB.
- DINOv3 files: 197.7 MB (either route).
- sam2 package source: 0.39 MB.
- sam2 source tarball (one fetch, deleted after extraction): 55.6 MB.
- pip deps for the sam2 venv: ~0.4 MB.
- **Total ≈ 263.4 + 55.6 + 0.4 + 197.7 (DINOv3, fetched 1 Nov) ≈ 517 MB, all done.** The user's approval covers the ~17 MB over the 0.5 GB cap (team-lead).