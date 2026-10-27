# judge: image mode / colour of E1 cells vs test/train cells as stored in release 20221008 (does grayscale conversion differ?)
import glob, os, csv, collections
import numpy as np
from PIL import Image
R=os.path.expanduser('~/mtp/datasets/BenchmarkEL_releases/dataset_20221008')
img={os.path.basename(p)[:-4]:p for p in glob.glob(R+'/el_images_*/*.png')}
M='/home/yugma/mtp/research/results/e1/ext117_manifest.csv'
e1=[r['stem'] for r in csv.DictReader(open(M)) if r['in_external_pool']=='0']
SP=os.path.expanduser('~/mtp/datasets/splits_benchmark/')
te=[os.path.basename(l.strip()).replace('.png','') for l in open(SP+'test.txt') if l.strip()]
tr=[os.path.basename(l.strip()).replace('.png','') for l in open(SP+'train.txt') if l.strip()]
def info(stems):
    c=collections.Counter(); colour=0; n=0; sizes=collections.Counter()
    for s in stems:
        if s not in img: c['missing']+=1; continue
        im=Image.open(img[s]); c[im.mode]+=1; sizes[im.size]+=1; n+=1
        if im.mode in ('RGB','RGBA'):
            a=np.asarray(im.convert('RGB')).astype(int)
            if (np.abs(a[...,0]-a[...,1]).max()>8) or (np.abs(a[...,1]-a[...,2]).max()>8): colour+=1
    return dict(c), colour, n, sizes.most_common(3)
for name,st in [('E1',e1),('test',te),('train CSIR',[s for s in tr if s.startswith('CSIR')])]:
    print(name, info(st))
