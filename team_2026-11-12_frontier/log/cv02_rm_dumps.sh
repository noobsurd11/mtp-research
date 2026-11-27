n=0; bad=0; df -h /tmp | tail -1
while read B run md5; do
  f=$B/runs/$run/RUN.md5
  [ -f "$f" ] && [ "$(md5sum < $f | cut -c1-32)" = "$md5" ] || { echo "SKIP mismatch $run"; bad=$((bad+1)); continue; }
  d=$(ls -d $B/dumps/elbench1/*/$run 2>/dev/null)
  [ -n "$d" ] && [ "$(echo "$d" | wc -l)" = 1 ] || { echo "SKIP nodir $run"; bad=$((bad+1)); continue; }
  echo "$d" | grep -qE "^/tmp/noob_el/bench_(52e3f14|d3a3280)/dumps/elbench1/[A-Za-z0-9_]+/$run\$" || { echo "SKIP path $d"; bad=$((bad+1)); continue; }
  rm -rf -- "$d" && n=$((n+1)) && echo "$(date -u +%FT%T) removed $d (gaint copy verified, RUN.md5 $md5)" >> /tmp/noob_el/removed_relayed_dumps_20261115.log
done <<'LIST'
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f2_s5 7fd54492ec60e317e2f0ae5db0f18cda
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f3_s6 41d477af89d6e8c1b794299b3c84a646
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f3_s5 a7aee3c21731369e84c67d5c39a11cae
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f2_s6 a67428e70659dbe19803cb0d665f7e39
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f0_s5 847627e9f649658b207c22e71cb9552c
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f0_s6 0532a59143a7f836cb006659dee21f28
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f1_s5 93fe112a2932bdedf06491538e77ac17
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f1_s6 488cd9fafe7c2b050b3ddd6f3079a09d
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f4_s5 6f29a23d81f23918470289d1daec9169
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f0_s5 c63cbcb5c0db0a793a4157cef9819834
/tmp/noob_el/bench_52e3f14 r1_dlv3p_r34_pf_f4_s6 4816fb94702b5eabbb37324fbef975b7
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f0_s6 96e80b9b08ed5a78f79b2d36c29d9682
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f2_s5 aaf3c6e292baadf38f438923393014b1
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f2_s6 4426bdd525fead9ba175f825c79c937a
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f1_s6 c9ba8db8d64724e6d4d6d76bf817d0a0
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f1_s5 6260f19238c43b5f0e27af008379b726
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f3_s5 085460d204ce5567a776bfc52d0c6a17
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f3_s6 a8a103ec4e455886c44120ea508c2b3a
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f4_s5 b29ce8fce3aaf3985a0ebe6c1213484f
/tmp/noob_el/bench_52e3f14 r1_hanifi_vgg16_unet_pf_f4_s6 3fd8455d75819eccedaab8aacc297fc3
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f0_s5 e91e445afdd1b6f5a08089978ba10b16
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f0_s6 429ca31f4d2e92d2af00336b45ea2e60
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f1_s5 a7a870de83c4fc7730563011a53e10d2
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f1_s6 964aeea061981cd1e620404a7e4d490d
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f2_s6 85af320f4524030c97809db38ce8973e
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f2_s5 7b1ea0ea745ad2af40f1defcdcb0c320
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f3_s5 9b81d4764004145203b19b14705e0cee
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f3_s6 32a65e0105ab40071ef95ebded0d7ec1
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f4_s5 5d4614024d99ba975652a20713d1b6a5
/tmp/noob_el/bench_52e3f14 r1_pratt_dlv3p_wcec_f4_s6 081a100759a9400f1ef13e4d5c0a47c2
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f0_s6 efed56de204a35424e5bb3ef00818655
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f0_s5 76441202fb3e6d022af60918cacbf022
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f2_s5 911b4edb675cdea767ed6a1121bc34cf
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f2_s6 3ad3e1dc677ef730abc16558ff6ec179
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f1_s5 5e47a6e3b6def7d983d8f05c5d919875
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f1_s6 9c0e218304847312aac579792517b5f0
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f3_s5 ad5af3e03dc41c17732557a713d6ed5b
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f3_s6 6833065200f5287572790a74f7c79ca2
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f4_s5 87f587ba44376f988f7efcfd6b3a237e
/tmp/noob_el/bench_52e3f14 r1_ucf_dlv3_r50_pf_f4_s6 cc23d4e4547a580cc44844ce6ed84746
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f0_s5 090cce81057b41314cf69026a22b267d
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f0_s6 60a03f8fd780bb82ab38b29aac5dcd25
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f1_s5 85ed0afecb43d9cafc528f5bebccd200
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f1_s6 51fdcb2477f27e267c0c1e1c1bcf07a7
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f2_s5 9c75546412c5350da24b10953e2a71d3
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f2_s6 fc7174240fdd7cde98b360c411e304d5
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f3_s5 6358a5b0f456f9356b4b3c2d236cb420
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f3_s6 b1dad667eae8c9c3828b3e200deea17f
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f0_s5 b93fa61a1a1f69e5304733e3e4df4df1
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f0_s6 10a1289fb6dcac062bd9ae58079e7499
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f4_s5 860731a68ebddd1c8fdea5f954885b9c
/tmp/noob_el/bench_52e3f14 r1_unet_r34_pf_f4_s6 653c5fec7159d2aaad059340fccb05dc
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f0_s7 5f681c72b297ae6f723671662f5393d6
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f0_s8 f5bd421df695e10af4749e2716420d1d
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f0_s9 b2f61b367850e6673cd0ba627b2d4457
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f1_s5 201b193984c52591af68f4247814ae10
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f1_s6 7301ccb83f2f7701ab855044971366e8
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f2_s5 f2cbc869d07e3a2b29ebd7e21eae081d
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f2_s6 023bdf8c4db30f36f3a70840fc348985
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f1_s8 bb0b3b0106b5faa18d81247ddc1cb0c9
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f1_s9 fa1c3710d73aca8e3ea9c64470cbac69
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f1_s7 84bda02ec1eb436376878226d067000b
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f2_s7 257587d57a8e3d048e3358c7889f5975
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f2_s8 8d517dce64973fe585f8995518926d38
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f3_s5 17f0a78e6d0c8cddffbda4dc162c54e0
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f3_s6 595ffdda14e340340a4babe777a02ff8
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f2_s9 1884184c1d2ded4205fc940b0a6f6cb1
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f3_s8 8391602023bfee8c49024a16fab2b65a
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f3_s9 4ec44c2c1460a94b5803eb6f2a710c7f
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f3_s7 cf785d047157f421e819e03850254d2d
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f4_s6 f9d12d968f371ac2937a21dcf7b00d7a
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f4_s5 046957f2a351ec0332430bd86ff2e8ce
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f0_s5 42b163fd8bfc2be39ffdec38a55ead5c
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f0_s6 3c37dd8958ccb1b53f873689a5ee9db4
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f1_s5 55668de12af0dca35f7bbc8a211b3cf7
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f2_s5 6bfbabbf9bffeca3020303c237110d1b
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f1_s6 b3fbf6a89e8efa662b1d4f6d6a6effe5
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f3_s5 edcb63423ba2ef372c802d960b5edbea
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f2_s6 bcf2855bb719fe707646f7d63bee514e
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f3_s6 13f393830bda19983f5996138f354077
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f4_s5 952a3e443db097826e8118e54dbf3b05
/tmp/noob_el/bench_d3a3280 w1c2_house_v11_f4_s6 7ec0a3e6f5209cefc00596e3f3fd00fc
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f0_s5 d62c35902b434e5e44aee159030e84c0
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f1_s5 1c9b9ae54746b5323529f13504f3c4dc
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f0_s6 5f21c0bd38a5dc85797874257a473b8f
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f2_s5 7b033cb5bdf2314e7f0b8949a4c7996a
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f1_s6 b194b755e0a0d2db5d95024b29234ada
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f4_s9 10bda19558a9804218f7bfbc27a8ca55
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f4_s8 fba9945c97fd63e9316bebb56512ca6a
/tmp/noob_el/bench_d3a3280 w1c1_pf_v11_f4_s7 ff59d7b8c41c6b2609ff9793f20155bb
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f2_s6 04be40a55359629c0ec2f79321d044b2
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f3_s5 2411d99df8ed387d06a408e69e9bd1a4
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f3_s6 e035aa17042b36da419562a2127ef4dd
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f4_s5 8b4ca145ac488dca0bec33ba0baba0bc
/tmp/noob_el/bench_d3a3280 w1c3_pf_v1_f4_s6 166dce28bec4fabe132f245ab092dd24
LIST
echo "removed $n dump dirs; skipped $bad"; df -h /tmp | tail -1; du -sh /tmp/noob_el/bench_52e3f14 /tmp/noob_el/bench_d3a3280 | tr "\n" ";"; echo; ls /tmp/noob_el/bench_52e3f14/runs/*/RUN.md5 | wc -l; ls /tmp/noob_el/bench_52e3f14/experiments/r1_unet_r34_pf_f0_s5/checkpoints
