# x4: dump folder templates on gaint ({k} fold, {s} seed); sourced by x4 scripts. cv5v3, cv02, fp32.
RLY=/home/noob/work/bench_relay
PF_T="$RLY/c3base/c3_pf_v11_f{k}_s{s}/dumps/elbench1/house_r34_unetpp_pf_v11/c3_pf_v11_f{k}_s{s}"                       # PF, key model
COMBO_BN_T="$RLY/c3x/c3x_hrnet_swad_v11_f{k}_s{s}/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/c3x_hrnet_swad_v11_f{k}_s{s}"  # key swad_bn
COMBO_T="$COMBO_BN_T.swad"                                                                                         # key swad (the x4 comparator)
# X4_T QN SHORT METHOD SUFFIX: a relayed x4 run x4_<SHORT>_f{k}_s{s} of queue QN; SUFFIX '' (card weights_key) or '.swad'
X4_T(){ echo "$RLY/x4_$1/x4_$2_f{k}_s{s}/dumps/elbench1/$3/x4_$2_f{k}_s{s}$4"; }
