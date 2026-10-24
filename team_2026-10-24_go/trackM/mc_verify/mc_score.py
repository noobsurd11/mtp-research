"""MC independent scorer: reads MD's per-cell M0 JSONs (24x24 conf + crack_rel2), recomputes pooled metrics.
Usage: python mc_score.py <json> [...]   (prints per run; no shared code with MD's m0_analyze.py)"""
import json,sys,numpy as np
NC,CR,IN=24,14,11
TWINS={'CFVS_00006_r5_c5','CFVS_00033_r8_c4','CFVS_00035_r8_c4','CFVS_00042_r8_c4','CFVS_00018_r4_c4','CFVS_00027_r4_c4','ARTS_00020_r5_c1'}
NOISY='CSIR_00070_r8_c4'
def pool(cells,keep):
    C=np.zeros((NC,NC));r=np.zeros(4)
    for s,c in cells.items():
        if keep(s): C+=np.array(c['conf'],float).reshape(NC,NC); r+=c['crack_rel2']
    return C,r
def met(C,r,cls_gt=None):
    tp=np.diag(C);g=C.sum(1);p=C.sum(0);den=g+p-tp
    iou=np.where(den>0,tp/np.maximum(den,1),np.nan)
    present=g>0 if cls_gt is None else cls_gt
    o=dict(crack_iou=iou[CR],crack_P=tp[CR]/max(p[CR],1),crack_R=tp[CR]/max(g[CR],1),
           inact_iou=iou[IN],inact_P=tp[IN]/max(p[IN],1),inact_R=tp[IN]/max(g[IN],1))
    rp=r[0]/max(r[1],1);rr=r[2]/max(r[3],1);o.update(relP2=rp,relR2=rr,relF1=2*rp*rr/max(rp+rr,1e-12))
    o['miou_gt']=np.nanmean(iou[present]);m2=present.copy();m2[[0,7]]=False;o['miou_gt_nobgpad']=np.nanmean(iou[m2])
    o['miou24']=np.nanmean(iou);o['iou']=iou;o['present']=present
    return o
SETS={'all':lambda s:True,'noNoisy':lambda s:s!=NOISY,'noTwins':lambda s:s not in TWINS,'noBoth':lambda s:s!=NOISY and s not in TWINS}
for src in ['CFVS','BMRK','ARTS','CSIR']: SETS[src]=(lambda q:lambda s:s.startswith(q))(src)
def score(path,split='test'):
    d=json.load(open(path));cells=d['cells'][split];out={}
    Call,_=pool(cells,lambda s:True);gtcls=Call.sum(1)>0
    for k,f in SETS.items():
        C,r=pool(cells,f);out[k]=met(C,r,gtcls)
    return d,out
if __name__=='__main__':
    for p in sys.argv[1:]:
        d,o=score(p)
        a=o['all'];print(d['run'],d['step'],'crack %.4f P %.4f R %.4f inact %.4f relF1 %.4f mIoU_gt %.4f nobgpad %.4f n_gtcls %d'%(a['crack_iou'],a['crack_P'],a['crack_R'],a['inact_iou'],a['relF1'],a['miou_gt'],a['miou_gt_nobgpad'],a['present'].sum()))
