# D42 notes (WIP)
started 13 Nov; covered ids from other D files in scratchpad covered_ids.txt
queries:
q1 thin structure noisy misaligned labels (2025+)
q2 curvilinear foundation model fine-tuning (2025+)
q3 tiny defect few labeled synthetic diffusion (2025+)
q4 imprecise boundary annotations label shift tolerant (2024+)
q5 DINOv3 dense features small dataset (2025+)
q6 feature upsampling thin structures (2025+) - mostly covered by D22/D24
q7 diffusion prior dense prediction few labels (2025+)
q8 sub-pixel centerline annotation offset (2023+) - noise
q9 multi-source heterogeneous annotation conventions (2025+) - noise
candidates so far: 2604.24575 diffusion generalist seg learner; 2409.11355 fine-tune image-cond diffusion (WACV25); 2508.00442 TopoTTA; 2512.17263 AnyCXR conditional joint annotation
q10 small training set beats FMs (2026)
q11 crack seg label noise width tolerance (2025+)
q12 rare class generative augmentation (2025+)
web1 CVPR 2026 thin noisy; web2 NeurIPS 2025 boundary label noise
cands: 2607.03068 PixCon FM-teacher SSL; 2604.10963 aleatoric VFM
q13 RankSEG (covered D18)
q14 rotation equivariant thin (noise)
q15 hard negative confounder outlier exposure (noise)
web3 ICCV25 thin; web4 MICCAI25 vessel noisy; web5 ICLR26 small-data FM
cands: 2607.05965 single-mask annotation noise detection MICCAI26; 2509.17816 GLARE continual SSL (TMLR26)
q16 formula-driven pretraining seg (SegRCDB ICCV23)
q17 domain-specific norm / MoE multi-domain (noise)
q18 non-uniform downsampling small objects (noise)
webs: crack label noise 2026 (extended); EL foundation 2026
q19 large kernel (ShiftwiseConv CVPR25 2401.12736)
q20 procedural synthetic curves pretraining (rock joint 2602.07590)
q21 data attribution seg (AIO2 2403.01641, 2506.05647)
web: ECCV 2026 thin/noise (SEMIR covered; CSWinUNETR 2606.19824 MICCAI26 code github.com/labhai/CSWinUNETR NEW)
web: CVPR 2026 defect synth (FAST 2509.20295 NeurIPS25 code github.com/Chhro123/fast-foreground-aware-anomaly-synthesis NEW)
ShiftwiseConv 2401.12736 CVPR25 code github.com/lidc54/shift-wiseConv NEW
single-mask noise detection 2607.05965 MICCAI26 code per abstract (unverified URL)
webfetch papernotes NeurIPS2025 segmentation list (45 entries)
cands: DiDA 2412.10339 NeurIPS25 degradation intermediate domains UDA; SDD 2510.17299 NeurIPS25 SSL dense degradation; ECOCSeg 2512.06870 NeurIPS25 code github.com/Woof6/ECOCSeg
webfetch papernotes CVPR2026 segmentation (125) + ICCV2025 segmentation (75)
cands: Learn2Synth 2411.16719 ICCV25; SACM dual-level adapter CVPR26 oral (no arXiv id; CVF only, same group as UCS 2504.04034 covered); MatchMask CVPR26 (no id, code unverified); ConformalSAM ICCV25; Kalos CVPR26 IAA metric
q22 spurious context / layout OOD (noise)
q23 synthetic-only domain randomization thin crack (InsCore? 2505.13099 Industrial Synthetic Segment Pretraining)
ConformalSAM 2507.15803 ICCV25 new; Learn2Synth code github.com/HuXiaoling/Learn2Synth (from abstract)
snowball: citations of NSegment+ (SegFaultLoc doi:10.1145/3832783.3837428 ASE26; Beyond NN interp 2504.01527), citations of Learn2Synth (nothing new)
fulltext read: CSWinUNETR (FIVES Dice 90.71 vs nnUNetv2 89.26, FFHQ-Wrinkle 64.75 vs 63.27; 31M params; code github.com/labhai/CSWinUNETR), ConformalSAM (VOC full +1.7 vs AllSpark; ADE 1/128 +10)
bench cands: Kalos 2603.27197 CVPR26; Torch-Uncertainty 2511.10282 NeurIPS25; SDD 2510.17299 code github.com/EldercatSAM/SSL-Degradation
more: DINOv3-IML 2604.16083 code github.com/Irennnne/DINOv3-IML; SegRCDB 2309.17083 code github.com/dahlian00/SegRCDB; rock joint 2602.07590; ECOCSeg; writing final md now
DONE: final report D42_recent_venue_sweep.md written 13 Nov
