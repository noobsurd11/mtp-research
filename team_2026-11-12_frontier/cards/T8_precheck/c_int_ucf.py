import csv, json, os, sys, random, numpy as np, collections
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
R=os.path.expanduser('~/mtp/datasets/UCF-EL-Defect')
imgs={}
for sp in ('train','test'):
    d=f'{R}/training/data/{sp}/images'
    for f in os.listdir(d): imgs[os.path.splitext(f)[0]]=(f'{d}/{f}', f'{R}/training/data/{sp}/annotations')
regs=collections.defaultdict(list)
with open(f'{R}/AnnotationsCombined.csv') as fh:
    for r in csv.DictReader(fh):
        st=os.path.splitext(r['filename'])[0]
        if st not in imgs: continue
        c=json.loads(r['region_attributes'] or '{}').get('Defect_Class'); g=json.loads(r['region_shape_attributes'] or '{}')
        if c: regs[st].append((c,g))
random.seed(0)
out=collections.defaultdict(list); sizes=collections.Counter(); isoarea=[]
for cls in ('Crack_Isolated','Crack_Resistive','Crack_Closed'):
    cand=[s for s in regs if any(c==cls for c,_ in regs[s])]
    for s in random.sample(cand,min(300,len(cand))):
        p,ad=imgs[s]
        if p.endswith('.png'): continue
        im=Image.open(p).convert('L'); W,H=im.size; a=np.array(im).astype(float)
        mp=os.path.join(ad,'Annotated_'+os.path.splitext(os.path.basename(p))[0]+'.png')
        if not os.path.exists(mp): continue
        m=np.array(Image.open(mp))
        if m.shape!=a.shape: continue
        cv=Image.new('L',(W,H),0); dr=ImageDraw.Draw(cv)
        for c,g in regs[s]:
            if c!=cls: continue
            if g.get('name')=='polygon': dr.polygon(list(zip(g['all_points_x'],g['all_points_y'])),fill=1)
            elif g.get('name')=='rect': dr.rectangle([g['x'],g['y'],g['x']+g['width'],g['y']+g['height']],fill=1)
        reg=np.array(cv).astype(bool)
        if cls!='Crack_Closed': reg=ndi.binary_erosion(reg,iterations=2)
        bg=(m==0)
        if reg.sum()<30 or bg.sum()<500: continue
        out[cls].append(float(np.median(a[reg])/max(np.median(a[bg]),1e-6)))
        sizes[(W,H)]+=1
        if cls=='Crack_Isolated': isoarea.append(reg.sum()/(W*H))
for cls,v in out.items():
    print(cls,'n=%d ratio median %.3f IQR %.3f-%.3f; share <=0.60: %.2f'%(len(v),np.median(v),*np.percentile(v,[25,75]),np.mean(np.array(v)<=0.60)))
print('isolated region area share of image: median %.3f IQR %.3f-%.3f'%(np.median(isoarea),*np.percentile(isoarea,[25,75])))
print('sizes',sizes.most_common(4))
